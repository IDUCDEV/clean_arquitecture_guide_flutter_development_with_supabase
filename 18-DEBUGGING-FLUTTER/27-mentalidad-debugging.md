# 27 — Mentalidad de Debugging: Piensa como un Debugger, no como un Prompt

> Antes de aprender herramientas, aprende a pensar. Este capítulo establece la filosofía que te hará independiente de la IA para diagnosticar bugs.

---

## 1. El problema real: debugging dependiente

La mayoría de developers en 2026 tienen este ciclo:

```
Bug aparece → Pedirle a la IA que lo resuelva → Copiar la solución → Siguiente bug
```

Esto es problemático porque:

- **No entiendes POR QUÉ** algo falló, solo que "ahora funciona"
- **No sabes detectar** si la solución de la IA introduce nuevos bugs
- **No puedes distinguir** entre una solución correcta y una que "parece" correcta
- **Te vuelves más lento** sin IA, porque nunca desarrollaste la habilidad

El debugging no es una herramienta. Es una **mentalidad**.

---

## 2. La filosofía: "No adivines, observa"

Un desarrollador principiante adivina:

```
"Creo que el problema es que el BLoC no emite el estado"
```

Un desarrollador experimentado observa:

```
"BLoC emite LoginLoading en la línea 195. Breakpoint ahí. event.email es null.
 El problema está en el handler del formulario, no en el BLoC."
```

La diferencia es **evidencia vs hipótesis**.

### 2.1 Regla #1: Nunca supongas, verifica

| ❌ Suposición | ✅ Verificación |
|---|---|
| "Creo que es un null" | Inspecciona la variable: ¿es null? |
| "Creo que el estado no cambia" | Pon un breakpoint en el emit: ¿se ejecuta? |
| "Creo que la API falla" | Mira Network View: ¿qué status code devuelve? |
| "Creo que es un rebuild innecesario" | Agrega `debugPrintRebuildDirtyWidgets`: ¿quién rebuilda? |

### 2.2 Regla #2: Reduce el espacio de búsqueda

Cuando no sabes dónde está el bug, no revises todo el código. Usa **binary search debugging**:

```
Tu app tiene 100 archivos. El bug está en alguno.

1. Pon un breakpoint a mitad del flujo (archivo 50)
2. ¿El bug está antes o después?
3. Repite con la mitad correcta
4. En 7 pasos (log2 de 100) encuentras el archivo exacto
```

### 2.3 Regla #3: Reproduce antes de arreglar

Si no puedes reproducir el bug, no puedes arreglarlo. Punto.

```
❌ "Me pasó una vez, voy a cambiar esto y espero que se arregle"
✅ "Puedo reproducir el bug en 3 pasos exactos. Ahora puedo testear mi fix."
```

---

## 3. Framework de debugging en 5 pasos

Estos 5 pasos funcionan para **cualquier bug**, en cualquier lenguaje:

### Paso 1: REPRODUCIR

**Preguntas clave:**
- ¿Qué hago exactamente para que el bug aparezca?
- ¿Pasa siempre o solo a veces?
- ¿En qué dispositivo/plataforma?
- ¿Con qué datos de entrada?

**Acción:**
```
1. Abre un documento nuevo (puede ser un comment en el código)
2. Escribe los steps exactos para reproducir
3. Ejecuta esos steps. Si el bug no aparece, ajusta hasta que sea consistente
```

### Paso 2: AISLAR

**Preguntas clave:**
- ¿En qué función/método ocurre?
- ¿En qué capa de la arquitectura? (UI, Domain, Data)
- ¿Es un problema de datos, lógica o presentación?

**Acción:**
```
1. Pon un breakpoint al inicio del flujo (ej: handler del evento)
2. F10 (Step Over) hasta que el comportamiento anormal aparezca
3. Ahora sabes en qué rango de código está el bug
4. Repite: pon un breakpoint a mitad de ese rango
5. En 3-5 iteraciones, encuentras la línea exacta
```

### Paso 3: DIAGNOSTICAR

**Preguntas clave:**
- ¿Qué valor tiene la variable en el momento del error?
- ¿Qué camino tomó el código? (call stack)
- ¿Qué era el estado antes del error?

**Acción:**
```
1. En el breakpoint, mira VARIABLES: ¿qué valores hay?
2. Agrega WATCH para las variables sospechosas
3. Usa Debug Console para evaluar expresiones
4. Mira el CALL STACK para ver cómo llegaste ahí
5. La respuesta está en los datos, no en tu intuición
```

### Paso 4: CORREGIR

**Preguntas clave:**
- ¿Cuál es el fix más mínimo que resuelve el problema?
- ¿Este fix rompe algo más?
- ¿Puedo probar que el fix funciona?

**Acción:**
```
1. Escribe el fix más pequeño posible
2. NO refactores al mismo tiempo (un cambio a la vez)
3. Ejecuta los steps del Paso 1: ¿el bug ya no aparece?
4. Ejecuta tests existentes: ¿algo se rompió?
```

### Paso 5: VERIFICAR

**Preguntas clave:**
- ¿El bug original está resuelto?
- ¿Introduje nuevos bugs?
- ¿Los tests pasan?
- ¿Puedo reproducir el escenario original sin el bug?

**Acción:**
```
1. Reproduce los steps exactos del Paso 1
2. Verifica que el comportamiento sea el esperado
3. Ejecuta la suite de tests
4. Si todo pasa, documenta: qué era el bug y cómo lo arreglaste
```

---

## 4. Cuándo SÍ usar la IA (y cuándo NO)

La IA es una herramienta poderosa. El problema no es usarla, es **usarla sin entender**.

### 4.1 SÍ usa la IA cuando:

| Situación | Por qué |
|---|---|
| Ya entiendes el bug y necesitas help con la sintaxis del fix | La IA es rápida para code generation |
| Necesitas un snippet boilerplate (ej: configurar un interceptor HTTP) | No es lógica de negocio |
| Quieres aprender un patrón nuevo (ej: cómo usar un package) | Es documentación en formato conversacional |
| Tienes un error de compilación que no entiendes | La IA puede explicar el mensaje de error |

### 4.2 NO uses la IA cuando:

| Situación | Por qué |
|---|---|
| No sabes POR QUÉ algo falla | Necesitas diagnosticar, no recibir una solución ciega |
| El bug es de lógica de negocio | Solo tú (y tu team) entienden la lógica |
| La solución "parece" funcionar pero no sabes por qué | Estás introduciendo deuda técnica oculta |
| Es un bug de performance o memory leak | La IA no puede medir tu app en tu dispositivo |
| Necesitas entender el call stack completo | La IA no tiene contexto de tu estado en runtime |

### 4.3 El test definitivo

Antes de pedir ayuda a la IA, hazte esta pregunta:

> **"¿Podría explicarle a otro developer exactamente qué está pasando y por qué?"**

Si la respuesta es NO, **no entiendes el bug todavía**. Usar la IA ahora solo enmascara el problema.

Si la respuesta es SÍ, **úsala** para acelerar el fix.

---

## 5. La checklist universal: 15 preguntas ANTES de pedir ayuda a la IA

Imprime esto y ponlo al lado de tu monitor:

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

Si más de 3 están sin marcar, **estás pidiendo ayuda prematuramente**.

---

## 6. Ejercicio mental: mapea tu debugging

Dado este escenario:

```
Tu app de Flutter tiene un BLoC de login. Cuando el usuario presiona "Login",
la app se queda en loading indefinidamente. No muestra error, no navega.
```

**Antes de tocar cualquier herramienta**, responde:

1. ¿Dónde pondrías tu primer breakpoint?
2. ¿Qué variable inspeccionarías primero?
3. ¿QuéExpressions agregarías al WATCH?
4. ¿Qué buscarías en el CALL STACK?
5. ¿Qué consultarías en la Debug Console?

**Respuesta esperada:**

```
1. Breakpoint en el handler del evento LoginSubmitted (línea donde se llama loginUseCase)
2. Inspeccionar: event.email, event.password, y el resultado de loginUseCase
3. WATCH: state.runtimeType (para ver si cambia de LoginInitial a LoginLoading)
4. CALL STACK: verificar que el BLoC recibió el evento correctamente
5. Debug Console: evaluar await loginUseCase(LoginParams(email: "test", password: "123"))
   directamente para ver si el UseCase retorna algo
```

Si podías responder esto **sin pedir ayuda a la IA**, ya estás desarrollando la mentalidad.

---

## 7. Mentalidad anti-AI-dependency: resumen

```
┌──────────────────────────────────────────────────────────────┐
│                    EL CICLO CORRECTO                         │
│                                                              │
│  Bug aparece                                                 │
│      ↓                                                       │
│  REPRODUCIR (steps exactos)                                  │
│      ↓                                                       │
│  AISLAR (breakpoints + binary search)                        │
│      ↓                                                       │
│  DIAGNOSTICAR (inspeccionar datos, call stack)               │
│      ↓                                                       │
│  ¿Entiendo el problema?                                      │
│      ↓                                                       │
│  SÍ → CORREGIR (fix mínimo) → VERIFICAR                     │
│  NO → Volver a DIAGNOSTICAR con más breakpoints              │
│                                                              │
│  Solo después de DIAGNOSTICAR puedes usar IA para            │
│  acelerar el fix (si la necesitas)                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Resumen

| Concepto | Descripción |
|---|---|
| "No adivines, observa" | Usa breakpoints y datos, no intuición |
| Binary search | Reduce el espacio de búsqueda a la mitad en cada paso |
| Reproducir primero | Si no puedes reproducir, no puedes arreglar |
| Fix mínimo | Un cambio a la vez, sin refactorizar |
| IA como acelerador | Úsala para coding, no para diagnóstico |
| Checklist universal | 15 preguntas ANTES de pedir ayuda |

---

## 📚 Referencias

- [VS Code | Debugging](https://code.visualstudio.com/docs/editor/debugging) — Fundamentos del debugger
- [Flutter | Debugging tools](https://docs.flutter.dev/tools) — Panorama de herramientas de debugging
- [The Debugging Book](https://www.debuggingbook.org/) — Metodología de debugging (general, no Flutter)

---

> 📖 **Siguiente:** [01-fundamentos-debugging.md](./01-fundamentos-debugging.md) — Fundamentos del debugging en VS Code: modos de compilación, interfaz del debugger y flujo completo
