import { Badge } from "@/components/ui";
import { Modal } from "@/components/ui/Modal";
import type { CameraLookup, Event } from "@/types/api";
import {
  formatDateTime,
  formatEventMetadata,
  formatEventType,
  formatSeverity,
  severityVariant,
} from "@/utils/format";

interface EventDetailModalProps {
  event: Event | null;
  camera?: CameraLookup;
  onClose: () => void;
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 sm:flex-row sm:items-start sm:justify-between sm:gap-4">
      <dt className="shrink-0 text-sm text-[var(--color-muted)]">{label}</dt>
      <dd className="text-sm font-medium text-[var(--color-foreground)] sm:text-right">
        {value}
      </dd>
    </div>
  );
}

export function EventDetailModal({ event, camera, onClose }: EventDetailModalProps) {
  if (!event) {
    return null;
  }

  const metadataRows = formatEventMetadata(event.metadata);

  return (
    <Modal
      open={Boolean(event)}
      title={formatEventType(event.event_type)}
      description="Detalle del evento detectado por el sistema."
      onClose={onClose}
      panelClassName="max-w-2xl"
    >
      <div className="space-y-6">
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant={severityVariant(event.severity)}>
            Severidad {formatSeverity(event.severity)}
          </Badge>
          <span className="text-xs text-[var(--color-muted)]">
            ID {event.id.slice(0, 8)}…
          </span>
        </div>

        <dl className="space-y-3 rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface-hover)] p-4">
          <DetailRow label="Fecha del evento" value={formatDateTime(event.occurred_at)} />
          {event.started_at && (
            <DetailRow label="Inicio detectado" value={formatDateTime(event.started_at)} />
          )}
          {event.ended_at && (
            <DetailRow label="Fin detectado" value={formatDateTime(event.ended_at)} />
          )}
          <DetailRow
            label="Cámara"
            value={
              camera
                ? `${camera.name} — ${camera.location}`
                : event.camera_id.slice(0, 8) + "…"
            }
          />
          <DetailRow label="Registrado en sistema" value={formatDateTime(event.created_at)} />
        </dl>

        {metadataRows.length > 0 ? (
          <section>
            <h3 className="mb-3 text-sm font-semibold">Información detectada</h3>
            <dl className="space-y-3">
              {metadataRows.map((row) => (
                <DetailRow key={row.key} label={row.label} value={row.value} />
              ))}
            </dl>
          </section>
        ) : (
          <p className="text-sm text-[var(--color-muted)]">
            No hay datos adicionales para este evento.
          </p>
        )}

        {event.metadata && Object.keys(event.metadata).length > 0 && (
          <details className="rounded-[var(--radius-md)] border border-[var(--color-border)]">
            <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-[var(--color-muted)]">
              Ver datos técnicos (JSON)
            </summary>
            <pre className="overflow-x-auto border-t border-[var(--color-border)] bg-[var(--color-surface-hover)] p-4 text-xs">
              {JSON.stringify(event.metadata, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </Modal>
  );
}
