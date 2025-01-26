import logging
import random
from typing import Any
from uuid import uuid4

from advanced_alchemy.extensions.litestar import SQLAlchemySerializationPlugin
from litestar import Litestar, get, post, Request, Response, MediaType
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from litestar.logging import LoggingConfig
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

import consts
from back.db.base import create_session, Room, UserRole, RoomUser, DBSettings, RoomStatus, RoundStages
from back.db.utils import dump_room
from back.db.query_utils import get_or_create_user, get_or_404_room, get_room_users, get_room, get_last_round, \
    create_round, acquire_advisory_lock, end_round
from consts import ROOM_CODE_ALLOWED_CHARS
from spotify import spotify_api

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
logger.addHandler(logging.StreamHandler())


def generate_room_code(length):
    return ''.join(random.choices(ROOM_CODE_ALLOWED_CHARS, k=length))


@post("/room")
async def create_room(admin_uuid: str) -> dict[str, Any]:
    async with create_session() as session:
        user = await get_or_create_user(session, admin_uuid)

        room = Room(
            pk=str(uuid4()),
            code=generate_room_code(4),
            game_state={},
            status=RoomStatus.NEW.value,
            created_by=user.pk,
        )
        session.add(room)

        return await dump_room(session, admin_uuid, room, [])


@post("/room/{room_code:str}/join")
async def join_room(room_code: str, nickname: str, user_uuid: str) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            required_status=RoomStatus.NEW,
            lock=True,
        )

        room_user_stmt = (
            select(RoomUser)
            .where(RoomUser.room_uuid == room.pk, RoomUser.nickname == nickname)
        )
        if (await session.execute(room_user_stmt)).scalar():
            raise HTTPException(status_code=400, detail="Nickname already taken")

        user = await get_or_create_user(session, user_uuid)
        room_user = RoomUser(nickname=nickname, role=UserRole.PLAYER.value, user_uuid=user.pk, room_uuid=room.pk)
        session.add(room_user)
    return Response(status_code=201, content={})


@post("/room/{room_code:str}/user/{user_pk:str}/increment", deprecated=True)
async def increase_points(room_code: str, user_pk: str) -> dict[str, Any]:
    async with create_session() as session:
        room = await get_room(session, room_code, lock=True)

        room_user_stmt = (
            select(RoomUser)
            .where(RoomUser.room_uuid == room.pk, RoomUser.user_uuid == user_pk)
        )
        if not (await session.execute(room_user_stmt)).scalar():
            raise HTTPException(status_code=400, detail="User not found")

        flag_modified(room, "game_state")
        room.game_state.setdefault("points", {})
        room.game_state["points"].setdefault(user_pk, 0)
        room.game_state["points"][user_pk] += 1

    return room.game_state


@get("/room/{room_code:str}")
async def get_game(room_code: str, user_uuid: str) -> dict:
    async with create_session() as session:
        room = await get_or_404_room(session, room_code)
        room_users = await get_room_users(session, room_code)
        return await dump_room(session, user_uuid, room, room_users)


@post("/room/{room_code:str}/start")
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
            raise HTTPException(status_code=404, detail="Need at least two players to start the game")

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


@post("/room/{room_code:str}/submit/group")
async def submit_group(room_code: str, user_uuid: str, group_id: str) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            forbidden_created_by=user_uuid,
            required_status=RoomStatus.RUNNING,
            lock=True,
        )

        current_round = await get_last_round(
            room.rounds,
            required_suggester=user_uuid,
            required_stage=RoundStages.GROUP_SUGGESTION,
        )

        current_round.group_id = group_id
        current_round.current_stage = RoundStages.TRACKS_SUBMISSION

    return Response(status_code=200, content={})


@post("/room/{room_code:str}/submit/track")
async def submit_track(room_code: str, user_uuid: str, track_id: str | None = None) -> Response:
    async with create_session() as session:
        room = await get_room(
            session,
            room_code,
            forbidden_created_by=user_uuid,
            required_status=RoomStatus.RUNNING,
            lock=True,
        )

        if not room.rounds:
            raise RuntimeError("Unreachable")
        current_round = await get_last_round(
            room.rounds,
            forbidden_suggester=user_uuid,
            required_stage=RoundStages.TRACKS_SUBMISSION,
        )
        if user_uuid in current_round.submissions:
            raise HTTPException(status_code=400, detail="User already submitted")

        current_round.submissions[user_uuid] = track_id
        flag_modified(current_round, "submissions")

        players = await get_room_users(session, room_code)
        if len(current_round.submissions) == len(players) - 1:
            await end_round(current_round)

    return Response(status_code=200, content={})


@post("/room/{room_code:str}/next-round")
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


@get("/search/group")
async def search_groups(q: str) -> list:
    groups = []
    results = spotify_api.search(q=q, limit=10, type='artist')
    for artist in results['artists']['items']:
        if artist['images']:
            image_url = sorted(artist['images'], key=lambda image: image['height'])[0]['url']
        else:
            image_url = ''

        groups.append({
            'name': artist['name'],
            'id': artist['id'],
            'image_url': image_url,
        })

    return groups


@get("/search/track")
async def search_tracks(group_id: str, q: str) -> list:
    artist = spotify_api.artist(group_id)
    tracks = []
    results = spotify_api.search(q=f'{q} artist:"{artist["name"]}"', limit=50, type='track')
    for track in results['tracks']['items']:
        if track['artists'][0]['id'] == group_id:
            tracks.append({
                'id': track['id'],
                'name': track['name'],
            })

    return tracks


def plain_text_exception_handler(_: Request, exc: Exception) -> Response:
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", "")
    return Response(
        media_type=MediaType.TEXT,
        content=detail,
        status_code=status_code,
    )


logging_config = LoggingConfig(
    root={"level": "INFO", "handlers": ["queue_listener"]},
    formatters={
        "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
    },
    log_exceptions="always",
)

settings = DBSettings()
settings.setup()
app = Litestar(
    [create_room, join_room, increase_points, get_game, start_game, submit_group, submit_track, next_round, search_groups, search_tracks],
    plugins=[SQLAlchemySerializationPlugin()],
    exception_handlers={HTTPException: plain_text_exception_handler},
    cors_config=CORSConfig(allow_origins=consts.ALLOW_ORIGINS),
    logging_config=logging_config,
)
