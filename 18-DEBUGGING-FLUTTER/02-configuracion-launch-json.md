# 02 — Configuración de `launch.json` para Flutter

> Cómo lanzar, adjuntar y combinar sesiones de depuración de Flutter desde VS Code con `launch.json`.

---

## 1. ¿Qué es `launch.json`?

`launch.json` es el archivo de configuración que le dice a VS Code **cómo ejecutar y debuggear** tu aplicación. Vive en `.vscode/launch.json` y define:

- Qué comando ejecutar (`flutter run`, `flutter run --profile`, etc.)
- Qué plataforma usar (Android, iOS, Web, Desktop)
- Qué argumentos pasar a `flutter run` y al programa
- A qué proceso adjuntarse (attach)

---

## 2. Estructura básica

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart"
    }
  ],
  "compounds": [
    {
      "name": "App + Worker",
      "configurations": ["Flutter (Debug)", "Worker"]
    }
  ]
}
```

- `configurations`: lista de configuraciones individuales
- `compounds`: combinaciones de configuraciones que se lanzan juntas

---

## 3. Configuración mínima para Flutter

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart"
    }
  ]
}
```

Con esto, presionando F5 se ejecuta tu app en debug mode. Para crear el archivo desde cero: panel **Run and Debug** → **create a launch.json file**.

---

## 4. Propiedades importantes

### 4.1 `name`

Nombre que aparece en el dropdown de debugging. Usa nombres descriptivos.

### 4.2 `type`

Siempre `"dart"` para Flutter (usa la extensión Dart-Code).

### 4.3 `request`

- `"launch"`: lanza una nueva sesión (`flutter run`)
- `"attach"`: se adjunta a un proceso ya en ejecución

### 4.4 `program`

Punto de entrada. Por defecto `"lib/main.dart"`.

### 4.5 `flutterMode`

- `"debug"` (default)
- `"profile"`
- `"release"` (sin debugging; útil solo para verificar builds)

### 4.6 `args`

Argumentos que recibe el **programa** que se ejecuta:

```json
"args": ["--my-program-flag"]
```

En tests, `args` son argumentos del test runner (`--name`, `--plain-name`, etc.).

### 4.7 `toolArgs`

Argumentos que se pasan a la herramienta `flutter run`:

```json
"toolArgs": ["-d", "emulator-5554", "--verbose"]
```

### 4.8 `dartDefine`

Arreglo de pares `key=value` que se convierten en `--dart-define` para `flutter run`:

```json
"dartDefine": ["SUPABASE_URL=http://localhost:54321", "ENV=dev"]
```

Equivalente en `toolArgs`: `"toolArgs": ["--dart-define=ENV=dev"]`. Prefiere `dartDefine` por legibilidad.

### 4.9 `deviceId`

Fuerza un dispositivo concreto (sobreescribe el selector de F5):

```json
"deviceId": "emulator-5554"
```

### 4.10 `env`

Variables de entorno del proceso:

```json
"env": {
  "SUPABASE_URL": "http://localhost:54321"
}
```

---

## 5. Configuración multi-plataforma

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart"
    },
    {
      "name": "Flutter (Profile)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "profile"
    },
    {
      "name": "Android (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "debug",
      "toolArgs": ["-d", "android"]
    },
    {
      "name": "iOS (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "debug",
      "toolArgs": ["-d", "ios"]
    },
    {
      "name": "Chrome (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "debug",
      "toolArgs": ["-d", "chrome"]
    },
    {
      "name": "macOS (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "debug",
      "toolArgs": ["-d", "macos"]
    },
    {
      "name": "Linux (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "debug",
      "toolArgs": ["-d", "linux"]
    },
    {
      "name": "Windows (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "debug",
      "toolArgs": ["-d", "windows"]
    }
  ]
}
```

---

## 6. Configuraciones con Supabase

Para apps con Supabase es útil tener configuraciones por ambiente:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "App (Dev - Local Supabase)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main_development.dart",
      "dartDefine": ["SUPABASE_URL=http://localhost:54321"]
    },
    {
      "name": "App (Staging)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main_staging.dart",
      "dartDefine": ["SUPABASE_URL=https://staging.supabase.co"]
    },
    {
      "name": "App (Production)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main_production.dart",
      "dartDefine": ["SUPABASE_URL=https://prod.supabase.co"]
    }
  ]
}
```

> **Seguridad**: nunca pongas claves secretas (p. ej. la `anon key` de producción) directamente en `launch.json`. Úsalas vía `String.fromEnvironment` desde un `.env` o desde las variables de entorno del sistema.

---

## 7. Configuración con Flutter Flavors

Si usas flavors (development, staging, production):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Development",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "toolArgs": ["--flavor", "development", "-t", "lib/main_development.dart"]
    },
    {
      "name": "Production",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "toolArgs": ["--flavor", "production", "-t", "lib/main_production.dart"],
      "flutterMode": "profile"
    }
  ]
}
```

`--flavor` y `-t` son banderas de `flutter run`, por eso van en `toolArgs`.

---

## 8. Attach a un proceso en ejecución

Hay dos formas de adjuntarte a una app que ya corre.

### 8.1 Desde VS Code

Configuración `attach`: la extensión **descubre automáticamente** la app en ejecución (no hace falta una URI del VM service):

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to running app",
      "type": "dart",
      "request": "attach",
      "program": "lib/main.dart"
    }
  ]
}
```

Si hay varios procesos y quieres forzar uno, usa `deviceId` (o el selector de la barra de estado al iniciar el attach).

### 8.2 Desde la terminal

```bash
# Terminal 1: lanza la app
flutter run

# Terminal 2: se adjunta a la app en ejecución
flutter attach
```

`flutter attach` descubre la app por sí solo. Opciones útiles:

```bash
# Filtrar por puerto del VM service
flutter attach --device-vmservice-port 8181

# Evitar el prompt si hay varios procesos (Android: package name / iOS: bundle id)
flutter attach --app-id com.example.miapp
```

> **Nota**: la app debe estar corriendo en modo `debug` o `profile` para poder adjuntarse. En `release` no hay VM service al que conectar.

---

## 9. Configuración para testing

Para ejecutar tests con debugging:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Test (all)",
      "type": "dart",
      "request": "launch",
      "program": "test/widget_test.dart"
    },
    {
      "name": "Test (specific)",
      "type": "dart",
      "request": "launch",
      "program": "test/features/auth/login_test.dart",
      "args": ["--name", "login exitoso"]
    }
  ]
}
```

---

## 10. Compounds: ejecutar múltiples configuraciones

Los compounds permiten lanzar varias configuraciones simultáneamente:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "App Flutter",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart"
    },
    {
      "name": "Worker Dart",
      "type": "dart",
      "request": "launch",
      "program": "bin/worker.dart"
    }
  ],
  "compounds": [
    {
      "name": "App + Worker",
      "configurations": ["App Flutter", "Worker Dart"],
      "stopAll": true,
      "preLaunchTask": ""
    }
  ]
}
```

- `stopAll`: detiene todas las configuraciones al terminar una
- `preLaunchTask`: ejecuta una task de VS Code (de `.vscode/tasks.json`) antes de lanzar

---

## 11. Variable Substitution

`launch.json` soporta variables que se resuelven en tiempo de ejecución:

### 11.1 Variables comunes

| Variable | Qué resuelve | Ejemplo |
|---|---|---|
| `${workspaceFolder}` | Raíz del workspace | `/home/user/mi-app` |
| `${file}` | Archivo activo en el editor | `lib/main.dart` |
| `${fileBasename}` | Solo el nombre del archivo | `main.dart` |
| `${fileDirname}` | Directorio del archivo activo | `lib` |
| `${cwd}` | Directorio de trabajo actual | `/home/user/mi-app` |
| `${env:NAME}` | Variable de entorno | `${env:HOME}` → `/home/user` |
| `${command:ید}` | Resultado de un comando | `${command:flutter}` |

### 11.2 Ejemplo práctico

```json
{
  "name": "Debug current file",
  "type": "dart",
  "request": "launch",
  "program": "${file}"
}
```

Esto lanza siempre el archivo que tengas abierto. Útil para debugging rápido.

---

## 12. Platform-specific properties

Puedes definir propiedades que solo apliquen a una plataforma:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "windows": {
        "program": "lib/main_windows.dart"
      },
      "linux": {
        "program": "lib/main_linux.dart"
      },
      "osx": {
        "program": "lib/main_macos.dart"
      }
    }
  ]
}
```

---

## 13. `presentation` — Ordenar y agrupar configuraciones

Controla cómo aparecen en el dropdown de debugging:

```json
{
  "name": "Flutter (Debug)",
  "type": "dart",
  "request": "launch",
  "program": "lib/main.dart",
  "presentation": {
    "order": 1,
    "group": "Flutter",
    "hidden": false
  }
}
```

| Propiedad | Qué hace |
|---|---|
| `order` | Orden en el dropdown (menor = primero) |
| `group` | Agrupar bajo un submenu |
| `hidden` | Ocultar del dropdown (accesible solo vía Command Palette) |

---

## 14. `preLaunchTask` y `postDebugTask`

Integra con `tasks.json` para ejecutar tareas antes/después de debug:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "preLaunchTask": "flutter pub get",
      "postDebugTask": "flutter analyze"
    }
  ]
}
```

Requiere un `tasks.json` correspondiente:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "flutter pub get",
      "type": "shell",
      "command": "flutter",
      "args": ["pub", "get"],
      "presentation": { "reveal": "silent" }
    },
    {
      "label": "flutter analyze",
      "type": "shell",
      "command": "flutter",
      "args": ["analyze"],
      "presentation": { "reveal": "always" }
    }
  ]
}
```

---

## 15. Mejores prácticas

1. **Nunca guardes secrets en `launch.json`**: usa variables de entorno o `.env`
2. **Usa `flutterMode` en lugar de banderas sueltas**: es más limpio que `toolArgs: ["--profile"]`
3. **Nombra tus configuraciones descriptivamente**: "App (Dev)" no "Debug 1"
4. **Ten una configuración por plataforma**: para no cambiar cada vez
5. **Commit el `launch.json`**: es parte del proyecto, todos lo necesitan
6. **Usa `dartDefine` en vez de `--dart-define` dentro de `toolArgs`**: es más legible

---

## 12. Ejemplo completo de `launch.json` para un proyecto real

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart"
    },
    {
      "name": "Flutter (Profile)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "flutterMode": "profile"
    },
    {
      "name": "Android (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "toolArgs": ["-d", "android"]
    },
    {
      "name": "Chrome (Debug)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main.dart",
      "toolArgs": ["-d", "chrome"]
    },
    {
      "name": "Dev (Local Supabase)",
      "type": "dart",
      "request": "launch",
      "program": "lib/main_development.dart",
      "dartDefine": ["SUPABASE_URL=http://localhost:54321"]
    },
    {
      "name": "Attach to running app",
      "type": "dart",
      "request": "attach",
      "program": "lib/main.dart"
    },
    {
      "name": "Test (all)",
      "type": "dart",
      "request": "launch",
      "program": "test/widget_test.dart"
    }
  ]
}
```

---

## Resumen

| Propiedad | Descripción | Ejemplo |
|---|---|---|
| `name` | Nombre de la config | `"Flutter (Debug)"` |
| `type` | Tipo de debugger | `"dart"` |
| `request` | Launch o attach | `"launch"` |
| `program` | Punto de entrada | `"lib/main.dart"` |
| `flutterMode` | Modo de compilación | `"debug"`, `"profile"`, `"release"` |
| `toolArgs` | Args de `flutter run` | `["-d", "android"]` |
| `dartDefine` | Valores `--dart-define` | `["ENV=dev"]` |
| `deviceId` | Dispositivo forzado | `"emulator-5554"` |
| `env` | Variables de entorno | `{"KEY": "value"}` |
| `args` | Args del programa/test | `["--name", "login"]` |

---

## 📚 Referencias

- [Flutter | VS Code — Run and debug](https://docs.flutter.dev/tools/vs-code) — Documentación oficial de debugging en VS Code
- [VS Code | Debugging](https://code.visualstudio.com/docs/debugtest/debugging) — Conceptos de launch.json y configuraciones
- [VS Code | Debugging configuration](https://code.visualstudio.com/docs/debugtest/debugging-configuration) — Variable substitution, platform-specific, presentation
- [VS Code | Tasks](https://code.visualstudio.com/docs/editor/tasks) — Para `preLaunchTask` y `postDebugTask`
- [Dart-Code | Debugging](https://dartcode.org/docs/debugging/) — Guía oficial de la extensión Dart-Code

---

> 📖 **Siguiente:** [03-breakpoints-avanzados.md](./03-breakpoints-avanzados.md) — Todos los tipos de breakpoints disponibles en VS Code
