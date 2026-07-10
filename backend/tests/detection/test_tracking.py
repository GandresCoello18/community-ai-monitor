from app.detection.base import BoundingBox, RawDetection
from app.tracking.iou_tracker import IoUTracker


def _detection(object_class: str, x: int, y: int) -> RawDetection:
    return RawDetection(
        object_class=object_class,
        confidence=0.9,
        bbox=BoundingBox(x=x, y=y, width=50, height=100),
    )


def test_tracker_assigns_new_ids_to_new_objects() -> None:
    tracker = IoUTracker()

    tracked = tracker.update([_detection("person", 10, 10), _detection("car", 300, 10)])

    ids = {item.track_id for item in tracked}
    assert len(ids) == 2


def test_tracker_keeps_same_id_for_overlapping_object() -> None:
    tracker = IoUTracker(iou_threshold=0.3)

    first = tracker.update([_detection("person", 10, 10)])
    # Slightly moved box on the next frame → should match the same track.
    second = tracker.update([_detection("person", 14, 12)])

    assert first[0].track_id == second[0].track_id


def test_tracker_does_not_match_different_classes() -> None:
    tracker = IoUTracker(iou_threshold=0.3)

    first = tracker.update([_detection("person", 10, 10)])
    second = tracker.update([_detection("car", 10, 10)])

    assert first[0].track_id != second[0].track_id


def test_tracker_ages_out_missing_tracks() -> None:
    tracker = IoUTracker(iou_threshold=0.3, max_age=1)

    first = tracker.update([_detection("person", 10, 10)])
    tracker.update([])  # miss 1 (still alive)
    tracker.update([])  # miss 2 (aged out)
    reappear = tracker.update([_detection("person", 10, 10)])

    assert reappear[0].track_id != first[0].track_id


def test_tracker_returns_empty_for_no_detections() -> None:
    tracker = IoUTracker()

    assert tracker.update([]) == []
