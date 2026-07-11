import { NavLink, Outlet } from "react-router-dom";

import { BackendStatusBar } from "@/components/common/BackendStatusBar";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { mainNavItems } from "@/routes/paths";
import { cn } from "@/utils/cn";

export function DashboardLayout() {
  return (
    <div className="flex min-h-screen bg-[var(--color-background)]">
      <aside
        className="hidden w-64 shrink-0 border-r border-[var(--color-border)] bg-[var(--color-surface)] md:flex md:flex-col"
        aria-label="Navegación principal"
      >
        <div className="border-b border-[var(--color-border)] px-5 py-4">
          <p className="text-sm font-semibold">Community AI Monitor</p>
          <p className="text-xs text-[var(--color-muted)]">Panel de control</p>
        </div>
        <nav className="flex flex-1 flex-col gap-1 p-3">
          {mainNavItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  "rounded-[var(--radius-md)] px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-[var(--color-primary)]/10 text-[var(--color-primary)]"
                    : "text-[var(--color-foreground)] hover:bg-[var(--color-surface-hover)]",
                )
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-surface)] px-4 md:px-6">
          <BackendStatusBar />
          <ThemeToggle />
        </header>
        <main className="flex-1 overflow-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
