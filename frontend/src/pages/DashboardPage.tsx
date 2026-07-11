import { Card } from "@/components/ui";
import { QueryPanel } from "@/components/common/QueryPanel";
import { EventsTable } from "@/components/events/EventsTable";
import { useEventStatistics, useEvents } from "@/hooks/useEvents";

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <Card className="px-5 py-4">
      <p className="text-sm text-[var(--color-muted)]">{label}</p>
      <p className="mt-2 text-3xl font-semibold">{value}</p>
    </Card>
  );
}

export function DashboardPage() {
  const statsQuery = useEventStatistics();
  const eventsQuery = useEvents({ page: 1, limit: 8 });

  const stats = statsQuery.data;
  const recentEvents = eventsQuery.data?.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Panel</h1>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Resumen del estado de la comunidad.
        </p>
      </div>

      <QueryPanel
        isLoading={statsQuery.isLoading}
        error={statsQuery.error}
        emptyTitle="Sin estadísticas"
        emptyDescription="Aún no hay eventos registrados en el sistema."
        isEmpty={stats?.total === 0}
      >
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Eventos totales" value={stats?.total ?? 0} />
          <StatCard
            label="Tipos distintos"
            value={Object.keys(stats?.by_type ?? {}).length}
          />
          <StatCard
            label="Severidad alta"
            value={
              (stats?.by_severity?.high ?? 0) +
              (stats?.by_severity?.critical ?? 0)
            }
          />
          <StatCard
            label="Cámaras con actividad"
            value={Object.keys(stats?.by_camera ?? {}).length}
          />
        </div>
      </QueryPanel>

      <Card title="Eventos recientes" description="Últimos eventos detectados">
        <QueryPanel
          isLoading={eventsQuery.isLoading}
          error={eventsQuery.error}
          isEmpty={recentEvents.length === 0}
          emptyTitle="Sin eventos recientes"
          emptyDescription="Los nuevos eventos aparecerán aquí en tiempo real."
        >
          <EventsTable events={recentEvents} />
        </QueryPanel>
      </Card>
    </div>
  );
}
