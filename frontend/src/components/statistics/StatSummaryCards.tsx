import type { EventStatistics } from "@/types/api";

interface StatSummaryCardsProps {
  stats: EventStatistics;
}

function SummaryCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: number | string;
  hint?: string;
}) {
  return (
    <div className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-4 shadow-[var(--shadow-sm)]">
      <p className="text-sm text-[var(--color-muted)]">{label}</p>
      <p className="mt-1 text-3xl font-semibold tabular-nums">{value}</p>
      {hint && (
        <p className="mt-1 text-xs text-[var(--color-muted)]">{hint}</p>
      )}
    </div>
  );
}

export function StatSummaryCards({ stats }: StatSummaryCardsProps) {
  const highSeverity =
    (stats.by_severity.high ?? 0) + (stats.by_severity.critical ?? 0);
  const eventTypes = Object.keys(stats.by_type).length;
  const activeCameras = Object.keys(stats.by_camera).length;

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <SummaryCard label="Total de eventos" value={stats.total} />
      <SummaryCard
        label="Alta severidad"
        value={highSeverity}
        hint="Eventos con severidad alta o crítica"
      />
      <SummaryCard
        label="Tipos de evento"
        value={eventTypes}
        hint="Categorías distintas detectadas"
      />
      <SummaryCard
        label="Cámaras con actividad"
        value={activeCameras}
        hint="Cámaras que registraron eventos"
      />
    </div>
  );
}
