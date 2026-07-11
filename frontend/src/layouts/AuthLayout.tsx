import { Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-background)] px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-semibold">Community AI Monitor</h1>
          <p className="mt-2 text-sm text-[var(--color-muted)]">
            Acceso al sistema de monitoreo comunitario
          </p>
        </div>
        <Outlet />
      </div>
    </div>
  );
}
