from typing import Protocol

from app.rules.schemas.vehicle_metadata import VehicleMetadata


class PlateRecognitionProvider(Protocol):
    """Future interface for license-plate recognition (not implemented)."""

    def enrich(
        self,
        frame_bytes: bytes,
        metadata: VehicleMetadata,
    ) -> VehicleMetadata: ...


class NullPlateRecognitionProvider:
    """Default no-op provider until a dedicated LPR module exists."""

    def enrich(
        self,
        frame_bytes: bytes,
        metadata: VehicleMetadata,
    ) -> VehicleMetadata:
        return metadata
