import random
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.games.registry import game_registry
from src.models import Room, RoomStatus, Player, GameRound, RoundStatus


class RoomService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_room(self, player_name: str) -> tuple[Room, Player]:
        """Create a new room and add the creator as host."""
        room = Room()
        self.session.add(room)
        await self.session.flush()

        player = Player(
            room_id=room.id,
            name=player_name,
            is_host=True,
        )
        self.session.add(player)
        await self.session.flush()

        room.host_id = player.id
        await self.session.flush()

        return room, player

    async def get_room_by_code(self, code: str) -> Room | None:
        """Get room by code with players and current round loaded."""
        result = await self.session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(Room.code == code.upper())
        )
        return result.scalar_one_or_none()

    async def join_room(self, code: str, player_name: str) -> tuple[Room, Player] | None:
        """Join an existing room. Returns None if room not found or game already started."""
        room = await self.get_room_by_code(code)
        if room is None:
            return None

        if room.status != RoomStatus.WAITING:
            return None

        player = Player(
            name=player_name,
            is_host=False,
        )
        room.players.append(player)
        await self.session.flush()

        return room, player

    async def start_game(self, room: Room, player_id: int) -> GameRound | None:
        """Start the game. Only host can start. Returns the first round or None if not allowed."""
        if room.host_id != player_id:
            return None

        if room.status != RoomStatus.WAITING:
            return None

        if len(room.players) < 2:
            return None

        room.status = RoomStatus.PLAYING
        room.current_round_number = 1

        game_round = await self._create_round(room)
        return game_round

    async def _create_round(self, room: Room) -> GameRound:
        """Create a new game round with random target number."""
        game_settings = game_registry.get_settings(room.game_type)
        min_target = game_settings.get("min_target", 1)
        max_target = game_settings.get("max_target", 100)
        target = random.randint(min_target, max_target)

        game_round = GameRound(
            round_number=room.current_round_number,
            target_number=target,
            status=RoundStatus.ACTIVE,
        )
        room.rounds.append(game_round)
        await self.session.flush()

        # Reset all player guesses
        for player in room.players:
            player.current_guess = None

        return game_round

    async def submit_guess(self, room: Room, player_id: int, guess: int) -> bool:
        """Submit a guess for the current round. Returns True if successful."""
        if room.status != RoomStatus.PLAYING:
            return False

        player = next((p for p in room.players if p.id == player_id), None)
        if player is None:
            return False

        current_round = self._get_current_round(room)
        if current_round is None or current_round.status != RoundStatus.ACTIVE:
            return False

        player.current_guess = guess
        return True

    def _get_current_round(self, room: Room) -> GameRound | None:
        """Get the current active round for the room."""
        for r in room.rounds:
            if r.round_number == room.current_round_number and r.status == RoundStatus.ACTIVE:
                return r
        return None

    async def finish_round(self, room: Room) -> list[dict]:
        """Finish the current round, calculate scores, and return results."""
        current_round = self._get_current_round(room)
        if current_round is None:
            return []

        current_round.status = RoundStatus.FINISHED
        current_round.finished_at = datetime.now(timezone.utc)

        target = current_round.target_number
        results = []

        # Calculate distances and sort by closest
        player_distances = []
        for player in room.players:
            if player.current_guess is not None:
                distance = abs(player.current_guess - target)
                player_distances.append((player, distance))
            else:
                player_distances.append((player, None))

        # Sort by distance (None = didn't guess = worst)
        player_distances.sort(key=lambda x: (x[1] is None, x[1] if x[1] is not None else 0))

        # Award points: 1st place = 10, 2nd = 5, 3rd = 3, rest = 1 (if guessed)
        points_table = [10, 5, 3]
        for i, (player, distance) in enumerate(player_distances):
            if distance is not None:
                points = points_table[i] if i < len(points_table) else 1
                player.score += points
            else:
                points = 0

            results.append({
                "player_id": player.id,
                "player_name": player.name,
                "guess": player.current_guess,
                "distance": distance,
                "points_earned": points,
            })

        return results

    async def remove_player(self, room: Room, player_id: int) -> bool:
        """Remove a player from the room. Returns True if successful."""
        player = next((p for p in room.players if p.id == player_id), None)
        if player is None:
            return False

        await self.session.delete(player)
        room.players.remove(player)

        # If host left, assign new host or close room
        if room.host_id == player_id and room.players:
            room.host_id = room.players[0].id
            room.players[0].is_host = True

        return True

