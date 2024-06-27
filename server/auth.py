from dotenv import load_dotenv

load_dotenv()

from datetime import datetime, timedelta
from functools import wraps
from sanic import text
import jwt
import os


def check_token(token):
    try:
        secret = os.environ["JWT_SECRET"] if os.environ.get("JWT_SECRET") else "BALLS"
        jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError or jwt.exceptions.ExpiredSignatureError:
        return False

    return True


def create_token(payload):
    secret_key = os.environ["JWT_SECRET"] if os.environ.get("JWT_SECRET") else "BALLS"
    token = jwt.encode(
        payload,
        secret_key,
        algorithm="HS256",
    )
    return token
