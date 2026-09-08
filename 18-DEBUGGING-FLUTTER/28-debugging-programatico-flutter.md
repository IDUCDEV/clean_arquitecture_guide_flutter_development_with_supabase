# 28 — Debugging Programático: Herramientas de Debug desde el Código

> Flutter ofrece un arsenal de flags, métodos y widgets para diagnosticar problemas directamente desde tu código Dart, sin necesidad de breakpoints ni DevTools. Conócelos para cuando el debugger tradicional no es la mejor opción.

---

## 1. ¿Cuándo usar debugging programático?

| Escenario | Herramienta debugger (VS Code) | Herramienta programática |
|---|---|---|
| Necesitas pausar en una línea específica | Breakpoint | — |
| Necesitas ver qué rebuilda un widget | — | `debugPrintRebuildDirtyWidgets` |
| Necesitas ver el árbol de widgets | — | `debugDumpWidgetTree()` |
| Necesitas ver bounds de cada widget | — | `debugPaintSizeEnabled` |
| El bug solo pasa en release (no puedes debuggear) | — | `FlutterError.onError` |
| Necesitas logging continuo sin pausas | Logpoint | `debugPrint()` |
| Necesitas ver qué se repinta | — | `debugProfilePaintsEnabled` |

El debugging programático es tu arsenal para bugs que **no puedes pausar** o que necesitas **monitorear continuamente**.

---

## 2. `debugPrint()` — La alternativa inteligente a `print()`

### 2.1 Por qué no usar `print()`

```dart
// ❌ print() envía todo al log de Android/iOS de golpe
for (var i = 0; i < 1000; i++) {
  print('Item $i'); // Puede causar "lost connection to VM"
}
```

### 2.2 Por qué usar `debugPrint()`

```dart
// ✅ debugPrint() hace throttling (limita la velocidad de salida)
for (var i = 0; i < 1000; i++) {
  debugPrint('Item $i'); // Salida gradual, no se corta
}
```

### 2.3 `debugPrintThrottled()` — El throttling explícito

```dart
// Útil cuando quieres controlar la velocidad manualmente
debugPrintThrottled('Mensaje que puede repetirse mucho');
```

### 2.4 En producción se desactiva automáticamente

```dart
// debugPrint() NO se ejecuta en release mode
// print() SÍ se ejecuta (y puede filtrar información)
debugPrint('Esto solo se ve en debug/profile'); // ← No aparece en release
```

> **Regla de oro:** Usa `debugPrint()` en vez de `print()` siempre. Es más seguro (no filtra en producción) y más estable (no causa lost connections).

---

## 3. Dump de árboles: ver la estructura de tu UI

### 3.1 `debugDumpWidgetTree()` — Árbol de widgets

```dart
// En cualquier punto de tu código (ej: dentro de un onPressed)
onPressed: () {
  debugDumpWidgetTree(); // Imprime el árbol completo de widgets
}
```

**Salida típica:**
```
MaterialApp
 └─Directionality
   └─Overlay
     └─[Stack]
       └─Positioned
         └─Positioned
           └─RawDialogRoute
             └─_ModalScope
               └─Stack
                 └─_SubtreeGuard
                   └─StatefulBuilder
                     └─Center
                       └─Padding
                         └─SizedBox
                           └─Column ← Tu widget está aquí
                             ├─Text("Login")
                             ├─TextField
                             └─ElevatedButton
```

**Cuándo usarlo:**
- Cuando no entiendes por qué un widget no se ve
- Cuando necesitas ver qué widgets envuelven al tuyo
- Cuando un widget tiene constraints inesperados

### 3.2 `debugDumpRenderTree()` — Árbol de render

```dart
debugDumpRenderTree(); // Imprime el árbol de render objects
```

**Cuándo usarlo:**
- Cuando sospechas un problema de layout
- Cuando necesitas ver el tamaño y posición exactos de cada widget
- Cuando hay un render overflow que no entiendes

### 3.3 `debugDumpLayerTree()` — Árbol de capas

```dart
debugDumpLayerTree(); // Imprime las capas de composición (GPU)
```

**Cuándo usarlo:**
- Cuando hay problemas visuales (artefactos, parpadeos)
- Cuando necesitas entender cómo Flutter compone la UI en capas

### 3.4 `debugDumpSemanticsTree()` — Árbol de accesibilidad

```dart
debugDumpSemanticsTree(); // Imprime el árbol de semántica (accesibilidad)
```

**Cuándo usarlo:**
- Cuando estás implementando soporte para screen readers
- Cuando los widgets no tienen la semántica correcta (Semantics widget)

### 3.5 `debugDumpSemanticsTree(SemanticsBinding.instance.rootPipelineOwner)` — Versión completa

```dart
// Para ver el árbol completo incluyendo nodos no visibles
debugDumpSemanticsTree(
  SemanticsBinding.instance.rootPipelineOwner,
);
```

---

## 4. Flags de debug: activar overlays visuales

### 4.1 `debugPaintSizeEnabled` — Bounds y constraints

```dart
import 'package:flutter/rendering.dart';

void main() {
  debugPaintSizeEnabled = true; // Activa overlay de bounds
  runApp(MyApp());
}
```

**Qué muestra:**
- Bordes azules para cada widget (muestra sus bounds)
- Padding en amarillo
- Margins en verde claro
- Constraints con líneas punteadas

### 4.2 `debugPaintLayerBordersEnabled` — Bordes de capas

```dart
import 'package:flutter/rendering.dart';

void main() {
  debugPaintLayerBordersEnabled = true; // Bordes de cada capa
  runApp(MyApp());
}
```

**Qué muestra:**
- Bordes de colores aleatorios para cada capa de composición
- Útil para entender por qué hay parpadeos o regiones que no se repintan

### 4.3 `debugPaintPointersEnabled` — Área de touch

```dart
import 'package:flutter/rendering.dart';

void main() {
  debugPaintPointersEnabled = true; // Muestra área de touch
  runApp(MyApp());
}
```

**Qué muestra:**
- Regiones en rojo donde el touch está siendo procesado
- Útil para entender por qué un widget no responde a taps

### 4.4 `debugPaintBaselinesEnabled` — Baselines de texto

```dart
import 'package:flutter/rendering.dart';

void main() {
  debugPaintBaselinesEnabled = true; // Muestra baselines
  runApp(MyApp());
}
```

**Qué muestra:**
- Líneas que muestran las baselines de texto
- Útil para alinear texto manualmente

---

## 5. Debug de rebuilds: quién se actualiza y cuándo

### 5.1 `debugPrintRebuildDirtyWidgets` — Log cada rebuild

```dart
import 'package:flutter/widgets.dart';

void main() {
  debugPrintRebuildDirtyWidgets = true; // Log cada rebuild
  runApp(MyApp());
}
```

**Salida típica:**
```
Rebuilding: MyHomePage
Rebuilding: Text("Counter: 5")
Rebuilding: ElevatedButton
Rebuilding: MyHomePage  ← ¡Este se rebuilda demasiado!
```

**Cuándo usarlo:**
- Cuando tu app se siente lenta y no sabes qué widget rebuilda de más
- Cuando sospechas rebuilds innecesarios
- Para validar que `const` y `RepaintBoundary` están funcionando

### 5.2 `debugPrintLayouts` — Log cada layout

```dart
import 'package:flutter/rendering.dart';

void main() {
  debugPrintLayouts = true; // Log cada layout
  runApp(MyApp());
}
```

**Cuándo usarlo:**
- Cuando un widget tiene tamaño inesperado
- Cuando hay constraints que no entiendes
- Para entender el flujo de layout de un widget complejo

### 5.3 `debugProfilePaintsEnabled` — Qué widgets se repintan

```dart
import 'package:flutter/rendering.dart';

void main() {
  debugProfilePaintsEnabled = true; // Log cada repaint
  runApp(MyApp());
}
```

**Cuándo usarlo:**
- Cuando hay jank visual (parpadeos, tartamudeo)
- Para identificar qué widget se repinta innecesariamente
- Para validar que `RepaintBoundary` está funcionando

---

## 6. Performance Overlay desde código

### 6.1 `showPerformanceOverlay`

```dart
import 'package:flutter/material.dart';

void main() {
  runApp(
    Stack(
      children: [
        MyApp(),
        PerformanceOverlay.all(), // Overlay de performance
      ],
    ),
  );
}
```

**Qué muestra:**
- Barra superior: GPU rendering time (verde < 16ms, rojo > 16ms)
- Barra inferior: UI thread time (verde < 16ms, rojo > 16ms)

### 6.2 `WidgetsFlutterBinding.ensureInitialized()` + flag

```dart
import 'package:flutter/material.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Solo en debug mode
  assert(() {
    debugPaintSizeEnabled = true;
    debugPrintRebuildDirtyWidgets = true;
    return true;
  }());
  
  runApp(MyApp());
}
```

> **Nota:** Los `assert()` solo se ejecutan en debug mode. En profile/release se ignoran automáticamente.

---

## 7. Manejo de errores: personalizar la respuesta

### 7.1 `FlutterError.onError` — Capturar errores de Flutter

```dart
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

void main() {
  FlutterError.onError = (FlutterErrorDetails details) {
    // Log personalizado
    FlutterError.presentError(details);
    
    // O enviar a un servicio de crash reporting
    if (kReleaseMode) {
      // Sentry.captureException(details.exception, stackTrace: details.stack);
    }
  };
  
  runApp(MyApp());
}
```

**Cuándo usarlo:**
- Para personalizar cómo se reportan los errores de Flutter
- Para enviar crashes a un servicio (Sentry, Crashlytics)
- Para mostrar un UI de error en vez del widget rojo por defecto

### 7.2 `ErrorWidget.builder` — Personalizar pantalla de error

```dart
import 'package:flutter/material.dart';

void main() {
  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Material(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error, color: Colors.red, size: 48),
              const SizedBox(height: 16),
              Text(
                'Algo salió mal',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 8),
              Text(details.exceptionAsString()),
            ],
          ),
        ),
      ),
    );
  };
  
  runApp(MyApp());
}
```

### 7.3 `debugCheckElevationsEnabled` — Detectar sombras incorrectas

```dart
import 'package:flutter/rendering.dart';

void main() {
  debugCheckElevationsEnabled = true; // Detecta problemas de elevación
  runApp(MyApp());
}
```

---

## 8. Assertions personalizadas

### 8.1 `assert()` con mensajes descriptivos

```dart
class LoginUseCase {
  final UserRepository repository;
  
  LoginUseCase({required this.repository});
  
  Future<User> call(LoginParams params) {
    // Assertions solo se ejecutan en debug mode
    assert(
      params.email.isNotEmpty,
      'Email no puede estar vacío. Verificar que el formulario valide antes de llamar al UseCase.',
    );
    assert(
      params.password.length >= 8,
      'Password debe tener al menos 8 caracteres. Recibido: ${params.password.length}',
    );
    
    return repository.login(params);
  }
}
```

### 8.2 Assertions con lógica compleja

```dart
class CartState {
  final List<CartItem> items;
  
  CartState({required this.items}) {
    assert(
      items.every((item) => item.quantity > 0),
      'Todos los items deben tener cantidad > 0. '
      'Items con cantidad inválida: ${items.where((i) => i.quantity <= 0).map((i) => i.id)}',
    );
    assert(
      items.length <= 50,
      'Carrito no puede tener más de 50 items únicos. Recibido: ${items.length}',
    );
  }
}
```

### 8.3 Assertions en development pero no en producción

```dart
// Los assert() solo se ejecutan en debug mode
// En profile/release, se ignoran completamente
assert(
  () {
    // Tu lógica de validación aquí
    _validateState();
    return true;
  }(),
  'Descripción del error',
);
```

---

## 9. Resumen: tabla de todas las herramientas programáticas

| Herramienta | Qué hace | Cuándo usarla |
|---|---|---|
| `debugPrint()` | Logging con throttling | Siempre (en vez de `print()`) |
| `debugDumpWidgetTree()` | Imprime árbol de widgets | No entiendes la estructura de UI |
| `debugDumpRenderTree()` | Imprime árbol de render | Problemas de layout/tamaño |
| `debugDumpLayerTree()` | Imprime capas GPU | Artefactos visuales |
| `debugDumpSemanticsTree()` | Imprime árbol de accesibilidad | Screen readers |
| `debugPaintSizeEnabled` | Overlay de bounds | Constraints inesperados |
| `debugPaintLayerBordersEnabled` | Bordes de capas | Parpadeos, regiones |
| `debugPaintPointersEnabled` | Área de touch | Widgets no responden a taps |
| `debugPaintBaselinesEnabled` | Baselines de texto | Alineación de texto |
| `debugPrintRebuildDirtyWidgets` | Log cada rebuild | Performance, rebuilds innecesarios |
| `debugPrintLayouts` | Log cada layout | Widgets con tamaño inesperado |
| `debugProfilePaintsEnabled` | Log cada repaint | Jank visual |
| `showPerformanceOverlay` | Overlay de frames | Medir performance en runtime |
| `FlutterError.onError` | Capturar errores Flutter | Crash reporting personalizado |
| `ErrorWidget.builder` | Pantalla de error custom | UI de error en producción |
| `debugCheckElevationsEnabled` | Detectar sombras | Problemas de elevación |
| `assert()` con mensajes | Validaciones debug-only | Invariantes en development |

---

## 10. Patrón recomendado: debug flags condicionales

```dart
import 'package:flutter/foundation.dart';
import 'package:flutter/rendering.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Solo en debug mode: activar herramientas de debugging
  assert(() {
    debugPaintSizeEnabled = false;       // Cambiar a true cuando necesites
    debugPrintRebuildDirtyWidgets = false; // Cambiar a true cuando necesites
    debugPaintLayerBordersEnabled = false;
    debugProfilePaintsEnabled = false;
    return true;
  }());
  
  // En todos los modos: manejo de errores personalizado
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    if (kReleaseMode) {
      // Reportar a servicio de crashes
    }
  };
  
  ErrorWidget.builder = (details) {
    return const Material(
      child: Center(child: Text('Error inesperado')),
    );
  };
  
  runApp(MyApp());
}
```

> **Consejo:** No actives todos los flags al mismo tiempo. Activa uno a la vez según el tipo de bug que estés investigando. Los flags se pueden togglear en caliente sin reiniciar la app (solo cambia el valor y haz hot reload).

---

## Resumen

| Concepto | Descripción |
|---|---|
| `debugPrint()` | Logging seguro con throttling (no filtra en release) |
| Dump methods | Ver árboles de widgets, render, layers, semantics |
| Debug flags | Overlays visuales para bounds, touch, rebuilds |
| `FlutterError.onError` | Capturar y personalizar errores de Flutter |
| `assert()` | Validaciones que solo corren en debug mode |
| Patrón condicional | Activar flags con `assert(() { ... }())` |

---

## 📚 Referencias

- [Flutter | Debug from code](https://docs.flutter.dev/testing/debugging#debugging-from-code) — Documentación oficial de debugging programático
- [Flutter | Common errors](https://docs.flutter.dev/testing/common-errors) — Errores comunes y sus soluciones
- [Flutter | Debug flags](https://api.flutter.dev/flutter/rendering/rendering-library.html) — Todos los flags de rendering

---

> 📖 **Anterior:** [27-mentalidad-debugging.md](./27-mentalidad-debugging.md) — Mentalidad de debugging: piensa como un debugger
> 📖 **Siguiente:** [01-fundamentos-debugging.md](./01-fundamentos-debugging.md) — Fundamentos del debugging en VS Code
