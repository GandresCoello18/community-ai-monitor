import pytest


@pytest.mark.asyncio
async def test_list_cameras_returns_seeded_data(seeded_client) -> None:
    response = await seeded_client.get("/api/v1/cameras")

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["total"] == 2
    assert len(payload["data"]) == 2
    assert payload["data"][0]["name"]


@pytest.mark.asyncio
async def test_list_events_returns_seeded_data(seeded_client) -> None:
    response = await seeded_client.get("/api/v1/events")

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["total"] == 2
    assert payload["data"][0]["event_type"] in {"long_presence", "crowd_detected"}


@pytest.mark.asyncio
async def test_get_camera_not_found_returns_standard_error(client) -> None:
    response = await client.get("/api/v1/cameras/00000000-0000-0000-0000-000000000001")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CAMERA_NOT_FOUND"
