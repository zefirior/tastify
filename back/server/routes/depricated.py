from typing import Any

from litestar import post
from litestar.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from back.db.base import RoomUser, create_session
from back.db.query_utils import get_room


@post('/room/{room_code:str}/user/{user_pk:str}/increment', deprecated=True)
async def increase_points(room_code: str, user_pk: str) -> dict[str, Any]:
    async with create_session() as session:
        room = await get_room(session, room_code, lock=True)

        room_user_stmt = select(RoomUser).where(RoomUser.room_uuid == room.pk, RoomUser.user_uuid == user_pk)
        if not (await session.execute(room_user_stmt)).scalar():
            raise HTTPException(status_code=400, detail='User not found')

        flag_modified(room, 'game_state')
        room.game_state.setdefault('points', {})
        room.game_state['points'].setdefault(user_pk, 0)
        room.game_state['points'][user_pk] += 1

    return room.game_state
