from app.core.config import Settings
from app.tracking.base import ObjectTracker
from app.tracking.iou_tracker import IoUTracker


def create_tracker(settings: Settings) -> ObjectTracker:
    """Build a per-camera tracker.

    A new instance must be created for each camera stream because trackers are
    stateful (they keep track history for one video source).
    """
    return IoUTracker(
        iou_threshold=settings.tracking_iou_threshold,
        max_age=settings.tracking_max_age,
    )
