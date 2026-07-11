from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.capture.preview import PreviewFrameStore


@pytest.mark.asyncio
async def test_preview_snapshot_returns_jpeg(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Preview Test Camera",
            "location": "Test",
            "stream_url": "rtsp://demo/camera-preview",
            "is_active": True,
        },
    )
    camera_id = create_response.json()["data"]["id"]

    preview_store = PreviewFrameStore()
    preview_store.update(
        UUID(camera_id),
        b"\xff\xd8\xff",
        captured_at=datetime.now(UTC),
        width=640,
        height=480,
    )

    transport = seeded_client._transport  # type: ignore[attr-defined]
    app = transport.app
    app.state.preview_store = preview_store

    response = await seeded_client.get(f"/api/v1/cameras/{camera_id}/preview")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content.startswith(b"\xff\xd8")


@pytest.mark.asyncio
async def test_preview_snapshot_not_available(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Preview Empty Camera",
            "location": "Test",
            "stream_url": "rtsp://demo/camera-empty",
            "is_active": True,
        },
    )
    camera_id = create_response.json()["data"]["id"]

    transport = seeded_client._transport  # type: ignore[attr-defined]
    app = transport.app
    app.state.preview_store = PreviewFrameStore()

    response = await seeded_client.get(f"/api/v1/cameras/{camera_id}/preview")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PREVIEW_NOT_AVAILABLE"
