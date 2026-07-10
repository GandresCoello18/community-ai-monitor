from fastapi import APIRouter

from app.api.v1 import cameras, events, health, streams

router = APIRouter()
router.include_router(health.router)
router.include_router(cameras.router)
router.include_router(events.router)
router.include_router(streams.router)
