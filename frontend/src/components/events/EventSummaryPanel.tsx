import { Button, Card } from "@/components/ui";
import { QueryPanel } from "@/components/common/QueryPanel";
import { useGenerateSummary, useSummaries } from "@/hooks/useSummaries";
import { formatDateTime } from "@/utils/format";

export function EventSummaryPanel() {
  const summariesQuery = useSummaries(3);
  const generateMutation = useGenerateSummary();
  const summaries = summariesQuery.data?.data ?? [];
  const latest = summaries[0];

  return (
    <Card
      title="Resumen con inteligencia artificial"
      description="Análisis en lenguaje natural de los eventos recientes. No reemplaza la revisión humana."
      footer={
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-[var(--color-muted)]">
            El resumen analiza un periodo de eventos, no un evento individual.
          </p>
          <Button
            size="sm"
            disabled={generateMutation.isPending}
            onClick={() => generateMutation.mutate()}
          >
            {generateMutation.isPending ? "Generando…" : "Generar resumen de hoy"}
          </Button>
        </div>
      }
    >
      <QueryPanel
        isLoading={summariesQuery.isLoading}
        error={summariesQuery.error}
        isEmpty={!latest && !generateMutation.isPending}
        emptyTitle="Sin resúmenes todavía"
        emptyDescription='Pulsa "Generar resumen de hoy" para crear un análisis con IA de las últimas 24 horas.'
      >
        <div className="space-y-4">
          {generateMutation.isError && (
            <p className="rounded-[var(--radius-md)] border border-[var(--color-destructive)]/30 bg-[var(--color-destructive)]/10 px-4 py-3 text-sm text-[var(--color-destructive)]">
              No se pudo generar el resumen. Verifica que Ollama esté activo en el backend.
            </p>
          )}
          {latest && (
            <article className="rounded-[var(--radius-md)] border border-[var(--color-border)] bg-[var(--color-surface-hover)] p-4">
              <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-[var(--color-muted)]">
                <span>
                  Periodo: {formatDateTime(latest.period_start)} —{" "}
                  {formatDateTime(latest.period_end)}
                </span>
                <span>·</span>
                <span>{latest.total_events} eventos analizados</span>
                <span>·</span>
                <span>
                  {latest.llm_model} ({latest.llm_provider})
                </span>
              </div>
              <p className="whitespace-pre-wrap text-sm leading-relaxed">
                {latest.summary_text}
              </p>
            </article>
          )}

          {summaries.length > 1 && (
            <section>
              <h3 className="mb-2 text-sm font-semibold text-[var(--color-muted)]">
                Resúmenes anteriores
              </h3>
              <ul className="space-y-2">
                {summaries.slice(1).map((summary) => (
                  <li
                    key={summary.id}
                    className="rounded-[var(--radius-md)] border border-[var(--color-border)] px-4 py-3"
                  >
                    <p className="text-xs text-[var(--color-muted)]">
                      {formatDateTime(summary.period_start)} —{" "}
                      {formatDateTime(summary.period_end)} · {summary.total_events} eventos
                    </p>
                    <p className="mt-1 line-clamp-2 text-sm">{summary.summary_text}</p>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </QueryPanel>
    </Card>
  );
}
