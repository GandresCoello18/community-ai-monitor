from dataclasses import dataclass
from typing import Literal

from app.core.config import Settings

SceneType = Literal["street", "park", "general"]


@dataclass(frozen=True, slots=True)
class ParkZoneConfig:
    """Normalized frame zones for park analytics (0.0–1.0)."""

    playground: tuple[float, float, float, float] = (0.0, 0.0, 0.33, 0.55)
    sports: tuple[float, float, float, float] = (0.33, 0.0, 0.66, 0.55)
    green: tuple[float, float, float, float] = (0.66, 0.0, 1.0, 0.55)


@dataclass(frozen=True, slots=True)
class RulesConfig:
    """Centralized thresholds for the community rule engine."""

    enabled: bool = True
    cooldown_seconds: float = 60.0
    scene_type: SceneType = "general"

    # Person rules
    person_long_stay_enabled: bool = True
    person_long_stay_seconds: float = 1200.0
    person_repeated_activity_enabled: bool = True
    person_repeated_activity_window_seconds: float = 1800.0
    person_repeated_activity_min_visits: int = 3
    person_repeated_activity_zone_radius: float = 80.0
    person_hidden_activity_enabled: bool = True
    person_hidden_stay_seconds: float = 900.0
    person_hidden_max_movement: float = 20.0
    crowd_enabled: bool = True
    crowd_threshold: int = 15
    high_density_enabled: bool = True
    high_density_min_people: int = 3
    high_density_threshold: float = 0.15

    # Vehicle rules
    vehicle_long_parking_enabled: bool = True
    vehicle_parking_seconds: float = 600.0
    vehicle_parking_movement_threshold: float = 15.0
    double_parking_enabled: bool = True
    double_parking_seconds: float = 180.0
    street_zone_y_start: float = 0.55
    wrong_direction_enabled: bool = False
    expected_traffic_direction: Literal["ltr", "rtl"] = "ltr"
    wrong_direction_min_displacement: float = 40.0

    # Park rules
    park_occupancy_enabled: bool = True
    park_occupancy_change_threshold: int = 5
    park_empty_enabled: bool = True
    park_empty_seconds: float = 1800.0
    park_zones: ParkZoneConfig = ParkZoneConfig()

    # Object / animal
    abandoned_object_enabled: bool = True
    abandoned_object_seconds: float = 900.0
    abandoned_object_movement_threshold: float = 15.0
    abandoned_object_classes: frozenset[str] = frozenset(
        {"backpack", "handbag", "suitcase", "bicycle"}
    )
    animal_enabled: bool = True
    animal_classes: frozenset[str] = frozenset({"dog", "cat"})
    animal_cooldown_seconds: float = 60.0

    # Placeholders for future specialized models
    trash_detected_enabled: bool = False
    obstruction_detected_enabled: bool = False

    # Legacy event type aliases (backward compatibility)
    emit_legacy_event_types: bool = True

    @classmethod
    def from_settings(cls, settings: Settings) -> "RulesConfig":
        return cls(
            enabled=settings.rule_engine_enabled,
            cooldown_seconds=settings.event_cooldown_seconds,
            scene_type=settings.rule_scene_type,  # type: ignore[arg-type]
            person_long_stay_enabled=(
                settings.rule_person_long_stay_enabled
                and settings.event_long_presence_enabled
            ),
            person_long_stay_seconds=settings.rule_person_long_stay_seconds,
            person_repeated_activity_enabled=settings.rule_person_repeated_activity_enabled,
            person_repeated_activity_window_seconds=(
                settings.rule_person_repeated_activity_window_seconds
            ),
            person_repeated_activity_min_visits=(
                settings.rule_person_repeated_activity_min_visits
            ),
            person_repeated_activity_zone_radius=(
                settings.rule_person_repeated_activity_zone_radius
            ),
            person_hidden_activity_enabled=settings.rule_person_hidden_activity_enabled,
            person_hidden_stay_seconds=settings.rule_person_hidden_stay_seconds,
            person_hidden_max_movement=settings.rule_person_hidden_max_movement,
            crowd_enabled=settings.event_crowd_enabled,
            crowd_threshold=settings.rule_crowd_threshold,
            high_density_enabled=settings.event_high_density_enabled,
            high_density_min_people=settings.event_high_density_min_people,
            high_density_threshold=settings.event_high_density_threshold,
            vehicle_long_parking_enabled=settings.rule_vehicle_long_parking_enabled,
            vehicle_parking_seconds=settings.rule_vehicle_parking_seconds,
            vehicle_parking_movement_threshold=(
                settings.rule_vehicle_parking_movement_threshold
            ),
            double_parking_enabled=settings.rule_double_parking_enabled,
            double_parking_seconds=settings.rule_double_parking_seconds,
            street_zone_y_start=settings.rule_street_zone_y_start,
            wrong_direction_enabled=settings.rule_wrong_direction_enabled,
            expected_traffic_direction=settings.rule_expected_traffic_direction,  # type: ignore[arg-type]
            wrong_direction_min_displacement=settings.rule_wrong_direction_min_displacement,
            park_occupancy_enabled=settings.rule_park_occupancy_enabled,
            park_occupancy_change_threshold=settings.rule_park_occupancy_change_threshold,
            park_empty_enabled=settings.rule_park_empty_enabled,
            park_empty_seconds=settings.rule_park_empty_seconds,
            abandoned_object_enabled=settings.event_abandoned_object_enabled,
            abandoned_object_seconds=settings.rule_abandoned_object_seconds,
            abandoned_object_movement_threshold=(
                settings.event_abandoned_movement_threshold
            ),
            abandoned_object_classes=settings.event_abandoned_class_set,
            animal_enabled=settings.rule_animal_enabled,
            animal_classes=settings.rule_animal_class_set,
            animal_cooldown_seconds=settings.rule_animal_cooldown_seconds,
            trash_detected_enabled=settings.rule_trash_detected_enabled,
            obstruction_detected_enabled=settings.rule_obstruction_detected_enabled,
            emit_legacy_event_types=settings.rule_emit_legacy_event_types,
        )
