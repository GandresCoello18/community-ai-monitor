import pytest


@pytest.mark.asyncio
async def test_create_camera_masks_rtsp_credentials_in_response(seeded_client) -> None:
    response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "IP Camera",
            "location": "Entrada",
            "stream_url": "rtsp://admin:secret@192.168.1.99:554/live",
            "is_active": True,
        },
    )

    assert response.status_code == 201
    stream_url = response.json()["data"]["stream_url"]
    assert "secret" not in stream_url
    assert "admin" not in stream_url
    assert "***@" in stream_url


@pytest.mark.asyncio
async def test_create_camera_returns_201(seeded_client) -> None:
    payload = {
        "name": "Camera Webcam Test",
        "location": "Oficina",
        "stream_url": "webcam://0",
        "is_active": True,
    }

    response = await seeded_client.post("/api/v1/cameras", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["data"]["name"] == payload["name"]
    assert body["data"]["stream_url"] == payload["stream_url"]
    assert body["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_create_camera_validation_error(client) -> None:
    response = await client.post("/api/v1/cameras", json={"name": "", "location": ""})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_list_cameras_includes_created_camera(seeded_client) -> None:
    await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Camera Extra",
            "location": "Zona Sur",
            "stream_url": "rtsp://demo/camera-03",
        },
    )

    response = await seeded_client.get("/api/v1/cameras")

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 3
