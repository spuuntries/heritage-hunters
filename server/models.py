from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel
from enum import Enum
import json


class BodyType(str, Enum):
    TINGGI = "TINGGI"
    PENDEK = "PENDEK"
    BESAR = "BASER"
    KURUS = "KURUS"


class User(Model):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=256)
    password = fields.TextField()
    body = fields.CharEnumField(BodyType)


class RegisterUserRequest(BaseModel):
    username: str
    body: str


class LoginUserRequest(BaseModel):
    username: str
    password: str
