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

**Fase actual:** FASE 11 — Cámaras reales RTSP (completada). FASE 10 (Frontend) diferida.

## Probar el backend (ahora)

Con Docker levantado, puedes explorar la API y el simulador de cámaras:

| Endpoint | Descripción |
|----------|-------------|
| `GET /api/v1/health` | Estado de API y base de datos |
| `GET /api/v1/cameras` | Listado de cámaras (paginado) |
| `POST /api/v1/cameras` | Crear cámara |
| `GET /api/v1/cameras/{id}` | Detalle de cámara |
| `GET /api/v1/events` | Eventos (paginado, filtros) |
| `GET /api/v1/events/statistics` | Estadísticas agregadas de eventos |
| `GET /api/v1/cameras/{id}/stream/status` | Estado del stream (frames + detecciones) |
| `GET /api/v1/streams/status` | Todos los streams activos |
| `POST /api/v1/cameras/{id}/stream/start` | Iniciar stream (solo desarrollo) |
| `GET /api/v1/events` | Eventos generados por reglas (paginado) |
| `GET /api/v1/detections` | Detecciones YOLO persistidas (paginado) |
| `GET /api/v1/summaries` | Resúmenes generados por IA (paginado) |
| `POST /api/v1/summaries/generate` | Generar resumen del período con LLM |
| `WS /api/v1/ws/events` | Eventos en tiempo real (WebSocket) |
| `GET /docs` | Documentación interactiva |

```bash
docker compose up -d --build

# Ver simuladores activos (auto-inician en desarrollo)
curl http://localhost:8000/api/v1/streams/status

# Estado de una cámara
curl http://localhost:8000/api/v1/cameras/{camera_id}/stream/status
```

**Fuentes de video soportadas:**

| `stream_url` | Fuente | Genera detecciones |
|--------------|--------|--------------------|
| `rtsp://demo/...` | Sintética (sin hardware) | No (sin píxeles) |
| `file:///ruta/video.mp4` | Archivo local | Sí (con YOLO) |
| `webcam://0` | Webcam local | Sí (con YOLO) |
| `rtsp://usuario:pass@ip/...` | Cámara IP / RTSP real | Sí (FASE 11) |

**Qué aún NO está disponible:** frontend (FASE 10, diferida).

## Motor de eventos (FASE 6)

Las detecciones alimentan reglas de negocio independientes:

```
Detecciones → EventEngine → Evento en PostgreSQL
```

| Regla | Evento | Condición |
|-------|--------|-----------|
| Conteo | `crowd_detected` | Personas ≥ umbral |
| Aglomeración | `high_density` | Densidad de área ≥ umbral |
| Permanencia | `long_presence` | Objeto visible > X segundos |
| Abandonado | `abandoned_object` | Objeto sin movimiento > X segundos |

Consultar eventos generados:

```bash
curl "http://localhost:8000/api/v1/events?limit=20"
```

Umbrales configurables en `.env` (ver `.env.example`, sección FASE 6).

## Resúmenes con IA — Ollama (FASE 7)

Los eventos estructurados se resumen en lenguaje natural con un LLM local
gratuito vía [Ollama](https://ollama.com) (sin API keys ni nube):

```
Eventos (JSON) → prompt → Ollama (llama3.2:3b) → resumen en español → PostgreSQL
```

El LLM **nunca** recibe video ni imágenes, solo metadatos de eventos.

### Requisitos

```bash
# Instalar Ollama (https://ollama.com/download) y descargar el modelo
ollama pull llama3.2:3b
```

### Uso

```bash
# Generar resumen de las últimas 24 horas
curl -X POST http://localhost:8000/api/v1/summaries/generate

# Con período específico
curl -X POST http://localhost:8000/api/v1/summaries/generate \
  -H "Content-Type: application/json" \
  -d '{"period_start":"2026-07-10T00:00:00Z","period_end":"2026-07-10T23:59:59Z"}'

# Listar resúmenes generados
curl http://localhost:8000/api/v1/summaries
```

Configuración en `.env` (`LLM_MODEL`, `LLM_BASE_URL`, etc.). Si el backend corre
en Docker y Ollama en el host, usar `LLM_BASE_URL=http://host.docker.internal:11434`
(ya es el default en `docker-compose.yml`). Si Ollama no está activo, el endpoint
responde `503 LLM_PROVIDER_ERROR` sin afectar el resto del sistema.

## WebSockets — tiempo real (FASE 9)

Cuando el motor de eventos crea un evento, se emite por WebSocket:

```
Detección → Evento → PostgreSQL → WebSocket → Cliente (dashboard)
```

### Conectar

| URL | Room | Recibe |
|-----|------|--------|
| `ws://localhost:8000/api/v1/ws/events` | `dashboard:global` | Todos los eventos |
| `ws://localhost:8000/api/v1/ws/events?camera_id={uuid}` | `camera:{uuid}` | Solo esa cámara |

### Formato de mensaje

```json
{
  "event": "event.created",
  "timestamp": "2026-07-10T15:30:00Z",
  "data": {
    "id": "uuid",
    "camera_id": "uuid",
    "event_type": "crowd_detected",
    "severity": "low",
    "occurred_at": "2026-07-10T15:30:00Z",
    "metadata": { "people_count": 8 }
  }
}
```

Al conectar recibirás primero `connection.established` con las rooms activas.
Desactivar con `WEBSOCKET_ENABLED=false` en `.env`.

## Cámaras IP / RTSP (FASE 11)

En producción las cámaras se registran con URL RTSP. El backend se conecta por red
(no USB/webcam):

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/api/v1/cameras `
  -ContentType "application/json" `
  -Body '{"name":"Entrada","location":"Parque","stream_url":"rtsp://user:pass@192.168.1.50:554/stream1"}'
```

Luego inicia el procesamiento (desarrollo):

```powershell
Invoke-RestMethod -Method Post "http://localhost:8000/api/v1/cameras/{id}/stream/start"
```

**Producción (Docker):** el contenedor `backend` debe poder alcanzar la IP de la
cámara en la red. Usa `RTSP_TRANSPORT=tcp`. Las credenciales se guardan en BD pero
**nunca se devuelven** en la API (respuesta enmascarada: `rtsp://***@192.168...`).

Reconexión automática si el stream se cae (`RTSP_RECONNECT_DELAY_SECONDS`).

## Detección con YOLO (FASE 5)

El pipeline de visión convierte frames en detecciones estructuradas:

```
Frame → YOLO (detección) → IoUTracker (tracking) → PostgreSQL
```

Solo se persisten metadatos (clase, confianza, bounding box, `track_id` temporal
y timestamp). **Nunca se almacenan imágenes ni rostros** (privacidad por diseño).

La dependencia de YOLO (`ultralytics`, arrastra `torch`) es pesada, por lo que
**no** se incluye en la imagen Docker por defecto. Si no está instalada, la
detección se desactiva de forma segura (`NullDetector`) y la captura sigue
funcionando.

### Probar con tu webcam (local)

La webcam requiere acceso al hardware, así que se ejecuta **fuera de Docker**:

```bash
# 1) Levantar solo la base de datos en Docker
docker compose up -d database

# 2) Backend en local con dependencias de ML
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt -r requirements-ml.txt

# 3) Configurar entorno local (copiar .env.example a .env en la raíz)
#    DATABASE_URL=postgresql://cam_user:cam_dev_password@localhost:5432/community_ai_monitor
#    DETECTION_ENABLED=true

# 4) Migraciones + seed + servidor
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Luego apunta una cámara del seed a tu webcam (por ejemplo, con pgAdmin o SQL)
cambiando su `stream_url` a `webcam://0`, o crea la cámara con esa URL. Al
iniciar el stream, YOLO procesará los frames y verás las detecciones:

```bash
curl "http://localhost:8000/api/v1/detections?limit=20"
curl "http://localhost:8000/api/v1/streams/status"
```

> La primera ejecución descarga los pesos del modelo (`yolov8n.pt`) automáticamente.

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
