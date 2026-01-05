from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.models import RoomStatus, RoundStatus
from src.schemas import (
    CreateRoomRequest,
    CreateRoomResponse,
    JoinRoomRequest,
    JoinRoomResponse,
    RoomResponse,
    PlayerResponse,
    GuessRequest,
    GameRoundResponse,
)
from src.schemas.websocket import WSEventType
from src.services import RoomService, connection_manager

router = APIRouter()


def _build_room_response(room, hide_target: bool = True) -> RoomResponse:
    """Build a RoomResponse from a Room model."""
    current_round = None
    for r in room.rounds:
        if r.round_number == room.current_round_number:
            # Hide target number during active round
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

    return RoomResponse(
        id=room.id,
        code=room.code,
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


@router.post("", response_model=CreateRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    request: CreateRoomRequest,
    session: AsyncSession = Depends(get_session_dep),
):
    """Create a new game room and become the host."""
    service = RoomService(session)
    room, player = await service.create_room(request.player_name)
    await session.commit()

    # Reload room with relationships
    room = await service.get_room_by_code(room.code)

    return CreateRoomResponse(
        room=_build_room_response(room),
        player_id=player.id,
    )


@router.post("/{code}/join", response_model=JoinRoomResponse)
async def join_room(
    code: str,
    request: JoinRoomRequest,
    session: AsyncSession = Depends(get_session_dep),
):
    """Join an existing game room."""
    service = RoomService(session)
    result = await service.join_room(code, request.player_name)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or game already started",
        )

    room, player = result
    await session.commit()

    # Reload room with relationships
    room = await service.get_room_by_code(room.code)

    # Notify other players
    await connection_manager.broadcast_to_room(
        room.code,
        WSEventType.PLAYER_JOINED,
        {"player": PlayerResponse.model_validate(player).model_dump(mode="json")},
    )

    return JoinRoomResponse(
        room=_build_room_response(room),
        player_id=player.id,
    )


@router.get("/{code}", response_model=RoomResponse)
async def get_room(
    code: str,
    session: AsyncSession = Depends(get_session_dep),
):
    """Get room state by code."""
    service = RoomService(session)
    room = await service.get_room_by_code(code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    return _build_room_response(room)


@router.post("/{code}/start", response_model=RoomResponse)
async def start_game(
    code: str,
    player_id: int,
    session: AsyncSession = Depends(get_session_dep),
):
    """Start the game (host only)."""
    service = RoomService(session)
    room = await service.get_room_by_code(code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    game_round = await service.start_game(room, player_id)

    if game_round is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start game. Check if you are host, game is in waiting state, and there are at least 2 players.",
        )

    await session.commit()

    # Reload room with relationships
    room = await service.get_room_by_code(code)
    room_response = _build_room_response(room)

    # Notify all players
    await connection_manager.broadcast_to_room(
        room.code,
        WSEventType.GAME_STARTED,
        {"room": room_response.model_dump(mode="json")},
    )

    return room_response


@router.post("/{code}/guess", response_model=RoomResponse)
async def submit_guess(
    code: str,
    request: GuessRequest,
    session: AsyncSession = Depends(get_session_dep),
):
    """Submit a guess for the current round."""
    service = RoomService(session)
    room = await service.get_room_by_code(code)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found",
        )

    success = await service.submit_guess(room, request.player_id, request.guess)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit guess. Check if game is active and you are a player.",
        )

    await session.commit()

    # Reload room
    room = await service.get_room_by_code(code)

    # Notify other players that someone guessed (without revealing the guess)
    await connection_manager.broadcast_to_room(
        room.code,
        WSEventType.GUESS_SUBMITTED,
        {"player_id": request.player_id},
        exclude_player_id=request.player_id,
    )

    return _build_room_response(room)

