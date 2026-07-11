import { Badge, Button } from "@/components/ui";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/Table";
import type { CameraLookup, Event } from "@/types/api";
import {
  formatDateTime,
  formatEventType,
  formatSeverity,
  severityVariant,
} from "@/utils/format";

interface EventsTableProps {
  events: Event[];
  camerasById?: Record<string, CameraLookup>;
  onSelectEvent?: (event: Event) => void;
  showActions?: boolean;
}

function cameraLabel(cameraId: string, camerasById?: Record<string, CameraLookup>): string {
  const camera = camerasById?.[cameraId];
  if (camera) {
    return camera.name;
  }
  return `${cameraId.slice(0, 8)}…`;
}

export function EventsTable({
  events,
  camerasById,
  onSelectEvent,
  showActions = true,
}: EventsTableProps) {
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeader>Tipo</TableHeader>
          <TableHeader>Severidad</TableHeader>
          <TableHeader>Fecha</TableHeader>
          <TableHeader>Cámara</TableHeader>
          {showActions && onSelectEvent && <TableHeader>Acción</TableHeader>}
        </TableRow>
      </TableHead>
      <TableBody>
        {events.map((event) => (
          <TableRow key={event.id}>
            <TableCell className="font-medium">
              {formatEventType(event.event_type)}
            </TableCell>
            <TableCell>
              <Badge variant={severityVariant(event.severity)}>
                {formatSeverity(event.severity)}
              </Badge>
            </TableCell>
            <TableCell className="text-[var(--color-muted)]">
              {formatDateTime(event.occurred_at)}
            </TableCell>
            <TableCell className="text-[var(--color-muted)]">
              <span title={camerasById?.[event.camera_id]?.location}>
                {cameraLabel(event.camera_id, camerasById)}
              </span>
            </TableCell>
            {showActions && onSelectEvent && (
              <TableCell>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onSelectEvent(event)}
                >
                  Ver detalle
                </Button>
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
