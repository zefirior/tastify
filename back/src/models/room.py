import enum
import secrets
import string
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.player import Player
    from src.models.game_round import GameRound


class RoomStatus(enum.Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"
    ABANDONED = "abandoned"  # Closed due to inactivity


def generate_room_code() -> str:
    """Generate a random 6-character uppercase room code."""
    return "".join(secrets.choice(string.ascii_uppercase) for _ in range(6))


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(6), unique=True, index=True, default=generate_room_code)
    game_type: Mapped[str] = mapped_column(String(50), default="guess_number", index=True)
    status: Mapped[RoomStatus] = mapped_column(Enum(RoomStatus), default=RoomStatus.WAITING)
    host_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_round_number: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    players: Mapped[list["Player"]] = relationship("Player", back_populates="room", cascade="all, delete-orphan")
    rounds: Mapped[list["GameRound"]] = relationship("GameRound", back_populates="room", cascade="all, delete-orphan")
