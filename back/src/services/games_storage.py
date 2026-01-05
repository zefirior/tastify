import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from src.db import async_session_maker
from src.models import Room, RoomStatus
from src.schemas import RoomResponse, PlayerResponse, GameRoundResponse
from src.models.game_round import RoundStatus

logger = logging.getLogger(__name__)


def _build_room_dict(room: Room, hide_target: bool = True) -> dict[str, Any]:
    """Build a room dict from a Room model."""
    current_round = None
    for r in room.rounds:
        if r.round_number == room.current_round_number:
            target = None if (hide_target and r.status == RoundStatus.ACTIVE) else r.target_number
            current_round = {
                "id": r.id,
                "round_number": r.round_number,
                "target_number": target,
                "status": r.status.value,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            }
            break

    return {
        "id": room.id,
        "code": room.code,
        "status": room.status.value,
        "host_id": room.host_id,
        "current_round_number": room.current_round_number,
        "created_at": room.created_at.isoformat() if room.created_at else None,
        "updated_at": room.updated_at.isoformat() if room.updated_at else None,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "score": p.score,
                "current_guess": p.current_guess,
                "is_host": p.is_host,
                "connected_at": p.connected_at.isoformat() if p.connected_at else None,
            }
            for p in room.players
        ],
        "current_round": current_round,
    }


class GamesStorage:
    """
    In-memory storage for active game states.
    Periodically syncs with database and broadcasts changes via WebSocket.
    """

    def __init__(self):
        # room_code -> room state dict
        self._games: dict[str, dict[str, Any]] = {}
        self._running = False
        self._interval = 0.5  # seconds
        self._connection_manager = None

    def set_connection_manager(self, manager):
        """Set the connection manager for broadcasting."""
        self._connection_manager = manager

    def get_room_codes_with_connections(self) -> set[str]:
        """Get room codes that have active WebSocket connections."""
        if self._connection_manager is None:
            return set()
        return set(self._connection_manager.connections.keys())

    def get_game(self, room_code: str) -> dict[str, Any] | None:
        """Get cached game state."""
        return self._games.get(room_code)

    def set_game(self, room_code: str, state: dict[str, Any]):
        """Update cached game state."""
        self._games[room_code] = state

    def remove_game(self, room_code: str):
        """Remove game from cache."""
        self._games.pop(room_code, None)

    async def start(self):
        """Start the periodic sync loop."""
        self._running = True
        logger.info(f"Starting GamesStorage sync loop (interval: {self._interval}s)")
        
        while self._running:
            try:
                await self._sync_games()
            except Exception as e:
                logger.exception(f"Error in GamesStorage sync: {e}")
            
            await asyncio.sleep(self._interval)

    def stop(self):
        """Stop the sync loop."""
        self._running = False

    async def _sync_games(self):
        """Fetch relevant games from DB and broadcast changes."""
        connected_room_codes = self.get_room_codes_with_connections()
        
        if not connected_room_codes:
            # No active connections, clear cache
            self._games.clear()
            return

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        async with async_session_maker() as session:
            # Fetch rooms that:
            # 1. Are active (WAITING or PLAYING)
            # 2. Were updated within the last hour
            # 3. Have active WebSocket connections
            result = await session.execute(
                select(Room)
                .options(selectinload(Room.players), selectinload(Room.rounds))
                .where(
                    or_(
                        Room.status.in_([RoomStatus.WAITING, RoomStatus.PLAYING]),
                        Room.updated_at >= one_hour_ago,
                        Room.code.in_(connected_room_codes),
                    )
                )
            )
            rooms = result.scalars().all()

        # Process each room
        rooms_to_broadcast: list[tuple[str, dict[str, Any]]] = []
        
        for room in rooms:
            new_state = _build_room_dict(room)
            old_state = self._games.get(room.code)
            
            # Check if state changed
            if old_state != new_state:
                self._games[room.code] = new_state
                
                # Only broadcast if there are active connections for this room
                if room.code in connected_room_codes:
                    rooms_to_broadcast.append((room.code, new_state))

        # Clean up rooms that are no longer relevant
        current_room_codes = {r.code for r in rooms}
        for code in list(self._games.keys()):
            if code not in current_room_codes and code not in connected_room_codes:
                del self._games[code]

        # Broadcast changes
        for room_code, state in rooms_to_broadcast:
            await self._broadcast_state(room_code, state)

    async def _broadcast_state(self, room_code: str, state: dict[str, Any]):
        """Broadcast room state to all connected players."""
        if self._connection_manager is None:
            return

        await self._connection_manager.broadcast_to_room(
            room_code,
            "room_state",
            {"room": state},
        )


# Global instance
games_storage = GamesStorage()

