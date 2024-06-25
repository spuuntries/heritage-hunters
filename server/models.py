from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel
from enum import Enum
import json


class BodyType(str, Enum):
    TINGGI = "TINGGI"
    PENDEK = "PENDEK"
    BESAR = "BESAR"
    KURUS = "KURUS"


async def get_next_value():
    tracker = await AutoincrementTracker.first()
    if not tracker:
        tracker = await AutoincrementTracker.create(current_value=500)
    current_value = tracker.current_value
    tracker.current_value += 1
    await tracker.save()
    return current_value


class AutoincrementTracker(Model):
    id = fields.IntField(pk=True)
    current_value = fields.IntField(default=500)

    class Meta:
        table = "autoincrement_tracker"


class User(Model):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    clientid = fields.IntField(default=get_next_value)
    name = fields.CharField(max_length=256)
    password = fields.TextField()
    body = fields.CharEnumField(BodyType)


class RegisterUserRequest(BaseModel):
    username: str
    body: str


class LoginUserRequest(BaseModel):
    username: str
    password: str
