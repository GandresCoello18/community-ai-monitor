export type DateRangePreset =
  | "today"
  | "yesterday"
  | "7d"
  | "30d"
  | "all"
  | "custom";

export interface DateRangeParams {
  start_date?: string;
  end_date?: string;
}

export const DATE_RANGE_PRESETS: Array<{
  id: DateRangePreset;
  label: string;
}> = [
  { id: "today", label: "Hoy" },
  { id: "yesterday", label: "Ayer" },
  { id: "7d", label: "7 días" },
  { id: "30d", label: "30 días" },
  { id: "all", label: "Todo" },
  { id: "custom", label: "Personalizado" },
];

function toIso(date: Date): string {
  return date.toISOString();
}

function startOfLocalDay(date: Date): Date {
  const value = new Date(date);
  value.setHours(0, 0, 0, 0);
  return value;
}

function endOfLocalDay(date: Date): Date {
  const value = new Date(date);
  value.setHours(23, 59, 59, 999);
  return value;
}

function addDays(date: Date, days: number): Date {
  const value = new Date(date);
  value.setDate(value.getDate() + days);
  return value;
}

export function getDateRangeParams(
  preset: DateRangePreset,
  customStart?: string,
  customEnd?: string,
  now: Date = new Date(),
): DateRangeParams {
  switch (preset) {
    case "today":
      return {
        start_date: toIso(startOfLocalDay(now)),
        end_date: toIso(endOfLocalDay(now)),
      };
    case "yesterday": {
      const yesterday = addDays(now, -1);
      return {
        start_date: toIso(startOfLocalDay(yesterday)),
        end_date: toIso(endOfLocalDay(yesterday)),
      };
    }
    case "7d":
      return {
        start_date: toIso(startOfLocalDay(addDays(now, -6))),
        end_date: toIso(endOfLocalDay(now)),
      };
    case "30d":
      return {
        start_date: toIso(startOfLocalDay(addDays(now, -29))),
        end_date: toIso(endOfLocalDay(now)),
      };
    case "custom": {
      if (!customStart || !customEnd) {
        return {};
      }
      const start = startOfLocalDay(new Date(`${customStart}T00:00:00`));
      const end = endOfLocalDay(new Date(`${customEnd}T00:00:00`));
      if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime()) || start > end) {
        return {};
      }
      return { start_date: toIso(start), end_date: toIso(end) };
    }
    case "all":
    default:
      return {};
  }
}

export function formatDateRangeLabel(
  preset: DateRangePreset,
  params: DateRangeParams,
): string {
  const presetLabel = DATE_RANGE_PRESETS.find((item) => item.id === preset)?.label;
  if (preset === "all") {
    return "Todo el historial";
  }
  if (preset === "custom" && params.start_date && params.end_date) {
    const formatter = new Intl.DateTimeFormat("es", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
    return `${formatter.format(new Date(params.start_date))} – ${formatter.format(new Date(params.end_date))}`;
  }
  return presetLabel ?? "Período seleccionado";
}

export function formatDayLabel(dayKey: string): string {
  return new Intl.DateTimeFormat("es", {
    day: "numeric",
    month: "short",
  }).format(new Date(`${dayKey}T12:00:00`));
}

export function sortDayEntries(
  byDay: Record<string, number>,
): Array<[string, number]> {
  return Object.entries(byDay).sort(([left], [right]) => left.localeCompare(right));
}
