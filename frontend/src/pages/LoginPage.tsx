import { Card, EmptyState } from "@/components/ui";

export function LoginPage() {
  return (
    <Card title="Iniciar sesión" description="Autenticación pendiente de implementación.">
      <EmptyState
        title="Próximamente"
        description="La autenticación real se implementará en una fase posterior."
      />
    </Card>
  );
}
