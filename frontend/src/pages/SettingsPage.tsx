import { Card, EmptyState } from "@/components/ui";

export function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Configuración</h1>
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          Preferencias del sistema y parámetros operativos.
        </p>
      </div>
      <Card>
        <EmptyState
          title="Configuración no disponible"
          description="Las opciones de configuración se habilitarán en fases posteriores."
        />
      </Card>
    </div>
  );
}
