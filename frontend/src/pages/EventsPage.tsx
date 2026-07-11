import { useMemo, useState } from "react";

import { Button, Card } from "@/components/ui";
import { QueryPanel } from "@/components/common/QueryPanel";
import { EventDetailModal } from "@/components/events/EventDetailModal";
import { EventSummaryPanel } from "@/components/events/EventSummaryPanel";
import { EventsTable } from "@/components/events/EventsTable";
import { useCameras } from "@/hooks/useCameras";
import { useEvents } from "@/hooks/useEvents";
import type { CameraLookup, Event } from "@/types/api";

function buildCameraMap(
  cameras: { id: string; name: string; location: string }[],
): Record<string, CameraLookup> {
  return Object.fromEntries(
    cameras.map((camera) => [
      camera.id,
      { name: camera.name, location: camera.location },
    ]),
  );
}

export function EventsPage() {
  const [page, setPage] = useState(1);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const limit = 20;
  const eventsQuery = useEvents({ page, limit });
  const camerasQuery = useCameras();
  const events = eventsQuery.data?.data ?? [];
  const total = eventsQuery.data?.meta.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  const camerasById = useMemo(
    () => buildCameraMap(camerasQuery.data?.data ?? []),
    [camerasQuery.data?.data],
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Eventos</h1>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Historial de eventos detectados por el sistema. Pulsa &quot;Ver detalle&quot; para
          consultar la información completa de cada alerta.
        </p>
      </div>

      <EventSummaryPanel />

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
          <EventsTable
            events={events}
            camerasById={camerasById}
            onSelectEvent={setSelectedEvent}
          />
        </QueryPanel>
      </Card>

      <EventDetailModal
        event={selectedEvent}
        camera={
          selectedEvent ? camerasById[selectedEvent.camera_id] : undefined
        }
        onClose={() => setSelectedEvent(null)}
      />
    </div>
  );
}
