import uuid

import pytest
from litestar import Litestar
from litestar.testing import AsyncTestClient


@pytest.mark.asyncio
async def test_app_ping(test_client: AsyncTestClient[Litestar]):
    response = await test_client.post('/room', params={'admin_uuid': str(uuid.uuid4())})
    assert response.status_code == 201
