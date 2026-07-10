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

**Fase actual:** FASE 2 — Backend base (completada). Siguiente: FASE 3 — Base de datos.

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

# Servidor
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
