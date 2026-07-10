# Community AI Monitor

## Contexto General del Proyecto

## 1. Descripción

Community AI Monitor es una plataforma inteligente de monitoreo comunitario basada en visión por computadora e inteligencia artificial.

El objetivo principal es transformar fuentes de video provenientes de cámaras en información útil para una comunidad, barrio o zona determinada, permitiendo observar patrones, detectar eventos relevantes y generar información que ayude a mejorar seguridad, organización y toma de decisiones.

El sistema NO tiene como objetivo identificar personas mediante reconocimiento facial ni realizar vigilancia invasiva.

El enfoque está basado en:

- detección de objetos,
- análisis de comportamiento,
- generación de eventos,
- estadísticas,
- alertas,
- resúmenes inteligentes utilizando modelos de lenguaje.

---

# 2. Objetivos del Proyecto

## Objetivo principal

Construir un sistema capaz de analizar cámaras en tiempo real y convertir imágenes en datos estructurados que permitan responder preguntas como:

- ¿Qué está ocurriendo actualmente?
- ¿Qué eventos relevantes ocurrieron?
- ¿Cuáles son los patrones normales de actividad?
- ¿Qué situaciones pueden requerir atención?

---

## Objetivos secundarios

- Crear una arquitectura escalable.
- Separar claramente procesamiento de IA y lógica de negocio.
- Utilizar modelos abiertos siempre que sea posible.
- Minimizar costos operativos.
- Aplicar buenas prácticas profesionales.
- Crear un proyecto demostrable para portafolio.

---

# 3. Filosofía del Proyecto

El proyecto debe priorizar:

1. Simplicidad antes que complejidad.
2. Código mantenible antes que soluciones rápidas.
3. Arquitectura preparada para crecer.
4. Bajo costo operacional.
5. Uso responsable de inteligencia artificial.

La IA debe ser utilizada como una herramienta de apoyo, no como un sistema autónomo de toma de decisiones críticas.

---

# 4. Arquitectura General

El proyecto utiliza una arquitectura de monorepositorio.

Estructura:

```
community-ai-monitor/
├── backend/              # API y procesamiento
├── frontend/             # Dashboard web (SPA React)
├── docs/                 # Documentación técnica adicional
├── docker/               # Archivos Docker
├── .cursor/              # Reglas de desarrollo para Cursor
├── PROJECT_CONTEXT.md
├── IMPLEMENTATION_PLAN.md
├── README.md
├── .gitignore
└── docker-compose.yml
```

---

# 5. Backend

## Tecnología principal

Python.

Framework principal:

- FastAPI

Responsabilidades:

- API REST.
- Gestión de cámaras.
- Gestión de eventos.
- Comunicación con modelos IA.
- Persistencia de información.
- Procesamiento asíncrono.
- Comunicación en tiempo real.

---

# 6. Frontend

Tecnología:

- React SPA

Responsabilidad:

- Dashboard.
- Visualización de cámaras.
- Estadísticas.
- Alertas.
- Historial de eventos.
- Comunicación mediante API y WebSockets.

El frontend debe mantenerse desacoplado del procesamiento de inteligencia artificial.

---

# 7. Procesamiento de Video

Flujo principal:

```

Camera

↓

Video Capture

↓

Object Detection

↓

Object Tracking

↓

Event Detection

↓

Database

↓

AI Summary

↓

Frontend

```

---

# 8. Computer Vision

El sistema utilizará modelos especializados.

Responsabilidades:

## Object Detection

Detectar elementos como:

- Personas.
- Vehículos.
- Bicicletas.
- Animales.
- Objetos.

Modelo inicial:

- YOLO.

---

## Object Tracking

Permitir seguimiento temporal.

Ejemplo:

```

Persona detectada

↓

ID temporal asignado

↓

Movimiento registrado

↓

Salida de escena

```

Tecnologías consideradas:

- ByteTrack.
- BoT-SORT.

---

# 9. Sistema de Eventos

La lógica principal del negocio estará basada en eventos.

Ejemplos:

## Persona permanece demasiado tiempo

Entrada:

```

Persona detectada
Duración: 30 minutos

```

Resultado:

```

Evento:
Permanencia prolongada

```

---

## Objeto abandonado

Entrada:

```

Objeto detectado

Sin interacción

Tiempo > límite configurado

```

Resultado:

```

Evento:
Objeto posiblemente abandonado

```

---

## Aglomeraciones

Entrada:

```

Cantidad personas > límite

```

Resultado:

```

Evento:
Concentración inusual

````

---

# 10. Inteligencia Artificial Generativa

El modelo de lenguaje NO procesa directamente video.

Responsabilidad:

- Crear resúmenes.
- Explicar eventos.
- Responder preguntas.
- Generar reportes.

Entrada:

```json
{
 "events": [
   {
    "type":"crowd",
    "people":15
   }
 ]
}
````

Salida:

Texto descriptivo generado.

---

# 11. Modelos LLM

Prioridad:

1. Modelos abiertos.
2. Bajo costo.
3. Ejecución local cuando sea posible.

Modelos considerados:

* Llama.
* Qwen.
* Mistral.

El modelo debe ser intercambiable.

No crear dependencias fuertes hacia un único proveedor.

---

# 12. Base de Datos

Base principal:

PostgreSQL.

La base debe almacenar:

* Cámaras.
* Configuraciones.
* Detecciones.
* Eventos.
* Alertas.
* Estadísticas.
* Resúmenes.

La información histórica es un elemento central del sistema.

---

# 13. Comunicación en Tiempo Real

Se utilizarán WebSockets para:

* Nuevos eventos.
* Alertas.
* Actualizaciones del dashboard.

Ejemplo:

```
Detector

↓

Evento generado

↓

WebSocket

↓

Frontend actualizado
```

---

# 14. Configuración

Toda configuración modificable debe estar fuera del código.

Ejemplos:

* Límites de detección.
* Tiempo para eventos.
* Configuración de cámaras.
* Modelo utilizado.
* Nivel de confianza.

Utilizar:

* Variables de entorno.
* Archivos de configuración.

---

# 15. Principios de Desarrollo

## Código

Debe ser:

* Legible.
* Modular.
* Documentado.
* Fácil de probar.

Evitar:

* Código duplicado.
* Funciones gigantes.
* Dependencias innecesarias.
* Soluciones temporales sin documentar.

---

# 16. Uso de Inteligencia Artificial para Desarrollo

Este proyecto será desarrollado utilizando asistencia de IA.

La IA puede:

* Generar código.
* Proponer soluciones.
* Crear documentación.
* Revisar implementaciones.

Pero:

Todas las decisiones arquitectónicas finales deben ser revisadas por el desarrollador responsable.

La IA no reemplaza:

* criterio técnico,
* revisión de seguridad,
* decisiones de arquitectura.

---

# 17. Reglas Generales para Cursor

Cuando Cursor genere código debe:

* Respetar la arquitectura existente.
* No crear nuevas dependencias sin justificar.
* No modificar archivos fuera del alcance solicitado.
* Mantener compatibilidad con código existente.
* Priorizar soluciones simples.
* Crear código preparado para pruebas.
* Explicar decisiones importantes.

Antes de implementar cambios grandes:

1. Analizar arquitectura actual.
2. Explicar propuesta.
3. Esperar confirmación cuando exista impacto importante.

---

# 18. Evolución futura

Posibles extensiones:

* Múltiples cámaras.
* Diferentes comunidades.
* Aplicación móvil.
* Integración con WhatsApp.
* Notificaciones inteligentes.
* Análisis predictivo.
* Integración con cámaras externas.

---

# 19. Estado actual

Fase actual:

FASE 2 — Backend base (completada).

Siguiente fase:

FASE 3 — Base de datos y modelos iniciales (PostgreSQL, SQLAlchemy, Alembic).

Prioridad de implementación (ver `IMPLEMENTATION_PLAN.md`):

1. Infraestructura.
2. Backend base.
3. Base de datos y modelos.
4. Simulador de cámara.
5. Pipeline de visión (YOLO + tracking).
6. Motor de eventos.
7. LLM.
8. API pública.
9. WebSockets.
10. Frontend.
11. Cámaras reales.
