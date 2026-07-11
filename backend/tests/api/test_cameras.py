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


@pytest.mark.asyncio
async def test_update_camera_partial_fields(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Camera Original",
            "location": "Zona Norte",
            "stream_url": "rtsp://192.168.1.50:8080/h264_pcm.sdp",
            "is_active": True,
        },
    )
    camera_id = create_response.json()["data"]["id"]

    response = await seeded_client.patch(
        f"/api/v1/cameras/{camera_id}",
        json={
            "name": "Camera Actualizada",
            "stream_url": "http://192.168.1.50:8080/video",
        },
    )

    assert response.status_code == 200
    body = response.json()["data"]
    assert body["id"] == camera_id
    assert body["name"] == "Camera Actualizada"
    assert body["location"] == "Zona Norte"
    assert body["stream_url"] == "http://192.168.1.50:8080/video"
    assert body["is_active"] is True


@pytest.mark.asyncio
async def test_update_camera_masks_rtsp_credentials_in_response(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Camera Secure",
            "location": "Entrada",
            "stream_url": "rtsp://demo/camera-update-mask",
        },
    )
    camera_id = create_response.json()["data"]["id"]

    response = await seeded_client.patch(
        f"/api/v1/cameras/{camera_id}",
        json={"stream_url": "rtsp://admin:secret@192.168.1.99:554/live"},
    )

    assert response.status_code == 200
    stream_url = response.json()["data"]["stream_url"]
    assert "secret" not in stream_url
    assert "admin" not in stream_url
    assert "***@" in stream_url


@pytest.mark.asyncio
async def test_update_camera_empty_payload_returns_422(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Camera Empty Patch",
            "location": "Test",
            "stream_url": "rtsp://demo/camera-empty-patch",
        },
    )
    camera_id = create_response.json()["data"]["id"]

    response = await seeded_client.patch(f"/api/v1/cameras/{camera_id}", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_update_camera_not_found(seeded_client) -> None:
    response = await seeded_client.patch(
        "/api/v1/cameras/00000000-0000-0000-0000-000000000000",
        json={"name": "No existe"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CAMERA_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_camera_returns_deleted_camera(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Camera To Delete",
            "location": "Test Zone",
            "stream_url": "rtsp://demo/camera-delete",
            "is_active": True,
        },
    )
    camera_id = create_response.json()["data"]["id"]

    response = await seeded_client.delete(f"/api/v1/cameras/{camera_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == camera_id
    assert body["data"]["name"] == "Camera To Delete"
    assert body["data"]["is_active"] is False


@pytest.mark.asyncio
async def test_delete_camera_not_found(seeded_client) -> None:
    response = await seeded_client.delete(
        "/api/v1/cameras/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CAMERA_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_camera_excludes_from_list_and_get(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Camera Hidden After Delete",
            "location": "Test",
            "stream_url": "rtsp://demo/camera-hidden",
        },
    )
    camera_id = create_response.json()["data"]["id"]

    list_before = await seeded_client.get("/api/v1/cameras")
    total_before = list_before.json()["meta"]["total"]

    delete_response = await seeded_client.delete(f"/api/v1/cameras/{camera_id}")
    assert delete_response.status_code == 200

    list_after = await seeded_client.get("/api/v1/cameras")
    assert list_after.json()["meta"]["total"] == total_before - 1
    assert camera_id not in {item["id"] for item in list_after.json()["data"]}

    get_response = await seeded_client.get(f"/api/v1/cameras/{camera_id}")
    assert get_response.status_code == 404
    assert get_response.json()["error"]["code"] == "CAMERA_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_camera_twice_returns_not_found(seeded_client) -> None:
    create_response = await seeded_client.post(
        "/api/v1/cameras",
        json={
            "name": "Camera Double Delete",
            "location": "Test",
            "stream_url": "rtsp://demo/camera-double",
        },
    )
    camera_id = create_response.json()["data"]["id"]

    first = await seeded_client.delete(f"/api/v1/cameras/{camera_id}")
    second = await seeded_client.delete(f"/api/v1/cameras/{camera_id}")

    assert first.status_code == 200
    assert second.status_code == 404
