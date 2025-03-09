import random
from typing import Any
from uuid import uuid4

from litestar import Response, get, post
from litestar.exceptions import HTTPException
from sqlalchemy import select

from back.consts import ROOM_CODE_ALLOWED_CHARS
from back.db.base import Room, RoomStatus, RoomUser, RoundStages, UserRole, create_session
from back.db.query_utils import (
    acquire_advisory_lock,
    create_round,
    get_last_round,
    get_or_404_room,
    get_or_create_user,
    get_room,
    get_room_users,
)
from back.db.utils import dump_room


@post('/room')
async def create_room(admin_uuid: str) -> dict[str, Any]:
    async with create_session() as session:
        user = await get_or_create_user(session, admin_uuid)

        room = Room(
            pk=str(uuid4()),
            code=_generate_room_code(4),
            game_state={},
            status=RoomStatus.NEW.value,
            created_by=user.pk,
        )
        session.add(room)

        return await dump_room(session, admin_uuid, room, [])


@post('/room/{room_code:str}/join')
async def join_room(room_code: str, nickname: str, user_uuid: str) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            required_status=RoomStatus.NEW,
            lock=True,
        )

        room_user_stmt = select(RoomUser).where(RoomUser.room_uuid == room.pk, RoomUser.nickname == nickname)
        if (await session.execute(room_user_stmt)).scalar():
            raise HTTPException(status_code=400, detail='Nickname already taken')

        user = await get_or_create_user(session, user_uuid)
        room_user = RoomUser(nickname=nickname, role=UserRole.PLAYER.value, user_uuid=user.pk, room_uuid=room.pk)
        session.add(room_user)
    return Response(status_code=201, content={})


@get('/room/{room_code:str}')
async def get_game(room_code: str, user_uuid: str) -> dict:
    async with create_session() as session:
        room = await get_or_404_room(session, room_code)
        room_users = await get_room_users(session, room_code)
        return await dump_room(session, user_uuid, room, room_users)


@post('/room/{room_code:str}/start')
async def start_game(room_code: str, user_uuid: str) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            required_created_by=user_uuid,
            required_status=RoomStatus.NEW,
            lock=True,
        )

        room_users = await get_room_users(session, room_code)
        if len(room_users) < 2:
            raise HTTPException(status_code=404, detail='Need at least two players to start the game')

        room.status = RoomStatus.RUNNING
        room.total_rounds = len(room_users)

        await create_round(
            session,
            room_uuid=room.pk,
            suggester_uuid=room_users[0].pk,
            number=1,
            room_users=room_users,
        )

    return Response(status_code=200, content={})


@post('/room/{room_code:str}/next-round')
async def next_round(room_code: str, user_uuid: str) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            forbidden_created_by=user_uuid,
            required_status=RoomStatus.RUNNING,
        )
        await acquire_advisory_lock(session, room)

        previous_round = await get_last_round(
            room.rounds,
            required_suggester=user_uuid,
            required_stage=RoundStages.END_ROUND,
        )

        if previous_round.number == room.total_rounds:
            room.status = RoomStatus.FINISHED
        else:
            room_users = await get_room_users(session, room_code)
            await create_round(
                session,
                room_uuid=room.pk,
                suggester_uuid=room_users[previous_round.number].pk,
                number=previous_round.number + 1,
                room_users=room_users,
            )

    return Response(status_code=200, content={})


def _generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))
