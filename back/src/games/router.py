"""Generic game router factory for creating game-specific API routes."""

import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.games.base import GameAction
from src.games.registry import game_registry
from src.models import Room, RoomStatus, RoundStatus
from src.schemas import PlayerResponse, GameRoundResponse
from src.schemas.websocket import WSEventType
from src.services import connection_manager, games_storage
from src.services.games_storage import _build_room_dict

logger = logging.getLogger(__name__)


# Request/Response schemas
class CreateRoomRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)


class JoinRoomRequest(BaseModel):
    player_name: str = Field(..., min_length=1, max_length=50)


class GameRoomResponse(BaseModel):
    """Response for game room state."""

    id: int
    code: str
    game_type: str
    status: RoomStatus
    host_id: int | None
    current_round_number: int
    created_at: Any
    updated_at: Any
    players: list[PlayerResponse] = []
    current_round: GameRoundResponse | None = None

    model_config = {"from_attributes": True}


class CreateRoomResponse(BaseModel):
    room: GameRoomResponse
    player_id: int


class JoinRoomResponse(BaseModel):
    room: GameRoomResponse
    player_id: int


class ActionRequest(BaseModel):
    """Generic action request - actual validation is done by game's action_schema."""

    action: str
    # Additional fields will be validated by game's action_schema


class ActionResponse(BaseModel):
    success: bool
    message: str | None = None
    data: dict[str, Any] | None = None
    room: GameRoomResponse | None = None


class GameInfoResponse(BaseModel):
    """Information about available games."""

    games: list[dict[str, Any]]
    default_game: str


def _build_game_room_response(room: Room, hide_target: bool = True) -> GameRoomResponse:
    """Build a GameRoomResponse from a Room model."""
    current_round = None
    for r in room.rounds:
        if r.round_number == room.current_round_number:
            target = None if (hide_target and r.status == RoundStatus.ACTIVE) else r.target_number
            current_round = GameRoundResponse(
                id=r.id,
                round_number=r.round_number,
                target_number=target,
                status=r.status,
                started_at=r.started_at,
                finished_at=r.finished_at,
            )
            break

    return GameRoomResponse(
        id=room.id,
        code=room.code,
        game_type=room.game_type,
        status=room.status,
        host_id=room.host_id,
        current_round_number=room.current_round_number,
        created_at=room.created_at,
        updated_at=room.updated_at,
        players=[
            PlayerResponse(
                id=p.id,
                name=p.name,
                score=p.score,
                current_guess=p.current_guess,
                is_host=p.is_host,
                connected_at=p.connected_at,
            )
            for p in room.players
        ],
        current_round=current_round,
    )


async def get_session_dep():
    async for session in get_session():
        yield session


def create_games_router() -> APIRouter:
    """
    Create the main games router with all game-specific routes.
    
    Routes:
    - GET /api/games/ - List available games
    - POST /api/games/{game}/rooms - Create room
    - POST /api/games/{game}/rooms/{code}/join - Join room
    - GET /api/games/{game}/rooms/{code} - Get room state
    - POST /api/games/{game}/rooms/{code}/actions - Execute action
    - WS /api/games/{game}/rooms/{code}/ws - WebSocket
    """
    router = APIRouter()

    @router.get("", response_model=GameInfoResponse)
    async def list_games():
        """List all available games and their info."""
        return GameInfoResponse(
            games=game_registry.get_all_games_info(),
            default_game=game_registry.default_game_type or "",
        )

    @router.post(
        "/{game_type}/rooms",
        response_model=CreateRoomResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_room(
        game_type: str,
        request: CreateRoomRequest,
        session: AsyncSession = Depends(get_session_dep),
    ):
        """Create a new game room for the specified game type."""
        # Validate game type
        game = game_registry.get_game(game_type)
        if game is None or not game_registry.is_game_enabled(game_type):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game '{game_type}' not found or not enabled",
            )

        # Import here to avoid circular imports
        from src.models import Player

        # Create room with game type
        room = Room(game_type=game_type)
        session.add(room)
        await session.flush()

        # Create host player
        player = Player(
            room_id=room.id,
            name=request.player_name,
            is_host=True,
        )
        session.add(player)
        await session.flush()

        room.host_id = player.id
        await session.commit()

        # Reload room with relationships
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        result = await session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(Room.id == room.id)
        )
        room = result.scalar_one()

        return CreateRoomResponse(
            room=_build_game_room_response(room),
            player_id=player.id,
        )

    @router.post("/{game_type}/rooms/{code}/join", response_model=JoinRoomResponse)
    async def join_room(
        game_type: str,
        code: str,
        request: JoinRoomRequest,
        session: AsyncSession = Depends(get_session_dep),
    ):
        """Join an existing game room."""
        # Validate game type
        game = game_registry.get_game(game_type)
        if game is None or not game_registry.is_game_enabled(game_type):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game '{game_type}' not found or not enabled",
            )

        from src.models import Player
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        # Find room
        result = await session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(Room.code == code.upper())
        )
        room = result.scalar_one_or_none()

        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        if room.game_type != game_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room is for game '{room.game_type}', not '{game_type}'",
            )

        if room.status != RoomStatus.WAITING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Game has already started",
            )

        # Create player
        player = Player(
            name=request.player_name,
            is_host=False,
        )
        room.players.append(player)
        await session.flush()
        await session.commit()

        # Reload room
        result = await session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(Room.id == room.id)
        )
        room = result.scalar_one()

        # Notify other players
        await connection_manager.broadcast_to_room(
            room.code,
            WSEventType.PLAYER_JOINED,
            {"player": PlayerResponse.model_validate(player).model_dump(mode="json")},
        )

        # Call game's on_player_join hook
        await game.on_player_join(room, player.id, session)

        return JoinRoomResponse(
            room=_build_game_room_response(room),
            player_id=player.id,
        )

    @router.get("/{game_type}/rooms/{code}", response_model=GameRoomResponse)
    async def get_room_state(
        game_type: str,
        code: str,
        session: AsyncSession = Depends(get_session_dep),
    ):
        """Get the current state of a game room."""
        # Validate game type
        if not game_registry.is_game_enabled(game_type):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game '{game_type}' not found or not enabled",
            )

        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        result = await session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(Room.code == code.upper())
        )
        room = result.scalar_one_or_none()

        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        if room.game_type != game_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room is for game '{room.game_type}', not '{game_type}'",
            )

        return _build_game_room_response(room)

    @router.post("/{game_type}/rooms/{code}/actions", response_model=ActionResponse)
    async def execute_action(
        game_type: str,
        code: str,
        request: dict[str, Any],  # Accept raw dict, validate with game's schema
        player_id: int,
        session: AsyncSession = Depends(get_session_dep),
    ):
        """
        Execute a game-specific action.
        
        The action payload depends on the game type. Each game defines its own
        action schema with available actions and their parameters.
        """
        # Validate game type
        game = game_registry.get_game(game_type)
        if game is None or not game_registry.is_game_enabled(game_type):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game '{game_type}' not found or not enabled",
            )

        # Validate action against game's schema
        try:
            action = game.action_schema.model_validate(request)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=e.errors(),
            )

        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        # Find room
        result = await session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(Room.code == code.upper())
        )
        room = result.scalar_one_or_none()

        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        if room.game_type != game_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room is for game '{room.game_type}', not '{game_type}'",
            )

        # Verify player is in room
        player = next((p for p in room.players if p.id == player_id), None)
        if player is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Player not found in room",
            )

        # Execute the action
        action_result = await game.execute_action(room, player_id, action, session)
        await session.commit()

        # Reload room for response
        result = await session.execute(
            select(Room)
            .options(selectinload(Room.players), selectinload(Room.rounds))
            .where(Room.id == room.id)
        )
        room = result.scalar_one()

        # Broadcast if needed
        if action_result.broadcast_event:
            broadcast_data = action_result.broadcast_data or {}
            # Add room state to broadcast
            broadcast_data["room"] = _build_game_room_response(room).model_dump(mode="json")
            await connection_manager.broadcast_to_room(
                room.code,
                action_result.broadcast_event,
                broadcast_data,
                exclude_player_id=player_id if action_result.broadcast_event == "guess_submitted" else None,
            )

        return ActionResponse(
            success=action_result.success,
            message=action_result.message,
            data=action_result.data,
            room=_build_game_room_response(room),
        )

    @router.websocket("/{game_type}/rooms/{code}/ws")
    async def websocket_endpoint(
        websocket: WebSocket,
        game_type: str,
        code: str,
        player_id: int,
    ):
        """WebSocket endpoint for real-time game updates."""
        # Validate game type
        game = game_registry.get_game(game_type)
        if game is None or not game_registry.is_game_enabled(game_type):
            await websocket.close(code=4004, reason=f"Game '{game_type}' not found")
            return

        room_code = code.upper()

        # Verify room and player exist before accepting connection
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        async for session in get_session():
            result = await session.execute(
                select(Room)
                .options(selectinload(Room.players), selectinload(Room.rounds))
                .where(Room.code == room_code)
            )
            room = result.scalar_one_or_none()

            if room is None:
                await websocket.close(code=4004, reason="Room not found")
                return

            if room.game_type != game_type:
                await websocket.close(code=4004, reason="Wrong game type for room")
                return

            player = next((p for p in room.players if p.id == player_id), None)
            if player is None:
                await websocket.close(code=4004, reason="Player not found in room")
                return
            break

        await connection_manager.connect(websocket, room_code, player_id)

        try:
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    await _handle_ws_message(game_type, room_code, player_id, message)
                except json.JSONDecodeError:
                    await connection_manager.send_to_player(
                        room_code,
                        player_id,
                        WSEventType.ERROR,
                        {"message": "Invalid JSON"},
                    )
        except WebSocketDisconnect:
            connection_manager.disconnect(room_code, player_id)

            await connection_manager.broadcast_to_room(
                room_code,
                WSEventType.PLAYER_LEFT,
                {"player_id": player_id},
            )

    return router


async def _handle_ws_message(game_type: str, room_code: str, player_id: int, message: dict):
    """Handle incoming WebSocket messages."""
    event = message.get("event")

    if event == "ping":
        await connection_manager.send_to_player(room_code, player_id, "pong", {})

    elif event == "get_state":
        state = games_storage.get_game(room_code)

        if state is None:
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload

            async for session in get_session():
                result = await session.execute(
                    select(Room)
                    .options(selectinload(Room.players), selectinload(Room.rounds))
                    .where(Room.code == room_code)
                )
                room = result.scalar_one_or_none()
                if room:
                    state = _build_room_dict(room)
                    games_storage.set_game(room_code, state)
                break

        if state:
            await connection_manager.send_to_player(
                room_code,
                player_id,
                "room_state",
                {"room": state},
            )
        else:
            await connection_manager.send_to_player(
                room_code,
                player_id,
                WSEventType.ERROR,
                {"message": "Room not found"},
            )

