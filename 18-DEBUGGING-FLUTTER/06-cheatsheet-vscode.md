# 06 — Cheatsheet: Debugging en VS Code

> Referencia rápida de atajos, expresiones, plantillas de `launch.json` y errores comunes al depurar Flutter en VS Code.

---

## 1. Atajos de teclado esenciales

| Atajo | Acción | Descripción |
|---|---|---|
| `F5` | Start / Continue | Iniciar depuración o continuar hasta el próximo breakpoint |
| `Ctrl+F5` | Run Without Debugging | Ejecutar sin pausar (sin sesión de debug) |
| `Shift+F5` | Stop | Detener depuración |
| `Ctrl+Shift+F5` | Restart | Reiniciar depuración (en Flutter equivale al hot restart) |
| `F10` | Step Over | Ejecutar siguiente línea sin entrar en funciones |
| `F11` | Step Into | Entrar dentro de función/método |
| `Shift+F11` | Step Out | Salir de la función actual |
| `F9` | Toggle Breakpoint | Agregar/quitar breakpoint en la línea actual |
| `Ctrl+Shift+F9` | Inline Breakpoint | Pausar en un statement específico de la línea (Win/Linux; en macOS: `Shift+F9`) |

> **Nota**: "Run to Cursor", "Conditional Breakpoint" y "Disable All Breakpoints" no tienen atajo por defecto: se acceden con click derecho o desde la Command Palette. Puedes asignarles atajos en el editor de Keyboard Shortcuts.

### 1.1 Navegación de paneles

| Atajo | Panel |
|---|---|
| `Ctrl+Shift+D` | Run and Debug (sidebar) |
| `Ctrl+Shift+Y` | Debug Console |
| `Ctrl+Shift+E` | Explorer |
| `Ctrl+Shift+F` | Search |
| `Ctrl+Shift+P` | Command Palette |

---

## 2. Panel VARIABLES

| Sección | Qué contiene |
|---|---|
| **Local** | Variables declaradas en la función actual |
| **Closure** | Variables capturadas por closures |
| **Global** | Variables globales del archivo |
| **Fields** | Campos de la instancia actual (en un método) |

### 2.1 Acciones útiles

| Acción | Cómo |
|---|---|
| Expandir objeto | Click en la flecha |
| Ver valor | Hover sobre la variable |
| Copiar valor | Click derecho > Copy Value |
| Copiar como expresión | Click derecho > Copy as Expression |
| Modificar valor | Click derecho > Set Value |
| Filtrar | `Ctrl+Alt+F` (Win/Linux) / `Alt+Cmd+F` (macOS) |

### 2.2 CALL STACK

| Elemento | Significado |
|---|---|
| ▶ Frame actual | Punto de ejecución donde está pausado |
| ⏸ Frame pausado | Pausado en un breakpoint |
| 🧵 Hilo | Hilo de ejecución (en Dart: isolate) |
| 📦 Isolate | Aislamiento de memoria con su propio stack |

---

## 3. Sintaxis de expresiones (WATCH / Debug Console)

### 3.1 Acceso a propiedades

```
variable.property
variable.property.subProperty
```

### 3.2 Índices y colecciones

```
myList[0]
myMap["key"]
mySet.first
```

### 3.3 Métodos de inspección

```
myVariable.toString()
myVariable.runtimeType
myList.length
myList.isEmpty
myMap.keys.toList()
```

### 3.4 Operaciones condicionales

```
counter > 0 ? "positive" : "negative"
user?.name ?? "Anonymous"
list.isNotEmpty
```

### 3.5 Cuidado con side effects

```
// Llamar métodos puede ejecutar lógica y cambiar estado
user.isValid()
controller.text
```

---

## 4. Tipos de breakpoints — Referencia rápida

| Tipo | Icono | Cómo crearlo | Cuándo usarlo |
|---|---|---|---|
| Línea | 🔴 | Click gutter o F9 | Punto de parada básico |
| Condicional (Expression) | 🔴+📝 | Click derecho → Conditional | Cuando se cumple una expresión |
| Hit Count | 🔴+🔢 | Click derecho → Conditional → Hit Count | Cada N ocurrencias |
| Logpoint (Log Message) | 🟢 diamante | Click derecho → Add Logpoint | Logging sin pausar |
| Inline | 🔴 pequeño | `Ctrl+Shift+F9` | En un statement específico de la línea |
| Function | 🔵 | Panel BREAKPOINTS → `+` | Al entrar a una función por nombre |
| Data | 🔷 | VARIABLES → click derecho | Cuando cambia un valor (soporte limitado) |

---

## 5. `launch.json` — Plantillas comunes

### 5.1 Debug Flutter básico

```json
{
  "name": "Flutter Debug",
  "type": "dart",
  "request": "launch",
  "program": "lib/main.dart"
}
```

### 5.2 Flutter con `--dart-define`

```json
{
  "name": "Flutter + Dart Define",
  "type": "dart",
  "request": "launch",
  "program": "lib/main.dart",
  "dartDefine": ["ENV=dev"]
}
```

### 5.3 Flutter test

```json
{
  "name": "Debug Test",
  "type": "dart",
  "request": "launch",
  "program": "test/widget_test.dart",
  "args": ["--plain-name", "test name"]
}
```

### 5.4 Attach a un proceso existente

```json
{
  "name": "Attach",
  "type": "dart",
  "request": "attach",
  "program": "lib/main.dart"
}
```

> La extensión descubre automáticamente la app en ejecución. No hace falta especificar una URI del VM Service.

### 5.5 Multiple targets (compound)

```json
{
  "compounds": [
    {
      "name": "App + Worker",
      "configurations": ["Flutter App", "Dart Worker"]
    }
  ]
}
```

---

## 6. Debug Console — Comandos útiles

### 6.1 Inspección directa

```dart
// Ver tipo de variable
myVar.runtimeType

// Ver contenido de lista
myList → [1, 2, 3, 4, 5]

// Ver contenido de mapa
myMap → { "key": "value", "count": 42 }
```

### 6.2 Expresiones evaluables

```dart
// Operaciones matemáticas
counter + 1
items.length * 2

// Strings
"Count: $counter"
user.name.toUpperCase()

// Condicionales
isActive && isVerified ? "Active User" : "Pending"

// Colecciones
users.where((u) => u.age > 18).toList()
products.map((p) => p.name).join(", ")
```

### 6.3 Llamadas con side effects (usar con cuidado)

```dart
// Imprimir valor (se ve en la consola)
print("DEBUG: $variable")

// Llamar un getter
controller.text
```

---

## 7. Hot Reload durante debugging

| Acción | Cómo | Efecto |
|---|---|---|
| Hot Reload | `r` en terminal/Debug Console o botón 🔄 del toolbar | Mantiene estado, actualiza UI |
| Hot Restart | `R` en terminal o `Ctrl+Shift+F5` (Debug: Restart) | Resetea estado completo |
| Run without debugging | `Ctrl+F5` | Ejecuta sin sesión de debug |

### 7.1 Hot Reload preserva:

- Estado actual de BLoC/Cubit/Provider
- Posición de scroll
- Contenido de campos de texto
- Resultado de cálculos previos

### 7.2 Hot Restart resetea:

- Todos los estados a valores iniciales
- Conexiones de streams
- Datos en memoria
- Controllers (dispose + recrear)

> **Importante**: `Ctrl+F5` es "Run Without Debugging", NO hot reload. El hot reload no tiene atajo por defecto: se dispara con `r` o desde el toolbar.

---

## 8. Errores comunes y soluciones

### 8.1 "Could not find a Flutter app to attach to"

```
Causa: No hay ninguna app en ejecución con VM service activo
Solución: Lanza la app con `flutter run` (modo debug) antes de hacer attach
```

### 8.2 "Application finished"

```
Causa: La app terminó o no está en modo debug
Solución: Verifica que estés en modo --debug, no --release
```

### 8.3 "Function breakpoints not working"

```
Causa: El debugger de Dart no resuelve el nombre de la función
Solución: Usa un breakpoint de línea en la primera línea de la función
```

### 8.4 "Variables show <optimized out>"

```
Causa: El compilador optimizó la variable (ocurre en profile/release)
Solución: Usa --debug, o agrega un print()/logpoint antes del breakpoint
```

---

## 9. Command Palette (`Ctrl+Shift+P`) — Debug

| Comando | Acción |
|---|---|
| `Debug: Start Debugging` | Iniciar (F5) |
| `Debug: Stop Debugging` | Detener (Shift+F5) |
| `Debug: Restart Debugging` | Reiniciar (Ctrl+Shift+F5) |
| `Debug: Open Debug Console` | Abrir Debug Console |
| `Debug: Toggle Breakpoint` | Breakpoint en el cursor |
| `Debug: Remove All Breakpoints` | Limpiar todos |
| `Debug: Disable All Breakpoints` | Deshabilitar todos |
| `Flutter: Hot Reload` | Hot reload |
| `Flutter: Hot Restart` | Hot restart |
| `Dart: Open DevTools Inspector` | Abrir el Flutter Inspector en DevTools |

---

## 10. Variable Substitution — Referencia rápida

| Variable | Ejemplo de resolución |
|---|---|
| `${workspaceFolder}` | `/home/user/mi-app` |
| `${file}` | `lib/features/login/presentation/pages/login_page.dart` |
| `${fileBasename}` | `login_page.dart` |
| `${fileDirname}` | `lib/features/login/presentation/pages` |
| `${env:HOME}` | `/home/user` |
| `${env:PATH}` | `/usr/bin:/usr/local/bin:...` |

Uso: `"program": "${file}"` → lanza el archivo activo en el editor.

---

## 11. Platform-specific & Presentation — Referencia rápida

### Platform-specific

```json
"windows": {"program": "lib/main_windows.dart"},
"linux": {"program": "lib/main_linux.dart"},
"osx": {"program": "lib/main_macos.dart"}
```

### Presentation

```json
"presentation": {"order": 1, "group": "Flutter", "hidden": false}
```

- `order`: posición en el dropdown (menor = primero)
- `group`: agrupar en submenu
- `hidden`: ocultar del dropdown

---

## 12. Flujo de debugging típico

```
1. F5 (Start)
     ↓
2. Breakpoint alcanzado
     ↓
3. Inspeccionar VARIABLES
     ↓
4. Agregar WATCH si es necesario
     ↓
5. F10 (Step Over) para recorrer código
     ↓
6. F11 (Step Into) para ver dentro de una función
     ↓
7. Debug Console para evaluar expresiones
     ↓
8. F5 (Resume) para continuar hasta el siguiente BP
     ↓
9. Repetir hasta encontrar el bug
     ↓
10. Fix + Hot Restart
```

---

## Resumen

- **Atajos clave**: `F5` (start/continue), `Ctrl+F5` (sin debug), `Shift+F5` (stop), `F9` (toggle BP), `F10` (step over), `F11` (step into), `Ctrl+Shift+F5` (hot restart).
- **Templates**: `flutter`, `dart`, `flutter test` y `Flutter Attach` cubren el 90% de los casos.
- **Debug Console**: evalúa expresiones y llama funciones en vivo; `Set Value` modifica variables en caliente.
- **Hot Reload** preserva estado; **Hot Restart** lo resetea (widgets `StatefulWidget` e instancias de repositorios).
- **Errores típicos**: "Could not find a Flutter app to attach to" (codebase incorrecto), "Variables show <optimized out>" (modo profile, no debug).

---

## 📚 Referencias

- [VS Code | Default keyboard shortcuts](https://code.visualstudio.com/docs/reference/default-keybindings) — Atajos por defecto de VS Code
- [VS Code | Debugging](https://code.visualstudio.com/docs/editor/debugging) — Conceptos del debugger
- [Dart-Code | Debugging](https://dartcode.org/docs/debugging/) — Detalles del debugger Dart/Flutter
- [Flutter | VS Code](https://docs.flutter.dev/tools/vs-code) — Guía oficial de VS Code para Flutter

---

> 📖 **Siguiente:** [07-practicas-vscode.md](./07-practicas-vscode.md) — Prácticas y ejercicios de debugging con VS Code
