from uuid import UUID

from app.core.config import Settings
from app.rules.config import RulesConfig
from app.rules.engine import RuleEngine
from app.rules.rules.animal_rules import build_animal_rules
from app.rules.rules.maintenance_rules import build_maintenance_rules
from app.rules.rules.object_rules import build_object_rules
from app.rules.rules.park_rules import build_park_rules
from app.rules.rules.person_rules import build_person_rules
from app.rules.rules.traffic_rules import build_traffic_rules
from app.rules.rules.vehicle_rules import build_vehicle_rules


def build_rules(settings: Settings) -> list[object]:
    config = RulesConfig.from_settings(settings)
    rules: list[object] = []

    rules.extend(build_person_rules(config))
    rules.extend(build_traffic_rules(config))
    rules.extend(build_object_rules(config))
    rules.extend(build_animal_rules(config))

    scene = config.scene_type
    if scene in {"street", "general"}:
        rules.extend(build_vehicle_rules(config))
    if scene in {"park", "general"}:
        rules.extend(build_park_rules(config))

    rules.extend(build_maintenance_rules(config))

    if not config.enabled:
        return []
    return rules


def create_rule_engine(camera_id: UUID, settings: Settings) -> RuleEngine:
    return RuleEngine(camera_id, build_rules(settings))  # type: ignore[arg-type]
