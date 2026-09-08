# 29 — Playbook de Debugging Sistemático

> Un paso-a-paso reproducible para diagnosticar CUALQUIER bug sin pedir ayuda a la IA. Imprime este archivo y tenlo al lado de tu monitor.

---

## 1. El playbook en 6 pasos

```
┌─────────────────────────────────────────────────────────┐
│  PASO 1: ENTENDER    → ¿Qué se esperaba vs qué pasó?  │
│  PASO 2: REPRODUCIR  → Steps exactos, siempre falla   │
│  PASO 3: AISLAR      → Binary search con breakpoints    │
│  PASO 4: DIAGNOSTICAR → Datos, call stack, watch        │
│  PASO 5: CORREGIR    → Fix mínimo, un cambio a la vez   │
│  PASO 6: VERIFICAR   → Reproducir + tests + regresión  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Paso 1: ENTENDER

### 2.1 Preguntas obligatorias

Responde estas preguntas **por escrito** (en un comment, un doc, o un notepad):

```
1. ¿Qué behavior esperaba ver?
2. ¿Qué behavior veo en realidad?
3. ¿Cuándo empezó a pasar? (¿antes funcionaba?)
4. ¿Pasa siempre o solo a veces?
5. ¿En qué dispositivo/plataforma?
6. ¿Con qué datos de entrada?
7. ¿Cambie algo recientemente? (git log --oneline -10)
```

### 2.2 Patrón de error: "No sabes qué esperabas"

Si no puedes responder la pregunta #1, **el bug no es técnico, es de requirements**. Habla con tu team/product owner antes de debugging.

### 2.3 Git como herramienta de debugging

```bash
# Ver cambios recientes
git log --oneline -10

# Ver qué cambió en un archivo específico
git log --oneline --follow lib/presentation/bloc/login/login_bloc.dart

# Comparar con una versión que funcionaba
git diff HEAD~5 lib/presentation/bloc/login/login_bloc.dart

# Si sabes cuándo funcionaba, volver temporalmente
git stash  # Guardar cambios actuales
git checkout <commit-hash>  # Ir a la versión que funcionaba
# Probar → si funciona, el bug está en los cambios entre ese commit y HEAD
git checkout -  # Volver al HEAD
git stash pop  # Recuperar cambios
```

---

## 3. Paso 2: REPRODUCIR

### 3.1 Escribir los steps exactos

```
Steps para reproducir:
1. Abrir la app
2. Ir a la pantalla de login
3. Escribir "test@email.com" en el campo de email
4. Escribir "12345678" en el campo de password
5. Presionar el botón "Login"
6. OBSERVAR: la app se queda en loading indefinidamente
```

### 3.2 Si el bug es intermitente

```
¿Cuándo falla?
- ¿Con datos específicos? → Probar con esos datos exactos
- ¿Después de cierto tiempo? → Esperar ese tiempo
- ¿En cierto orden de acciones? → Repetir ese orden exacto
- ¿Con cierto estado previo? → Forzar ese estado primero
```

### 3.3 Si no puedes reproducir

```
Opciones:
1. Agregar logging detallado (debugPrint) en el flujo sospechoso
2. Reproducir en el mismo entorno (mismo dispositivo, misma versión OS)
3. Buscar reports de usuarios: ¿qué tenían en común?
4. Usar DevTools → Logging para ver qué pasa en background
```

---

## 4. Paso 3: AISLAR (Binary Search Debugging)

### 4.1 El principio

En vez de leer 50 archivos buscando el bug, usa **binary search**:

```
Tu flujo tiene 10 pasos. El bug está en alguno.

1. Pon breakpoint en el paso 5 (mitad)
2. Ejecuta hasta el breakpoint
3. ¿El estado es correcto hasta aquí? → Bug está entre 6-10
4. ¿El estado ya es incorrecto? → Bug está entre 1-5
5. Repite con la mitad correcta
6. En 3-4 iteraciones encuentras el paso exacto
```

### 4.2 Ejemplo práctico: BLoC de login

```
Flujo: LoginSubmitted → validate → LoginUseCase → repository → api → emit(result)

Breakpoint 1: LoginSubmitted (línea 10) → event.email = "test@test.com" ✓
Breakpoint 2: validate (línea 15) → datos válidos ✓
Breakpoint 3: LoginUseCase (línea 20) → params correctos ✓
Breakpoint 4: repository.login (línea 25) →Aquí el result es Left(failure) ✗

→ El bug está entre el UseCase y el repository
→ Investigar el repository
```

### 4.3 Qué inspeccionar en cada breakpoint

| Capa | Qué inspeccionar |
|---|---|
| Evento | `event.email`, `event.password`, campos del evento |
| Validate | Resultado de la validación, errores |
| UseCase | `params` que recibe, `result` que retorna |
| Repository | Datos que envía, respuesta que recibe |
| API/Datasource | Request body, response body, status code, headers |
| State | `state.runtimeType`, campos del estado emitido |

---

## 5. Paso 4: DIAGNOSTICAR

### 5.1 Herramientas de diagnóstico en orden

```
1. VARIABLES panel → ¿Qué valor tiene la variable sospechosa?
2. WATCH → Agregar表达式 clave: state.runtimeType, result.runtimeType
3. CALL STACK → ¿Cómo llegué aquí? ¿Qué función me llamó?
4. Debug Console → Evaluar expresiones, probar "what if"
5. debugPrint() → Agregar logging para el siguiente paso
```

### 5.2 Expresiones útiles para WATCH

```dart
// Tipo de estado actual
state.runtimeType

// ¿Es un error?
result.runtimeType == Left<Failure, User>

// Contenido de un mapa
myMap.keys.toList()

// Tamaño de una lista
myList.length

// Primer elemento
myList.first

// ¿Está vacío?
myList.isEmpty

// Valor de un campo específico
(user as User).email
```

### 5.3 Debug Console como laboratorio

```dart
// En la Debug Console, puedes probar cosas SIN modificar el código:

// Crear un objeto y probarlo
final params = LoginParams(email: "test@test.com", password: "12345678");
params.isValid()  // → true/false

// Llamar un método y ver el resultado
await repository.login(params)  // → Left(failure) o Right(user)

// Verificar un controller
controller.text  // → "valor actual"

// Probar una expresión condicional
state is LoginLoading  // → true/false
```

---

## 6. Paso 5: CORREGIR

### 6.1 Reglas del fix

```
1. UN CAMBIO A LA VEZ (no refactores mientras debuggeas)
2. FIX MÍNIMO (lo más pequeño que resuelva el problema)
3. NO AGREGUES FEATURES (eso es para después)
4. COMMIT DESPUÉS DEL FIX (para poder volver si algo se rompe)
```

### 6.2 Tipos de fix comunes

| Tipo de bug | Fix típico |
|---|---|
| Null safety | Agregar `?` o `?? defaultValue` |
| Estado no se actualiza | Verificar `emit()` se ejecuta |
| Widget no se ve | Verificar constraints, `Expanded`/`Flexible` |
| API falla | Verificar headers, URL, body |
| Memory leak | Agregar `cancel()` en `dispose()` |
| Performance | Agregar `const`, `RepaintBoundary`, `ListView.builder` |

### 6.3 El fix estándar de null safety

```dart
// ❌ Antes (crash)
final userName = user.name;

// ✅ Después (seguro)
final userName = user?.name ?? 'Unknown';
```

---

## 7. Paso 6: VERIFICAR

### 7.1 Checklist de verificación

```
□ 1. Reproducir los steps del Paso 2: ¿el bug ya no aparece?
□ 2. Ejecutar tests existentes: ¿todos pasan?
□ 3. Probar el happy path completo: ¿la app funciona normal?
□ 4. Probar edge cases: ¿qué pasa con datos vacíos, límites, etc.?
□ 5. Probar en otro dispositivo/emulador: ¿especifico de plataforma?
□ 6. Verificar que no hay regressions en funcionalidad relacionada
```

### 7.2 Si algo se rompió

```
1. Revirt el fix: git checkout <archivo>
2. Vuelve al Paso 3 (Aislar)
3. Busca una solución que no rompa lo existente
4. O: agrega un test que cubra el caso que se rompió
```

---

## 8. Matriz de debugging: tipo de bug → herramienta

| Tipo de bug | Primer breakpoint | Qué inspeccionar | Fix típico |
|---|---|---|---|
| **UI se ve mal** | Widget builder o initState | Constraints, tamaño, bounds | `Expanded`, `Flexible`, `SizedBox` |
| **Estado no cambia** | `emit()` del BLoC/Cubit | `state.runtimeType`, params | Verificar `emit()` se ejecuta |
| **API falla** | Llamada HTTP | Request/response, headers | URL, Authorization, body |
| **Navegación falla** | `context.push()`/`go()` | Ruta, parámetros, auth guard | Verificar ruta en GoRouter |
| **Build error** | — | Mensaje de error completo | Tipos, imports, null safety |
| **Performance** | — | Frames > 16ms | `const`, `ListView.builder` |
| **Memory leak** | — | Objetos que crecen | `cancel()`, `dispose()` |
| **Hot reload no funciona** | — | Tipo de cambio | Hot Restart en vez de Reload |

---

## 9. Checklist universal: 15 preguntas ANTES de pedir ayuda

```
□ 1. ¿Puedo reproducir el bug consistentemente?
□ 2. ¿Sé exactamente qué pasos lo provocan?
□ 3. ¿En qué archivo/functión ocurre?
□ 4. ¿Qué valor tiene la variable sospechosa en el momento del error?
□ 5. ¿Qué dice el call stack?
□ 6. ¿Qué cambió recientemente? (git log)
□ 7. ¿Es un error de compilación o de runtime?
□ 8. ¿Es un error nuevo o existente?
□ 9. ¿Puedo hacer un breakpoint en el lugar correcto?
□ 10. ¿Inspeccioné las variables con WATCH/Debug Console?
□ 11. ¿Leí el error COMPLETO (no solo la primera línea)?
□ 12. ¿Busqué el error en Google/Stack Overflow primero?
□ 13. ¿Revisé la documentación oficial del package/API?
□ 14. ¿Puedo explicar el problema a otro developer?
□ 15. ¿Entiendo QUÉ está fallando (no solo QUÉ hacer para arreglarlo)?
```

---

## 10. Ejercicio integrador: 3 bugs graduales

### Bug 1 (Fácil): El contador no aumenta

```
Tu app tiene un CounterCubit. Cuando presionas "+", el contador no cambia.

Steps para reproducir:
1. Abrir la app
2. Presionar el botón "+"
3. OBSERVAR: el contador sigue en 0

Tu trabajo:
1. ¿Dónde pondrías el primer breakpoint?
2. ¿Qué variable inspeccionarías?
3. Encuentra el fix (pista: revisa el handler del evento)
```

**Respuesta:**
```
1. Breakpoint en increment() del Cubit
2. Inspeccionar: state.counter, el valor antes del emit
3. Fix probable: el Cubit no hace emit(state.copyWith(counter: state.counter + 1))
```

### Bug 2 (Medio): La lista no carga

```
Tu app tiene un ListCubit que carga items de una API. La lista queda vacía siempre.

Steps para reproducir:
1. Abrir la app
2. Navegar a la pantalla de lista
3. OBSERVAR: "No hay items" aunque la API tiene datos

Tu trabajo:
1. Binary search: ¿dónde está el bug? (evento → usecase → repository → datasource → API)
2. ¿Qué inspeccionarías en cada breakpoint?
3. Encuentra el fix
```

**Respuesta:**
```
1. Breakpoint en datasource → ver qué retorna la API
2. Si la API retorna datos pero el repository no los parsea → bug en el mapper
3. Si la API retorna vacío → bug en la query o en los headers
```

### Bug 3 (Difícil): La app se congela después de navegar

```
Tu app tiene una pantalla de chat. Después de 30 segundos de chat, la app se congela.

Steps para reproducir:
1. Abrir la app
2. Ir a la pantalla de chat
3. Enviar 5-10 mensajes
4. Esperar 30 segundos
5. OBSERVAR: la app se congela

Tu trabajo:
1. ¿Qué tipo de bug es? (memory leak, timer, stream)
2. ¿Qué herramienta usarías primero?
3. Encuentra el fix (pista: busca streams/timers no cancelados)
```

**Respuesta:**
```
1. Memory leak o timer leak
2. DevTools → Memory → Heap Snapshot (comparar antes y después)
3. Fix: cancelar streams/timers en dispose()
   - Buscar: Stream.listen() sin cancel()
   - Buscar: Timer.periodic() sin cancel()
   - Buscar: StreamController sin close()
```

---

## Resumen

| Paso | Qué hacer | Herramienta |
|---|---|---|
| 1. Entender | Responder 7 preguntas | Notepad, git log |
| 2. Reproducir | Steps exactos | Tu app |
| 3. Aislar | Binary search con breakpoints | VS Code debugger |
| 4. Diagnosticar | Variables, watch, call stack | VS Code debugger |
| 5. Corregir | Fix mínimo, un cambio a la vez | Editor de código |
| 6. Verificar | Reproducir + tests | Tu app, terminal |

---

## 📚 Referencias

- [27-mentalidad-debugging.md](./27-mentalidad-debugging.md) — La filosofía detrás de este playbook
- [26-workflow-debugging-por-tipo.md](./26-workflow-debugging-por-tipo.md) — Workflows específicos por tipo de bug
- [VS Code | Debugging](https://code.visualstudio.com/docs/editor/debugging) — Herramientas del debugger
- [Flutter | Debugging tools](https://docs.flutter.dev/tools) — Herramientas de debugging de Flutter

---

> 📖 **Anterior:** [26-workflow-debugging-por-tipo.md](./26-workflow-debugging-por-tipo.md) — Workflow por tipo de bug
> 📖 **Siguiente:** [30-referencia-rapida-flutter-debugging.md](./30-referencia-rapida-flutter-debugging.md) — Referencia rápida de todo el módulo
