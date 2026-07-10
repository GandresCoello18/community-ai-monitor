import logging
import threading

import numpy as np

from app.detection.base import BoundingBox, RawDetection

logger = logging.getLogger(__name__)


class YOLODetector:
    """Object detector backed by an Ultralytics YOLO model.

    The heavy `ultralytics`/`torch` dependency is imported lazily so the rest
    of the app can run without it (see `detection.factory`).
    """

    def __init__(
        self,
        model_path: str,
        *,
        confidence: float = 0.4,
        allowed_classes: frozenset[str] | None = None,
        device: str = "cpu",
    ) -> None:
        from ultralytics import YOLO  # noqa: PLC0415 (lazy, optional dependency)

        self._model = YOLO(model_path)
        self._model_path = model_path
        self._confidence = confidence
        self._allowed_classes = allowed_classes
        self._device = device
        # Ultralytics models are not safe for concurrent inference from
        # multiple camera worker threads; serialize access.
        self._lock = threading.Lock()
        logger.info(
            "YOLO detector loaded model=%s device=%s conf=%.2f",
            model_path,
            device,
            confidence,
        )

    @property
    def model_name(self) -> str:
        return self._model_path

    def detect(self, image: np.ndarray) -> list[RawDetection]:
        with self._lock:
            results = self._model.predict(
                source=image,
                conf=self._confidence,
                device=self._device,
                verbose=False,
            )

        detections: list[RawDetection] = []
        for result in results:
            names = result.names
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                class_index = int(box.cls[0])
                object_class = names.get(class_index, str(class_index))
                if (
                    self._allowed_classes is not None
                    and object_class not in self._allowed_classes
                ):
                    continue

                x1, y1, x2, y2 = (float(value) for value in box.xyxy[0])
                detections.append(
                    RawDetection(
                        object_class=object_class,
                        confidence=round(float(box.conf[0]), 4),
                        bbox=BoundingBox(
                            x=int(x1),
                            y=int(y1),
                            width=int(x2 - x1),
                            height=int(y2 - y1),
                        ),
                    )
                )
        return detections
