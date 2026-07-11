import { Link } from "react-router-dom";

import { EmptyState } from "@/components/ui";
import { paths } from "@/routes/paths";
import { cn } from "@/utils/cn";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <EmptyState
        title="Página no encontrada"
        description="La ruta que buscas no existe o fue movida."
        action={
          <Link
            to={paths.dashboard}
            className={cn(
              "inline-flex h-10 items-center justify-center rounded-[var(--radius-md)] px-4 text-sm font-medium",
              "bg-[var(--color-primary)] text-[var(--color-primary-foreground)] hover:opacity-90",
            )}
          >
            Ir al panel
          </Link>
        }
      />
    </div>
  );
}
