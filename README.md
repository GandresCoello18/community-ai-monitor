# Community AI Monitor

Plataforma inteligente de monitoreo comunitario basada en **visión por computadora** e **inteligencia artificial**. Convierte streams de cámaras en eventos estructurados, estadísticas, alertas y resúmenes en lenguaje natural — **sin reconocimiento facial ni vigilancia invasiva**.

<img width="1115" height="769" alt="Captura de pantalla 2026-07-11 133303" src="https://github.com/user-attachments/assets/8f43ea9d-ab38-4b39-9d86-d3d1de323f4d" />


---

## Tabla de contenidos

- [Objetivo y principios](#objetivo-y-principios)
- [Estado del proyecto](#estado-del-proyecto)
- [Stack tecnológico](#stack-tecnológico)
- [Arquitectura](#arquitectura)
- [Estructura del monorepositorio](#estructura-del-monorepositorio)
- [Inicio rápido](#inicio-rápido)
- [Frontend (dashboard)](#frontend-dashboard)
- [Backend (API y procesamiento)](#backend-api-y-procesamiento)
- [Pipeline de video](#pipeline-de-video)
- [Motor de reglas y eventos](#motor-de-reglas-y-eventos)
- [API REST](#api-rest)
- [WebSockets (tiempo real)](#websockets-tiempo-real)
- [Vista previa en vivo (MJPEG)](#vista-previa-en-vivo-mjpeg)
- [Detección con YOLO](#detección-con-yolo)
- [Cámaras IP / RTSP / IP Webcam](#cámaras-ip--rtsp--ip-webcam)
- [Resúmenes con IA (Ollama)](#resúmenes-con-ia-ollama)
- [Notificaciones Telegram](#notificaciones-telegram)
- [Privacidad y seguridad](#privacidad-y-seguridad)
- [Buenas prácticas del proyecto](#buenas-prácticas-del-proyecto)
- [Testing y calidad de código](#testing-y-calidad-de-código)
- [Variables de entorno](#variables-de-entorno)
- [Documentación adicional](#documentación-adicional)
- [Pendiente / roadmap](#pendiente--roadmap)

---

## Objetivo y principios

Transformar fuentes de video en información útil para una comunidad, barrio o zona determinada:

- ¿Qué está ocurriendo ahora?
- ¿Qué eventos relevantes ocurrieron?
- ¿Qué patrones son normales y cuáles requieren atención?

**Principios de diseño:**

| Principio | Implementación |
|-----------|----------------|
| Privacidad por diseño | Sin reconocimiento facial; frames en memoria; eventos estructurados en BD |
| Separación de capas | Captura → CV → Reglas → Persistencia → LLM / Notificaciones |
| IA como apoyo | El LLM recibe JSON de eventos, nunca video |
| Bajo costo operativo | Modelos abiertos (YOLO, Ollama), Telegram Bot API gratuita |
| Código mantenible | Monorepo, capas delgadas, adaptadores intercambiables, tests automatizados |

---

## Estado del proyecto

| Fase | Descripción | Estado |
|------|-------------|--------|
| 0–4 | Monorepo, Docker, backend base, PostgreSQL | ✅ Completada |
| 5 | YOLO + tracking (IoU) | ✅ Completada |
| 6 | Motor de eventos / reglas comunitarias | ✅ Completada |
| 7 | Resúmenes LLM (Ollama) | ✅ Completada |
| 9 | WebSockets tiempo real | ✅ Completada |
| 10 | Frontend React (dashboard) | 🔄 En progreso (sin autenticación aún) |
| 11 | Cámaras reales RTSP / IP Webcam | ✅ Completada |
| 12 | Notificaciones Telegram (backend) | ✅ Completada |

Detalle por fase: [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md).

---

## Stack tecnológico

### Backend

| Componente | Tecnología |
|------------|------------|
| Runtime | Python 3.12+ |
| API | FastAPI, Uvicorn |
| Validación / config | Pydantic v2, pydantic-settings |
| ORM | SQLAlchemy 2.0 (async) |
| Driver BD | asyncpg (PostgreSQL), aiosqlite (tests) |
| Migraciones | Alembic |
| HTTP cliente | httpx (Ollama, Telegram) |
| Visión | OpenCV, NumPy, FFmpeg (RTSP) |
| Detección | Ultralytics YOLO (`yolov8n.pt`, opcional) |
| Tracking | IoU Tracker (IDs temporales) |
| LLM | Ollama (Llama u otros modelos locales) |
| Tests | pytest, pytest-asyncio |
| Lint / formato | Ruff |

### Frontend

| Componente | Tecnología |
|------------|------------|
| UI | React 19, TypeScript |
| Build | Vite 8 |
| Estilos | Tailwind CSS v4 (light/dark) |
| Routing | React Router 7 |
| Datos REST | TanStack Query, Axios |
| Tiempo real | WebSocket nativo (FastAPI) |
| Estado global | Zustand (tema) |
| Tests | Vitest, React Testing Library |
| Lint | Oxlint |

### Infraestructura

| Componente | Tecnología |
|------------|------------|
| Base de datos | PostgreSQL 16 |
| Contenedores | Docker, Docker Compose |
| Admin BD (opcional) | pgAdmin (`--profile tools`) |
| LLM local | Ollama (host, fuera del contenedor backend) |
| Alertas | Telegram Bot API |

> **Redis** está planificado para colas futuras; aún no se usa.

---

## Arquitectura

```mermaid
flowchart TB
    subgraph Fuentes["Fuentes de video"]
        CAM[RTSP / IP Webcam / Webcam / Archivo / Sintética]
    end

    subgraph Backend["Backend FastAPI"]
        W[Camera Worker async]
        CV[YOLO + IoU Tracker]
        RE[Rule Engine]
        EIS[Event Ingestion Service]
        WS[WebSocket Manager]
        NS[Notification Service]
        SS[Summary Service]
    end

    subgraph Persistencia["PostgreSQL"]
        DB[(Cámaras · Detecciones · Eventos · Métricas · Resúmenes)]
    end

    subgraph Clientes["Clientes"]
        FE[React Dashboard]
        TG[Grupo Telegram]
    end

    OLL[Ollama local]

    CAM --> W --> CV --> RE --> EIS
    EIS --> DB
    EIS --> WS --> FE
    EIS --> NS --> TG
    FE -->|REST /api/v1| Backend
    SS --> OLL
    SS --> DB
    FE -->|POST /summaries| SS
```

**Flujo obligatorio de IA:**

<img width="1376" height="768" alt="Diagrama-de-flujo-de-arquitectura-para-Community-AI-Monitor" src="https://github.com/user-attachments/assets/65874f95-8d52-40a1-a4d0-1985c53b54c0" />


```
Video → Computer Vision → Eventos estructurados → LLM / Notificaciones
```

El LLM y Telegram **nunca** procesan streams de video directamente.

---

## Estructura del monorepositorio

```
community-ai-monitor/
├── backend/
│   ├── app/
│   │   ├── api/              # Routers HTTP (capa delgada)
│   │   ├── capture/          # Fuentes de video (RTSP, MJPEG, webcam…)
│   │   ├── core/             # Config, logging, excepciones
│   │   ├── database/         # Sesión async, seed
│   │   ├── detection/        # YOLO, pipeline, factory
│   │   ├── events/           # Motor de eventos legacy
│   │   ├── llm/              # Ollama provider, prompts
│   │   ├── models/           # Entidades SQLAlchemy
│   │   ├── notifications/    # Telegram, filtros, servicio
│   │   ├── repositories/     # Acceso a PostgreSQL
│   │   ├── rules/            # Reglas comunitarias modulares
│   │   ├── schemas/          # DTOs Pydantic (contratos API)
│   │   ├── services/         # Lógica de negocio
│   │   ├── tracking/         # IoU tracker
│   │   ├── websocket/        # Manager + router WS
│   │   └── workers/          # Camera workers (asyncio)
│   ├── alembic/              # Migraciones
│   ├── docs/                 # Docs técnicas (Telegram, etc.)
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── requirements-ml.txt   # YOLO/torch (opcional, pesado)
├── frontend/
│   └── src/
│       ├── api/              # Cliente Axios
│       ├── components/       # UI reutilizable
│       ├── hooks/            # React Query, WebSocket
│       ├── pages/            # Dashboard, cámaras, eventos…
│       ├── services/         # WebSocket nativo
│       └── styles/           # Tema CSS
├── .cursor/rules/            # Reglas de desarrollo (IA + calidad)
├── docker-compose.yml
├── PROJECT_CONTEXT.md
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Inicio rápido

### Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Node.js 20+ y Yarn (frontend)
- Python 3.12+ (desarrollo backend local)

### Con Docker (recomendado para empezar)

```bash
# Levantar PostgreSQL + backend
docker compose up -d --build

# Health check
curl http://localhost:8000/api/v1/health

# Documentación interactiva (solo desarrollo)
# http://localhost:8000/docs

# pgAdmin opcional → http://localhost:5050
docker compose --profile tools up -d

# Detener
docker compose down
```

### Full stack local (backend + frontend)

```bash
# Terminal 1 — base de datos
docker compose up -d database

# Terminal 2 — backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env   # ajustar DATABASE_URL si hace falta
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Terminal 3 — frontend
cd frontend
yarn install
yarn dev
# → http://localhost:5173
```

El frontend usa proxy de Vite: `/api` → `http://localhost:8000`.

---

## Frontend (dashboard)

SPA React con panel de control en español.

| Ruta | Pantalla |
|------|----------|
| `/dashboard` | Panel: estadísticas, eventos recientes |
| `/cameras` | Lista de cámaras, estado de stream, vista previa MJPEG |
| `/events` | Historial paginado, detalle, resúmenes IA |
| `/statistics` | Gráficos y filtros por fecha (tipo, severidad, cámara, actividad diaria) |
| `/settings` | Configuración (placeholder) |
| `/login` | Login (placeholder, sin auth real aún) |

**Características:**

- Indicadores de conexión API y WebSocket en el header
- Modo claro / oscuro (Zustand + CSS variables)
- Actualización en tiempo real de eventos vía WebSocket
- Etiquetas en español para tipos de evento y severidad

```bash
cd frontend
yarn dev          # desarrollo
yarn build        # producción
yarn test         # Vitest
yarn lint         # Oxlint
```

Variables: `frontend/.env.example` (opcional; el proxy de Vite cubre desarrollo local).

---

## Backend (API y procesamiento)

Patrón de capas:

```
Router (api/) → Service (services/) → Repository (repositories/) → PostgreSQL
```

```bash
cd backend
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Calidad
ruff check .
ruff format .
pytest

# Hooks Git (desde la raíz del monorepo)
pre-commit install
pre-commit run --all-files
```

Variables: `backend/.env.example` → copiar a `backend/.env`.

---

## Pipeline de video

Los workers de cámara corren **fuera del ciclo de requests HTTP** (asyncio tasks):

```
Fuente de video
    ↓
Camera Worker (CameraSimulatorWorker)
    ↓
Frame en memoria (no persistido)
    ↓
Detection Pipeline (YOLO + IoU Tracker) — asyncio.to_thread
    ↓
Tracked Detections
    ↓
Rule Engine (reglas comunitarias)
    ↓
Event Ingestion Service
    ├→ PostgreSQL (eventos + métricas)
    ├→ WebSocket (event.created)
    └→ Notification Service → Telegram (si aplica)
```

La inferencia YOLO **no bloquea** el event loop de FastAPI.

---

## Motor de reglas y eventos

Las detecciones alimentan reglas modulares en `backend/app/rules/`. Una detección **no es** un evento; el evento surge cuando una regla de negocio lo determina.

| Tipo de evento | Descripción |
|----------------|-------------|
| `crowd_detected` | Aglomeración de personas |
| `high_density` | Alta densidad en zona |
| `long_presence` / `person_long_stay` | Permanencia prolongada |
| `person_repeated_activity` | Actividad repetida en zona |
| `person_hidden_activity` | Actividad poco visible |
| `vehicle_long_parking` | Vehículo estacionado mucho tiempo |
| `double_parking` | Posible estacionamiento doble |
| `wrong_direction` | Circulación en sentido incorrecto |
| `abandoned_object` | Posible objeto abandonado |
| `animal_detected` | Animal detectado |
| `park_occupancy_changed` | Cambio de ocupación en parque |
| `park_empty` | Parque vacío prolongado |
| `trash_detected` / `obstruction_detected` | Mantenimiento (opcionales) |

Severidades: `low`, `medium`, `high`, `critical`.

Umbrales y reglas activas: variables `RULE_*` y `EVENT_*` en `backend/.env`.

---

## API REST

Base: `/api/v1`. Respuestas paginadas: `{ data, meta }`. Errores: `{ error: { code, message } }`.

### Salud y sistema

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/health` | Estado API + base de datos |

### Cámaras

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/cameras` | Listado paginado |
| `POST` | `/cameras` | Crear cámara |
| `GET` | `/cameras/{id}` | Detalle |
| `PATCH` | `/cameras/{id}` | Actualización parcial (detiene stream si cambia `stream_url`) |
| `DELETE` | `/cameras/{id}` | Soft delete |
| `GET` | `/cameras/{id}/preview` | Último frame JPEG (memoria) |
| `GET` | `/cameras/{id}/preview/stream` | Stream MJPEG en vivo |
| `GET` | `/cameras/{id}/stream/status` | Estado del worker |
| `POST` | `/cameras/{id}/stream/start` | Iniciar stream (solo desarrollo) |
| `POST` | `/cameras/{id}/stream/stop` | Detener stream (solo desarrollo) |

### Eventos y estadísticas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/events` | Listado paginado (`camera_id`, `event_type`, `start_date`, `end_date`) |
| `GET` | `/events/statistics` | Agregados (`by_type`, `by_severity`, `by_camera`, `by_day`) |

### Detecciones, streams, resúmenes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/detections` | Detecciones YOLO persistidas |
| `GET` | `/streams/status` | Estado de todos los workers activos |
| `GET` | `/summaries` | Resúmenes IA generados |
| `POST` | `/summaries/generate` | Generar resumen de período con Ollama |

Documentación interactiva en desarrollo: `http://localhost:8000/docs`.

---

## WebSockets (tiempo real)

Endpoint: `WS /api/v1/ws/events`

| Conexión | Room | Recibe |
|----------|------|--------|
| Sin parámetros | `dashboard:global` | Todos los eventos |
| `?camera_id={uuid}` | `camera:{uuid}` | Solo esa cámara |

Formato de mensaje:

```json
{
  "event": "event.created",
  "timestamp": "2026-07-10T15:30:00Z",
  "data": {
    "id": "uuid",
    "camera_id": "uuid",
    "event_type": "crowd_detected",
    "severity": "medium",
    "occurred_at": "2026-07-10T15:30:00Z",
    "metadata": { "people_count": 8 }
  }
}
```

Al conectar: mensaje `connection.established`. Desactivar: `WEBSOCKET_ENABLED=false`.

---

## Vista previa en vivo (MJPEG)

Frames de preview se guardan **solo en memoria** (`PreviewFrameStore`), nunca en PostgreSQL.

- `GET /cameras/{id}/preview` — snapshot JPEG
- `GET /cameras/{id}/preview/stream` — multipart MJPEG para `<img>` o dashboard

Configuración: `CAMERA_PREVIEW_*` en `.env`. Cajas de detección opcionales: `CAMERA_PREVIEW_SHOW_DETECTIONS=true`.

---

## Detección con YOLO

```
Frame → YOLO → IoU Tracker → Detecciones estructuradas → PostgreSQL
```

Solo metadatos: clase, confianza, bounding box, `track_id` temporal, timestamp. **Sin imágenes ni rostros.**

YOLO (`ultralytics` + `torch`) **no** está en la imagen Docker por defecto. Sin instalarlo, `NullDetector` desactiva la detección de forma segura y la captura sigue funcionando.

### Instalación local con detección real

```bash
docker compose up -d database

cd backend
pip install -r requirements-dev.txt -r requirements-ml.txt
cp .env.example .env
# DETECTION_ENABLED=true
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Registrar cámara con `webcam://0`, `file:///ruta/video.mp4` o RTSP real. La primera ejecución descarga `yolov8n.pt`.

```bash
curl "http://localhost:8000/api/v1/detections?limit=20"
curl "http://localhost:8000/api/v1/streams/status"
```

---

## Cámaras IP / RTSP / IP Webcam

| `stream_url` | Fuente | Detecciones |
|--------------|--------|-------------|
| `rtsp://demo/...` | Sintética (dev, sin píxeles) | No |
| `rtsp://user:pass@ip:554/...` | Cámara IP RTSP | Sí (con YOLO + FFmpeg) |
| `rtsp://ip:8080/h264_*.sdp` | IP Webcam (auto → HTTP MJPEG si `IP_WEBCAM_PREFER_HTTP=true`) | Sí |
| `webcam://0` | Webcam local | Sí |
| `file:///ruta/video.mp4` | Archivo de video | Sí |

```powershell
# Crear cámara RTSP
Invoke-RestMethod -Method Post http://localhost:8000/api/v1/cameras `
  -ContentType "application/json" `
  -Body '{"name":"Entrada","location":"Parque","stream_url":"rtsp://user:pass@192.168.1.50:554/stream1"}'

# Iniciar procesamiento (desarrollo)
Invoke-RestMethod -Method Post "http://localhost:8000/api/v1/cameras/{id}/stream/start"
```

**Producción (Docker):** el contenedor `backend` debe alcanzar la IP de la cámara en LAN. Usar `RTSP_TRANSPORT=tcp`. Credenciales en BD pero **enmascaradas** en respuestas API (`rtsp://***@192.168...`). Reconexión automática: `RTSP_RECONNECT_DELAY_SECONDS`.

---

## Resúmenes con IA (Ollama)

```
Eventos (JSON) → prompt → Ollama → resumen en español → PostgreSQL
```

El LLM **nunca** recibe video ni imágenes.

### Requisitos

```bash
# https://ollama.com/download
ollama pull llama3.2:3b
```

### Uso

```bash
# Resumen últimas 24 h
curl -X POST http://localhost:8000/api/v1/summaries/generate

# Período específico
curl -X POST http://localhost:8000/api/v1/summaries/generate \
  -H "Content-Type: application/json" \
  -d '{"period_start":"2026-07-10T00:00:00Z","period_end":"2026-07-10T23:59:59Z"}'

curl http://localhost:8000/api/v1/summaries
```

Backend en Docker + Ollama en host: `LLM_BASE_URL=http://host.docker.internal:11434` (default en `docker-compose.yml`). Si Ollama no está activo: `503 LLM_PROVIDER_ERROR` sin afectar el resto.

Config: `LLM_MODEL`, `LLM_BASE_URL`, `LLM_TIMEOUT_SECONDS`, `SUMMARY_MAX_EVENTS`.

---

## Notificaciones Telegram

Canal principal para barrios **sin depender del dashboard**. Solo backend.

```
Evento persistido → NotificationService → Telegram Bot API → Grupo del barrio
```

| Severidad | Envío |
|-----------|-------|
| ≥ `NOTIFY_MIN_SEVERITY` (default: `medium`) | Mensaje de texto |
| ≥ `NOTIFY_PHOTO_MIN_SEVERITY` (default: `high`) | Texto + foto JPEG del frame (no persistida) |

Filtros: tipos permitidos, cooldown anti-spam, horario silencioso (UTC).

```env
NOTIFICATIONS_ENABLED=true
TELEGRAM_BOT_TOKEN=123456789:AA...
TELEGRAM_CHAT_ID=-1001234567890
NOTIFY_MIN_SEVERITY=medium
NOTIFY_PHOTO_MIN_SEVERITY=high
NOTIFY_COOLDOWN_SECONDS=300
```

Guía completa: [backend/docs/telegram-notifications.md](./backend/docs/telegram-notifications.md).

---

## Privacidad y seguridad

| Regla | Detalle |
|-------|---------|
| Sin reconocimiento facial | No implementado ni planificado |
| Frames en memoria | Preview y alertas JPEG no se guardan en BD por defecto |
| IDs de tracking temporales | Desaparecen tras el contexto del evento |
| Mensajes prudentes | "Posible aglomeración", no afirmaciones absolutas |
| Secretos en `.env` | Tokens Telegram, credenciales RTSP — nunca en el repo |
| URLs enmascaradas | `stream_url` oculta credenciales en respuestas API |
| Logs seguros | Sin tokens ni datos personales |
| CORS | Solo localhost en desarrollo |

Más detalle: [.cursor/rules/security-privacy.mdc](./.cursor/rules/security-privacy.mdc).

---

## Buenas prácticas del proyecto

1. **Capas delgadas:** endpoints sin lógica de negocio ni SQL directo.
2. **Repositorios:** todo acceso a PostgreSQL pasa por `repositories/`.
3. **Adaptadores:** YOLO, Ollama, Telegram intercambiables vía factory.
4. **Workers async:** captura e inferencia fuera del request HTTP.
5. **Contratos versionados:** `/api/v1`, DTOs Pydantic, tipos TypeScript.
6. **WebSocket con rooms:** no broadcast ciego a todos los clientes.
7. **Config externalizada:** `Settings` + variables de entorno.
8. **Tests con mocks:** sin modelos reales ni bot Telegram en CI.
9. **Migraciones Alembic:** cambios de esquema versionados.
10. **Reglas Cursor:** `.cursor/rules/` guían desarrollo asistido por IA.

Reglas completas: [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md), [.cursor/rules/](./.cursor/rules/).

---

## Testing y calidad de código

### Backend

```bash
cd backend
pytest                          # suite completa
pytest tests/notifications/     # Telegram, filtros
pytest tests/events/            # motor de eventos
ruff check . && ruff format .   # lint + formato
```

### Frontend

```bash
cd frontend
yarn test    # Vitest
yarn lint    # Oxlint
```

### Pre-commit (monorepo)

```bash
pre-commit install
pre-commit run --all-files
```

Política de testing: [.cursor/rules/testing-quality.mdc](./.cursor/rules/testing-quality.mdc).

---

## Variables de entorno

| Archivo | Alcance |
|---------|---------|
| [backend/.env.example](./backend/.env.example) | API, CV, reglas, RTSP, LLM, Telegram, WebSocket |
| [frontend/.env.example](./frontend/.env.example) | URL API/WS (opcional en dev) |
| [.env.example](./.env.example) | Docker Compose (PostgreSQL, puertos) |

Copiar a `.env` local (ignorados por Git). **Nunca commitear secretos.**

Secciones principales del backend:

- **App:** `APP_ENV`, `DEBUG`, `LOG_LEVEL`, `DATABASE_URL`
- **Cámaras / preview:** `CAMERA_*`, `CAMERA_PREVIEW_*`
- **Detección:** `DETECTION_*`
- **Reglas:** `RULE_*`, `EVENT_*`, `RULE_SCENE_TYPE`
- **LLM:** `LLM_*`
- **WebSocket:** `WEBSOCKET_ENABLED`
- **RTSP:** `RTSP_*`, `IP_WEBCAM_PREFER_HTTP`
- **Telegram:** `NOTIFICATIONS_*`, `TELEGRAM_*`, `NOTIFY_*`

---

## Documentación adicional

| Documento | Contenido |
|-----------|-----------|
| [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) | Contexto funcional, arquitectura, decisiones |
| [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) | Roadmap por fases |
| [backend/docs/telegram-notifications.md](./backend/docs/telegram-notifications.md) | Setup bot Telegram |
| [.cursor/rules/](./.cursor/rules/) | Backend, frontend, BD, privacidad, testing |

---

## Pendiente / roadmap

- [ ] Autenticación y autorización (roles admin / vecino)
- [ ] Despliegue frontend en Vercel (demo) + backend Docker en campo
- [ ] Redis / cola de workers para escala
- [ ] Tabla `Community` / `NotificationChannel` (un Telegram por barrio sin redeploy)
- [ ] WhatsApp Business (evaluación futura)

---

## Licencia y uso

Proyecto de portafolio y demostración técnica. Revisar licencias de YOLO (Ultralytics), Ollama y dependencias antes de uso comercial.

## 👨‍💻 Autores ✒️

- **Andrés Coello Goyes** - _SOFTWARE ENGINEER_ - [Andres Coello](https://linktr.ee/gandrescoello)

#### 🔗 Links

[![portfolio](https://img.shields.io/badge/my_portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://andrescoellog.com/)
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/andrescoellogoyes/)
[![twitter](https://img.shields.io/badge/twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://x.com/acoellogoyes)

## 🙏 Expresiones de Gratitud 🎁

- Pásate por mi perfil para ver algún otro proyecto 📢
- Desarrollemos alguna app juntos, puedes escribirme en mis redes
- Muchas gracias por pasarte por este proyecto 🤓

---

⌨️ con ❤️ por [Andres Coello Goyes](https://linktr.ee/gandrescoello) 😊

<img width="400" height="400" alt="1764558900283" src="https://github.com/user-attachments/assets/cde88968-7856-49ec-bdb1-53a82bf9caa3" />
