from datetime import datetime, timezone

import reflex as rx
import sqlmodel

from tastify.core.time_utils import get_datetime_column


class Room(rx.Model, table=True):
    code: str = sqlmodel.Field(unique=True)
    created_at: datetime = get_datetime_column()


class UserRoom(rx.Model, table=True):
    user_uid: str = sqlmodel.Field(foreign_key="user.uid", primary_key=True)
    room_id: int = sqlmodel.Field(foreign_key="room.id", primary_key=True)
    score: int = sqlmodel.Field(default=0)
    name: str
