import pytest


@pytest.mark.asyncio
async def test_health_check_returns_ok(client) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "ok"
    assert payload["data"]["database"] == "connected"
