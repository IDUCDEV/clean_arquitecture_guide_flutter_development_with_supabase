# Módulo 00 — Diseño de Producto MVP

**Design Sprint + Material Design 3 para apps Flutter**

---

## ¿Por qué este módulo?

Antes de escribir una sola línea de código, necesitas saber **qué construir** y **cómo debe verse y comportarse**. Este módulo une dos metodologías oficiales de Google:

| Metodología | Propósito |
|---|---|
| **Design Sprint Kit** | Definir y validar la idea del producto en 5 días (Understand → Define → Sketch → Decide → Prototype → Validate) |
| **Material Design 3** | Sistema de diseño visual para construir la interfaz (color, tipografía, componentes, motion) |

El resultado: un **MVP validado con usuarios** y **diseñado con el mismo sistema que usa Flutter nativamente**, listo para implementar.

---

## Estructura del módulo

| Archivo | Qué contiene |
|---|---|
| `01-design-sprint-intro.md` | Qué es Design Sprint, las 6 fases, adaptación para MVP mobile con Flutter |
| `02-understand-define.md` | Fases Understand + Define: mapa del problema, user journey, goal, alcance del MVP |
| `03-sketch-decide.md` | Fases Sketch + Decide: Crazy 8s, dot voting, storyboard del flujo crítico |
| `04-m3-fundamentos.md` | Fundamentos M3: color (tonal palettes, dynamic color), tipografía (type scale), shape |
| `05-m3-componentes-mobile.md` | Componentes M3 clave para mobile: NavigationBar, Cards, Buttons, SegmentedButton, SearchBar, Badges |
| `06-prototipado-validacion.md` | Prototipado (Fase 5) con M3 + Validate (Fase 6): test con usuarios, iteración |
| `07-m3-flutter-implementacion.md` | Llevar M3 a Flutter: `ColorScheme.fromSeed`, `ThemeData`, `ThemeExtensions`, Material You (M3 default desde Flutter 3.16) |
| `08-template-proyecto.md` | Explicación del template starter, cómo usarlo y personalizarlo |
| `09-caso-completo-mvp.md` | Caso integrador: app real desde Design Sprint → prototipo M3 → Flutter |
| `BIBLIOGRAFIA.md` | Enlaces oficiales y recursos adicionales |

Además, el directorio `template/` contiene un proyecto Flutter funcional con M3 + Clean Architecture listo para usar como punto de partida.

---

## Progresión sugerida

Si eres **Product Manager / Product Designer**:
```
01 → 02 → 03 → 04 → 05 → 06 → BIBLIOGRAFIA
```

Si eres **Flutter Developer**:
```
04 → 05 → 07 → 08 → 09 → template/
```

Si eres **ambos** (full-stack de producto):
```
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → template/
```

---

## Relación con otros módulos

| Este módulo | Se conecta con |
|---|---|
| `00-DISENIO-PRODUCTO-MVP` | → `01-CLEAN-ARCHITECTURE` (implementar la arquitectura del MVP) |
| `04-m3-fundamentos.md` | → `15-WIDGETS-FLUTTER` (implementar componentes M3 como widgets) |
| `05-m3-componentes-mobile.md` | → `16-BLOC-CUBIT` (conectar UI M3 con estado) |
| `09-caso-completo-mvp.md` | → `03-SUPABASE` (backend del MVP) |
