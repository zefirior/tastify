import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.jobs.base import BaseJob
from src.models import Room, RoomStatus, GameRound, RoundStatus
from src.schemas.websocket import WSEventType
from src.services import connection_manager
from src.services.room_service import RoomService

logger = logging.getLogger(__name__)


class GameTimerJob(BaseJob):
    """
    Background job that checks for rounds that have exceeded their time limit
    and processes round results.
    """

    lock_id = 1001  # Unique ID for game timer lock
    interval_seconds = settings.game_timer_job_interval
    job_name = "GameTimerJob"

    async def execute(self, session: AsyncSession):
        """Check for expired rounds and process them."""
        # Find all active rounds that have exceeded the time limit
        now = datetime.now(timezone.utc)
        
        result = await session.execute(
            select(GameRound)
            .options(selectinload(GameRound.room).selectinload(Room.players))
            .where(GameRound.status == RoundStatus.ACTIVE)
        )
        active_rounds = result.scalars().all()

        for game_round in active_rounds:
            elapsed = (now - game_round.started_at.replace(tzinfo=timezone.utc)).total_seconds()
            
            if elapsed >= settings.round_duration_seconds:
                await self._finish_round(session, game_round)

    async def _finish_round(self, session: AsyncSession, game_round: GameRound):
        """Finish a round, calculate scores, and broadcast results."""
        room = game_round.room
        logger.info(f"Finishing round {game_round.round_number} in room {room.code}")

        service = RoomService(session)
        
        # Reload room with all relationships to ensure fresh data
        room = await service.get_room_by_code(room.code)
        if room is None:
            return

        results = await service.finish_round(room)

        # Broadcast round results
        await connection_manager.broadcast_to_room(
            room.code,
            WSEventType.ROUND_FINISHED,
            {
                "round_number": game_round.round_number,
                "target_number": game_round.target_number,
                "results": results,
            },
        )

        # Check if game should continue or end
        # For now, let's play 3 rounds then finish
        if room.current_round_number >= 3:
            room.status = RoomStatus.FINISHED
            
            # Build final standings
            standings = sorted(
                [{"player_id": p.id, "name": p.name, "score": p.score} for p in room.players],
                key=lambda x: x["score"],
                reverse=True,
            )
            
            await connection_manager.broadcast_to_room(
                room.code,
                WSEventType.GAME_FINISHED,
                {"standings": standings},
            )
        else:
            # Start next round
            room.current_round_number += 1
            next_round = await service._create_round(room)
            
            await connection_manager.broadcast_to_room(
                room.code,
                WSEventType.ROUND_STARTED,
                {
                    "round_number": next_round.round_number,
                    "started_at": next_round.started_at.isoformat(),
                },
            )

