from pydantic import ValidationError
from sanic import Sanic, Request, json, HTTPResponse
from sanic_limiter import Limiter, get_remote_address
from tortoise import Tortoise, run_async
from tortoise.contrib.sanic import register_tortoise
from dbsetup import init as initdb
from auth import check_token, create_token
import socketio
import niceware
import crypto
import models
import json
import os

sio = socketio.AsyncServer(async_mode="sanic")
app = Sanic(name="sanic_application")
limiter = Limiter(app, key_func=get_remote_address)
sio.attach(app)
register_tortoise(app, db_url="sqlite://db.sqlite3", modules={"models": ["models"]})


@app.post("/register")
@limiter.limit("10/day")
async def register(request: Request):
    RegisterUserModel = models.RegisterUserRequest
    if not request.json:
        return HTTPResponse("Missing parameters", 400)
    try:
        RegisterUserModel.model_validate_json(json.dumps(request.json))
    except ValidationError as e:
        return HTTPResponse(str(e), 400)
    try:
        username = request.json.get("username")
        body = request.json.get("body")
        password = " ".join(niceware.generate_passphrase(8))
        hashed = crypto.derive_key(password)
        await models.User.create(name=username, password=hashed, body=body)
        return HTTPResponse(password, 200)
    except:
        return HTTPResponse("Internal server error", 500)


@app.post("/login")
@limiter.limit("20/minute")
async def login(request: Request):
    LoginUserModel = models.LoginUserRequest
    if not request.json:
        return HTTPResponse("Missing parameters", 400)
    try:
        LoginUserModel.model_validate_json(json.dumps(request.json))
    except ValidationError as e:
        return HTTPResponse(str(e), 400)
    try:
        username = request.json.get("username")
        password = request.json.get("password")
        password = " ".join(password.split())
        user = await models.User.get(name=username)
        if user.password == crypto.derive_key(
            plaintext=password, salt=bytes.fromhex(user.password.split("|")[-1])
        ):
            token = create_token({"user": user.name})
            return HTTPResponse(token, 200)
        else:
            return HTTPResponse("Unauthorized", 403)
    except:
        return HTTPResponse("Internal server error", 500)


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit("my_response", {"data": "Server generated event"})


@app.listener("before_server_start")
def before_server_start(sanic, loop):
    sio.start_background_task(background_task)


@sio.event
async def my_event(sid, message):
    await sio.emit("my_response", {"data": message["data"]}, room=sid)


@sio.event
async def join(sid, message):
    await sio.enter_room(sid, message["room"])
    await sio.emit(
        "my_response", {"data": "Entered room: " + message["room"]}, room=sid
    )


@sio.event
async def leave(sid, message):
    await sio.leave_room(sid, message["room"])
    await sio.emit("my_response", {"data": "Left room: " + message["room"]}, room=sid)


@sio.event
async def my_room_event(sid, message):
    await sio.emit("my_response", {"data": message["data"]}, room=message["room"])


@sio.event
async def disconnect_request(sid):
    await sio.disconnect(sid)


@sio.event
async def connect(sid, environ, auth, *args, **kwargs):
    print(auth)
    if not check_token(auth["token"]):
        await sio.emit("unauthorized", to=sid)
        await sio.disconnect(sid)
        return
    await sio.emit("connected", None, to=sid)


@sio.event
def disconnect(sid):
    print("Client disconnected")


if __name__ == "__main__":
    app.run(port=5000, dev=True)
