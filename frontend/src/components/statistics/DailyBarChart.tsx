import { Card } from "@/components/ui";
import { formatDayLabel, sortDayEntries } from "@/utils/dateRange";

interface DailyBarChartProps {
  byDay: Record<string, number>;
  className?: string;
}

export function DailyBarChart({ byDay, className }: DailyBarChartProps) {
  const entries = sortDayEntries(byDay);
  const maxValue = entries.reduce((max, [, value]) => Math.max(max, value), 0);

  return (
    <Card
      title="Actividad por día"
      description="Cantidad de eventos registrados en cada día del período."
      className={className}
    >
      {entries.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">
          No hay actividad registrada en este período.
        </p>
      ) : (
        <div
          className="flex h-48 items-end gap-2 sm:gap-3"
          role="img"
          aria-label="Gráfico de barras verticales por día"
        >
          {entries.map(([day, value]) => {
            const heightPercent =
              maxValue > 0 ? Math.max((value / maxValue) * 100, 8) : 0;

            return (
              <div
                key={day}
                className="flex min-w-0 flex-1 flex-col items-center gap-2"
              >
                <span className="text-xs font-semibold tabular-nums text-[var(--color-foreground)]">
                  {value}
                </span>
                <div className="flex w-full flex-1 items-end">
                  <div
                    className="w-full rounded-t-[var(--radius-sm)] bg-[var(--color-primary)] transition-[height] duration-300"
                    style={{ height: `${heightPercent}%` }}
                    title={`${formatDayLabel(day)}: ${value} eventos`}
                  />
                </div>
                <span className="max-w-full truncate text-center text-[10px] text-[var(--color-muted)] sm:text-xs">
                  {formatDayLabel(day)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
