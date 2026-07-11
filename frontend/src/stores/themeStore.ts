import { useEffect } from "react";
import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { ThemeMode } from "@/types";

interface ThemeState {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
  toggleMode: () => void;
}

function resolveTheme(mode: ThemeMode): "light" | "dark" {
  if (mode === "system") {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }
  return mode;
}

function applyTheme(mode: ThemeMode): void {
  const resolved = resolveTheme(mode);
  document.documentElement.classList.toggle("dark", resolved === "dark");
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: "system",
      setMode: (mode) => {
        applyTheme(mode);
        set({ mode });
      },
      toggleMode: () => {
        const current = resolveTheme(get().mode);
        const next: ThemeMode = current === "dark" ? "light" : "dark";
        applyTheme(next);
        set({ mode: next });
      },
    }),
    {
      name: "cam-theme",
      onRehydrateStorage: () => (state) => {
        if (state) {
          applyTheme(state.mode);
        }
      },
    },
  ),
);

/** Applies persisted theme on app mount. */
export function useThemeInitializer(): void {
  const mode = useThemeStore((state) => state.mode);

  useEffect(() => {
    applyTheme(mode);

    if (mode !== "system") {
      return;
    }

    const media = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => applyTheme("system");
    media.addEventListener("change", handler);
    return () => media.removeEventListener("change", handler);
  }, [mode]);
}
