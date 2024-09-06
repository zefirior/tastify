from datetime import datetime, timezone

import reflex as rx
import sqlmodel


def get_utc_now():
    return datetime.now(timezone.utc)


class Room(rx.Model, table=True):
    """Game room."""
    code: str = sqlmodel.Field(unique=True)
    created_at: datetime = sqlmodel.Field(
        default_factory=lambda : get_utc_now(),
        sa_type=sqlmodel.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sqlmodel.func.now(),
        },
        nullable=False,
    )


class UserRoom(rx.Model, table=True):
    """User's room."""
    user_uid: str = sqlmodel.Field(foreign_key="user.uid", primary_key=True)
    room_id: int = sqlmodel.Field(foreign_key="room.id", primary_key=True)
    name: str
