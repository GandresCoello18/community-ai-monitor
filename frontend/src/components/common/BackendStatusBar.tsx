import { Badge } from "@/components/ui";
import { useHealth } from "@/hooks/useHealth";
import { useRealtimeEvents } from "@/hooks/useRealtimeEvents";

const statusLabels = {
  connected: "Tiempo real activo",
  connecting: "Conectando…",
  disconnected: "Desconectado",
  error: "Error WS",
  idle: "Inactivo",
} as const;

export function BackendStatusBar() {
  const { data: health, isLoading, isError } = useHealth();
  const { status: wsStatus } = useRealtimeEvents();

  const apiLabel = isLoading
    ? "Verificando API…"
    : isError
      ? "API no disponible"
      : health?.status === "ok"
        ? "API conectada"
        : "API con problemas";

  const apiVariant = isError ? "danger" : health?.status === "ok" ? "success" : "warning";
  const wsVariant =
    wsStatus === "connected"
      ? "success"
      : wsStatus === "error"
        ? "danger"
        : "default";

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant={apiVariant}>{apiLabel}</Badge>
      <Badge variant={wsVariant}>{statusLabels[wsStatus]}</Badge>
    </div>
  );
}
