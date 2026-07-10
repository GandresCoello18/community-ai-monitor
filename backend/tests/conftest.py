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
def test_settings() -> Settings:
    return Settings(
        app_env="testing",
        debug=False,
        log_level="WARNING",
        seed_demo_data=False,
        camera_simulator_enabled=False,
        camera_simulator_auto_start=False,
        database_url="sqlite+aiosqlite:///:memory:",
    )


@pytest.fixture
async def app(test_settings: Settings):
    get_settings.cache_clear()
    reset_database_state()

    engine = get_engine(test_settings)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    application = create_app(settings=test_settings)
    yield application

    await dispose_engine()
    reset_database_state()
    get_settings.cache_clear()


@pytest.fixture
async def seeded_app(test_settings: Settings):
    get_settings.cache_clear()
    reset_database_state()

    engine = get_engine(test_settings)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = get_session_factory(test_settings)
    async with session_factory() as session:
        await seed_demo_data(session)

    application = create_app(settings=test_settings)
    yield application

    await dispose_engine()
    reset_database_state()
    get_settings.cache_clear()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def seeded_client(seeded_app):
    transport = ASGITransport(app=seeded_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
