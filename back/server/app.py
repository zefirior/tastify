from advanced_alchemy.extensions.litestar import SQLAlchemySerializationPlugin
from litestar import Litestar, MediaType, Request, Response
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException
from litestar.logging import LoggingConfig

from back import consts
from back.server.routes import (
    create_room,
    get_game,
    join_room,
    next_round,
    search_groups,
    search_tracks,
    start_game,
    submit_group,
    submit_track,
)
from back.server.routes.depricated import increase_points


def plain_text_exception_handler(_: Request, exc: Exception) -> Response:
    status_code = getattr(exc, 'status_code', 500)
    detail = getattr(exc, 'detail', '')
    return Response(
        media_type=MediaType.TEXT,
        content=detail,
        status_code=status_code,
    )


def get_app():
    logging_config = LoggingConfig(
        root={'level': 'INFO', 'handlers': ['queue_listener']},
        formatters={'standard': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}},
        log_exceptions='always',
    )

    routers = [
        create_room,
        join_room,
        increase_points,
        get_game,
        start_game,
        submit_group,
        submit_track,
        next_round,
        search_groups,
        search_tracks,
    ]
    return Litestar(
        routers,
        plugins=[SQLAlchemySerializationPlugin()],
        exception_handlers={HTTPException: plain_text_exception_handler},
        cors_config=CORSConfig(allow_origins=consts.ALLOW_ORIGINS),
        logging_config=logging_config,
    )
