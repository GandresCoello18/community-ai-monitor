from dataclasses import dataclass, field

from app.detection.base import BoundingBox, RawDetection
from app.tracking.base import TrackedDetection


def _iou(a: BoundingBox, b: BoundingBox) -> float:
    """Intersection-over-Union of two bounding boxes."""
    ax2, ay2 = a.x + a.width, a.y + a.height
    bx2, by2 = b.x + b.width, b.y + b.height

    inter_x1 = max(a.x, b.x)
    inter_y1 = max(a.y, b.y)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    intersection = inter_w * inter_h
    if intersection == 0:
        return 0.0

    union = (a.width * a.height) + (b.width * b.height) - intersection
    return intersection / union if union > 0 else 0.0


@dataclass(slots=True)
class _Track:
    track_id: int
    object_class: str
    bbox: BoundingBox
    misses: int = 0


@dataclass(slots=True)
class IoUTracker:
    """Lightweight, dependency-free online tracker based on IoU matching.

    Suitable for low frame-rate community monitoring. It assigns temporal track
    IDs by greedily matching detections to recent tracks of the same class.
    The `ObjectTracker` protocol keeps it swappable for ByteTrack/BoT-SORT
    later without touching the pipeline.
    """

    iou_threshold: float = 0.3
    max_age: int = 30
    _tracks: list[_Track] = field(default_factory=list, init=False)
    _next_id: int = field(default=1, init=False)

    def update(self, detections: list[RawDetection]) -> list[TrackedDetection]:
        matched_track_ids: set[int] = set()
        results: list[TrackedDetection] = []

        for detection in detections:
            best_track = self._find_best_match(detection, matched_track_ids)
            if best_track is None:
                best_track = _Track(
                    track_id=self._next_id,
                    object_class=detection.object_class,
                    bbox=detection.bbox,
                )
                self._next_id += 1
                self._tracks.append(best_track)
            else:
                best_track.bbox = detection.bbox
                best_track.misses = 0

            matched_track_ids.add(best_track.track_id)
            results.append(
                TrackedDetection(
                    track_id=best_track.track_id,
                    object_class=detection.object_class,
                    confidence=detection.confidence,
                    bbox=detection.bbox,
                )
            )

        self._age_out(matched_track_ids)
        return results

    def _find_best_match(
        self,
        detection: RawDetection,
        matched_track_ids: set[int],
    ) -> _Track | None:
        best_track: _Track | None = None
        best_iou = self.iou_threshold
        for track in self._tracks:
            if track.track_id in matched_track_ids:
                continue
            if track.object_class != detection.object_class:
                continue
            score = _iou(track.bbox, detection.bbox)
            if score >= best_iou:
                best_iou = score
                best_track = track
        return best_track

    def _age_out(self, matched_track_ids: set[int]) -> None:
        surviving: list[_Track] = []
        for track in self._tracks:
            if track.track_id not in matched_track_ids:
                track.misses += 1
            if track.misses <= self.max_age:
                surviving.append(track)
        self._tracks = surviving
