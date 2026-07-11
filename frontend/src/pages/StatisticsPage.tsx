import { useMemo, useState } from "react";

import { QueryPanel } from "@/components/common/QueryPanel";
import {
  DailyBarChart,
  HorizontalBarChart,
  StatSummaryCards,
  StatisticsFilters,
  type BarChartItem,
} from "@/components/statistics";
import { useCameras } from "@/hooks/useCameras";
import { useEventStatistics } from "@/hooks/useEvents";
import {
  getDateRangeParams,
  type DateRangePreset,
} from "@/utils/dateRange";
import { formatEventType, formatSeverity } from "@/utils/format";

function severityBarColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case "critical":
    case "high":
      return "var(--color-destructive)";
    case "medium":
      return "var(--color-warning)";
    case "low":
    default:
      return "var(--color-info)";
  }
}

function recordToBarItems(
  items: Record<string, number>,
  formatKey: (key: string) => string,
  colorForKey?: (key: string) => string,
): BarChartItem[] {
  return Object.entries(items).map(([key, value]) => ({
    key,
    label: formatKey(key),
    value,
    color: colorForKey?.(key),
  }));
}

export function StatisticsPage() {
  const [preset, setPreset] = useState<DateRangePreset>("7d");
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");

  const dateRange = useMemo(
    () => getDateRangeParams(preset, customStart, customEnd),
    [preset, customStart, customEnd],
  );

  const skipCustomQuery =
    preset === "custom" && (!customStart || !customEnd || !dateRange.start_date);

  const statsQuery = useEventStatistics(dateRange);
  const camerasQuery = useCameras();
  const stats = statsQuery.data;

  const cameraNames = Object.fromEntries(
    (camerasQuery.data?.data ?? []).map((camera) => [camera.id, camera.name]),
  );

  const typeItems = useMemo(
    () => recordToBarItems(stats?.by_type ?? {}, formatEventType),
    [stats?.by_type],
  );

  const severityItems = useMemo(
    () =>
      recordToBarItems(
        stats?.by_severity ?? {},
        formatSeverity,
        severityBarColor,
      ),
    [stats?.by_severity],
  );

  const cameraItems = useMemo(
    () =>
      recordToBarItems(stats?.by_camera ?? {}, (cameraId) =>
        cameraNames[cameraId] ?? `Cámara ${cameraId.slice(0, 8)}…`,
      ),
    [stats?.by_camera, cameraNames],
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Estadísticas</h1>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Visualiza tendencias y distribución de eventos. Filtra por día o rango
          de fechas.
        </p>
      </div>

      <StatisticsFilters
        preset={preset}
        customStart={customStart}
        customEnd={customEnd}
        onPresetChange={setPreset}
        onCustomStartChange={setCustomStart}
        onCustomEndChange={setCustomEnd}
      />

      <QueryPanel
        isLoading={statsQuery.isLoading && !skipCustomQuery}
        error={skipCustomQuery ? null : statsQuery.error}
        isEmpty={!skipCustomQuery && stats?.total === 0}
        emptyTitle="Sin estadísticas"
        emptyDescription="No hay eventos en el período seleccionado. Prueba otro rango de fechas."
      >
        {stats && !skipCustomQuery && (
          <div className="space-y-6">
            <StatSummaryCards stats={stats} />

            <DailyBarChart byDay={stats.by_day ?? {}} />

            <div className="grid gap-4 xl:grid-cols-2">
              <HorizontalBarChart
                title="Por tipo de evento"
                description="Eventos más frecuentes en el período."
                items={typeItems}
              />
              <HorizontalBarChart
                title="Por severidad"
                description="Distribución según nivel de atención."
                items={severityItems}
              />
            </div>

            <HorizontalBarChart
              title="Por cámara"
              description="Cámaras con mayor actividad registrada."
              items={cameraItems}
            />
          </div>
        )}
      </QueryPanel>

      {skipCustomQuery && (
        <p className="text-sm text-[var(--color-muted)]">
          Elige un rango personalizado para ver las estadísticas.
        </p>
      )}
    </div>
  );
}
