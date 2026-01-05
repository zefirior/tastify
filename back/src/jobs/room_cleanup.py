import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.jobs.base import BaseJob
from src.models import Room, RoomStatus
from src.schemas.websocket import WSEventType
from src.services import connection_manager

logger = logging.getLogger(__name__)


class RoomCleanupJob(BaseJob):
    """
    Background job that closes rooms that have been inactive for too long.
    
    Rooms in WAITING or PLAYING status that haven't been updated within
    the configured threshold will be closed with ABANDONED status.
    """

    lock_id = 1002  # Unique ID for room cleanup lock
    interval_seconds = settings.room_cleanup_job_interval
    job_name = "RoomCleanupJob"

    async def execute(self, session: AsyncSession):
        """Find and close inactive rooms."""
        threshold = datetime.now(timezone.utc) - timedelta(
            hours=settings.room_inactivity_threshold_hours
        )

        # Find all active rooms (WAITING or PLAYING) with old updated_at
        result = await session.execute(
            select(Room).where(
                Room.status.in_([RoomStatus.WAITING, RoomStatus.PLAYING]),
                Room.updated_at < threshold,
            )
        )
        inactive_rooms = result.scalars().all()

        for room in inactive_rooms:
            await self._close_room(session, room)

    async def _close_room(self, session: AsyncSession, room: Room):
        """Close an inactive room with ABANDONED status."""
        logger.info(
            f"Closing inactive room {room.code} "
            f"(last updated: {room.updated_at}, status: {room.status.value})"
        )

        room.status = RoomStatus.ABANDONED

        # Notify any connected clients that the room was closed
        await connection_manager.broadcast_to_room(
            room.code,
            WSEventType.ROOM_CLOSED,
            {"reason": "inactivity"},
        )

