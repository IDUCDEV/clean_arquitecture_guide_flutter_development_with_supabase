# Módulo 18: Debugging con VS Code y Flutter DevTools

> El debugging es la habilidad que separa a un desarrollador junior de uno senior. No se trata solo de encontrar errores, sino de **entender el comportamiento de tu aplicación** en tiempo real, diagnosticar problemas de performance, detectar memory leaks y optimizar cada aspecto de tu app. En la era de la IA, esta habilidad es más importante que nunca: **debuggear sin depender de la IA** es lo que te hace un developer verdaderamente productivo.

Este módulo cubre tres pilares del debugging:

1. **Mentalidad y methodology** — Cómo pensar como un debugger (anti-AI-dependency)
2. **VS Code Debugging** — El debugger integrado en tu IDE
3. **Flutter DevTools** — La suite completa de profiling y diagnóstico
4. **Debugging programático** — Herramientas de debug desde el código Dart
5. **Debugging por capa** — Ejecutar cada capa de Clean Architecture aislada con el debugger (modo andamiaje SDD)

---

## Mapa mental: cuándo usar qué

```
Necesito entender CÓMO debugear (mentalidad)
  └── 27-mentalidad-debugging.md → Playbook sistemático (29)

Necesito pausar la ejecución en una línea
  └── VS Code Debugger (F5, breakpoints, stepping)

Necesito ver qué rebuilda / qué se repinta
  └── 28-debugging-programatico-flutter.md (debugPrintRebuildDirtyWidgets)

Necesito ver el árbol de widgets sin DevTools
  └── debugDumpWidgetTree() (28)

Mi app se siente lenta o tiene jank
  └── DevTools > Performance View

Sospecho un memory leak
  └── DevTools > Memory View

Un request HTTP falla o es lento
  └── DevTools > Network View

No entiendo por qué un widget se ve mal
  └── DevTools > Flutter Inspector

Necesito una referencia rápida de todo
  └── 30-referencia-rapida-flutter-debugging.md

Implementé una capa del andamiaje SDD y quiero verificarla aislada
  └── 31-debugging-por-capa.md (scratchpad, dart run / flutter run -t)
  └── Modo real (datasource→Supabase) vs Modo stub (usecase/cubit)
```

---

## Requisitos previos

| Módulo | Por qué |
|---|---|
| [05-TESTING](../05-TESTING/) | Testing y debugging se complementan |
| [16-BLOC-CUBIT](../16-BLOC-CUBIT/) | Debugging de BLoC/Cubit es escenario principal |
| [01-CLEAN-ARCHITECTURE](../01-CLEAN-ARCHITECTURE/) | Entender capas para saber dónde poner breakpoints |
| [03-SUPABASE](../03-SUPABASE/) | Debugging de llamadas a Supabase |
| [02-SPEC-DRIVEN-DEVELOPMENT](../02-SPEC-DRIVEN-DEVELOPMENT/) | Andamiaje SDD: contexto del capítulo 31 (verificar capa a capa) |

---

## Contenido del módulo

### Los 30 capítulos

| # | Archivo | Descripción |
|---|---|---|
| **Fase 0: Mentalidad** | | |
| 27 | [27-mentalidad-debugging.md](./27-mentalidad-debugging.md) | Mentalidad de debugging: piensa como un debugger |
| **Fase 1: Fundamentos VS Code** | | |
| 1 | [01-fundamentos-debugging.md](./01-fundamentos-debugging.md) | Fundamentos del debugging en Flutter |
| 2 | [02-configuracion-launch-json.md](./02-configuracion-launch-json.md) | Configuración de launch.json |
| 3 | [03-breakpoints-avanzados.md](./03-breakpoints-avanzados.md) | Breakpoints avanzados en VS Code |
| 4 | [04-inspeccion-datos-consola.md](./04-inspeccion-datos-consola.md) | Inspección de datos en la consola |
| 5 | [05-multi-target-remoto.md](./05-multi-target-remoto.md) | Multi-target y debugging remoto |
| 6 | [06-cheatsheet-vscode.md](./06-cheatsheet-vscode.md) | Cheatsheet de debugging en VS Code |
| 7 | [07-practicas-vscode.md](./07-practicas-vscode.md) | Prácticas de debugging en VS Code |
| **Fase 1.5: Debugging desde código** | | |
| 28 | [28-debugging-programatico-flutter.md](./28-debugging-programatico-flutter.md) | Herramientas de debug desde código Dart |
| **Fase 2: DevTools** | | |
| 8 | [08-fundamentos-devtools.md](./08-fundamentos-devtools.md) | Fundamentos de Flutter DevTools |
| 9 | [09-inspector-layout.md](./09-inspector-layout.md) | Flutter Inspector y layout |
| 10 | [10-performance-view.md](./10-performance-view.md) | Performance View: frames y jank |
| 11 | [11-cpu-profiler.md](./11-cpu-profiler.md) | CPU Profiler y flame charts |
| 12 | [12-memory-profiler.md](./12-memory-profiler.md) | Memory View: heap, leaks y GC |
| 13 | [13-network-view.md](./13-network-view.md) | Network View: requests HTTP |
| 14 | [14-debugger-view.md](./14-debugger-view.md) | Debugger View en DevTools |
| 15 | [15-logging-view.md](./15-logging-view.md) | Logging View |
| 16 | [16-app-size.md](./16-app-size.md) | App Size: reducir el tamaño |
| 17 | [17-cheatsheet-devtools.md](./17-cheatsheet-devtools.md) | Cheatsheet de DevTools |
| 18 | [18-practicas-devtools.md](./18-practicas-devtools.md) | Prácticas con DevTools |
| **Fase 3: Rendimiento** | | |
| 19 | [19-fundamentos-rendimiento.md](./19-fundamentos-rendimiento.md) | Fundamentos de rendimiento |
| 20 | [20-optimizar-rebuilds.md](./20-optimizar-rebuilds.md) | Optimizar rebuilds |
| 21 | [21-memory-leak-detection.md](./21-memory-leak-detection.md) | Detección de memory leaks |
| 22 | [22-rendering-complejo.md](./22-rendering-complejo.md) | Rendering complejo: listas y slivers |
| 23 | [23-cheatsheet-optimizacion.md](./23-cheatsheet-optimizacion.md) | Cheatsheet de optimización |
| 24 | [24-practicas-optimizacion.md](./24-practicas-optimizacion.md) | Prácticas de optimización |
| **Fase 4: Maestría** | | |
| 25 | [25-debugging-asincrono.md](./25-debugging-asincrono.md) | Debugging asíncrono |
| 26 | [26-workflow-debugging-por-tipo.md](./26-workflow-debugging-por-tipo.md) | Workflow por tipo de bug |
| 29 | [29-playbook-debugging-sistematico.md](./29-playbook-debugging-sistematico.md) | Playbook de debugging sistemático |
| **Fase 4.5: Debugging por capa** | | |
| 31 | [31-debugging-por-capa.md](./31-debugging-por-capa.md) | Ejecución aislada de cada capa de Clean Architecture con el debugger (modo andamiaje SDD) |
| **Fase 5: Referencia** | | |
| 30 | [30-referencia-rapida-flutter-debugging.md](./30-referencia-rapida-flutter-debugging.md) | Referencia rápida de todo el módulo |

### Progresión recomendada

```
Fase 0: Mentalidad (NUEVO - empezar aquí si eres nuevo en debugging)
  └── mentalidad-debugging → filosofía anti-dependencia-AI

Fase 1: Fundamentos (VS Code)
  ├── fundamentos -> launch.json -> breakpoints
  └── inspección de datos -> multi-target

Fase 1.5: Debugging desde código (NUEVO)
  └── Herramientas programáticas: debug flags, dump methods, assertions

Fase 2: DevTools
  ├── fundamentos -> inspector -> performance
  └── CPU profiler -> memory -> network -> logging -> app size

Fase 3: Rendimiento
  ├── fundamentos de rendimiento -> optimizar rebuilds
  └── memory leaks -> rendering complejo

Fase 4: Maestría
  ├── debugging asíncrono -> workflow por tipo de bug
  └── playbook sistemático (NUEVO - tu hoja de ruta para diagnosticar cualquier bug)

Fase 4.5: Debugging por capa (NUEVO)
  └── ejecución aislada por capa (scratchpad) → cómo verificar cada capa
      del andamiaje SDD con el debugger, sin depender de la IA ni de la app completa

Fase 5: Referencia (NUEVO)
  └── referencia rápida imprimible con TODO el módulo en una página
```

---

## Herramientas que necesitas

| Herramienta | Versión mínima | Para qué |
|---|---|---|
| VS Code | 1.80+ | IDE con debugger integrado |
| Extensión Dart | latest | Debugging Dart/Flutter |
| Extensión Flutter | latest | Soporte Flutter en VS Code |
| Flutter SDK | 3.22+ | DevTools incluido |
| DevTools | 2.23+ | Suite de profiling |

---

## Convenciones en este módulo

- Los ejemplos usan **Clean Architecture** (ver módulo 01)
- State management: **BLoC/Cubit** (ver módulo 16)
- Backend: **Supabase** (ver módulo 03)
- Los escenarios prácticos son **reales y reproducibles**
- Cada cheatsheet es una **referencia rápida imprimible**
- Todas las mediciones de rendimiento se hacen en **profile mode** (`flutter run --profile`)

---

## Fuentes oficiales

- [VS Code Debugging](https://code.visualstudio.com/docs/debugtest/debugging)
- [VS Code Debugging Configuration](https://code.visualstudio.com/docs/debugtest/debugging-configuration)
- [Flutter Debugging tools](https://docs.flutter.dev/tools/debugging)
- [Flutter DevTools](https://docs.flutter.dev/tools/devtools)
- [Flutter Inspector](https://docs.flutter.dev/tools/devtools/inspector)
- [Performance View](https://docs.flutter.dev/tools/devtools/performance)
- [Memory View](https://docs.flutter.dev/tools/devtools/memory)
- [Network View](https://docs.flutter.dev/tools/devtools/network)
