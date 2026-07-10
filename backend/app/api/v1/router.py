from fastapi import APIRouter

from app.api.v1 import cameras, detections, events, health, streams, summaries
from app.websocket.router import router as ws_router

router = APIRouter()
router.include_router(health.router)
router.include_router(cameras.router)
router.include_router(events.router)
router.include_router(detections.router)
router.include_router(streams.router)
router.include_router(summaries.router)
router.include_router(ws_router, prefix="/ws")
