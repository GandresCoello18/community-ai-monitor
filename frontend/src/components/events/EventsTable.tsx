import { Badge } from "@/components/ui";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/Table";
import type { Event } from "@/types/api";
import {
  formatDateTime,
  formatEventType,
  severityVariant,
} from "@/utils/format";

interface EventsTableProps {
  events: Event[];
}

export function EventsTable({ events }: EventsTableProps) {
  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableHeader>Tipo</TableHeader>
          <TableHeader>Severidad</TableHeader>
          <TableHeader>Fecha</TableHeader>
          <TableHeader>Cámara</TableHeader>
        </TableRow>
      </TableHead>
      <TableBody>
        {events.map((event) => (
          <TableRow key={event.id}>
            <TableCell className="font-medium capitalize">
              {formatEventType(event.event_type)}
            </TableCell>
            <TableCell>
              <Badge variant={severityVariant(event.severity)}>
                {event.severity}
              </Badge>
            </TableCell>
            <TableCell className="text-[var(--color-muted)]">
              {formatDateTime(event.occurred_at)}
            </TableCell>
            <TableCell className="font-mono text-xs text-[var(--color-muted)]">
              {event.camera_id.slice(0, 8)}…
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
