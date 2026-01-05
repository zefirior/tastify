from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.jobs.room_cleanup import RoomCleanupJob
from src.models import Room, RoomStatus


class TestRoomCleanupJob:
    """Tests for the RoomCleanupJob."""

    async def test_closes_inactive_waiting_room(self, session: AsyncSession):
        """Test that inactive WAITING rooms are closed with ABANDONED status."""
        # Create a room that is older than the threshold
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        room = Room(status=RoomStatus.WAITING)
        session.add(room)
        await session.flush()

        # Manually set updated_at to an old value
        room.updated_at = old_time
        await session.commit()

        # Run the cleanup job
        job = RoomCleanupJob()
        with patch.object(job, "interval_seconds", 0):  # Skip interval for testing
            with patch("src.jobs.room_cleanup.connection_manager") as mock_cm:
                mock_cm.broadcast_to_room = AsyncMock()
                await job.execute(session)

        await session.commit()

        # Verify the room was closed
        result = await session.execute(select(Room).where(Room.id == room.id))
        updated_room = result.scalar_one()
        assert updated_room.status == RoomStatus.ABANDONED

        # Verify broadcast was sent
        mock_cm.broadcast_to_room.assert_called_once()

    async def test_closes_inactive_playing_room(self, session: AsyncSession):
        """Test that inactive PLAYING rooms are closed with ABANDONED status."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        room = Room(status=RoomStatus.PLAYING)
        session.add(room)
        await session.flush()

        room.updated_at = old_time
        await session.commit()

        job = RoomCleanupJob()
        with patch("src.jobs.room_cleanup.connection_manager") as mock_cm:
            mock_cm.broadcast_to_room = AsyncMock()
            await job.execute(session)

        await session.commit()

        result = await session.execute(select(Room).where(Room.id == room.id))
        updated_room = result.scalar_one()
        assert updated_room.status == RoomStatus.ABANDONED

    async def test_does_not_close_recently_updated_room(self, session: AsyncSession):
        """Test that recently updated rooms are not closed."""
        # Create a room that was updated recently
        room = Room(status=RoomStatus.WAITING)
        session.add(room)
        await session.commit()

        job = RoomCleanupJob()
        with patch("src.jobs.room_cleanup.connection_manager") as mock_cm:
            mock_cm.broadcast_to_room = AsyncMock()
            await job.execute(session)

        await session.commit()

        result = await session.execute(select(Room).where(Room.id == room.id))
        updated_room = result.scalar_one()
        assert updated_room.status == RoomStatus.WAITING  # Not changed

        # Verify no broadcast was sent
        mock_cm.broadcast_to_room.assert_not_called()

    async def test_does_not_close_finished_room(self, session: AsyncSession):
        """Test that FINISHED rooms are not affected even if old."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        room = Room(status=RoomStatus.FINISHED)
        session.add(room)
        await session.flush()

        room.updated_at = old_time
        await session.commit()

        job = RoomCleanupJob()
        with patch("src.jobs.room_cleanup.connection_manager") as mock_cm:
            mock_cm.broadcast_to_room = AsyncMock()
            await job.execute(session)

        await session.commit()

        result = await session.execute(select(Room).where(Room.id == room.id))
        updated_room = result.scalar_one()
        assert updated_room.status == RoomStatus.FINISHED  # Not changed

    async def test_does_not_close_already_abandoned_room(self, session: AsyncSession):
        """Test that ABANDONED rooms are not processed again."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        room = Room(status=RoomStatus.ABANDONED)
        session.add(room)
        await session.flush()

        room.updated_at = old_time
        await session.commit()

        job = RoomCleanupJob()
        with patch("src.jobs.room_cleanup.connection_manager") as mock_cm:
            mock_cm.broadcast_to_room = AsyncMock()
            await job.execute(session)

        await session.commit()

        result = await session.execute(select(Room).where(Room.id == room.id))
        updated_room = result.scalar_one()
        assert updated_room.status == RoomStatus.ABANDONED

        # Verify no broadcast was sent
        mock_cm.broadcast_to_room.assert_not_called()

    async def test_closes_multiple_inactive_rooms(self, session: AsyncSession):
        """Test that multiple inactive rooms are closed in one execution."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)

        room1 = Room(status=RoomStatus.WAITING)
        room2 = Room(status=RoomStatus.PLAYING)
        room3 = Room(status=RoomStatus.WAITING)  # Recent, should not be closed

        session.add_all([room1, room2, room3])
        await session.flush()

        room1.updated_at = old_time
        room2.updated_at = old_time
        # room3 keeps its default recent updated_at
        await session.commit()

        job = RoomCleanupJob()
        with patch("src.jobs.room_cleanup.connection_manager") as mock_cm:
            mock_cm.broadcast_to_room = AsyncMock()
            await job.execute(session)

        await session.commit()

        # Verify room1 and room2 were closed
        result = await session.execute(select(Room).where(Room.id == room1.id))
        assert result.scalar_one().status == RoomStatus.ABANDONED

        result = await session.execute(select(Room).where(Room.id == room2.id))
        assert result.scalar_one().status == RoomStatus.ABANDONED

        # Verify room3 was not closed
        result = await session.execute(select(Room).where(Room.id == room3.id))
        assert result.scalar_one().status == RoomStatus.WAITING

        # Verify two broadcasts were sent
        assert mock_cm.broadcast_to_room.call_count == 2

    async def test_job_has_correct_configuration(self):
        """Test that the job has the correct lock_id and name."""
        job = RoomCleanupJob()
        assert job.lock_id == 1002
        assert job.job_name == "RoomCleanupJob"

