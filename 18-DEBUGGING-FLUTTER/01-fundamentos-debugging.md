# 01 — Fundamentos del Debugging en VS Code

> Por qué el debugging es una habilidad clave en Flutter, cómo funcionan los modos de compilación y qué herramientas te ofrece VS Code.

---

## 0. Mentalidad del debugger

> Antes de aprender herramientas, establece la mentalidad. Lee [27-mentalidad-debugging.md](./27-mentalidad-debugging.md) para entender la filosofía: "No adivines, observa".

Los 3 principios clave:

1. **No supongas, verifica** — Usa breakpoints y datos, no intuición
2. **Reduce el espacio de búsqueda** — Binary search debugging (a la mitad en cada paso)
3. **Reproduce antes de arreglar** — Si no puedes reproducir, no puedes arreglar

Y la regla anti-dependencia-AI:

> **"¿Podrías explicarle a otro developer exactamente qué está pasando?"** Si la respuesta es NO, no entiendes el bug todavía. Usa el debugger para entenderlo antes de pedir ayuda.

---

## 1. ¿Qué es el debugging?

Debugging es el proceso de **encontrar y corregir errores** en tu código. Pero no se trata solo de cazar bugs: es entender el comportamiento de tu aplicación en tiempo real, inspeccionar el estado del programa en cualquier momento y razonar sobre por qué algo no funciona como esperabas.

El debugger es tu lupa para ver dentro de la máquina. Sin él, estás adivinando. Con él, estás **observando**.

---

## 2. ¿Por qué el debugging en Flutter es especial?

Flutter tiene particularidades que lo hacen diferente de otros frameworks:

1. **Build methods**: se ejecutan muchas veces, no sabes cuándo
2. **State management (BLoC/Cubit)**: el estado vive en objetos que se crean/destruyen
3. **Hot Reload**: cambias código sin reiniciar, pero el estado persiste
4. **Two threads**: UI thread (Dart) y Raster thread (GPU)
5. **Widgets son inmutables**: se recrean en cada rebuild

Esto significa que necesitas herramientas específicas para entender qué está pasando.

---

## 3. Modos de compilación en Flutter

Flutter tiene 3 modos de compilación, y cada uno impacta el debugging:

### 3.1 Debug Mode

```
flutter run
```

- **Para qué**: desarrollo diario
- **Optimizaciones**: NINGUNA (todo es lento)
- **Assertions**: HABILITADOS (validan constraints e invariantes)
- **Hot Reload**: SÍ funciona
- **Debugging**: COMPLETO (breakpoints, stepping, inspección)
- **Rendimiento**: NO REPRESENTATIVO (no medir performance aquí)

### 3.2 Profile Mode

```
flutter run --profile
```

- **Para qué**: medir performance real
- **Optimizaciones**: MAYORÍA habilitadas
- **Assertions**: DESHABILITADOS
- **Hot Reload**: NO funciona (Hot Restart sí)
- **Debugging**: PARCIAL (breakpoints sí, pero más lento)
- **Rendimiento**: REPRESENTATIVO (medir aquí)

### 3.3 Release Mode

```
flutter run --release
flutter build apk
```

- **Para qué**: producción
- **Optimizaciones**: TODAS habilitadas
- **Assertions**: DESHABILITADOS
- **Hot Reload**: NO funciona
- **Debugging**: NO DISPONIBLE
- **Rendimiento**: ÓPTIMO

> **Regla de oro**: Para debugging usa `debug`. Para medir performance usa `profile`. Nunca midas performance en `debug`.

---

## 4. Interfaz del debugger de VS Code

Cuando presionas F5 y empieza una sesión de debugging, VS Code muestra 5 componentes principales:

```
┌─────────────────────────────────────────────────────────┐
│  1. Debug Toolbar (barra flotante)                      │
│  [▶ Continue] [⏭ Step Over] [↓ Step Into] [↑ Step Out] │
├──────────────────────┬──────────────────────────────────┤
│                      │                                  │
│  2. Run and Debug    │  Editor de código                │
│     View (sidebar)   │  (con breakpoints marcados)      │
│                      │                                  │
│  - CALL STACK        │                                  │
│  - VARIABLES         │                                  │
│  - WATCH             │                                  │
│  - BREAKPOINTS       │                                  │
│                      │                                  │
├──────────────────────┴──────────────────────────────────┤
│  3. Debug Console (panel inferior)                      │
│  > Output del debugger, expresiones evaluadas           │
├─────────────────────────────────────────────────────────┤
│  4. Status Bar (barra de estado - color naranja)        │
│  [Debug: flutter (debug)] ← indica sesión activa        │
└─────────────────────────────────────────────────────────┘
```

### 4.1 Componentes detallados

#### Debug Toolbar

Botones flotantes para controlar la sesión:

| Botón | Atajo | Qué hace |
|---|---|---|
| Continue / Pause | `F5` | Reanuda hasta el próximo breakpoint, o pausa |
| Step Over | `F10` | Ejecuta la siguiente línea sin entrar en funciones |
| Step Into | `F11` | Entra en la siguiente función |
| Step Out | `Shift+F11` | Sale de la función actual |
| Restart | `Ctrl+Shift+F5` | Reinicia la sesión de debugging |
| Stop | `Shift+F5` | Detiene la sesión |

#### Run and Debug View (Sidebar)

Panel izquierdo con 4 secciones:

- **CALL STACK**: Muestra la pila de llamadas. Cuando hay multi-target, cada sesión es un top-level element.
- **VARIABLES**: Variables locales y del scope actual. Se actualizan con el stack frame seleccionado.
- **WATCH**: Expresiones que defines para monitorear. Se evalúan en cada pausa.
- **BREAKPOINTS**: Lista de todos los breakpoints. Puedes habilitar/deshabilitar/eliminar.

#### Debug Console

Panel inferior donde:
- Se muestra stdout/stderr del debugger
- Puedes evaluar expresiones Dart en tiempo real
- Funciona como REPL (Read-Eval-Print Loop)
- Soporta autocompletado y sintaxis

#### Status Bar

Cuando hay una sesión activa, la barra de estado cambia a **color naranja** (o el color accent de tu tema). Muestra el nombre de la configuración de debug activa.

---

## 5. Flujo completo de debugging

```
1. Abrir proyecto en VS Code
   └── Asegurarse de que la extensión Flutter está instalada

2. Configurar launch.json (si es necesario)
   └── Ver archivo 02-configuracion-launch-json.md

3. Poner breakpoints
   └── Click en el gutter (margen izquierdo) o F9

4. Iniciar sesión
   └── F5 o Run > Start Debugging

5. Seleccionar dispositivo
   └── Emulador, simulador o dispositivo físico

6. Ejecutar la acción que activa el bug
   └── La app se pausa en el breakpoint

7. Inspeccionar
   └── Variables, Watch, Call Stack, Debug Console

8. Navegar por el código
   └── Step Into, Step Over, Step Out

9. Encontrar el problema
   └── Modificar código si es necesario

10. Continuar ejecución
    └── F5 para continuar, Shift+F5 para detener
```

---

## 6. Ejemplo: primer breakpoint

Imagina que tienes un BLoC de login:

```dart
// lib/presentation/bloc/login/login_bloc.dart
class LoginBloc extends Bloc<LoginEvent, LoginState> {
  final LoginUseCase loginUseCase;

  LoginBloc({required this.loginUseCase}) : super(LoginInitial()) {
    on<LoginSubmitted>(_onLoginSubmitted);
  }

  Future<void> _onLoginSubmitted(
    LoginSubmitted event,
    Emitter<LoginState> emit,
  ) async {
    emit(LoginLoading());  // <-- PON AQUÍ UN BREAKPOINT

    final result = await loginUseCase(
      LoginParams(
        email: event.email,
        password: event.password,
      ),
    );

    result.fold(
      (failure) => emit(LoginError(failure.message)),  // <-- Y AQUÍ
      (user) => emit(LoginSuccess(user)),               // <-- Y AQUÍ
    );
  }
}
```

**Pasos:**

1. Haz click en el gutter de la línea del `emit(LoginLoading())` (aparece un círculo rojo)
2. Presiona F5
3. La app compila y se abre en el emulador
4. Escribe email y password, presiona "Login"
5. **La app se pausa** en esa línea
6. En el panel VARIABLES verás `event.email` y `event.password`
7. Presiona F10 para avanzar línea por línea
8. Observa cómo el estado cambia de `LoginInitial` a `LoginLoading`

---

## 7. Ejemplo: Debug Console

Durante una sesión, puedes abrir la Debug Console (`Ctrl+Shift+Y`) y escribir expresiones:

```dart
// En la Debug Console, puedes evaluar:
> event.email
"usuario@ejemplo.com"

> state.runtimeType
"LoginLoading"

> await loginUseCase(LoginParams(email: "test@test.com", password: "123"))
// Esto ejecuta el UseCase en tiempo real y te muestra el resultado
```

Esto es extremadamente útil para:
- Verificar que un objeto tiene los valores esperados
- Ejecutar código sin modificar el archivo
- Probar comportamientos "qué pasaría si..."

---

## 8. Debugging con Hot Reload vs Hot Restart

### 8.1 Hot Reload (`r` en la terminal o Debug Console)

- **Qué hace**: Reinyecta código Dart compilado sin reiniciar la app
- **Estado**: SE MANTIENE (BLoC, variables globales, etc.)
- **Breakpoints**: SE MANTIENEN
- **Uso**: Cambios visuales rápidos (colores, texto, layout)

### 8.2 Hot Restart (`R` en la terminal o `Ctrl+Shift+F5`)

- **Qué hace**: Reinicia completamente la app
- **Estado**: SE PIERDE todo
- **Breakpoints**: SE LIMPIAN (hay que volver a ponerlos)
- **Uso**: Cambios en initializers, `main()`, rutas, `initState`

> **Consejo**: Si tu bug depende del estado inicial de la app, usa Hot Restart. Si es un cambio visual, usa Hot Reload.

> **Nota sobre atajos**: `Ctrl+Shift+F5` en VS Code ejecuta el comando **Debug: Restart** (que en Flutter equivale al hot restart). El **hot reload** no tiene atajo por defecto: se dispara con `r` en la terminal o Debug Console, o con el botón **Hot Reload** del Debug Toolbar.

---

## Resumen

| Concepto | Descripción |
|---|---|
| Debug Mode | Compilación sin optimizaciones, debugging completo |
| Profile Mode | Compilación optimizada, para medir performance |
| Release Mode | Producción, sin debugging |
| F5 | Iniciar/continuar debugging |
| F9 | Toggle breakpoint |
| F10 | Step over |
| F11 | Step into |
| Shift+F11 | Step out |
| Debug Console | REPL para evaluar expresiones |
| Hot Reload | Cambio sin reiniciar, estado se mantiene |
| Hot Restart | Reinicio completo, estado se pierde |

---

## 📚 Referencias

- [Flutter | Debugging tools](https://docs.flutter.dev/tools/debugging) — Debugging desde código y herramientas de Flutter
- [Flutter | VS Code](https://docs.flutter.dev/tools/vs-code) — Guía oficial de VS Code para Flutter
- [Flutter | Hot reload](https://docs.flutter.dev/tools/hot-reload) — Qué se puede y no se puede hot reload
- [Flutter | Build modes](https://docs.flutter.dev/testing/build-modes) — Debug, Profile y Release en detalle
- [VS Code | Debugging](https://code.visualstudio.com/docs/debugtest/debugging) — Conceptos generales del debugger
- [27-mentalidad-debugging.md](./27-mentalidad-debugging.md) — Filosofía de debugging: piensa como un debugger
- [28-debugging-programatico-flutter.md](./28-debugging-programatico-flutter.md) — Herramientas de debug desde código

---

> 📖 **Siguiente:** [02-configuracion-launch-json.md](./02-configuracion-launch-json.md) — Cómo configurar `launch.json` para lanzar y adjuntar sesiones de depuración
