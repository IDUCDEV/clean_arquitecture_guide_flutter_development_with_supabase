# 30 — Referencia Rápida: Todo el Debugging en una Página

> Cheatsheet ultra-densa de TODO el módulo. Imprime esto y tenlo al lado de tu monitor.

---

## 1. Atajos de VS Code

| Atajo | Acción |
|---|---|
| `F5` | Start / Continue debugging |
| `Ctrl+F5` | Run without debugging |
| `Shift+F5` | Stop debugging |
| `Ctrl+Shift+F5` | Restart (Hot Restart en Flutter) |
| `F9` | Toggle breakpoint |
| `F10` | Step over |
| `F11` | Step into |
| `Shift+F11` | Step out |
| `Ctrl+Shift+F9` | Inline breakpoint |
| `Ctrl+Shift+D` | Run and Debug panel |
| `Ctrl+Shift+Y` | Debug Console |

---

## 2. Panel de Debug

```
┌─────────────────────────────────────────────────┐
│ VARIABLES  │ Locales, campos, closures           │
│ WATCH      │ Expresiones que monitoreas          │
│ CALL STACK │ Pila de llamadas (frames)           │
│ BREAKPOINTS│ Lista de todos los breakpoints      │
├─────────────────────────────────────────────────┤
│ DEBUG CONSOLE │ REPL para evaluar expresiones    │
│ (Ctrl+Shift+Y)│                                  │
└─────────────────────────────────────────────────┘
```

---

## 3. Breakpoints

| Tipo | Icono | Cómo | Cuándo |
|---|---|---|---|
| Línea | 🔴 | Click gutter / F9 | Pausar en una línea |
| Expression | 🔴+📝 | Click derecho → Conditional | Cuando se cumple condición |
| Hit Count | 🔴+🔢 | Conditional → Hit Count | Cada N veces |
| Logpoint | 🟢💎 | Click derecho → Add Logpoint | Log sin pausar |
| Inline | 🔴 small | Ctrl+Shift+F9 | Statement específico |

---

## 4. launch.json — Templates

### Debug Flutter
```json
{"name":"Flutter (Debug)","type":"dart","request":"launch","program":"lib/main.dart"}
```

### Profile
```json
{"name":"Flutter (Profile)","type":"dart","request":"launch","program":"lib/main.dart","flutterMode":"profile"}
```

### Con flavors
```json
{"name":"Dev","type":"dart","request":"launch","program":"lib/main.dart","toolArgs":["--flavor","development","-t","lib/main_development.dart"]}
```

### Con dart-define
```json
{"name":"Dev+Env","type":"dart","request":"launch","program":"lib/main.dart","dartDefine":["ENV=dev","SUPABASE_URL=http://localhost:54321"]}
```

### Attach
```json
{"name":"Attach","type":"dart","request":"attach","program":"lib/main.dart"}
```

### Test
```json
{"name":"Test","type":"dart","request":"launch","program":"test/widget_test.dart","args":["--name","test name"]}
```

### Compound (App + Worker)
```json
"compounds":[{"name":"App+Worker","configurations":["Flutter","Worker"]}]
```

---

## 5. Debug Flags de Flutter

### Desde `main()`
```dart
import 'package:flutter/rendering.dart';

void main() {
  // Bounds y constraints
  debugPaintSizeEnabled = true;
  
  // Bordes de capas
  debugPaintLayerBordersEnabled = true;
  
  // Área de touch
  debugPaintPointersEnabled = true;
  
  // Baselines de texto
  debugPaintBaselinesEnabled = true;
  
  // Log cada rebuild
  debugPrintRebuildDirtyWidgets = true;
  
  // Log cada layout
  debugPrintLayouts = true;
  
  // Log cada repaint
  debugProfilePaintsEnabled = true;
  
  runApp(MyApp());
}
```

### Debugging programático
```dart
// Árbol de widgets
debugDumpWidgetTree();

// Árbol de render
debugDumpRenderTree();

// Capas GPU
debugDumpLayerTree();

// Accesibilidad
debugDumpSemanticsTree();
```

### Manejo de errores
```dart
FlutterError.onError = (details) {
  FlutterError.presentError(details);
};

ErrorWidget.builder = (details) {
  return const Material(child: Center(child: Text('Error')));
};
```

### Performance Overlay
```dart
Stack(children: [MyApp(), PerformanceOverlay.all()]);
```

### Assertions (solo debug mode)
```dart
assert(myValue != null, 'myValue no puede ser null');
```

---

## 6. Debug Console — Expresiones útiles

```dart
// Tipo
variable.runtimeType

// Contenido
myList → [1, 2, 3]
myMap → {"key": "value"}

// Operaciones
counter + 1
myList.length
myList.isEmpty
user?.name ?? "Anonymous"

// Condicionales
state is LoginLoading ? "cargando" : "listo"
```

---

## 7. Hot Reload vs Hot Restart

| | Hot Reload (`r`) | Hot Restart (`Ctrl+Shift+F5`) |
|---|---|---|
| Estado | Se mantiene | Se pierde todo |
| Breakpoints | Se mantienen | Se limpian |
| Uso | Cambios visuales | Cambios en main/initState |
| Velocidad | ~segundos | ~5-10 segundos |

### NO se recarga con Hot Reload:
- `initState()`
- `main()`
- `const` values
- Imports
- Static fields

---

## 8. Workflow de 6 pasos

```
1. ENTENDER     → ¿Qué se esperaba vs qué pasó?
2. REPRODUCIR   → Steps exactos, siempre falla
3. AISLAR       → Binary search con breakpoints
4. DIAGNOSTICAR → Variables, watch, call stack
5. CORREGIR     → Fix mínimo, un cambio a la vez
6. VERIFICAR    → Reproducir + tests + regresión
```

---

## 9. Matriz: tipo de bug → herramienta

| Bug | Primera acción | Herramienta |
|---|---|---|
| UI se ve mal | Select Widget | Flutter Inspector |
| Estado no cambia | Breakpoint en emit() | Debugger |
| API falla | Network View | DevTools |
| Build error | Leer error completo | Terminal |
| Performance | Performance Overlay | DevTools |
| Memory leak | Heap Snapshot | DevTools Memory |
| Hot reload no funciona | Hot Restart | Ctrl+Shift+F5 |

---

## 10. Checklist universal

```
□ Puedo reproducir el bug
□ Sé los steps exactos
□ Sé en qué archivo/functión ocurre
□ Inspeccioné las variables
□ Leí el error completo
□ Revisé git log
□ Busqué en Google/Stack Overflow
□ Revisé la documentación oficial
□ Puedo explicar el problema
□ Entiendo QUÉ falla (no solo QUÉ hacer)
```

---

## 📚 Módulos relacionados

| Tema | Archivo |
|---|---|
| Mentalidad | [27-mentalidad-debugging.md](./27-mentalidad-debugging.md) |
| Fundamentos VS Code | [01-fundamentos-debugging.md](./01-fundamentos-debugging.md) |
| launch.json | [02-configuracion-launch-json.md](./02-configuracion-launch-json.md) |
| Breakpoints | [03-breakpoints-avanzados.md](./03-breakpoints-avanzados.md) |
| Inspección datos | [04-inspeccion-datos-consola.md](./04-inspeccion-datos-consola.md) |
| Multi-target | [05-multi-target-remoto.md](./05-multi-target-remoto.md) |
| Cheatsheet VS Code | [06-cheatsheet-vscode.md](./06-cheatsheet-vscode.md) |
| Prácticas VS Code | [07-practicas-vscode.md](./07-practicas-vscode.md) |
| Debug programático | [28-debugging-programatico-flutter.md](./28-debugging-programatico-flutter.md) |
| Playbook sistemático | [29-playbook-debugging-sistematico.md](./29-playbook-debugging-sistematico.md) |
| Workflow por tipo | [26-workflow-debugging-por-tipo.md](./26-workflow-debugging-por-tipo.md) |

---

> 📖 **Volver al índice:** [README.md](./README.md)
