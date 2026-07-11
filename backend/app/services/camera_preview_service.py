import asyncio
from collections.abc import AsyncIterator
from uuid import UUID

from app.capture.preview import PreviewFrameStore, PreviewSnapshot
from app.core.config import Settings
from app.core.exceptions import AppException, NotFoundError

MJPEG_BOUNDARY = "frame"


class CameraPreviewService:
    """Serves in-memory live previews without persisting frames."""

    def __init__(self, settings: Settings, preview_store: PreviewFrameStore) -> None:
        self._settings = settings
        self._preview_store = preview_store

    def get_snapshot(self, camera_id: UUID) -> PreviewSnapshot:
        self._ensure_enabled()
        snapshot = self._preview_store.get(camera_id)
        if snapshot is None:
            raise NotFoundError(
                "PREVIEW_NOT_AVAILABLE",
                "No preview available. Ensure the camera stream is running.",
            )
        return snapshot

    async def mjpeg_stream(self, camera_id: UUID) -> AsyncIterator[bytes]:
        self._ensure_enabled()
        fps = self._settings.camera_preview_fps
        interval = 1.0 / fps if fps > 0 else 0.5

        while True:
            snapshot = self._preview_store.get(camera_id)
            if snapshot is not None:
                yield (
                    f"--{MJPEG_BOUNDARY}\r\n"
                    f"Content-Type: image/jpeg\r\n"
                    f"Content-Length: {len(snapshot.jpeg)}\r\n\r\n"
                ).encode()
                yield snapshot.jpeg
                yield b"\r\n"
            try:
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break

    def ensure_enabled(self) -> None:
        self._ensure_enabled()

    def _ensure_enabled(self) -> None:
        if not self._settings.camera_preview_enabled:
            raise AppException(
                code="PREVIEW_DISABLED",
                message="Camera preview is disabled",
                status_code=404,
            )
