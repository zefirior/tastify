"""Timer job for Guess the Number game - handles round timing and transitions."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.games.registry import game_registry
from src.jobs.base import BaseJob
from src.models import Room, RoomStatus, GameRound, RoundStatus
from src.schemas.websocket import WSEventType
from src.services import connection_manager
from src.services.room_service import RoomService

logger = logging.getLogger(__name__)


class GuessNumberTimerJob(BaseJob):
    """
    Background job for Guess the Number game.
    
    Handles:
    - Checking for rounds that have exceeded their time limit
    - Detecting when all players have voted (early round completion)
    - Processing round results and awarding points
    - Starting new rounds after the between-rounds delay
    - Finishing the game after all rounds are complete
    """

    lock_id = 1001  # Unique ID for game timer lock
    interval_seconds = settings.game_timer_job_interval
    job_name = "GuessNumberTimerJob"

    async def execute(self, session: AsyncSession):
        """Check for expired rounds, early completion, and start new rounds."""
        # Step 1: Find and finish rounds that should end
        await self._check_and_finish_rounds(session)

        # Step 2: Start new rounds for rooms that are ready
        await self._check_and_start_rounds(session)

    async def _check_and_finish_rounds(self, session: AsyncSession):
        """Check for rounds that should be finished (time expired or all voted)."""
        now = datetime.now(timezone.utc)

        # Only process rounds for guess_number game
        result = await session.execute(
            select(GameRound)
            .options(selectinload(GameRound.room).selectinload(Room.players))
            .where(GameRound.status == RoundStatus.ACTIVE)
        )
        active_rounds = result.scalars().all()

        for game_round in active_rounds:
            # Skip rounds from other game types
            if game_round.room.game_type != "guess_number":
                continue

            started_at = game_round.started_at.replace(tzinfo=timezone.utc)
            elapsed = (now - started_at).total_seconds()
            
            # Get round duration from game settings
            game_settings = game_registry.get_settings(game_round.room.game_type)
            round_duration = game_settings.get("round_duration_seconds", 30)
            
            time_expired = elapsed >= round_duration
            all_voted = self._all_players_voted(game_round.room)

            if time_expired or all_voted:
                reason = "time expired" if time_expired else "all players voted"
                logger.info(
                    f"Finishing round {game_round.round_number} "
                    f"in room {game_round.room.code} ({reason})"
                )
                await self._finish_round(session, game_round)

    async def _check_and_start_rounds(self, session: AsyncSession):
        """Check for rooms ready to start the next round."""
        now = datetime.now(timezone.utc)

        # Only process guess_number rooms
        result = await session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(
                Room.status == RoomStatus.PLAYING,
                Room.game_type == "guess_number",
            )
        )
        playing_rooms = result.scalars().all()

        for room in playing_rooms:
            # Find the most recent round
            if not room.rounds:
                continue

            latest_round = max(room.rounds, key=lambda r: r.round_number)

            # Only proceed if the latest round is finished
            if latest_round.status != RoundStatus.FINISHED:
                continue

            # Check if enough time has passed since the round finished
            if latest_round.finished_at is None:
                continue

            finished_at = latest_round.finished_at.replace(tzinfo=timezone.utc)
            elapsed_since_finish = (now - finished_at).total_seconds()

            # Get between rounds delay from game settings
            game_settings = game_registry.get_settings(room.game_type)
            between_rounds_delay = game_settings.get("between_rounds_delay_seconds", 5)

            if elapsed_since_finish >= between_rounds_delay:
                await self._start_next_round_or_finish(session, room)

    def _all_players_voted(self, room: Room) -> bool:
        """Check if all players in the room have submitted their guess."""
        if not room.players:
            return False
        return all(player.current_guess is not None for player in room.players)

    async def _finish_round(self, session: AsyncSession, game_round: GameRound):
        """Finish a round and broadcast results (don't start next round yet)."""
        room = game_round.room
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

    async def _start_next_round_or_finish(
        self, session: AsyncSession, room: Room
    ):
        """Start the next round or finish the game if all rounds are complete."""
        service = RoomService(session)

        # Reload room to get fresh data
        room = await service.get_room_by_code(room.code)
        if room is None:
            return

        # Check if game should end (total_rounds played)
        game_settings = game_registry.get_settings(room.game_type)
        total_rounds = game_settings.get("total_rounds", 3)
        if room.current_round_number >= total_rounds:
            room.status = RoomStatus.FINISHED

            # Build final standings
            standings = sorted(
                [
                    {"player_id": p.id, "name": p.name, "score": p.score}
                    for p in room.players
                ],
                key=lambda x: x["score"],
                reverse=True,
            )

            await connection_manager.broadcast_to_room(
                room.code,
                WSEventType.GAME_FINISHED,
                {"standings": standings},
            )
            logger.info(f"Game finished in room {room.code}")
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
            logger.info(
                f"Started round {next_round.round_number} in room {room.code}"
            )

