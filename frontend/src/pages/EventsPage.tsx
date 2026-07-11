import { useState } from "react";

import { Button, Card } from "@/components/ui";
import { QueryPanel } from "@/components/common/QueryPanel";
import { EventsTable } from "@/components/events/EventsTable";
import { useEvents } from "@/hooks/useEvents";

export function EventsPage() {
  const [page, setPage] = useState(1);
  const limit = 20;
  const eventsQuery = useEvents({ page, limit });
  const events = eventsQuery.data?.data ?? [];
  const total = eventsQuery.data?.meta.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Eventos</h1>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Historial de eventos detectados por el sistema.
        </p>
      </div>

      <Card
        title="Historial"
        description={`${total} evento${total === 1 ? "" : "s"} registrados`}
        footer={
          totalPages > 1 ? (
            <div className="flex items-center justify-between">
              <Button
                variant="secondary"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((current) => Math.max(1, current - 1))}
              >
                Anterior
              </Button>
              <span className="text-sm text-[var(--color-muted)]">
                Página {page} de {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages}
                onClick={() =>
                  setPage((current) => Math.min(totalPages, current + 1))
                }
              >
                Siguiente
              </Button>
            </div>
          ) : undefined
        }
      >
        <QueryPanel
          isLoading={eventsQuery.isLoading}
          error={eventsQuery.error}
          isEmpty={events.length === 0}
          emptyTitle="Sin eventos"
          emptyDescription="Cuando el motor de reglas detecte actividad, los eventos se mostrarán aquí."
        >
          <EventsTable events={events} />
        </QueryPanel>
      </Card>
    </div>
  );
}
