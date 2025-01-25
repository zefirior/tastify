from litestar import Litestar, get, post, Request, Response
import secrets

import random
import string


ROOM_CODE_LENGTH = 4
ROOM_CODE_ALLOWED_CHARS = string.ascii_uppercase + string.digits


def generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))

@post("/room")
async def create_room(request: Request) -> dict:
    return {
        'uuid': generate_room_code(15),
        'code': generate_room_code(4),
        'game_state': {}
    }

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



app = Litestar([create_room, join_room, increase_points, get_game])