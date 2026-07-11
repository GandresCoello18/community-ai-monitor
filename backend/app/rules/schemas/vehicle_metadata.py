from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VehicleMetadata:
    """Structured vehicle context for future plate-recognition integration."""

    tracking_id: int
    object_class: str
    plate_number: str | None = None
    plate_confidence: float | None = None
