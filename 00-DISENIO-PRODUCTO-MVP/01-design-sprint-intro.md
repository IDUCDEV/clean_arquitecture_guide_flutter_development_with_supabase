# 01 — Introducción al Design Sprint para MVP Mobile

## ¿Qué es un Design Sprint?

El **Design Sprint** es una metodología creada por Google para responder preguntas críticas de negocio a través del diseño, prototipado y testing con usuarios reales en **5 días**. Fue desarrollada por Jake Knapp en Google Ventures (GV) y hoy está documentada de forma oficial en [gv.com/sprint](https://www.gv.com/sprint/). El antiguo Design Sprint Kit de Google (con el que trabajó este tema durante años) sigue accesible como archivo histórico, pero ya no recibe soporte activo.

No es una metodología más. Es el estándar que Google usa internamente para validar productos antes de invertir en desarrollo.

## Las 6 fases

```
LUNES        MARTES      MIÉRCOLES    JUEVES      VIERNES
Understand → Define →   Sketch  →   Decide →   Prototype → Validate
(Entender)  (Definir)   (Bosquejar) (Decidir)   (Prototipar) (Validar)
```

| Fase | Duración | Objetivo |
|---|---|---|
| **Understand** | 1 día | Mapear el problema, alinear al equipo, recopilar información |
| **Define** | (incluido en Understand) | Definir el foco del sprint, metas y métricas de éxito |
| **Sketch** | 1 día | Generar soluciones individuales en papel |
| **Decide** | 1 día | Criticar, votar y decidir la mejor solución |
| **Prototype** | 1 día | Construir un prototipo realista (pero falso) |
| **Validate** | 1 día | Testear con 5 usuarios reales |

## ¿Por qué funciona?

1. **Comprime meses en 5 días**: lo que normalmente toma investigación, proof-of-concept y discusiones interminables se reduce a una semana enfocada.
2. **Pone al usuario en el centro**: el viernes tienes evidencia real, no suposiciones.
3. **Alinea al equipo**: diseño, producto e ingeniería trabajan juntos desde el día 1.

## Design Sprint vs. metodologías tradicionales

| Aspecto | Design Sprint | Agile/Scrum tradicional |
|---|---|---|
| Horizonte | Descubrimiento (descubrir qué construir) | Entrega (cómo construir ya definido) |
| Validación | Antes de escribir código | Después de escribir código |
| Riesgo | Bajo (prototipo rápido) | Alto (inversión en desarrollo) |
| Usuarios | 5 usuarios en 1 día | Usuarios reales en producción |
| Cambio de dirección | Gratis (solo papel) | Costoso (código desechado) |

## Adaptación para MVP mobile con Flutter

Un Design Sprint clásico asume que prototipas en herramientas como Figma o Keynote. Para un MVP mobile con Flutter, la adaptación es:

1. **Understand + Define**: mismos ejercicios (mapa, goal, expert interviews). El entregable es un **documento de alcance del MVP** con las pantallas críticas identificadas.

2. **Sketch + Decide**: mismos ejercicios. El entregable es un **storyboard** del flujo principal de la app.

3. **Prototype**: aquí puedes elegir:
   - **Opción A (recomendada para no-devs)**: Figma con el [kit de M3](https://www.figma.com/community/file/1035203688168086460). Rápido, sin código.
   - **Opción B (para devs)**: Flutter con el template M3 de este módulo. Más realista, más lento.
   - **Opción C (híbrida)**: Prototipo en Figma para validar el jueves, y mientras tanto preparar la base en Flutter con el template.

4. **Validate**: pruebas con usuarios sobre el prototipo. El entregable es un **informe de validación** con hallazgos y decisiones.

## Antes del Sprint: el equipo

Para un Sprint de app móvil necesitas:

| Rol | Cantidad | Responsabilidad |
|---|---|---|
| **Facilitador** | 1 | Cronometra, guía los ejercicios, no opina |
| **Decisor** | 1 | Dueño del producto, tiene la última palabra |
| **Diseñador UI/UX** | 1 | Domina M3, Figma, patrones mobile |
| **Flutter Dev** | 1 | Conoce viabilidad técnica, costos de implementación |
| **Experto en negocio** | 1 | Conoce el mercado, los usuarios, la competencia |

Mínimo viable: Facilitador + Decisor + Diseñador. Si eres solo tú, puedes hacer un Sprint en solitario (más lento, pero funciona).

## ¿Cuándo NO hacer un Design Sprint?

- Cuando el problema ya está muy definido y solo falta implementar
- Cuando no tienes acceso a usuarios para validar
- Cuando el equipo no puede comprometer 5 días completos
- Cuando necesitas un producto completo (el Sprint solo da un MVP validado)

---

**Siguiente: [02 — Understand + Define](02-understand-define.md)**
