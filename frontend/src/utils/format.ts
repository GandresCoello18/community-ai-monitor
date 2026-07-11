import type { BadgeVariant } from "@/components/ui/Badge";

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return "—";
  }
  return new Intl.DateTimeFormat("es", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

export {
  formatEventType,
  formatSeverity,
  formatObjectClass,
  severityVariant,
  formatEventMetadata,
} from "./events";
export type { MetadataRow } from "./events";

export function streamStatusVariant(status: string): BadgeVariant {
  switch (status.toLowerCase()) {
    case "running":
      return "success";
    case "error":
      return "danger";
    case "stopped":
      return "default";
    default:
      return "warning";
  }
}
