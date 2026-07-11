import { Card } from "@/components/ui";
import { cn } from "@/utils/cn";

export interface BarChartItem {
  key: string;
  label: string;
  value: number;
  color?: string;
}

interface HorizontalBarChartProps {
  title: string;
  description?: string;
  items: BarChartItem[];
  emptyMessage?: string;
  className?: string;
}

export function HorizontalBarChart({
  title,
  description,
  items,
  emptyMessage = "Sin datos para este período.",
  className,
}: HorizontalBarChartProps) {
  const sortedItems = [...items].sort((left, right) => right.value - left.value);
  const maxValue = sortedItems[0]?.value ?? 0;

  return (
    <Card title={title} description={description} className={className}>
      {sortedItems.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">{emptyMessage}</p>
      ) : (
        <ul
          className="space-y-4"
          role="list"
          aria-label={`Gráfico de barras: ${title}`}
        >
          {sortedItems.map((item) => {
            const widthPercent =
              maxValue > 0 ? Math.max((item.value / maxValue) * 100, 4) : 0;

            return (
              <li key={item.key} className="space-y-1.5">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="min-w-0 flex-1 truncate" title={item.label}>
                    {item.label}
                  </span>
                  <span className="shrink-0 font-semibold tabular-nums">
                    {item.value}
                  </span>
                </div>
                <div
                  className="h-2.5 overflow-hidden rounded-full bg-[var(--color-secondary)]"
                  aria-hidden
                >
                  <div
                    className={cn("h-full rounded-full transition-[width] duration-300")}
                    style={{
                      width: `${widthPercent}%`,
                      backgroundColor: item.color ?? "var(--color-primary)",
                    }}
                  />
                </div>
                <span className="sr-only">
                  {item.label}: {item.value} eventos
                </span>
              </li>
            );
          })}
        </ul>
      )}
    </Card>
  );
}
