from litestar import Litestar, get, post, Request, Response
import random
from litestar.plugins.sqlalchemy import SQLAlchemySerializationPlugin
import string
from uuid import UUID, uuid4

from db.base import create_session, DBSettings, Room

ROOM_CODE_LENGTH = 4
ROOM_CODE_ALLOWED_CHARS = string.ascii_uppercase + string.digits

def generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))

@post("/room")
async def create_room(request: Request) -> Room:
    # room = Room(uuid=generate_room_code(15), code=generate_room_code(4), game_state={})
    async with create_session() as session:
        room = Room(code=generate_room_code(4), game_state={})
        session.add(room)
    return room

@post("/room/{room_code: str}/join")
async def join_room(request: Request, room_code: str) -> dict:
    data = request.json()
    return {}

@post("/r/{room_code: str}/user/{uuid: str}/inc")
async def increase_points(request: Request, room_code: str, uuid: str) -> dict:
    data = request.json()
    new_data = {}
    # return Response(content=new_data, media_type="application/json")
    return {}

@get("/room/{room_code: str}")
async def get_game(room_code: str) -> str:
    return room_code


settings = DBSettings()
settings.setup()
app = Litestar([create_room, join_room, increase_points, get_game], plugins=[SQLAlchemySerializationPlugin()])