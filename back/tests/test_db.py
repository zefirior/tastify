import uuid

import pytest

from back.db.query_utils import get_or_create_user


@pytest.mark.asyncio
async def test_db_ping(create_test_session):
    async with create_test_session as session:
        user_uid = uuid.uuid4()
        user = await get_or_create_user(session, str(user_uid))
        assert user.pk == str(user_uid)
