import { QueryClientProvider } from "@tanstack/react-query";
import { type ReactNode } from "react";
import { RouterProvider } from "react-router-dom";

import { queryClient } from "@/config/queryClient";
import { WebSocketProvider } from "@/contexts/WebSocketContext";
import { appRouter } from "@/routes/AppRouter";
import { useThemeInitializer } from "@/stores/themeStore";

function ThemeInitializer({ children }: { children: ReactNode }) {
  useThemeInitializer();
  return children;
}

export function AppProviders() {
  return (
    <QueryClientProvider client={queryClient}>
      <WebSocketProvider autoConnect={false}>
        <ThemeInitializer>
          <RouterProvider router={appRouter} />
        </ThemeInitializer>
      </WebSocketProvider>
    </QueryClientProvider>
  );
}
