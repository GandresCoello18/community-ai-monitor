import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.database.seed import seed_demo_data
from app.database.session import dispose_engine, get_session_factory
from app.services.camera_stream_service import CameraStreamService
from app.websocket.manager import WebSocketManager

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        setup_logging(app_settings)
        logger.info("Starting %s [%s]", app_settings.app_name, app_settings.app_env)

        ws_manager = WebSocketManager(app_settings)
        app.state.ws_manager = ws_manager

        stream_service = CameraStreamService(app_settings, ws_manager=ws_manager)
        app.state.camera_stream_service = stream_service

        if app_settings.seed_demo_data and app_settings.is_development:
            session_factory = get_session_factory(app_settings)
            async with session_factory() as session:
                await seed_demo_data(session)

        if app_settings.camera_simulator_enabled and not app_settings.is_testing:
            session_factory = get_session_factory(app_settings)
            async with session_factory() as session:
                await stream_service.auto_start_active_cameras(session)

        yield

        await stream_service.stop_all()
        await dispose_engine()
        logger.info("Shutting down %s", app_settings.app_name)

    app = FastAPI(
        title=app_settings.app_name,
        version="0.1.0",
        docs_url="/docs" if app_settings.is_development else None,
        redoc_url="/redoc" if app_settings.is_development else None,
        lifespan=lifespan,
    )

    app.state.settings = app_settings

    register_exception_handlers(app)
    app.include_router(api_router, prefix=app_settings.api_v1_prefix)

    return app


app = create_app()
