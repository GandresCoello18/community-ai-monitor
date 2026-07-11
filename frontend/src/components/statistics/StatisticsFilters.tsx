import { Button, Input } from "@/components/ui";
import {
  DATE_RANGE_PRESETS,
  formatDateRangeLabel,
  getDateRangeParams,
  type DateRangeParams,
  type DateRangePreset,
} from "@/utils/dateRange";
import { cn } from "@/utils/cn";

interface StatisticsFiltersProps {
  preset: DateRangePreset;
  customStart: string;
  customEnd: string;
  onPresetChange: (preset: DateRangePreset) => void;
  onCustomStartChange: (value: string) => void;
  onCustomEndChange: (value: string) => void;
}

export function StatisticsFilters({
  preset,
  customStart,
  customEnd,
  onPresetChange,
  onCustomStartChange,
  onCustomEndChange,
}: StatisticsFiltersProps) {
  const rangeParams: DateRangeParams = getDateRangeParams(
    preset,
    customStart,
    customEnd,
  );
  const periodLabel = formatDateRangeLabel(preset, rangeParams);
  const customIncomplete =
    preset === "custom" && (!customStart || !customEnd || !rangeParams.start_date);

  return (
    <div className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-4 shadow-[var(--shadow-sm)]">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-3">
          <div>
            <p className="text-sm font-medium">Período</p>
            <p className="text-xs text-[var(--color-muted)]">{periodLabel}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {DATE_RANGE_PRESETS.map((item) => (
              <Button
                key={item.id}
                size="sm"
                variant={preset === item.id ? "primary" : "secondary"}
                onClick={() => onPresetChange(item.id)}
                aria-pressed={preset === item.id}
              >
                {item.label}
              </Button>
            ))}
          </div>
        </div>

        {preset === "custom" && (
          <div
            className={cn(
              "grid gap-3 sm:grid-cols-2",
              customIncomplete && "rounded-[var(--radius-md)] border border-[var(--color-warning)]/40 p-3",
            )}
          >
            <Input
              type="date"
              label="Desde"
              value={customStart}
              onChange={(event) => onCustomStartChange(event.target.value)}
            />
            <Input
              type="date"
              label="Hasta"
              value={customEnd}
              onChange={(event) => onCustomEndChange(event.target.value)}
            />
            {customIncomplete && (
              <p className="sm:col-span-2 text-xs text-[var(--color-warning)]">
                Selecciona fecha de inicio y fin para aplicar el filtro.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
