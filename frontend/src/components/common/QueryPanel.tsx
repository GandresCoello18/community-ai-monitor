import type { ReactNode } from "react";

import { ApiError } from "@/api";
import { EmptyState, Spinner } from "@/components/ui";

interface QueryPanelProps {
  isLoading: boolean;
  error: Error | null;
  isEmpty?: boolean;
  emptyTitle: string;
  emptyDescription?: string;
  children: ReactNode;
}

export function QueryPanel({
  isLoading,
  error,
  isEmpty = false,
  emptyTitle,
  emptyDescription,
  children,
}: QueryPanelProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner label="Cargando datos" />
      </div>
    );
  }

  if (error) {
    const message =
      error instanceof ApiError
        ? error.message
        : "No fue posible cargar la información.";
    return (
      <EmptyState
        title="Error al conectar con el servidor"
        description={`${message} Verifica que el backend esté activo en el puerto 8000.`}
      />
    );
  }

  if (isEmpty) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return children;
}
