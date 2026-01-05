import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.db import get_session
from src.schemas.websocket import WSEventType
from src.services import RoomService, connection_manager, games_storage

router = APIRouter()


@router.websocket("/{code}/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    code: str,
    player_id: int,
):
    """WebSocket endpoint for real-time game updates."""
    room_code = code.upper()
    
    # Verify room and player exist before accepting connection
    async for session in get_session():
        service = RoomService(session)
        room = await service.get_room_by_code(room_code)
        
        if room is None:
            await websocket.close(code=4004, reason="Room not found")
            return
        
        player = next((p for p in room.players if p.id == player_id), None)
        if player is None:
            await websocket.close(code=4004, reason="Player not found in room")
            return
        break

    await connection_manager.connect(websocket, room_code, player_id)

    try:
        while True:
            # Receive and handle messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_client_message(room_code, player_id, message)
            except json.JSONDecodeError:
                await connection_manager.send_to_player(
                    room_code,
                    player_id,
                    WSEventType.ERROR,
                    {"message": "Invalid JSON"},
                )
    except WebSocketDisconnect:
        connection_manager.disconnect(room_code, player_id)
        
        # Notify other players about disconnection
        await connection_manager.broadcast_to_room(
            room_code,
            WSEventType.PLAYER_LEFT,
            {"player_id": player_id},
        )


async def handle_client_message(room_code: str, player_id: int, message: dict):
    """Handle incoming WebSocket messages from clients."""
    event = message.get("event")
    data = message.get("data", {})

    if event == "ping":
        await connection_manager.send_to_player(
            room_code,
            player_id,
            "pong",
            {},
        )
    
    elif event == "get_state":
        # Return current room state from cache or fetch from DB
        state = games_storage.get_game(room_code)
        
        if state is None:
            # Fetch from DB if not in cache
            async for session in get_session():
                service = RoomService(session)
                room = await service.get_room_by_code(room_code)
                if room:
                    from src.services.games_storage import _build_room_dict
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
