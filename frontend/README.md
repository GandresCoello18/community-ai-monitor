# Community AI Monitor — Frontend

SPA React para el dashboard de monitoreo comunitario.

## Stack

- React 19 + TypeScript
- Vite
- Tailwind CSS v4 (CSS-first `@theme`)
- React Router
- TanStack Query
- Zustand (tema)
- Axios (HTTP)
- WebSocket nativo (backend FastAPI) + adapter Socket.io preparado

## Desarrollo local

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App: http://localhost:5173

Variables:

| Variable | Default |
|----------|---------|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` |
| `VITE_WS_BASE_URL` | `ws://localhost:8000/api/v1/ws` |

## Scripts

```bash
npm run dev      # servidor de desarrollo
npm run build    # build de producción
npm run test     # Vitest
npm run lint     # oxlint
```

## Arquitectura

Ver `src/` — capas separadas: `api/`, `services/`, `pages/`, `components/ui/`, `contexts/`, `stores/`.

La comunicación con el backend debe pasar por `src/api/client.ts`. WebSockets por `src/services/websocket/` y `WebSocketProvider`.

## Fase actual

Infraestructura base (FASE 10 — inicio). Sin autenticación ni llamadas API reales todavía.
