import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import reflex as rx
import sqlmodel

from sqlalchemy import JSON

from tastify.core.time_utils import get_datetime_column


class GameState(enum.StrEnum):
    NEW = "NEW"
    PREPARING = "PREPARING"
    PROPOSE = "PROPOSE"
    GUESS = "GUESS"
    RESULTS = "RESULTS"


"""
game data
{
    "rounds": {
        0: {
            "artist": {
                "name": "Linkin Park",
                "id": "6XyY86QOPPrYVGvF9ch6wz"
            },
            "players": {
                "user_uid": {
                    "track": {
                        "name": "In the End",
                        "id": "60a0Rd6pjrkxjPbaKzXjfq",
                    }
                }
            }
        }
    }
}
"""

@dataclass
class RoundArtistDto:
    name: str
    id: str


@dataclass
class RoundPlayerDto:
    track: dict[str, Any] | None
    skipped: bool = False


@dataclass
class GameRoundDto:
    selected_artist: dict[str, Any]
    players: dict[str, RoundPlayerDto]

    def get_selected_track(self) -> dict[str, Any] | None:
        return RoundArtistDto(**self.selected_artist)


@dataclass
class GameDto:
    rounds: dict[int, GameRoundDto]

    def get_round_data(self, round: int) -> GameRoundDto:
        return self.rounds[round]


class Game(rx.Model, table=True):
    room_id: int = sqlmodel.Field(foreign_key="room.id")
    state: GameState
    round: int = 0
    created_by: str = sqlmodel.Field(foreign_key="user.uid")
    created_at: datetime = get_datetime_column()
    data: GameDto = sqlmodel.Field(
        default={},
        sa_type=JSON,
    )

    def get_data(self) -> GameDto:
        return self.data

    def set_data(self, data):
        self.data = data


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
