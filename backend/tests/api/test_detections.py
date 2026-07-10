import pytest


@pytest.mark.asyncio
async def test_list_detections_returns_seeded_data(seeded_client) -> None:
    response = await seeded_client.get("/api/v1/detections")

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["total"] == 2
    assert len(payload["data"]) == 2
    assert payload["data"][0]["object_class"] == "person"
    assert "bbox" in payload["data"][0]


@pytest.mark.asyncio
async def test_list_detections_supports_pagination(seeded_client) -> None:
    response = await seeded_client.get("/api/v1/detections?page=1&limit=1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["limit"] == 1
    assert len(payload["data"]) == 1
    assert payload["meta"]["total"] == 2
