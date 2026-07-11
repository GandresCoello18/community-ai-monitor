import { Card } from "@/components/ui";
import { QueryPanel } from "@/components/common/QueryPanel";
import { useEventStatistics } from "@/hooks/useEvents";

function BreakdownList({
  title,
  items,
}: {
  title: string;
  items: Record<string, number>;
}) {
  const entries = Object.entries(items).sort(([, a], [, b]) => b - a);

  return (
    <Card title={title}>
      {entries.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">Sin datos.</p>
      ) : (
        <ul className="space-y-2">
          {entries.map(([key, value]) => (
            <li
              key={key}
              className="flex items-center justify-between text-sm"
            >
              <span className="capitalize">{key.replaceAll("_", " ")}</span>
              <span className="font-semibold">{value}</span>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

export function StatisticsPage() {
  const statsQuery = useEventStatistics();
  const stats = statsQuery.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Estadísticas</h1>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Métricas agregadas de eventos del sistema.
        </p>
      </div>

      <QueryPanel
        isLoading={statsQuery.isLoading}
        error={statsQuery.error}
        isEmpty={stats?.total === 0}
        emptyTitle="Sin estadísticas"
        emptyDescription="Las métricas aparecerán cuando existan eventos registrados."
      >
        <div className="grid gap-4 lg:grid-cols-3">
          <BreakdownList title="Por tipo" items={stats?.by_type ?? {}} />
          <BreakdownList title="Por severidad" items={stats?.by_severity ?? {}} />
          <BreakdownList title="Por cámara" items={stats?.by_camera ?? {}} />
        </div>
      </QueryPanel>
    </div>
  );
}
