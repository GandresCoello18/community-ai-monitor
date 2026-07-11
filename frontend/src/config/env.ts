/**
 * Environment configuration.
 * In dev, defaults use Vite proxy (/api → backend) to avoid CORS issues.
 */
function resolveApiBaseUrl(): string {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  return import.meta.env.DEV ? "/api/v1" : "http://localhost:8000/api/v1";
}

function resolveWsBaseUrl(): string {
  if (import.meta.env.VITE_WS_BASE_URL) {
    return import.meta.env.VITE_WS_BASE_URL;
  }
  if (import.meta.env.DEV && typeof window !== "undefined") {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/api/v1/ws`;
  }
  return "ws://localhost:8000/api/v1/ws";
}

export const env = {
  apiBaseUrl: resolveApiBaseUrl(),
  wsBaseUrl: resolveWsBaseUrl(),
  isDev: import.meta.env.DEV,
} as const;
