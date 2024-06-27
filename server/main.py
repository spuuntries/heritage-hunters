from uuid import uuid4
from engineio import client
from pydantic import ValidationError
from sanic import Sanic, Request, HTTPResponse
from sanic_limiter import Limiter, get_remote_address
from tortoise import Tortoise, run_async
from tortoise.contrib.sanic import register_tortoise
from dbsetup import init as initdb
from auth import check_token, create_token
from generate import generate_maze, generate_world
from dotenv import load_dotenv
import socketio
import niceware
import crypto
import random
import models
import sanic
import json
import jwt
import os

load_dotenv()
sio = socketio.AsyncServer(async_mode="sanic")
app = Sanic(name="hh_server")
limiter = Limiter(app, key_func=get_remote_address)
sio.attach(app)
register_tortoise(
    app,
    db_url="sqlite://db.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
)

NUMQUEUES = 4
QUEUESIZE = 2 if not os.environ.get("QUEUESIZE") else int(os.environ["QUEUESIZE"])
queues: dict[str, list[tuple[str, str]]] = {str(uuid4()): [] for _ in range(NUMQUEUES)}
rooms: list[list] = []


@app.post("/register")
@limiter.limit("4/day")
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
        userexists = await models.User.exists(name=username)
        if userexists:
            return HTTPResponse("Username exists", 409)
        password = " ".join(niceware.generate_passphrase(8))
        hashed = crypto.derive_key(password)
        await models.User.create(name=username, password=hashed, body=body)
        return HTTPResponse(password, 200)
    except:
        return HTTPResponse("Internal server error", 500)


@app.post("/login")
@limiter.limit("20/day")
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
            token = create_token({"user": user.name, "clientid": str(user.clientid)})
            return HTTPResponse(token, 200)
        else:
            return HTTPResponse("Unauthorized", 403)
    except:
        return HTTPResponse("Internal server error", 500)


async def queuestatus():
    global rooms
    while True:
        for _, queue in queues.items():
            for client in queue[1:]:
                await sio.emit("statusqueue", len(queue) - 1, to=client)
        if len(rooms):
            rooms = list(filter(lambda room: len(room), rooms))
        await sio.sleep(2)


async def processqueue():
    while True:
        for queueid, queue in queues.items():
            if len(queue) >= QUEUESIZE + 1:
                type = queue.pop(0)
                rooms.append(queue)
                for client, _ in queue:
                    await sio.emit("donequeue", None, to=client)

                if type == "maze":
                    maze = generate_maze(
                        39,
                        39,
                        players=list(map(lambda qe: qe[1], queue)),
                        enemies=["393"] * 20,
                        wall=13,
                    )

                    for client, _ in queue:
                        await sio.emit(
                            "worldgen",
                            (
                                maze,
                                list(map(lambda qe: qe[1], queue)),
                            ),
                            to=client,
                        )

                if type == "hide-n-seek":
                    world = generate_world(
                        39,
                        39,
                        players=list(map(lambda qe: qe[1], queue)),
                        enemies=["390"] * 5,
                        wall=10,
                    )

                    for client, _ in queue:
                        await sio.emit(
                            "worldgen",
                            (
                                world,
                                list(map(lambda qe: qe[1], queue)),
                            ),
                            to=client,
                        )
                queues[queueid] = []
        await sio.sleep(2)


@app.listener("before_server_start")
def before_server_start(sanic, loop):
    sio.start_background_task(queuestatus)
    sio.start_background_task(processqueue)


@sio.event
async def connect(sid, environ, auth, *args, **kwargs):
    print(auth)
    if not check_token(auth["token"]):
        await sio.emit("unauthorized", to=sid)
        await sio.disconnect(sid)
        return
    secret = os.environ["JWT_SECRET"] if os.environ.get("JWT_SECRET") else "BALLS"
    token = jwt.decode(auth["token"], secret, algorithms=["HS256"])
    print(token)
    await sio.emit("connected", token["clientid"], to=sid)


@sio.event
async def joinqueue(sid, type, clientid, *args, **kwargs):
    space = list(filter(lambda q: q[1] and q[1][0] == type, queues.items()))
    queueId = space[0][0] if space else random.choice(list(queues.keys()))  # type: ignore
    if not len(queues[queueId]):
        queues[queueId].append(type)
    queues[queueId].append((sid, clientid))
    print(queues)
    await sio.emit("idqueue", queueId, to=sid)


@sio.on("playermove")  # type: ignore
async def playermove(sid, id, x, y, status, *args, **kwargs):
    if any(client[0] == sid for room in rooms for client in room):
        room = next(room for room in rooms for client in room if client[0] == sid)
        for client, _ in room:
            if client == sid:
                continue
            await sio.emit(
                "stateupdate",
                {
                    "type": "move",
                    "id": id,
                    "x": round(x / 64) * 64,
                    "y": round(y / 64) * 64,
                    "stat": status,
                },
                to=client,
            )


@sio.event
async def disconnect(sid):
    print("Client disconnected")
    print(rooms)
    if any(client[0] == sid for queue in queues.values() for client in queue):
        queue = next(
            queue for queue in queues.values() for client in queue if client[0] == sid
        )
        trclient = list(filter(lambda client: client[0] == sid, queue))[0]
        queue.remove(trclient)
    if any(client[0] == sid for room in rooms for client in room):
        room = next(room for room in rooms for client in room if client[0] == sid)
        trclient = list(filter(lambda client: client[0] == sid, room))[0]
        room.remove(trclient)
        for client, _ in room:
            if client == sid:
                continue
            await sio.emit(
                "stateupdate",
                {
                    "type": "dc",
                    "id": str(trclient[1]),
                },
                to=client,
            )
