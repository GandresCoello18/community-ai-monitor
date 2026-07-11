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

export function formatEventType(eventType: string): string {
  return eventType.replaceAll("_", " ");
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
