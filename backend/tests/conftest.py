import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        app_env="testing",
        debug=True,
        log_level="WARNING",
    )


@pytest.fixture
def app(test_settings: Settings):
    get_settings.cache_clear()
    application = create_app(settings=test_settings)
    yield application
    get_settings.cache_clear()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
