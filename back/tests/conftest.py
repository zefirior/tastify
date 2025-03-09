from collections.abc import AsyncIterator

import pytest_asyncio
from litestar import Litestar
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from back.db.base import Session, create_all, create_session
from back.server.app import get_app


@pytest_asyncio.fixture(scope='session')
async def postgres():
    with PostgresContainer('postgres:16', driver='asyncpg') as postgres:
        async_engine = create_async_engine(postgres.get_connection_url(), echo=True)
        await create_all(async_engine, drop=True)
        yield postgres


@pytest_asyncio.fixture(autouse=True)
async def db(postgres: PostgresContainer):
    async_engine = create_async_engine(postgres.get_connection_url(), echo=True)
    Session.configure(bind=async_engine)
    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture()
def create_test_session(postgres):
    async_engine = create_async_engine(postgres.get_connection_url(), echo=True)
    session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    yield create_session(session_maker)


@pytest_asyncio.fixture()
async def test_client() -> AsyncIterator[AsyncTestClient[Litestar]]:
    app = get_app()
    app.debug = True

    async with AsyncTestClient(app=app) as client:
        yield client
