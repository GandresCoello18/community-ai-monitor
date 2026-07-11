# Notificaciones Telegram (Fase 12)

Alertas al grupo del barrio **sin depender del frontend**. El backend envía
mensajes cuando se persisten eventos que cumplen la política configurada.

## Requisitos

- Bot creado con [@BotFather](https://t.me/BotFather)
- Grupo de Telegram del barrio con el bot agregado como miembro
- Variables en `backend/.env` (ver `backend/.env.example`)

## Configuración del bot

1. Abrir [@BotFather](https://t.me/BotFather) en Telegram.
2. Enviar `/newbot` y seguir los pasos.
3. Copiar el **token** del bot (formato `123456789:AA...`).
4. Crear un grupo para el barrio e **invitar al bot**.
5. Enviar un mensaje de prueba en el grupo.
6. Obtener el **chat_id** del grupo:
   - Opción A: llamar a `getUpdates` de la Bot API tras el mensaje de prueba.
   - Opción B: usar un bot auxiliar como `@RawDataBot` en el grupo.
   - Los grupos suelen tener IDs negativos (ej. `-1001234567890`).

## Variables de entorno

```env
NOTIFICATIONS_ENABLED=true
NOTIFICATION_PROVIDER=telegram
TELEGRAM_BOT_TOKEN=123456789:AA...
TELEGRAM_CHAT_ID=-1001234567890
NOTIFY_MIN_SEVERITY=medium
NOTIFY_PHOTO_MIN_SEVERITY=high
NOTIFY_EVENT_TYPES=
NOTIFY_COOLDOWN_SECONDS=300
NOTIFY_QUIET_HOURS_START=
NOTIFY_QUIET_HOURS_END=
NOTIFY_ALERT_JPEG_MAX_WIDTH=640
NOTIFY_ALERT_JPEG_QUALITY=75
```

### Política de envío

| Condición | Comportamiento |
|-----------|----------------|
| `NOTIFICATIONS_ENABLED=false` | Sin envíos |
| Severidad &lt; `NOTIFY_MIN_SEVERITY` | Ignorado |
| `NOTIFY_EVENT_TYPES` vacío | Todos los tipos que pasen severidad |
| `NOTIFY_EVENT_TYPES=crowd_detected,high_density` | Solo esos tipos |
| Cooldown `(cámara, tipo)` | Anti-spam entre avisos repetidos |
| Horario silencioso (UTC) | Sin envíos en esa ventana |
| Severidad ≥ `NOTIFY_PHOTO_MIN_SEVERITY` | Texto + foto JPEG del frame actual |

Las fotos **no se persisten** en base de datos: se generan, envían y descartan.

## Privacidad

- Mensajes en tono de **posible** evento, sin identificar personas.
- No reconocimiento facial ni datos personales en el texto.
- El token del bot **nunca** debe commitearse al repositorio.

## Probar en local

1. Configurar `.env` con token y chat_id reales.
2. Reiniciar el backend.
3. Generar un evento con severidad `high` (por ejemplo aglomeración o densidad).
4. Verificar el mensaje (y foto si aplica) en el grupo.

## Costo

La [Telegram Bot API](https://core.telegram.org/bots/api) es gratuita. El costo
operativo es el mismo servidor que ya ejecuta el backend.
