"""Human-readable alert messages (Spanish, privacy-conscious)."""

from __future__ import annotations

from datetime import datetime

from app.models import Event

EVENT_TYPE_LABELS: dict[str, str] = {
    "person_long_stay": "Posible permanencia prolongada",
    "long_presence": "Posible presencia prolongada",
    "person_repeated_activity": "Posible actividad repetida en la zona",
    "person_hidden_activity": "Posible actividad poco visible",
    "crowd_detected": "Posible aglomeración",
    "high_density": "Posible alta densidad de personas",
    "vehicle_long_parking": "Posible vehículo estacionado mucho tiempo",
    "double_parking": "Posible estacionamiento doble",
    "wrong_direction": "Posible circulación incorrecta",
    "park_occupancy_changed": "Cambio de ocupación en parque",
    "park_empty": "Parque vacío por tiempo prolongado",
    "abandoned_object": "Posible objeto abandonado",
    "animal_detected": "Animal detectado",
    "trash_detected": "Posible basura detectada",
    "obstruction_detected": "Posible obstrucción detectada",
}

SEVERITY_LABELS: dict[str, str] = {
    "low": "Baja",
    "medium": "Media",
    "high": "Alta",
    "critical": "Crítica",
}


def format_event_type_label(event_type: str) -> str:
    normalized = event_type.strip().lower()
    if normalized in EVENT_TYPE_LABELS:
        return EVENT_TYPE_LABELS[normalized]
    return normalized.replace("_", " ")


def format_severity_label(severity: str) -> str:
    normalized = severity.strip().lower()
    return SEVERITY_LABELS.get(normalized, severity)


def format_event_alert_message(
    event: Event,
    *,
    camera_name: str,
    camera_location: str,
) -> str:
    """Build a concise alert without personal identifiers."""
    occurred = event.occurred_at.astimezone().strftime("%Y-%m-%d %H:%M %Z")
    event_label = format_event_type_label(event.event_type)
    severity_label = format_severity_label(event.severity)

    return (
        f"⚠️ Alerta — {camera_location}\n"
        f"Cámara: {camera_name}\n"
        f"Evento: {event_label}\n"
        f"Hora: {occurred}\n"
        f"Severidad: {severity_label}"
    )


def format_occurred_at(value: datetime) -> str:
    return value.astimezone().strftime("%Y-%m-%d %H:%M %Z")
