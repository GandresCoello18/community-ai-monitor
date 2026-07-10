import pytest

from app.core.exceptions import NotFoundError


@pytest.fixture
def app_with_error_route(app):
    @app.get("/api/v1/test-error")
    async def trigger_not_found() -> None:
        raise NotFoundError("TEST_NOT_FOUND", "Resource not found")

    return app


@pytest.fixture
async def error_client(app_with_error_route):
    from httpx import ASGITransport, AsyncClient

    transport = ASGITransport(app=app_with_error_route)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_app_exception_returns_standard_error_format(error_client) -> None:
    response = await error_client.get("/api/v1/test-error")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TEST_NOT_FOUND",
            "message": "Resource not found",
        },
    }
