from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base

if TYPE_CHECKING:
    from src.models.room import Room


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(50))
    score: Mapped[int] = mapped_column(Integer, default=0)
    current_guess: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_host: Mapped[bool] = mapped_column(default=False)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    room: Mapped["Room"] = relationship("Room", back_populates="players")

