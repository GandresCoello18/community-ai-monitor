# Community AI Monitor

Plataforma inteligente de monitoreo comunitario basada en visión por computadora e inteligencia artificial.

## Objetivo general

Transformar fuentes de video provenientes de cámaras en información útil para una comunidad, barrio o zona determinada. El sistema está orientado a detectar patrones, identificar eventos relevantes y apoyar la toma de decisiones, sin realizar reconocimiento facial ni vigilancia invasiva.

## Tecnologías previstas

| Área | Tecnología |
|------|------------|
| Backend | Python, FastAPI |
| Frontend | React (SPA) |
| Base de datos | PostgreSQL |
| Contenedores | Docker, Docker Compose |
| Visión por computadora | YOLO, OpenCV |
| Modelos de lenguaje | Modelos abiertos (intercambiables) |

## Documentación

- [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) — Contexto funcional, arquitectura y decisiones técnicas del proyecto.
- [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) — Plan de implementación por fases.
- [.cursor/rules/](./.cursor/rules/) — Reglas de desarrollo para asistencia con IA.

## Estructura del monorepositorio

```
community-ai-monitor/
├── backend/          # API y procesamiento (fases futuras)
├── frontend/         # Dashboard web (fases futuras)
├── docs/             # Documentación técnica adicional
├── docker/           # Archivos Docker (fases futuras)
├── .cursor/          # Reglas y configuración de Cursor
├── PROJECT_CONTEXT.md
├── IMPLEMENTATION_PLAN.md
└── docker-compose.yml
```

## Estado del proyecto

**Fase actual:** FASE 4 — Simulador de cámara (completada). Siguiente: FASE 5 — Computer Vision.

## Probar el backend (ahora)

Con Docker levantado, puedes explorar la API y el simulador de cámaras:

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/v1/health` | Estado de API y base de datos |
| `GET /api/v1/cameras` | Listado de cámaras (paginado) |
| `GET /api/v1/cameras/{id}/stream/status` | Estado del simulador de frames |
| `GET /api/v1/streams/status` | Todos los simuladores activos |
| `POST /api/v1/cameras/{id}/stream/start` | Iniciar simulador (solo desarrollo) |
| `GET /api/v1/events` | Eventos simulados en DB |
| `GET /docs` | Documentación interactiva |

```bash
docker compose up -d --build

# Ver simuladores activos (auto-inician en desarrollo)
curl http://localhost:8000/api/v1/streams/status

# Estado de una cámara
curl http://localhost:8000/api/v1/cameras/{camera_id}/stream/status
```

**Fuentes de video soportadas en FASE 4:**

| `stream_url` | Fuente |
|--------------|--------|
| `rtsp://demo/...` | Sintética (sin hardware) |
| `file:///ruta/video.mp4` | Archivo local |
| `webcam://0` | Webcam local |

**Qué aún NO está disponible:** detección YOLO, motor de eventos real, LLM, WebSockets ni frontend.

## Infraestructura local

Requisitos: Docker Desktop.

```bash
# Levantar PostgreSQL + backend API
docker compose up -d

# Health check
curl http://localhost:8000/api/v1/health

# Documentación API (solo en desarrollo)
# http://localhost:8000/docs

# Incluir pgAdmin (opcional, http://localhost:5050)
docker compose --profile tools up -d

# Detener servicios
docker compose down
```

## Desarrollo backend (sin Docker)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Servidor (requiere migraciones previas)
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Calidad de código (Ruff ≈ ESLint + Prettier en Python)
ruff check .
ruff format .

# Tests
pytest

# Hooks de Git (una vez, desde la raíz del monorepo)
cd ..
pre-commit install
pre-commit run --all-files
```

Las variables de entorno se documentan en `.env.example`. Para personalizarlas, copiar ese archivo a `.env` (ignorado por Git).
