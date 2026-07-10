from app.llm.schemas import SummaryContext

SUMMARY_SYSTEM_INSTRUCTIONS = (
    "Eres un asistente de monitoreo comunitario. Recibes eventos estructurados "
    "detectados por cámaras (conteos, permanencias, objetos abandonados). "
    "Redacta un resumen breve y claro en español para los administradores de la "
    "comunidad. No inventes datos que no estén en los eventos. No especules "
    "sobre identidades de personas. Usa un tono informativo y neutral."
)


def build_summary_prompt(context: SummaryContext) -> str:
    """Render the structured event context as a prompt for the LLM."""
    lines = [
        SUMMARY_SYSTEM_INSTRUCTIONS,
        "",
        f"Período: {context.period_start.isoformat()} a "
        f"{context.period_end.isoformat()}",
        f"Total de eventos: {context.total_events}",
        "",
        "Eventos por tipo:",
    ]
    for event_type, count in sorted(context.events_by_type.items()):
        lines.append(f"- {event_type}: {count}")

    lines.append("")
    lines.append("Eventos por severidad:")
    for severity, count in sorted(context.events_by_severity.items()):
        lines.append(f"- {severity}: {count}")

    lines.append("")
    lines.append("Detalle de eventos:")
    for event in context.events:
        detail = (
            f"- [{event.occurred_at.strftime('%H:%M')}] "
            f"{event.event_type} (severidad {event.severity}) "
            f"en {event.camera_name}"
        )
        if event.metadata:
            interesting = {
                key: value
                for key, value in event.metadata.items()
                if key in {"people_count", "duration_seconds", "object_class"}
            }
            if interesting:
                detail += f" — {interesting}"
        lines.append(detail)

    lines.append("")
    lines.append(
        "Escribe un resumen de 2 a 4 oraciones describiendo la actividad del "
        "período. Si hay eventos de severidad alta, menciónalos primero."
    )
    return "\n".join(lines)
