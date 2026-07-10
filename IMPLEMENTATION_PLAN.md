
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

---

# Fase 7 — LLM

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

---

# Fase 10 — Frontend

Ahora sí.

React:

* Dashboard.
* Lista de cámaras.
* Eventos.
* Estadísticas.
* Gráficos.

---

# Fase 11 — Cámaras reales

Finalmente:

Integrar:

* cámaras IP.
* RTSP.
* Streams reales.

Porque si empiezas aquí, los problemas de red/hardware mezclan problemas de software.

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
