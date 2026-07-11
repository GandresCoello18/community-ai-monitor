import type { BadgeVariant } from "@/components/ui/Badge";

/** Etiquetas en español para tipos de evento (snake_case del backend). */
const EVENT_TYPE_LABELS: Record<string, string> = {
  person_long_stay: "Permanencia prolongada de persona",
  long_presence: "Presencia prolongada",
  person_repeated_activity: "Actividad repetida en la zona",
  person_hidden_activity: "Actividad poco visible",
  crowd_detected: "Aglomeración detectada",
  high_density: "Alta densidad de personas",
  vehicle_long_parking: "Vehículo estacionado mucho tiempo",
  double_parking: "Posible estacionamiento doble",
  wrong_direction: "Circulación en sentido incorrecto",
  park_occupancy_changed: "Cambio de ocupación en parque",
  park_empty: "Parque vacío por tiempo prolongado",
  abandoned_object: "Posible objeto abandonado",
  animal_detected: "Animal detectado",
  trash_detected: "Basura detectada",
  obstruction_detected: "Obstrucción detectada",
};

const SEVERITY_LABELS: Record<string, string> = {
  low: "Baja",
  medium: "Media",
  high: "Alta",
  critical: "Crítica",
};

const OBJECT_CLASS_LABELS: Record<string, string> = {
  person: "Persona",
  bicycle: "Bicicleta",
  car: "Automóvil",
  motorcycle: "Motocicleta",
  bus: "Autobús",
  truck: "Camión",
  dog: "Perro",
  cat: "Gato",
  backpack: "Mochila",
  handbag: "Bolso",
  suitcase: "Maleta",
};

const METADATA_FIELD_LABELS: Record<string, string> = {
  duration_seconds: "Duración",
  track_id: "Seguimiento temporal",
  object_class: "Tipo de objeto",
  visit_count: "Visitas en la zona",
  window_seconds: "Ventana de análisis",
  people_count: "Personas detectadas",
  vehicle_count: "Vehículos detectados",
  density_ratio: "Nivel de densidad",
  rule_name: "Regla activada",
  peak_session: "Pico de actividad",
  by_class: "Conteo por tipo",
  zones: "Zonas",
};

export function formatEventType(eventType: string): string {
  const normalized = eventType.trim().toLowerCase();
  if (EVENT_TYPE_LABELS[normalized]) {
    return EVENT_TYPE_LABELS[normalized];
  }
  return normalized.replaceAll("_", " ");
}

export function formatSeverity(severity: string): string {
  const normalized = severity.trim().toLowerCase();
  return SEVERITY_LABELS[normalized] ?? severity;
}

export function formatObjectClass(value: string): string {
  const normalized = value.trim().toLowerCase();
  return OBJECT_CLASS_LABELS[normalized] ?? value;
}

export function severityVariant(severity: string): BadgeVariant {
  switch (severity.toLowerCase()) {
    case "critical":
    case "high":
      return "danger";
    case "medium":
      return "warning";
    case "low":
      return "info";
    default:
      return "default";
  }
}

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds} segundos`;
  }
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) {
    return `${minutes} minuto${minutes === 1 ? "" : "s"}`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (remainingMinutes === 0) {
    return `${hours} hora${hours === 1 ? "" : "s"}`;
  }
  return `${hours} h ${remainingMinutes} min`;
}

function formatMetadataValue(key: string, value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }

  if (key === "duration_seconds" || key === "window_seconds") {
    return formatDuration(Number(value));
  }

  if (key === "object_class" && typeof value === "string") {
    return formatObjectClass(value);
  }

  if (key === "density_ratio" && typeof value === "number") {
    return `${Math.round(value * 100)} %`;
  }

  if (typeof value === "object") {
    if (Array.isArray(value)) {
      return `${value.length} elemento${value.length === 1 ? "" : "s"}`;
    }
    return Object.entries(value as Record<string, unknown>)
      .map(([nestedKey, nestedValue]) => {
        const name = OBJECT_CLASS_LABELS[nestedKey]
          ? formatObjectClass(nestedKey)
          : nestedKey.replaceAll("_", " ");
        return `${name}: ${String(nestedValue)}`;
      })
      .join(", ");
  }

  return String(value);
}

export interface MetadataRow {
  key: string;
  label: string;
  value: string;
}

/** Convierte metadata del evento en filas legibles para la UI. */
export function formatEventMetadata(
  metadata: Record<string, unknown> | null,
): MetadataRow[] {
  if (!metadata) {
    return [];
  }

  const rows: MetadataRow[] = [];

  for (const [key, value] of Object.entries(metadata)) {
    if (key === "rule_name" && typeof value === "string") {
      rows.push({
        key,
        label: METADATA_FIELD_LABELS.rule_name ?? "Regla",
        value: formatEventType(value),
      });
      continue;
    }

    if (key === "by_class" && value && typeof value === "object") {
      const parts = Object.entries(value as Record<string, number>).map(
        ([className, count]) => `${formatObjectClass(className)}: ${count}`,
      );
      rows.push({
        key,
        label: "Conteo por tipo",
        value: parts.join(" · "),
      });
      continue;
    }

    rows.push({
      key,
      label: METADATA_FIELD_LABELS[key] ?? key.replaceAll("_", " "),
      value: formatMetadataValue(key, value),
    });
  }

  return rows;
}
