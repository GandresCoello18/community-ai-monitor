import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.database.base import Base
from app.database.seed import seed_demo_data
from app.database.session import (
    dispose_engine,
    get_engine,
    get_session_factory,
    reset_database_state,
)
from app.main import create_app


@pytest.fixture
async def dev_seeded_client():
    settings = Settings(
        app_env="development",
        debug=False,
        log_level="WARNING",
        seed_demo_data=False,
        camera_simulator_enabled=True,
        camera_simulator_auto_start=False,
        database_url="sqlite+aiosqlite:///:memory:",
    )
    get_settings.cache_clear()
    reset_database_state()

    engine = get_engine(settings)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = get_session_factory(settings)
    async with session_factory() as session:
        await seed_demo_data(session)

    application = create_app(settings=settings)
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    if hasattr(application.state, "camera_stream_service"):
        await application.state.camera_stream_service.stop_all()
    await dispose_engine()
    reset_database_state()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_start_and_get_stream_status(dev_seeded_client) -> None:
    cameras_response = await dev_seeded_client.get("/api/v1/cameras")
    camera_id = cameras_response.json()["data"][0]["id"]

    start_response = await dev_seeded_client.post(
        f"/api/v1/cameras/{camera_id}/stream/start",
    )
    assert start_response.status_code == 200
    assert start_response.json()["data"]["status"] == "running"
    assert start_response.json()["data"]["source_type"] == "synthetic"

    status_response = await dev_seeded_client.get(
        f"/api/v1/cameras/{camera_id}/stream/status",
    )
    assert status_response.status_code == 200
    assert status_response.json()["data"]["status"] == "running"

    streams_response = await dev_seeded_client.get("/api/v1/streams/status")
    assert streams_response.status_code == 200
    assert len(streams_response.json()["data"]["streams"]) >= 1
