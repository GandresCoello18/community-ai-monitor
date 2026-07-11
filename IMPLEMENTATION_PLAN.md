
```
IMPLEMENTATION_PLAN.md
```

Este será el "roadmap técnico" que Cursor debe seguir.

---

# Fase 0 — Preparación del monorepo

Objetivo: tener la estructura base.

Crear:

```
community-ai-monitor/

├── backend/
├── frontend/
├── docker/
├── docs/
├── .cursor/
├── docker-compose.yml
├── README.md
├── PROJECT_CONTEXT.md
└── IMPLEMENTATION_PLAN.md
```

Tareas:

- [x] Inicializar Git.
- [x] Configurar reglas Cursor.
- [x] Crear documentación base.
- [x] Definir variables de entorno (`.env.example`).

**Estado: COMPLETADA.**

---

# Fase 1 — Infraestructura local

Primero infraestructura.

¿Por qué?

Porque todo lo demás dependerá de servicios externos.

Crear Docker:

Servicios iniciales:

```yaml
services:

  backend:
    python
    fastapi

  database:
    postgres

  pgadmin:
    opcional

  redis:
    opcional inicialmente
```

Objetivo:

Poder ejecutar:

```bash
docker compose up
```

y tener:

* API funcionando.
* PostgreSQL funcionando.
* Migraciones funcionando.

Progreso:

- [x] `docker-compose.yml` con servicio `database` (PostgreSQL 16) y healthcheck.
- [x] `pgadmin` disponible como servicio opcional (profile `tools`).
- [x] Variables de entorno definidas en `.env.example`.
- [x] PostgreSQL verificado funcionando (`docker compose up -d`).
- [x] API funcionando — `GET /api/v1/health` responde correctamente.
- [x] Migraciones funcionando — Alembic en Docker y `alembic upgrade head`.

Nota: los criterios "API funcionando" y "Migraciones funcionando" no pueden
cumplirse en esta fase sin adelantar trabajo de las Fases 2 y 3. La
infraestructura queda lista para incorporarlos cuando corresponda.

**Estado: COMPLETADA (parte de infraestructura).**

---

# Fase 2 — Backend base

Aquí todavía NO entra IA.

Construir el esqueleto profesional:

```
backend/app

├── api
├── core
├── database
├── models
├── schemas
├── repositories
├── services
└── main.py
```

Implementar:

* FastAPI.
* Configuración.
* Variables de entorno.
* Logging.
* Manejo global de errores.
* Health check.

Ejemplo:

```
GET /api/v1/health

{
  "data": {
    "status": "ok"
  }
}
```

Progreso:

- [x] Estructura `backend/app` con capas separadas.
- [x] FastAPI con factory `create_app()` y lifespan.
- [x] Configuración con Pydantic Settings (`app/core/config.py`).
- [x] Logging estructurado (`app/core/logging.py`).
- [x] Excepciones personalizadas y handlers globales.
- [x] Health check en `GET /api/v1/health` vía servicio.
- [x] Dockerfile y servicio `backend` en Docker Compose.
- [x] Tests con pytest + httpx.

**Estado: COMPLETADA.**

---

# Fase 3 — Base de datos y modelos iniciales

Crear:

* PostgreSQL.
* SQLAlchemy.
* Alembic.

Primeras tablas:

```
Camera

Event

Detection

Configuration
```

Todavía con datos simulados.

Progreso:

- [x] SQLAlchemy 2.0 async con `asyncpg`.
- [x] Modelos con UUID, timestamps, JSONB y soft delete en cámaras.
- [x] Alembic con migración inicial (`001_initial_schema`).
- [x] Repositorios para acceso a datos.
- [x] Seed de datos simulados (cámaras, eventos, detecciones, configuración).
- [x] Health check con estado de base de datos.
- [x] Endpoints read-only: `GET /api/v1/cameras`, `GET /api/v1/events`.
- [x] Migraciones automáticas en Docker (`entrypoint.sh`).
- [x] Tests con SQLite en memoria + datos simulados.

**Estado: COMPLETADA.**

---

# Fase 4 — Simulador de cámara

Antes de conectar cámaras reales.

Crear un módulo que simule:

```
Video source

↓

Frames
```

Puede usar:

* archivo MP4,
* webcam local.

Objetivo:

Probar el pipeline sin depender de hardware.

Progreso:

- [x] Módulo `capture/` con adaptadores intercambiables (`FrameSource`).
- [x] Fuentes: `synthetic`, `file` (MP4), `webcam`.
- [x] Worker asyncio en background (`CameraSimulatorWorker`).
- [x] `CameraStreamService` para orquestar simuladores por cámara.
- [x] Auto-inicio en desarrollo para cámaras activas.
- [x] API de estado: `GET /cameras/{id}/stream/status`, `GET /streams/status`.
- [x] Control manual en desarrollo: `POST .../stream/start|stop`.
- [x] OpenCV headless integrado (sin almacenar frames en DB).

**Estado: COMPLETADA.**

---

# Fase 5 — Computer Vision Pipeline

Ahora sí entra IA.

Implementar:

## Captura

OpenCV.

↓

## Detección

YOLO.

↓

## Tracking

ByteTrack.

↓

## Persistencia

Guardar detecciones.

Ejemplo:

```
10:30:01

Camera 01

Person

Confidence 0.91
```

## Checklist

- [x] Módulo `detection/` con adaptadores intercambiables (`ObjectDetector`).
- [x] `YOLODetector` (Ultralytics) con carga perezosa de la dependencia.
- [x] `NullDetector` para degradar de forma segura sin YOLO instalado.
- [x] Módulo `tracking/` con `ObjectTracker` e `IoUTracker` (IDs temporales).
- [x] `DetectionPipeline`: detección → tracking (sin acceso a DB ni reglas).
- [x] `Frame.image` en memoria para el pipeline (nunca se persiste).
- [x] Worker ejecuta inferencia fuera del event loop (`asyncio.to_thread`),
      con intervalo configurable (`DETECTION_INTERVAL_SECONDS`).
- [x] Persistencia de detecciones vía `DetectionRepository` (track_id en metadata).
- [x] API `GET /api/v1/detections` (paginada, filtro `camera_id`).
- [x] Estado de stream incluye `detection_enabled`, `detections_processed`.
- [x] Dependencias ML separadas (`requirements-ml.txt`); Docker liviano.
- [x] Tests con mocks (tracker, pipeline, worker, endpoint). Sin modelo real.

**Nota técnica:** el tracker inicial es `IoUTracker` (simple, sin dependencias
pesadas y suficiente para baja tasa de FPS). La interfaz `ObjectTracker` permite
cambiar a ByteTrack/BoT-SORT más adelante sin tocar el pipeline.

**Estado: COMPLETADA.**

---

# Fase 6 — Motor de eventos

Aquí está el valor del producto.

Crear reglas:

Primero:

### Conteo

```
Person count > X
```

---

### Permanencia

```
Object duration > X minutos
```

---

### Aglomeración

```
People density > threshold
```

---

### Objeto abandonado

```
Object exists
+
No movement
+
Time exceeded
```

## Checklist

- [x] Módulo `events/` con `EventEngine` y contrato `EventRule`.
- [x] Regla `crowd_detection` (person count > X, con cooldown).
- [x] Regla `high_density` (aglomeración por área ocupada en frame).
- [x] Regla `long_presence` (permanencia > X segundos por track).
- [x] Regla `abandoned_object` (objeto estático > X segundos).
- [x] Reglas independientes en `events/rules/` (sin lógica en endpoints).
- [x] `EventIngestionService`: evalúa reglas y persiste eventos.
- [x] Integración post-detección en `CameraStreamService` (Detection → Rules → Event).
- [x] Configuración por variables de entorno (umbrales, cooldown, clases).
- [x] API existente `GET /api/v1/events` consume eventos generados.
- [x] Tests unitarios por regla + integración de persistencia.

**Estado: COMPLETADA.**

---

# Fase 6b — Motor de reglas comunitarias (Rule Engine)

Capa de interpretación sobre detecciones + tracking. No modifica YOLO ni modelos CV.

Flujo:

```
Detection → Tracking → Rule Engine → Events / Metrics → Database
```

## Checklist

- [x] Módulo `rules/` (`engine`, `base_rule`, `config`, `factory`, `utils`).
- [x] Reglas de personas: `person_long_stay`, `person_repeated_activity`, `person_hidden_activity`, `crowd_detected`.
- [x] Reglas de vehículos: `vehicle_long_parking`, `double_parking`, `wrong_direction` (opt-in).
- [x] Reglas de parque: `park_occupancy_changed`, `park_empty`, métricas por zona interna.
- [x] Reglas de objetos: `abandoned_object`.
- [x] Reglas de animales: `animal_detected`.
- [x] Tráfico / densidad: `high_density`, conteos y flujo vehicular (métricas).
- [x] Placeholders: `trash_detected`, `obstruction_detected`, LPR (`VehicleMetadata`, `PlateRecognitionProvider`).
- [x] Configuración centralizada (`RulesConfig` + variables `RULE_*`).
- [x] `EventIngestionService` integrado con `RuleEngine` y persistencia de métricas.
- [x] Modelo `CommunityMetric` + migración Alembic `003_community_metrics`.
- [x] Compatibilidad con módulo `events/` (alias legacy `long_presence` opcional).
- [x] Tests unitarios en `tests/rules/`.

**Estado: COMPLETADA.**

---

Después de tener eventos.

Nunca antes.

Implementar:

```
Events

↓

LLM

↓

Summary
```

Ejemplo:

Entrada:

```json
{
"events":10,
"crowd":true
}
```

Salida:

```
Durante la tarde hubo mayor concentración de personas...
```

## Checklist

- [x] Módulo `llm/` con proveedor intercambiable (`LLMProvider`).
- [x] `OllamaProvider` (modelos abiertos locales, sin API key).
- [x] Prompts en `llm/prompts.py` (resumen en español, sin datos personales).
- [x] Contexto estructurado (`SummaryContext`): solo eventos agregados, nunca frames.
- [x] Modelo `DailySummary` + migración `002_daily_summaries`.
- [x] `SummaryRepository` + `SummaryService` (eventos → prompt → LLM → DB).
- [x] API: `GET /api/v1/summaries`, `POST /api/v1/summaries/generate`.
- [x] Configuración por entorno (`LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL`).
- [x] Tests con provider mock (sin depender de Ollama real).
- [x] Verificado con Ollama real (`llama3.2:3b` en CPU).

**Nota técnica:** proveedor por defecto Ollama en `http://localhost:11434`.
Desde Docker se alcanza con `http://host.docker.internal:11434`. Si Ollama no
está disponible, el endpoint responde `503 LLM_PROVIDER_ERROR` sin afectar el
resto del sistema.

**Estado: COMPLETADA.**

---

# Fase 8 — API pública

Crear endpoints:

Cámaras:

```
GET /cameras
POST /cameras
```

Eventos:

```
GET /events
GET /events/statistics
```

Resumen:

```
GET /summaries
```

## Checklist

- [x] `GET /api/v1/cameras` — listado paginado (ya existía).
- [x] `POST /api/v1/cameras` — crear cámara (`CameraCreate`, status 201).
- [x] `GET /api/v1/events` — listado paginado con filtros (`camera_id`, `event_type`, fechas).
- [x] `GET /api/v1/events/statistics` — agregados por tipo, severidad y cámara.
- [x] `GET /api/v1/summaries` — listado de resúmenes IA (FASE 7).
- [x] DTOs Pydantic separados (`CameraCreate`, `EventStatisticsResponse`).
- [x] Lógica en servicios/repositorios (endpoints delgados).
- [x] Tests de API para creación de cámaras y estadísticas.

**Estado: COMPLETADA.**

---

# Fase 9 — Tiempo real

Agregar:

WebSockets.

Flujo:

```
Detection

↓

Event

↓

WebSocket

↓

Frontend
```

## Checklist

- [x] Módulo `websocket/` con `WebSocketManager` y contrato de mensajes.
- [x] Envelope estándar: `{ event, timestamp, data }` (`entity.action`).
- [x] Endpoint `WS /api/v1/ws/events` con rooms por cámara o dashboard.
- [x] Broadcast `event.created` al persistir eventos (FASE 6 → FASE 9).
- [x] Rooms: `dashboard:global` y `camera:{uuid}` (sin enviar todo a todos).
- [x] Mensaje `connection.established` al conectar.
- [x] Config `WEBSOCKET_ENABLED` para desactivar broadcast.
- [x] Tests de manager, schemas y endpoint WebSocket.

**Estado: COMPLETADA.**

---

# Fase 10 — Frontend

React dashboard (SPA).

## Fase 10a — Infraestructura base (completada)

- [x] Vite + React 19 + TypeScript estricto
- [x] Tailwind CSS v4 (`@theme`, light/dark)
- [x] React Router (login, dashboard, cámaras, eventos, estadísticas, config, 404)
- [x] Layouts: Auth, Dashboard, Main
- [x] TanStack Query + Axios (`api/client.ts`, errores centralizados)
- [x] WebSocket: servicio nativo + provider + hook (alineado con FastAPI)
- [x] Socket.io adapter preparado (no conectado; backend usa WS nativo)
- [x] Zustand (tema global)
- [x] Componentes UI base (Button, Card, Input, Modal, Table, Badge, Spinner, EmptyState)
- [x] Vitest + prueba de ejemplo

## Fase 10b — Pantallas de negocio (en progreso)

- [x] Dashboard con datos reales (estadísticas + eventos recientes).
- [x] Lista de cámaras con estado de stream.
- [x] Eventos con paginación + actualización vía WebSocket.
- [x] Estadísticas agregadas (por tipo, severidad, cámara).
- [x] Indicador de conexión API / WebSocket en header.
- [x] Vista previa en vivo por cámara (MJPEG, solo memoria).
- [ ] Gráficos.
- [ ] Autenticación.

**Estado Fase 10a: COMPLETADA. Fase 10b: EN PROGRESO.**

---

# Fase 11 — Cámaras reales

Finalmente:

Integrar:

* cámaras IP.
* RTSP.
* Streams reales.

Porque si empiezas aquí, los problemas de red/hardware mezclan problemas de software.

## Checklist

- [x] `RTSPFrameSource` con OpenCV + FFmpeg (`rtsp://`, `rtsps://`).
- [x] Reconexión automática tras fallos de lectura consecutivos.
- [x] Transporte configurable (`RTSP_TRANSPORT=tcp` recomendado en prod).
- [x] Buffer mínimo (`RTSP_BUFFER_SIZE=1`) para baja latencia.
- [x] Credenciales enmascaradas en logs y respuestas API (`mask_stream_url`).
- [x] `rtsp://demo/...` sigue usando fuente sintética (desarrollo).
- [x] Factory actualizado; ya no hay fallback sintético para RTSP real.
- [x] Docker: `ffmpeg` en imagen backend para decodificar RTSP.
- [x] Tests con mocks (factory, reconexión, enmascaramiento API).

**Estado: COMPLETADA.**

---

# Fase 12 — Notificaciones Telegram (backend)

Objetivo: alertar a cada barrio/comunidad **sin depender del frontend**.
El dashboard web (FASE 10) pasa a ser **opcional**; el canal principal de
información para vecinos es un **grupo de Telegram** por barrio.

## Contexto de producto

* No todos los barrios necesitan dashboard web.
* WhatsApp es el canal social habitual, pero la **Telegram Bot API es gratuita**,
  permite enviar fotos a grupos y es más simple de integrar que WhatsApp Business.
* El backend sigue procesando cámaras, reglas y eventos con normalidad.
* Solo se **notifica lo importante**, no cada detección ni cada evento de baja
  severidad.

## Alcance

**Solo backend.** Sin cambios obligatorios en frontend.

```
Detection → Rule Engine → Event persistido
                              ↓
                    NotificationService
                              ↓
                    TelegramProvider (HTTPS Bot API)
                              ↓
                    Grupo Telegram del barrio
```

## Módulo propuesto

```
backend/app/notifications/
├── base.py           # NotificationProvider (interfaz)
├── telegram.py       # Telegram Bot API (sendMessage, sendPhoto)
├── filters.py        # severidad, tipos, cooldown, horario
├── service.py        # NotificationService (orquestación)
└── factory.py        # create_notification_provider(settings)
```

Integración en `EventIngestionService._persist_events`: tras persistir y
broadcast WebSocket, evaluar si el evento debe notificarse.

## Política de envío

### Mensaje de texto

Enviar para eventos que cumplan **todos** los filtros configurables:

* `NOTIFICATIONS_ENABLED=true`
* Severidad ≥ `NOTIFY_MIN_SEVERITY` (ej. `medium`)
* `event_type` incluido en `NOTIFY_EVENT_TYPES` (lista blanca)
* Cooldown por `(camera_id, event_type)` respetado (`NOTIFY_COOLDOWN_SECONDS`)
* Opcional: ventana horaria (`NOTIFY_QUIET_HOURS_START` / `END`)

Texto prudente, sin identificar personas (privacidad por diseño):

```
⚠️ Alerta — Parque Central
Cámara: Entrada Norte
Evento: posible aglomeración
Hora: 2026-07-11 14:30 UTC
Severidad: high
```

### Foto adjunta (solo eventos más importantes)

Telegram permite enviar imágenes sin costo adicional. Usar captura **solo**
cuando la severidad esté en una lista explícita:

* `NOTIFY_PHOTO_MIN_SEVERITY=high` (solo `high`, o `high` + tipos concretos)
* Generar JPEG en el momento del evento desde `Frame.image` (ya disponible en
  `EventIngestionService.process_detections`)
* Reutilizar `encode_preview_jpeg(..., tracked=..., draw_detections=True)` para
  cajas de detección en la alerta
* **No persistir** la imagen en BD por defecto; enviar y descartar (o retención
  corta opcional en disco con TTL, documentada aparte)

Eventos `low` / `medium`: **solo texto**. Eventos `high` (y los que se
configuren): **texto + foto**.

## Configuración por entorno

Variables en `backend/.env` (ver `backend/.env.example`):

| Variable | Descripción |
|----------|-------------|
| `NOTIFICATIONS_ENABLED` | Activa/desactiva el canal |
| `NOTIFICATION_PROVIDER` | `telegram` (único por ahora) |
| `TELEGRAM_BOT_TOKEN` | Token del bot (`@BotFather`) |
| `TELEGRAM_CHAT_ID` | ID del grupo o canal destino |
| `NOTIFY_MIN_SEVERITY` | Mínimo para cualquier aviso (`medium`, `high`) |
| `NOTIFY_PHOTO_MIN_SEVERITY` | Mínimo para adjuntar foto (`high`) |
| `NOTIFY_EVENT_TYPES` | Lista CSV de tipos (vacío = todos los que pasen severidad) |
| `NOTIFY_COOLDOWN_SECONDS` | Anti-spam entre avisos del mismo tipo/cámara |
| `NOTIFY_ALERT_JPEG_MAX_WIDTH` | Ancho máximo de la captura de alerta |
| `NOTIFY_ALERT_JPEG_QUALITY` | Calidad JPEG de la captura |

Futuro (no bloqueante para MVP): tabla `Community` / `NotificationChannel` en
BD para **un grupo Telegram distinto por barrio** sin redeploy.

## Privacidad y seguridad

* No almacenar frames completos indefinidamente.
* Mensajes en tono de posible evento, no afirmaciones absolutas.
* No reconocimiento facial ni datos personales en el texto.
* `TELEGRAM_BOT_TOKEN` solo en variables de entorno, nunca en el repo.
* Log sin token ni contenido sensible de chats.

## Dependencias

* `httpx` (ya usado en el proyecto) o `aiohttp` para llamadas async a
  `https://api.telegram.org/bot<token>/sendMessage` y `sendPhoto`.
* Sin SDK obligatorio; la Bot API REST es suficiente.

## Checklist

- [ ] Módulo `notifications/` con interfaz `NotificationProvider`.
- [ ] `TelegramProvider`: `send_message`, `send_photo` (multipart).
- [ ] `NotificationFilter`: severidad, tipos, cooldown, quiet hours.
- [ ] `NotificationService` con registro de envíos (evitar duplicados).
- [ ] Hook en `EventIngestionService` post-persistencia.
- [ ] Captura JPEG en eventos con foto (`encode_preview_jpeg` + frame del evento).
- [ ] Variables en `Settings` + `backend/.env.example`.
- [ ] Tests con mock HTTP (sin bot real en CI).
- [ ] Documentación de setup del bot y obtención de `chat_id` en README o `docs/`.

## Setup del bot (operación)

1. En Telegram, abrir [@BotFather](https://t.me/BotFather) → `/newbot` → copiar **token**.
2. Crear grupo del barrio e **invitar al bot** como miembro.
3. Enviar un mensaje de prueba al grupo.
4. Obtener `chat_id` del grupo (API `getUpdates` o bot auxiliar como `@userinfobot` / `@RawDataBot`).
5. Configurar `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en `.env` del backend.
6. Reiniciar backend; disparar un evento de prueba con severidad `high`.

**Nota:** la Bot API de Telegram **no cobra por mensaje**. El costo operativo
es el mismo servidor Docker que ya corre el backend.

**Estado: PENDIENTE.**

---

# Orden resumido

```
1. Documentación
        ↓
2. Monorepo
        ↓
3. Docker + Infra
        ↓
4. Backend base
        ↓
5. PostgreSQL + modelos
        ↓
6. Simulador de cámara
        ↓
7. YOLO + Tracking
        ↓
8. Motor de eventos
        ↓
9. LLM
        ↓
10. API completa
        ↓
11. WebSockets
        ↓
12. Frontend
        ↓
13. Cámaras reales
        ↓
14. Notificaciones Telegram (backend, frontend opcional)
```

Mi recomendación adicional: antes de generar cualquier código, crear `IMPLEMENTATION_PLAN.md` y luego una regla adicional para Cursor:

```
.cursor/rules/implementation-flow.mdc
```

que le diga:

* leer el plan,
* ejecutar fases en orden,
* no saltar fases,
* marcar progreso,
* pedir confirmación antes de avanzar entre fases grandes.

Eso evitará que Cursor empiece creando un dashboard cuando todavía no existe ni el pipeline de datos.
