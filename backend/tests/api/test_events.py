import pytest


@pytest.mark.asyncio
async def test_event_statistics_returns_aggregates(seeded_client) -> None:
    response = await seeded_client.get("/api/v1/events/statistics")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["total"] == 2
    assert payload["data"]["by_type"]["crowd_detected"] == 1
    assert payload["data"]["by_type"]["long_presence"] == 1
    assert payload["data"]["by_severity"]["low"] == 1
    assert payload["data"]["by_severity"]["medium"] == 1
    assert len(payload["data"]["by_camera"]) == 2


@pytest.mark.asyncio
async def test_event_statistics_filters_by_type(seeded_client) -> None:
    response = await seeded_client.get(
        "/api/v1/events/statistics",
        params={"event_type": "crowd_detected"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["total"] == 1
    assert payload["data"]["by_type"] == {"crowd_detected": 1}
    assert payload["meta"]["event_type"] == "crowd_detected"


@pytest.mark.asyncio
async def test_list_events_filters_by_event_type(seeded_client) -> None:
    response = await seeded_client.get(
        "/api/v1/events",
        params={"event_type": "long_presence", "limit": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["total"] == 1
    assert payload["data"][0]["event_type"] == "long_presence"
