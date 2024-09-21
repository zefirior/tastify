import enum
from datetime import datetime

import reflex as rx
import sqlmodel

from tastify.core.time_utils import get_datetime_column


class GameState(enum.StrEnum):
    NEW = "NEW"
    PREPARING = "PREPARING"
    PROPOSE = "PROPOSE"
    GUESS = "GUESS"
    RESULTS = "RESULTS"


class Game(rx.Model, table=True):
    room_id: int = sqlmodel.Field(foreign_key="room.id")
    state: GameState
    round: int = 0
    created_by: str = sqlmodel.Field(foreign_key="user.uid")
    created_at: datetime = get_datetime_column()


class UserGame(rx.Model, table=True):
    user_uid: str = sqlmodel.Field(foreign_key="user.uid", primary_key=True)
    game_id: int = sqlmodel.Field(foreign_key="game.id", primary_key=True)
    order: int
    name: str
    score: int = 0
    active: bool = False

    def __eq__(self, other):
        if not self or not other:
            return False
        return self.user_uid == other.user_uid and self.game_id == other.game_id
