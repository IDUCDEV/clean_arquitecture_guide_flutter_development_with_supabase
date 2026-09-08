# 07 — Guía Paso a Paso: SDD con OpenSpec

> **Receta de cocina** para aplicar SDD a tu stack Flutter + Clean Architecture + Supabase usando OpenSpec. Cada fase dice exactamente qué comando ejecutar, qué archivo abrir, y qué escribir.

---

## 1. Cómo arrancar

### 1.1 Complejidad del cambio

Antes de tutto, clasifica el cambio:

| Nivel | Criterio | design.md | Puertas |
|-------|----------|-----------|---------|
| **Simple** | 1 feature, 0-1 tablas, 0 decisiones técnicas nuevas | No | 1 combinada |
| **Intermedia** | 1-2 features, 1-2 tablas, 1-2 decisiones técnicas | Sí (ligero) | 1-2 |
| **Compleja** | 3+ features, 3+ tablas, seguridad, cambios de contrato | Sí (completo) | 3 |

**Regla práctica:** si dudarías en mergearlo sin revisión de otro humano, es al menos Intermedia.

### 1.2 Artésano vs Copiloto

| Situación | Modo | Comando |
|-----------|------|---------|
| Sabes QUÉ construir, quieres pensar el diseño | **Artésano** | `/opsx-new-change` |
| No sabes bien QUÉ ni CÓMO, necesitas que la IA proponga | **Copiloto** | `/opsx-propose add-nombre` |
| Quieres explorar opciones antes de decidir | **Exploración** | `/opsx-explore` |

**Puedes mezclar:** empezar artesano y pedir a la IA que refine con `/opsx-update-change`.

---

## 2. Fase 0+1 — Crear el cambio (proposal.md + spec.md)

### Paso 1: Crear la carpeta de cambio

**Modo artésano:**
```bash
# En tu agente IA (OpenCode):
/opsx-new-change
```
OpenSpec crea el esqueleto:
```
openspec/changes/add-nombre/
├── proposal.md       ← esqueleto con secciones vacías
├── specs/
│   └── {capability}/
│       └── spec.md   ← secciones WHY/Purpose/Requirements vacías
├── design.md         ← vacío (lo llenas en Fase 2)
└── tasks.md          ← vacío (lo llenas en Fase 3)
```

**Modo copiloto:**
```bash
/opsx-propose add-nombre
```
La IA genera una primera versión de los 4 archivos. Tú solo revisas y ajustas.

### Paso 2: Llenar proposal.md

Abre `openspec/changes/add-nombre/proposal.md` y escribe:

#### Sección Impacto (Impact Report)

Ejecuta el checklist en tu codebase antes de escribir:
```bash
# Features similares
ls lib/features/

# Tablas Supabase existentes
ls supabase/migrations/

# DI y rutas
cat lib/core/di/service_locator.dart
cat lib/core/router/app_router.dart
```

Llena los 5 bullets:
```markdown
Impacto (Impact Report)
- Features afectadas: [nombre] existente provee [X]
- Reutilizable: [patrones, widgets, contratos que ya existen]
- Supabase: [tablas nuevas/existentes, RLS, migración nº XXXX]
- DI / rutas: [service_locator.dart (+N registros), app_router.dart (+N rutas)]
- Riesgos: [concurrencia, seguridad, breaking changes]
```

#### Sección Scope (Alcance)

```markdown
Scope (Alcance)
**Incluye:**
- [lista de lo que SÍ se construye]

**No incluye:**
- [lista de lo que explícitamente NO se construye]

**Dependencias:** [qué necesita para funcionar]
**Suposiciones:** [qué damos por hecho]
**Preguntas abiertas:** [cosas pendientes de resolver]
```

#### Sección Actores y permisos

```markdown
Actores y permisos
| Actor | Puede | No puede | Mapeo RLS |
|-------|-------|----------|-----------|
| [nombre] | [acciones] | [restricciones] | [política RLS] |
```

**Validación:** ejecuta `openspec validate` en la CLI:
```bash
openspec validate
```
Si hay errores de formato, OpenSpec te dice cuáles corregir.

**Tip:** usa `openspec status --change add-nombre` para ver un checklist de progreso de artifacts sin tener que revisar manualmente qué archivos faltan.

### Paso 3: Llenar spec.md

Abre `openspec/changes/add-nombre/specs/{capability}/spec.md` y escribe los requisitos EARS.

#### Cómo escribir un requisito EARS

Cada requisito tiene:
1. **ID único** (`REQ-XXX`)
2. **Nombre corto** descriptivo
3. **Cuerpo EARS** con uno de los 5 patrones
4. **Escenarios** con casos happy path + error + bordes

```markdown
ADDED Requirements

### Requirement: [Nombre descriptivo] (REQ-001)
[Descripción en lenguaje natural del requisito]

#### Scenario: [Happy path]
- **WHEN** [disparador]
- **THEN** el sistema DEBERÁ [acción esperada]

#### Scenario: [Error/borde]
- **IF** [condición de error]
- **THEN** el sistema DEBERÁ [respuesta con mensaje exacto entre comillas]

#### Scenario: [Borde numérico]
- **IF** [valor límite alcanzado]
- **THEN** el sistema DEBERá mostrar "[mensaje con umbral exacto]"
```

**Reglas de oro para escenarios:**
- Incluye mensajes de error EXACTOS entre comillas
- Incluye umbrales numéricos concretos (50 items, 50%, 2h antes)
- Cada escenario debe ser testeable SIN preguntar nada más
- Si no puedes testearlo, reescribe el escenario

**5 patrones EARS:**

| Patrón | Cuándo usarlo | Ejemplo |
|--------|---------------|---------|
| `WHEN/THEN` | Interacciones UI, eventos | `WHEN el cliente agrega un producto THEN el sistema DEBERÁ...` |
| `IF/THEN` | Errores, validaciones, bordes | `IF el stock es 0 THEN el sistema DEBERÁ mostrar "sin stock"` |
| `MIENTRAS/THEN` | Estados持续的 | `MIENTRAS el carrito tenga items EL SISTEMA DEBERÁ...` |
| `GIVEN/WHEN/THEN` | Aislamiento, seguridad | `GIVEN un cliente autenticado WHEN consulta su carrito THEN solo recibe filas propias` |
| `DONDE/THEN` | Feature flags | `DONDE el modo oscuro está habilitado EL SISTEMA DEBERÁ...` |

> **Criterios de aceptación:** Cada escenario EARS es un criterio de aceptación verificable. Cuando el usuario dice "esto es lo que debe pasar", ese enunciado se traduce a un `#### Scenario:` con `WHEN/THEN`. Los tests (unit, widget, integration) validan estos mismos criterios. Si un escenario no es testeable, reescríbelo hasta que lo sea.

### Paso 4: Iterar si es necesario

Si necesitas ajustar después de la Puerta 1:
```bash
/opsx-continue-change
```
Esto reabre el cambio para que continues editando proposal.md y spec.md.

### Paso 5: Puerta 1 — Validar requisitos

```bash
openspec validate
```

Checklist de la Puerta 1:
```
[ ] Cada historia pasa la prueba de precisión (actor + acción + objeto + propósito)
[ ] Todos los requisitos usan notación EARS con ID único (REQ-XXX)
[ ] Los bordes están cubiertos (valores límite, vacío, negativos, expirados)
[ ] Las preguntas abiertas del alcance están cerradas o documentadas
[ ] El formato delta es correcto (ADDED/MODIFIED/REMOVED según toque)
[ ] El Impact Report justifica el alcance elegido
[ ] `openspec validate` pasa sin errores
```

---

## 3. Fase 2 — Diseño técnico (design.md)

### Cuándo OMITIR design.md

Si el cambio es **Simple** (1 feature, 0-1 tablas, 0 decisiones técnicas, UI trivial), puedes saltar design.md. La skill `clean-arch-feature` derivará los archivos de los requisitos automáticamente. Un cambio Simple también **omite el archivo `.pen`** de pantallas.

### Qué escribir en design.md

Abre `openspec/changes/add-nombre/design.md` y llena estas secciones:

#### Context + Goals

```markdown
Context
[1-2 oraciones: qué existe hoy y qué cambia]

Goals / Non-Goals
- ✅ [objetivo claro]
- ❌ [anti-objetivo explícito]
```

#### Decisions (D1..Dn)

Registra solo decisiones **no obvia**. Señales de que merece registro:
- Elegir entre dos patrones válidos
- Depender de un paquete nuevo
- Tocar seguridad o datos sensibles
- Cambiar un contrato público

```markdown
Decisions

### D1: [Título de la decisión]
- Decision: [qué se eligió]
- Alternativas descartadas: [qué se descartó y por qué]
- Por qué: [razonamiento]
```

**Ejemplos de qué SÍ es decisión:**
- Elegir entre un Cubit vs dos Cubits
- Calcular impuestos en cliente vs RPC
- Usar tabla nueva vs extender tabla existente

**Ejemplos de qué NO es decisión:**
- Usar fpdart Either (es boundary del proyecto)
- Seguir el patrón de features existentes
- Nombrar archivos en snake_case (convención)

#### Ficheros afectados

Tabla **obligatoria** — sin ella el agente improvisa rutas:

```markdown
Ficheros afectados
| Elemento | Capa | Archivo | Req |
|----------|------|---------|-----|
| [Entity] | domain/entity | `lib/features/[name]/domain/entities/[file].dart` | REQ-001 |
| [Repository] | domain/repository | `lib/features/[name]/domain/repositories/[file].dart` | REQ-002..005 |
| [Model] | data/model | `lib/features/[name]/data/models/[file].dart` | REQ-001 |
| [DataSource] | data/datasource | `lib/features/[name]/data/datasources/[file].dart` | REQ-002 |
| [UseCase] | domain/usecase | `lib/features/[name]/domain/usecases/[file].dart` | REQ-003 |
| [Cubit/State] | presentation | `lib/features/[name]/presentation/cubit/…` | REQ-006 |
| [Page] | presentation | `lib/features/[name]/presentation/pages/[file].dart` | REQ-006 |
```

#### Contratos Dart clave

Escribe las interfaces ANTES de implementar. Copia el patrón de la feature más parecida:

```markdown
Contratos Dart clave

    // Repository interface
    abstract interface class [Name]Repository {
      Future<Either<Failure, [Type]>> [method]();
    }

    // States UI
    sealed class [Name]State {}
    class [Name]Initial extends [Name]State {}
    class [Name]Loading extends [Name]State {}
    class [Name]Loaded extends [Name]State { final [Type] data; }
    class [Name]Error extends [Name]State { final String message; }

#### Pantallas UI (UI-UX)

El diseño visual se hace con **Pencil** (módulo 08, diseño manual) y se guarda en `openspec/changes/add-nombre/design/<feature>-ui.pen` (JSON diffable en git). En `design.md` solo se registra el mapeo pantalla→REQ; los mensajes/estados exactos viven en la spec. Simple omite esta sección.

    UI-UX · Pantallas (archivo .pen)
    | Pantalla (.pen)        | Escenario REQ | Estados visibles        | Notas |
    |------------------------|---------------|-------------------------|-------|
    | <Page> | REQ-00x | vacio · con datos · error | snackbars con el mensaje exacto del escenario |

Ejemplo (add-cart):

    | Archivo esperado: openspec/changes/add-cart/design/add-cart-ui.pen (no incluido en el ejemplo) |
    | Pantalla          | Escenario REQ      | Estados visibles          | Notas |
    |-------------------|--------------------|---------------------------|-------|
    | CartPage (vacia)  | REQ-003            | EmptyState sin totales    | mensaje "Tu carrito esta vacio" |
    | CartPage (llena)  | REQ-001..004       | items + subtotal/impuesto/total | recalculo tras add/remove/cupon |
    | CartPage (error)  | REQ-001, REQ-004   | SnackBar "Producto {nombre} sin stock disponible" / "El cupon {codigo} ha expirado" | mensajes exactos de los escenarios |

#### Flujo de datos

Diagrama ASCII del recorrido completo, incluyendo errores:

Flujo de datos

    [Page] ──onTap──► [Cubit].[method]()
                        │ emit [Loading]
                        ▼
                 [UseCase](repository)
                        ▼
                 [RepositoryImpl] ──► [DataSource].[method]()
                        │                │ supabase.from('[table]').[operation]()
                        ▼                ▼
                 ◄── Either.right ◄── respuesta
                 │
                 └── Either.left(Failure) ──► [Error](message) ──► SnackBar

#### Backend Supabase

Backend Supabase
- **Tablas:** [nombres, columnas, tipos, FKs]
- **RLS:** [políticas por escenario, citando REQ]
- **RPCs:** [si aplica, firma y comportamiento]
- **Migración:** supabase/migrations/[XXXX].sql

#### Boundaries

Boundaries
- [regla 1]
- [regla 2]
- [regla 3]
```

### Paso: Puerta 2 — Validar diseño

```bash
openspec validate
```

Checklist de la Puerta 2:
```
[ ] La tabla de ficheros afectados cubre TODOS los requisitos de la Puerta 1
[ ] Los contratos compilan mentalmente (firmas coherentes entre capas)
[ ] El flujo de datos cubre caminos de éxito Y de error
[ ] RLS especificada para toda tabla nueva/modificada
[ ] Ninguna decisión importante quedó implícita
[ ] Se respeta el patrón de las features existentes (o se justifica el cambio)
[ ] Cada escenario REQ visible tiene su pantalla/estado diseñado (archivo .pen)
[ ] `openspec validate` pasa sin errores
```

---

## 4. Fase 3 — Tareas (tasks.md)

### Estructura de las 5 oleadas

Abre `openspec/changes/add-nombre/tasks.md` y escribe las tareas agrupadas en oleadas:

```markdown
# Tasks: add-<feature>
> Modo de implementación: andamiaje
>   andamiaje = la IA genera el scaffold (throw UnimplementedError() + TODOs citando REQ) y TÚ implementas los métodos críticos
>   completo  = la IA escribe todo (100%) y tú auditas cada diff contra la spec

1. Dominio
- [ ] 1.1 Entity [Name] (+ invariantes, REQ-001)
- [ ] 1.2 Interface [Name]Repository (REQ-002..005)
- [ ] 1.3 UseCases (uno por operación, REQ-003)

2. Capa de datos + Backend Supabase
- [ ] 2.1 Migración SQL tablas + RLS (REQ-005)   ← abre la capa: el flujo de datos es probable de inmediato
- [ ] 2.2 Models (fromJson/toJson, REQ-001)
- [ ] 2.3 RemoteDataSource (REQ-002)
- [ ] 2.4 [Name]RepositoryImpl (mapeo excepciones → Failure, REQ-002)

3. Estado y presentación
- [ ] 3.1 [Name]State sealed (REQ-006)
- [ ] 3.2 [Name]Cubit (REQ-006)
- [ ] 3.3 [Name]Page + widgets (REQ-006)

4. Integración
- [ ] 4.1 Registro en service_locator.dart
- [ ] 4.2 Ruta en app_router.dart

5. Tests
- [ ] 5.1 Unit tests entidades/usecases
- [ ] 5.2 Test repository impl (mock datasource) + integración contra la migración real
- [ ] 5.3 Widget test página clave

Trazabilidad
| Req | Tarea(s) | Test | Cubre escenario |
|-----|----------|------|-----------------|
| REQ-001 | 1.1, 2.2 | 5.1 | Happy path + error |
| REQ-002 | 1.2, 2.3, 2.4 | 5.2 | Happy path |
| REQ-003 | 1.3 | 5.1 | Happy path + borde |
| REQ-005 | 2.1 | 5.2 | Aislamiento RLS |
| REQ-006 | 3.1, 3.2, 3.3 | 5.3 | Loading + error |
```

### Anotación mínima por tarea

Cada tarea debe tener:
- **Qué se hace** (1-3 ficheros)
- **REQ** que implementa
- **Criterio de éxito** (verificable)

### Declarar el modo de implementación

La primera línea de `tasks.md` indica **quién escribe el código** en este cambio. Es una decisión binaria por cambio (no por tarea):

- **`andamiaje`** → la IA genera el scaffold (`throw UnimplementedError()` + TODO citando REQ-xxx) y **tú implementas los métodos críticos**. Es el modo recomendado para mantener la práctica de escritura de código.
- **`completo`** → la IA escribe el código al 100% y tú auditas cada diff contra la spec.

Para que `/opsx-apply-change` —el único motor de implementación del flujo— respete el modo de forma fiable, hay que configurar `openspec/config.yaml` una sola vez — ver [Fase 4](#fase-4--implementar-).

### Puerta 3 — Validar tareas

```bash
openspec validate
```

Checklist:
```
[ ] Cada requisito de la spec tiene ≥1 tarea que lo implementa
[ ] Cada tarea referencia su requisito (trazabilidad bidireccional)
[ ] Las dependencias definen el orden de oleadas correctamente
[ ] Ninguna tarea excede ~3 ficheros
[ ] Hay tareas de test para los escenarios críticos
[ ] tasks.md declara su modo de implementación (andamiaje | completo)
[ ] `openspec validate` pasa sin errores
```

---

## 5. Fase 4 — Implementar

### Modo andamiaje

```bash
/opsx-apply-change
```

El agente lee los 4 archivos y ejecuta las tareas **una a una**, generando scaffold por tarea (ficheros con `throw UnimplementedError()` + TODOs citando REQ-xxx), dejando la casilla en `- [ ]` y pausando. **Tú implementas la lógica crítica** (los métodos que exigen decisiones de negocio) antes de continuar con la siguiente tarea.

### Modo completo

```bash
/opsx-apply-change
```

El agente lee los 4 archivos y ejecuta **todas** las tareas, commit por tarea, escribiendo el 100% del código.

Audita cada oleada con [06-auditoria-codigo-ia.md](./06-auditoria-codigo-ia.md).

> **`/opsx-apply-change` respeta el modo de `tasks.md`.** Con `Modo: completo` el agente escribe el 100% de cada tarea. Con `Modo: andamiaje`, el agente genera **scaffold por tarea** (cuerpos en `throw UnimplementedError()` + TODO citando REQ), **deja la casilla en `- [ ]`** y pausa para que tú implementes — así no pierdes la práctica de escritura de la lógica crítica. Para que esto sea fiable, configura el proyecto **una sola vez**:

```yaml
# openspec/config.yaml — se añade una vez; el interruptor por cambio es la línea "Modo" de tasks.md
operations:
  apply:
    guidance:
      - "Si tasks.md declara 'Modo: andamiaje': NO escribas los bodies. Por cada tarea genera solo el scaffolding (throw UnimplementedError() + TODO citando REQ-xxx), NO marques la casilla - [x], y pausa para que el desarrollador complete e implemente."
      - "Si tasks.md declara 'Modo: completo': implementa la tarea al 100% contra la spec (caminos de éxito y error de los escenarios) y márcala - [x]."
```

`openspec/config.yaml` es de tu proyecto (lo genera `openspec init`); no se toca la herramienta. El CLI lo lee en `openspec instructions apply` y lo inyecta al agente como `operationGuidance` (canal oficial que el flujo built-in ordena seguir). Grano de los dos modos:

| Grano | Modo: andamiaje | Modo: completo |
|-------|-----------------|----------------|
| Qué escribe la IA | solo scaffold, por tarea | todo el código al 100% |
| Casillas | se quedan en `- [ ]` hasta que tú completes | se marcan `- [x]` al implementar |
| Ritmo | pausa al final de cada tarea | corre todo el cambio, commit por tarea |

### Verificar contra spec

Al cierre de cada oleada:

| Tarea | La spec dice | El código hace | Cumple |
|-------|--------------|----------------|--------|
| 2.1 Model | roundtrip JSON | ✔ test pasa | ✅ |
| 3.3 Cubit | estados sealed + mensajes | falta mensaje | ❌ → fix |

### Cerrar el cambio

```bash
# Revisar diffs de requisitos antes de archivar (recomendado)
openspec show add-nombre --diff

# Verificar que cumple las specs
/opsx-verify-change

# Archivar y consolidar specs vivas
/opsx-archive-change
```

Tras archive, las specs archivadas son la documentación viva del sistema.

---

## 6. Ejemplos prácticos de complejidad creciente

Los 3 ejemplos muestran el flujo completo de SDD con OpenSpec. Copia, adapta, y usa como referencia.

Antes de verlos, aquí tiene el esqueleto que repiten todos (y los 6 cambios de `ejemplos-cambios/`).

### El patrón que verás repetido

| Paso | Qué produces | Comando | Tu papel | Validación |
|------|--------------|---------|----------|------------|
| 0 · Clasificar | Simple / Intermedia / Compleja | — | tú decides | proporcionalidad |
| 1 · Crear cambio | carpeta `openspec/changes/<feat>/` | `/opsx-propose add-nombre` | revisas el esqueleto | `openspec validate` |
| 2 · proposal.md | WHY + Impact + Scope + Actores | `openspec instructions proposal --change <n>` | IA redacta → tú apruebas | — |
| 3 · spec.md | requisitos EARS con escenarios | `openspec instructions spec --change <n>` | IA redacta → tú apruebas | **Puerta 1** + Clarity Gate |
| 4 · design.md | ficheros, contratos, backend, decisiones | `openspec instructions design --change <n>` | IA redacta → tú apruebas | **Puerta 2** |
| 5 · tasks.md | 5 oleadas + trazabilidad + Modo | `openspec instructions tasks --change <n>` | IA redacta → tú apruebas | validate |
| 6 · Implementar | código + tests | `/opsx-apply-change` | andamiaje: implementas la lógica crítica · completo: auditas cada diff | tests verdes |
| 7 · Verificar · archivar | specs vivas consolidadas | `/opsx-verify-change` → `/opsx-archive-change` | auditas | **Puerta 3** |

**Observación clave:** hasta el Paso 5 la IA redacta los artefactos y tú los apruebas. Solo el Paso 6 depende del **Modo** declarado en `tasks.md`: `andamiaje` = la IA deja scaffold por tarea y tú implementas la lógica crítica; `completo` = la IA escribe todo y tú auditas cada diff contra la spec. El motor es siempre el mismo: `/opsx-apply-change`.

**Las plantillas de cada fase (con la explicación de qué va en cada parte) viven aquí mismo:** proposal.md y spec.md en §2 (Pasos 2-3), design.md en §3, tasks.md en §4, y los checklists de las 3 puertas en sus secciones. La plantilla completa consolidada está en [04-plantilla-cambio-openspec.md](./04-plantilla-cambio-openspec.md) y los cambios terminados en [`ejemplos-cambios/`](./ejemplos-cambios/).

---

### Ejemplo A: Simple — Cambiar color del tema de la app

**Contexto:** Quieres que el usuario pueda elegir entre tema claro y oscuro. Es un cambio que toca solo presentación, sin tablas nuevas ni decisiones técnicas.

**Clasificación:** Simple → sin design.md, 1 puerta combinada.

#### Paso 1: Crear el cambio

```bash
/opsx-propose add-theme-color
```

OpenSpec genera la carpeta `openspec/changes/add-theme-color/`. La IA llena los 4 archivos.

#### Paso 2: proposal.md (lo que escribiste)

```
# Proposal: add-theme-color

## Impacto (Impact Report)
- Features afectadas: ninguna directamente (configuración global de tema)
- Reutilizable: `AppTheme` en `lib/core/theme/` ya maneja tema claro
- Supabase: sin tablas nuevas
- DI / rutas: sin cambios
- Riesgos: ninguno

## Why (Problema)
Los usuarios no pueden cambiar entre tema claro y oscuro. La app solo tiene tema claro.

## What Changes (Solución)
Agregar toggle de tema claro/oscuro en la pantalla de configuración, persistiendo la preferencia del usuario.

## Capabilities
### New Capabilities
- `theme-color`: toggle de tema claro/oscuro con persistencia

## Scope (Alcance)
**Incluye:**
- Toggle en pantalla de settings
- Persistir preferencia en SharedPreferences
- Aplicar tema al iniciar la app

**No incluye:**
- Temas personalizados con colores custom
- Sincronización entre dispositivos

**Dependencias:** SharedPreferences (ya en pubspec)
**Suposiciones:** solo 2 temas: claro y oscuro
**Preguntas abiertas:** ~~¿sincronizar entre dispositivos?~~ → NO (fuera de alcance)

## Actores y permisos
| Actor | Puede | No puede | Mapeo RLS |
|-------|-------|----------|-----------|
| Usuario | Cambiar su tema, persistir preferencia | Cambiar tema de otros usuarios | N/A (datos locales)

## Impact
- Código: ~3 ficheros modificados en `lib/core/theme/` y `lib/features/settings/`
- Datos: sin tablas nuevas
- Breaking changes: ninguno
```

#### Paso 3: spec.md (lo que escribiste)

```
# Spec: theme-color

## WHY
Los usuarios prefieren temas oscuros para reducir fatiga visual. No hay forma de cambiar el tema actual.

## Purpose
Permitir al usuario elegir entre tema claro y oscuro, persistiendo su preferencia localmente.

## ADDED Requirements

### Requirement: Cambiar tema de la app (REQ-001)
El usuario cambiará entre tema claro y oscuro desde la configuración.

#### Scenario: Cambiar a tema oscuro
- **WHEN** el usuario toca el toggle de tema en settings
- **THEN** el sistema DEBERÁ aplicar el tema oscuro inmediatamente

#### Scenario: Cambiar a tema claro
- **WHEN** el usuario toca el toggle de tema estando en oscuro
- **THEN** el sistema DEBERÁ aplicar el tema claro inmediatamente

#### Scenario: Persistir preferencia
- **WHEN** el usuario cambia el tema
- **THEN** el sistema DEBERÁ guardar la preferencia en SharedPreferences

### Requirement: Recordar tema al iniciar (REQ-002)
La app cargará el tema guardado al abrir.

#### Scenario: App inicia con tema oscuro guardado
- **GIVEN** el usuario tiene guardado "tema oscuro"
- **WHEN** la app inicia
- **THEN** el sistema DEBERÁ mostrar el tema oscuro sin intervención del usuario

#### Scenario: Primera vez sin preferencia
- **GIVEN** el usuario nunca cambió el tema
- **WHEN** la app inicia
- **THEN** el sistema DEBERÁ usar el tema claro por defecto
```

#### Paso 4: design.md — NO se crea

Es Simple. La skill `clean-arch-feature` derivará los archivos automáticamente de los requisitos.

#### Paso 5: tasks.md

```
## 1. Dominio y datos base
- [ ] 1.1 Crear enum ThemeMode en `lib/core/theme/app_theme.dart` (REQ-001)

## 2. Capa de datos
- [ ] 2.1 Crear ThemeLocalDataSource en `lib/core/theme/theme_local_data_source.dart` (REQ-002)

## 3. Implementaciones
- [ ] 3.1 Crear ThemeCubit + ThemeState en `lib/core/theme/cubit/theme_cubit.dart` (REQ-001, REQ-002)

## 4. Presentación e integración
- [ ] 4.1 Agregar toggle en settings_page.dart (REQ-001)
- [ ] 4.2 Cargar tema guardado en main.dart (REQ-002)

## 5. Tests
- [ ] 5.1 Test ThemeCubit: cambiar tema + persistir (REQ-001, REQ-002)

## Trazabilidad
| Req | Tarea(s) | Test | Cubre escenario |
|-----|----------|------|-----------------|
| REQ-001 | 1.1, 2.1, 3.1, 4.1 | 5.1 | Toggle + persistir |
| REQ-002 | 2.1, 3.1, 4.2 | 5.1 | Cargar tema guardado + defecto |
```

#### Paso 6: Implementar y cerrar

**Modo completo (recomendado para Simple):**
```bash
/opsx-apply-change
# La IA escribe todo (son ~3 ficheros pequeños) y marca - [x]
# Auditas rápido cada diff contra REQ-001/REQ-002
```

**Modo andamiaje:** mismo comando, pero el agente genera el scaffold de los ~3 ficheros, deja las casillas en `- [ ]` y pausa; tú implementas el cubit (2 métodos: toggleTheme, loadTheme) y continúas.

```bash
# Cerrar
/opsx-verify-change
/opsx-archive-change
```

**Lo que aprendiste:** Un cambio Simple se resuelve en ~30 minutos. Solo necesitas proposal + spec. Sin design.md. Con `Modo: andamiaje` el agente deja el scaffold y tú implementas 2-3 métodos pequeños; con `Modo: completo` la IA lo escribe todo y tú auditas.

---

### Ejemplo B: Intermedia — Gestión de perfil de usuario

**Contexto:** Los usuarios necesitan ver y editar su perfil (nombre, email, foto). Ya existe la feature `auth` con login. Necesitas una pantalla de perfil que lea/escriba a Supabase.

**Clasificación:** Intermedia → design.md ligero, 1-2 puertas.

#### Paso 1: Crear el cambio

```bash
/opsx-propose add-user-profile
```

#### Paso 2: proposal.md

```
# Proposal: add-user-profile

## Impacto (Impact Report)
- Features afectadas: `auth` (user entity existente), `core/di` (+1 registro), `app_router` (+1 ruta)
- Reutilizable: `User` entity de auth, `Failure` hierarchy, patrón CRUD existente
- Supabase: tabla `profiles` nueva, RLS por dueño, migración nº 0008
- DI / rutas: service_locator.dart (+1 registro), app_router.dart (+1 ruta `/profile` con guard)
- Riesgos:actualización de perfil concurrente (2 pestañas), validación de email duplicado

## Why (Problema)
Los usuarios no pueden ver ni editar su perfil después del registro. El nombre se muestra como email completo y no hay forma de subir foto.

## What Changes (Solución)
Pantalla de perfil con visualización y edición de nombre, email y foto de perfil. Foto se sube a Supabase Storage.

## Capabilities
### New Capabilities
- `user-profile`: visualización y edición de perfil con upload de foto

## Scope (Alcance)
**Incluye:**
- Ver perfil (nombre, email, foto)
- Editar nombre y bio
- Subir foto de perfil (máx 2MB, JPEG/PNG)
- Pull-to-refresh para recargar datos

**No incluye:**
- Cambiar email (requiere verificación)
- Cambiar contraseña
- Verificación de email
- Eliminar cuenta

**Dependencias:** autenticación (login existente), Supabase Storage
**Suposiciones:** un usuario tiene un solo perfil; la foto se almacena en bucket `avatars`
**Preguntas abiertas:** ~~¿editar email requiere verificación?~~ → SÍ, fuera de alcance por ahora

## Actores y permisos
| Actor | Puede | No puede | Mapeo RLS |
|-------|-------|----------|-----------|
| Usuario | Ver/editar su perfil, subir su foto | Ver/editar perfil ajeno | `auth.uid() = user_id` |
| Admin | Ver perfiles (lectura) | Editar perfiles | claim `role = 'admin'` solo lectura |

## Impact
- Código: ~10 ficheros nuevos en `lib/features/user_profile/`
- Datos: 1 tabla + storage bucket + RLS + migración 0008
- Breaking changes: ninguno
```

#### Paso 3: spec.md

```
# Spec: user-profile

## WHY
El nombre del usuario se muestra como email completo después del registro. No hay forma de personalizar el perfil ni subir foto.

## Purpose
Permitir al usuario ver y editar su perfil (nombre, bio, foto) con validación de datos y upload seguro a Supabase Storage.

## ADDED Requirements

### Requirement: Ver perfil propio (REQ-001)
El usuario verá su perfil completo al acceder a la pantalla.

#### Scenario: Perfil con datos completos
- **GIVEN** un usuario con nombre, email y foto
- **WHEN** accede a la pantalla de perfil
- **THEN** el sistema DEBERÁ mostrar nombre, email, foto y bio

#### Scenario: Perfil sin datos opcionales
- **GIVEN** un usuario sin nombre ni bio establecidos
- **WHEN** accede a la pantalla de perfil
- **THEN** el sistema DEBERÁ mostrar "---" en nombre y bio, y un avatar por defecto

### Requirement: Editar nombre y bio (REQ-002)
El usuario editará su nombre y bio desde la pantalla de perfil.

#### Scenario: Editar nombre exitosamente
- **WHEN** el usuario guarda un nombre válido (2-50 caracteres)
- **THEN** el sistema DEBERÁ actualizar el perfil y mostrar "Perfil actualizado"

#### Scenario: Nombre muy corto
- **IF** el nombre tiene menos de 2 caracteres
- **THEN** el sistema DEBERÁ mostrar "El nombre debe tener al menos 2 caracteres"

#### Scenario: Nombre muy largo
- **IF** el nombre tiene más de 50 caracteres
- **THEN** el sistema DEBERÁ mostrar "El nombre no puede exceder 50 caracteres"

### Requirement: Subir foto de perfil (REQ-003)
El usuario subirá una foto de perfil desde la galería o cámara.

#### Scenario: Foto válida
- **WHEN** el usuario selecciona una imagen JPEG o PNG menor a 2MB
- **THEN** el sistema DEBERÁ subirla a Supabase Storage y actualizar la foto del perfil

#### Scenario: Archivo demasiado grande
- **IF** la imagen supera 2MB
- **THEN** el sistema DEBERÁ mostrar "La imagen no puede exceder 2MB"

#### Scenario: Formato no válido
- **IF** el archivo no es JPEG ni PNG
- **THEN** el sistema DEBERÁ mostrar "Solo se permiten archivos JPEG o PNG"

### Requirement: Aislamiento de perfil (REQ-004)
Cada usuario accederá únicamente a su propio perfil.

#### Scenario: Lectura propia
- **GIVEN** un usuario autenticado
- **WHEN** consulta su perfil
- **THEN** solo recibe su propia fila (`auth.uid() = user_id`)

#### Scenario: Intento de acceso ajeno
- **IF** un usuario intenta leer o editar el perfil de otro
- **THEN** Supabase DEBERÁ devolver conjunto vacío vía RLS
```

#### Paso 4: design.md (ligero)

```
# Design: user-profile

## Context
Existe la feature `auth` con User entity y login. Falta pantalla de perfil. Se necesita CRUD sobre tabla `profiles`.

## Goals / Non-Goals
- ✅ CRUD de perfil con validación
- ✅ Upload de foto a Supabase Storage
- ❌ Cambio de email (requiere verificación)
- ❌ Eliminar cuenta

## Decisions

### D1: Storage bucket `avatars` público vs privado
- Decision: bucket privado con URL firmada temporal
- Alternativas descartadas: público (riesgo de scraping de fotos)
- Por qué: fotos son datos personales; URL firmada expira en 1h

### D2: Validación de foto en cliente vs servidor
- Decision: validación en cliente (tamaño, formato) + Supabase RPC para resize
- Alternativas descartadas: solo servidor (latencia innecesaria para validación básica)
- Por qué: feedback inmediato al usuario; el servidor solo confirma

## Ficheros afectados
| Elemento | Capa | Archivo | Req |
|----------|------|---------|-----|
| UserProfile | domain/entity | `lib/features/user_profile/domain/entities/user_profile.dart` | REQ-001 |
| UserProfileRepository | domain/repository | `lib/features/user_profile/domain/repositories/user_profile_repository.dart` | REQ-001..004 |
| UserProfileModel | data/model | `lib/features/user_profile/data/models/user_profile_model.dart` | REQ-001 |
| UserProfileRemoteDataSource | data/datasource | `lib/features/user_profile/data/datasources/user_profile_remote_data_source.dart` | REQ-001..003 |
| UserProfileRepositoryImpl | data/repositories | `lib/features/user_profile/data/repositories/user_profile_repository_impl.dart` | REQ-001..004 |
| GetUserProfile | domain/usecase | `lib/features/user_profile/domain/usecases/get_user_profile.dart` | REQ-001 |
| UpdateUserProfile | domain/usecase | `lib/features/user_profile/domain/usecases/update_user_profile.dart` | REQ-002 |
| UploadProfilePhoto | domain/usecase | `lib/features/user_profile/domain/usecases/upload_profile_photo.dart` | REQ-003 |
| UserProfileCubit | presentation/cubit | `lib/features/user_profile/presentation/cubit/user_profile_cubit.dart` | REQ-001..003 |
| UserProfilePage | presentation/pages | `lib/features/user_profile/presentation/pages/user_profile_page.dart` | REQ-001..003 |

## Contratos Dart clave

```dart
abstract interface class UserProfileRepository {
  Future<Either<Failure, UserProfile>> getProfile(String userId);
  Future<Either<Failure, Unit>> updateProfile({required String userId, required String name, String? bio});
  Future<Either<Failure, String>> uploadPhoto({required String userId, required File image});
}

sealed class UserProfileState {}
class UserProfileInitial extends UserProfileState {}
class UserProfileLoading extends UserProfileState {}
class UserProfileLoaded extends UserProfileState {
  final UserProfile profile;
  UserProfileLoaded(this.profile);
}
class UserProfileError extends UserProfileState {
  final String message;
  UserProfileError(this.message);
}
```

## Flujo de datos

```
UserProfilePage ──load──► UserProfileCubit.getProfile()
                              │ emit UserProfileLoading
                              ▼
                       GetUserProfile(repository)
                              ▼
                       UserProfileRepositoryImpl ──► UserProfileRemoteDataSource.getProfile()
                              │                           │ supabase.from('profiles').select().eq('user_id', uid)
                              ▼                           ▼
                       ◄── Either.right(UserProfile) ◄── respuesta
                       │
                       └── Either.left(Failure) ──► UserProfileError(msg) ──► SnackBar
```

## Backend Supabase
- **Tabla:** `profiles` (user_id UUID PK FK → auth.users, name TEXT, bio TEXT, photo_url TEXT, created_at TIMESTAMPTZ)
- **RLS:** auth.uid() = user_id (lectura y escritura propia); admin solo lectura vía claim
- **Storage:** bucket `avatars` (privado, URL firmada 1h)
- **Migración:** supabase/migrations/0008_profiles.sql

## Boundaries
- Foto subida a Storage, URL guardada en tabla profiles (no foto inline)
- Validación de tamaño/formato solo en cliente
- Nombre obligatorio (2-50 chars), bio opcional (max 500 chars)
```

#### Paso 5: tasks.md

```
## 1. Dominio
- [ ] 1.1 Entity UserProfile en `lib/features/user_profile/domain/entities/user_profile.dart` (REQ-001)
- [ ] 1.2 Interface UserProfileRepository en `lib/features/user_profile/domain/repositories/user_profile_repository.dart` (REQ-001..004)
- [ ] 1.3 UseCases: GetUserProfile, UpdateUserProfile, UploadProfilePhoto (REQ-001..003)

## 2. Capa de datos + Backend Supabase
- [ ] 2.1 Migración SQL tabla profiles + RLS (REQ-004)
- [ ] 2.2 UserProfileModel (fromJson/toJson, snake_case mapping) (REQ-001)
- [ ] 2.3 UserProfileRemoteDataSource (select, update, storage upload) (REQ-001..003)
- [ ] 2.4 UserProfileRepositoryImpl (Either wrapper + Failure mapping) (REQ-001..004)

## 3. Estado y presentación
- [ ] 3.1 UserProfileState sealed (Initial, Loading, Loaded, Error) (REQ-001..003)
- [ ] 3.2 UserProfileCubit (getProfile, updateProfile, uploadPhoto) (REQ-001..003)
- [ ] 3.3 UserProfilePage (form con nombre, bio, foto) (REQ-001..003)

## 4. Integración
- [ ] 4.1 Registro en service_locator.dart (+1)
- [ ] 4.2 Ruta en app_router.dart (+1 con guard de sesión)

## 5. Tests
- [ ] 5.1 Test UserProfileModel: roundtrip JSON (REQ-001)
- [ ] 5.2 Test UserProfileCubit: getProfile, updateProfile, uploadPhoto (REQ-001..003)
- [ ] 5.3 Test UserProfilePage: estados loading, loaded, error (REQ-001..003)

## Trazabilidad
| Req | Tarea(s) | Test | Cubre escenario |
|-----|----------|------|-----------------|
| REQ-001 | 1.1, 1.2, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3 | 5.1, 5.2, 5.3 | Ver perfil + datos vacíos |
| REQ-002 | 1.3, 3.2, 3.3 | 5.2, 5.3 | Editar nombre exitoso + corto + largo |
| REQ-003 | 1.3, 2.3, 3.2, 3.3 | 5.2, 5.3 | Upload válido + grande + formato inválido |
| REQ-004 | 2.1 | 5.2 | Aislamiento RLS |
```

#### Paso 6: Validar y cerrar

```bash
# Puerta 1: validar requisitos
openspec validate

# Puerta 2: validar diseño
openspec validate

# Puerta 3: validar tareas
openspec validate
```

**Modo andamiaje:** `/opsx-apply-change` genera scaffold por tarea (bodies en `throw UnimplementedError()` + TODOs citando REQ) y pausa; tú implementas body por body.
**Modo completo:** `/opsx-apply-change` escribe todo el cambio → auditas cada diff con `06-auditoria-codigo-ia.md`.

```bash
/opsx-verify-change
/opsx-archive-change
```

**Lo que aprendiste:** Intermedia tiene design.md ligero. Los requisitos crecen (4 REQs, 10 escenarios) pero no se vuelven enormes. Las decisiones son pocas pero importantes (Storage privado vs público). La tabla de ficheros afectados ya es clave para que el agente no invente rutas.

---

### Ejemplo C: Compleja — Sistema de pagos con pasarela

**Contexto:** Tu app de e-commerce necesita cobrar. Integrarás una pasarela de pago (Stripe), crearás órdenes de compra, y manejarás estados de pago (pendiente, pagado, fallido, reembolsado). Toca múltiples features existentes (carrito, productos, inventario).

**Clasificación:** Compleja → design.md completo, 3 puertas.

#### Paso 1: Crear el cambio

```bash
/opsx-propose add-payments
```

#### Paso 2: proposal.md

```
# Proposal: add-payments

## Impacto (Impact Report)
- Features afectadas: `cart` (vaciar al pagar), `products` (descontar stock), `auth` (user_id para cobro), `core/di` (+3 registros), `app_router` (+2 rutas)
- Reutilizable: `Failure` hierarchy, `Cart` entity, patrón UseCase, `Either` pattern
- Supabase: tablas `orders`, `payments` nuevas; tabla `products` modificada (stock); 1 RPC `process_payment`; RLS por dueño; migración nº 0009
- DI / rutas: service_locator.dart (+3), app_router.dart (+2: `/checkout`, `/payment-result`)
- Riesgos: **pagos dobles** si falla la red entre Stripe y Supabase; **stock negativo** si 2 usuarios pagan el último ítem simultáneamente; **PCI compliance** (nunca almacenar datos de tarjeta)

## Why (Problema)
Los usuarios pueden agregar productos al carrito pero no tienen forma de pagar. El negocio no genera ingresos.

## What Changes (Solución)
Flujo de checkout completo: resumen del carrito → selección de método de pago → proceso de pago vía Stripe → confirmación y vaciado del carrito → historial de órdenes.

## Capabilities
### New Capabilities
- `checkout`: flujo de pago con Stripe, confirmación de orden, vaciado de carrito
- `payment-history`: historial de órdenes y estados de pago del usuario

## Scope (Alcance)
**Incluye:**
- Pantalla de checkout con resumen del carrito
- Proceso de pago con Stripe (tarjeta crédito/débito)
- Estados de pago: pendiente, pagado, fallido, reembolsado
- Vaciar carrito al pago exitoso
- Descontar stock al confirmar pago
- Historial de órdenes del usuario
- Webhook de Stripe para confirmar pagos async

**No incluye:**
- Métodos de pago adicionales (PayPal, transferencia)
- Facturación electrónica
- Reembolsos manuales (solo vía Stripe dashboard)
- Suscripciones o pagos recurrentes

**Dependencias:** Stripe API key, autenticación, carrito existente, productos con stock
**Suposiciones:** un pago = una orden; el stock se descuenta al confirmar (no al iniciar checkout); el webhook de Stripe llega en <30s
**Preguntas abiertas:** ~~¿reembolsos manuales?~~ → NO, vía Stripe dashboard; ~~¿stock se descuenta al iniciar checkout?~~ → NO, al confirmar pago

## Actores y permisos
| Actor | Puede | No puede | Mapeo RLS |
|-------|-------|----------|-----------|
| Cliente | Iniciar checkout, pagar, ver sus órdenes | Pagar por otro usuario, ver órdenes ajenas | `auth.uid() = user_id` |
| Admin | Ver todas las órdenes, procesar reembolsos | Crear órdenes por clientes | claim `role = 'admin'` |
| Stripe (webhook) | Confirmar estado de pago | Modificar datos de orden | verificar firma webhook |

## Impact
- Código: ~20 ficheros nuevos en `lib/features/checkout/` y `lib/features/payment_history/`
- Datos: 2 tablas nuevas + 1 RPC + RLS + migración 0009
- Breaking changes: `cart` se vacía al confirmar pago (comportamiento esperado)
```

#### Paso 3: spec.md

```
# Spec: checkout + payment-history

## WHY
El carrito existe pero no hay forma de cobrar. Los usuarios agregan productos pero nunca completan la compra.

## Purpose
Procesar pagos de forma segura con Stripe, crear órdenes, gestionar estados de pago, y mostrar historial al usuario.

## ADDED Requirements

### Requirement: Iniciar checkout (REQ-001)
El usuario verá el resumen de su carrito antes de pagar.

#### Scenario: Checkout con items
- **GIVEN** un carrito con 2 o más items
- **WHEN** el usuario accede a checkout
- **THEN** el sistema DEBERÁ mostrar resumen con items, subtotal, impuesto, total y botón "Pagar"

#### Scenario: Checkout con carrito vacío
- **IF** el carrito está vacío
- **THEN** el sistema DEBERÁ mostrar "Tu carrito está vacío" y redirigir a la tienda

### Requirement: Procesar pago con Stripe (REQ-002)
El sistema procesará el pago de forma segura.

#### Scenario: Pago exitoso
- **WHEN** el usuario confirma el pago y Stripe responde con status "succeeded"
- **THEN** el sistema DEBERÁ crear la orden, vaciar el carrito, descontar stock y mostrar "Pago exitoso"

#### Scenario: Pago rechazado por Stripe
- **IF** Stripe responde con status "failed"
- **THEN** el sistema DEBERÁ mostrar "El pago fue rechazado. Intenta con otro método" y mantener el carrito

#### Scenario: Error de red durante pago
- **IF** la comunicación con Stripe se interrumpe
- **THEN** el sistema DEBERÁ mostrar "Error de conexión. Verifica tu estado de pago antes de reintentar"

#### Scenario: Pago doble (idempotencia)
- **IF** el usuario presiona "Pagar" dos veces rápidamente
- **THEN** el sistema DEBERÁ procesar solo un pago (idempotency key de Stripe)

### Requirement: Confirmar pago vía webhook (REQ-003)
El sistema confirmará pagos pendientes cuando Stripe envíe el webhook.

#### Scenario: Webhook payment_intent.succeeded
- **GIVEN** una orden con estado "pendiente"
- **WHEN** llega el webhook payment_intent.succeeded de Stripe
- **THEN** el sistema DEBERÁ actualizar el estado a "pagado", vaciar carrito y descontar stock

#### Scenario: Webhook con firma inválida
- **IF** la firma del webhook no es válida
- **THEN** el sistema DEBERÁ rechazar el webhook con status 401 y no modificar datos

### Requirement: Gestionar estados de pago (REQ-004)
Cada orden tendrá un estado rastreable.

#### Scenario: Estados válidos
- **MIENTRAS** una orden exista
- **EL SISTEMA DEBERÁ** permitir solo transiciones válidas: pendiente → pagado, pendiente → fallido, pagado → reembolsado

#### Scenario: Transición inválida
- **IF** se intenta una transición no válida (ej: pagado → pendiente)
- **THEN** el sistema DEBERÁ rechazar la actualización

### Requirement: Aislamiento de órdenes (REQ-005)
Cada usuario verá solo sus propias órdenes.

#### Scenario: Lectura propia
- **GIVEN** un usuario autenticado
- **WHEN** consulta su historial de órdenes
- **THEN** solo recibe filas donde `auth.uid() = user_id`

#### Scenario: Intento de acceso ajeno
- **IF** un usuario intenta leer la orden de otro usuario
- **THEN** Supabase DEBERÁ devolver conjunto vacío vía RLS

### Requirement: Historial de órdenes (REQ-006)
El usuario verá su historial de compras.

#### Scenario: Con órdenes previas
- **GIVEN** un usuario con 3 órdenes pagadas
- **WHEN** accede al historial
- **THEN** el sistema DEBERÁ mostrar las 3 órdenes ordenadas por fecha descendente con total y estado

#### Scenario: Sin órdenes
- **GIVEN** un usuario sin órdenes
- **WHEN** accede al historial
- **THEN** el sistema DEBERÁ mostrar "Aún no tienes órdenes"
```

#### Paso 4: design.md (completo)

```
# Design: checkout + payment-history

## Context
Existe carrito con items y productos con stock. Falta el flujo de cobro. Se integra Stripe como pasarela.

## Goals / Non-Goals
- ✅ Pago seguro con Stripe (PCI: nunca almacenar datos de tarjeta)
- ✅ Órdenes con estados rastreables
- ✅ Idempotencia (sin pagos dobles)
- ✅ Webhook para confirmaciones async
- ❌ Métodos de pago alternativos
- ❌ Facturación electrónica
- ❌ Reembolsos manuales

## Decisions

### D1: Confirmar pago al recibir webhook vs al recibir respuesta de Stripe
- Decision: confirmar al recibir webhook payment_intent.succeeded
- Alternativas descartadas: confirmar al recibir respuesta de Stripe (puede ser ambigua si la red falla)
- Por qué: el webhook es la fuente de verdad de Stripe; la respuesta de la API puede ser incompleta si hay timeout

### D2: Descontar stock al iniciar checkout vs al confirmar pago
- Decision: descontar stock al confirmar pago (no al iniciar checkout)
- Alternativas descartadas: descontar al iniciar (bloquea stock durante minutos, reduce ventas)
- Por qué: stock negativo es preferible a stock bloqueado; si 2 usuarios pagan el último ítem, el segundo recibe "sin stock" al confirmar

### D3: Idempotency key generada en cliente vs servidor
- Decision: generar en servidor (una por checkout)
- Alternativas descartadas: en cliente (manipulable)
- Por qué: el servidor es la autoridad; el idempotency key se almacena en tabla payments

### D4: Tabla orders separada vs extender cart_items
- Decision: tabla `orders` separada con `order_items`
- Alternativas descartadas: extender cart_items con campos de orden
- Por qué: carrito es temporal, orden es persistente; separación de responsabilidades

## Ficheros afectados
| Elemento | Capa | Archivo | Req |
|----------|------|---------|-----|
| Order | domain/entity | `lib/features/checkout/domain/entities/order.dart` | REQ-004 |
| OrderItem | domain/entity | `lib/features/checkout/domain/entities/order_item.dart` | REQ-001 |
| Payment | domain/entity | `lib/features/checkout/domain/entities/payment.dart` | REQ-002 |
| PaymentStatus | domain/enum | `lib/features/checkout/domain/enums/payment_status.dart` | REQ-004 |
| CheckoutRepository | domain/repository | `lib/features/checkout/domain/repositories/checkout_repository.dart` | REQ-001..005 |
| OrderRepository | domain/repository | `lib/features/payment_history/domain/repositories/order_repository.dart` | REQ-005..006 |
| OrderModel | data/model | `lib/features/checkout/data/models/order_model.dart` | REQ-004 |
| PaymentModel | data/model | `lib/features/checkout/data/models/payment_model.dart` | REQ-002 |
| CheckoutRemoteDataSource | data/datasource | `lib/features/checkout/data/datasources/checkout_remote_data_source.dart` | REQ-001..003 |
| OrderRemoteDataSource | data/datasource | `lib/features/payment_history/data/datasources/order_remote_data_source.dart` | REQ-005..006 |
| CheckoutRepositoryImpl | data/repositories | `lib/features/checkout/data/repositories/checkout_repository_impl.dart` | REQ-001..005 |
| OrderRepositoryImpl | data/repositories | `lib/features/payment_history/data/repositories/order_repository_impl.dart` | REQ-005..006 |
| InitiateCheckout | domain/usecase | `lib/features/checkout/domain/usecases/initiate_checkout.dart` | REQ-001 |
| ProcessPayment | domain/usecase | `lib/features/checkout/domain/usecases/process_payment.dart` | REQ-002 |
| ConfirmPayment | domain/usecase | `lib/features/checkout/domain/usecases/confirm_payment.dart` | REQ-003 |
| GetOrderHistory | domain/usecase | `lib/features/payment_history/domain/usecases/get_order_history.dart` | REQ-006 |
| CheckoutCubit | presentation/cubit | `lib/features/checkout/presentation/cubit/checkout_cubit.dart` | REQ-001..004 |
| CheckoutPage | presentation/pages | `lib/features/checkout/presentation/pages/checkout_page.dart` | REQ-001..002 |
| PaymentResultPage | presentation/pages | `lib/features/checkout/presentation/pages/payment_result_page.dart` | REQ-002 |
| OrderHistoryCubit | presentation/cubit | `lib/features/payment_history/presentation/cubit/order_history_cubit.dart` | REQ-006 |
| OrderHistoryPage | presentation/pages | `lib/features/payment_history/presentation/pages/order_history_page.dart` | REQ-006 |
| StripeWebhookHandler | edge/function | `supabase/functions/stripe-webhook/index.ts` | REQ-003 |

## Contratos Dart clave

```dart
abstract interface class CheckoutRepository {
  Future<Either<Failure, Order>> initiateCheckout(String userId);
  Future<Either<Failure, Payment>> processPayment({required String orderId, required String paymentMethodId});
  Future<Either<Failure, Unit>> confirmPayment(String paymentIntentId);
}

abstract interface class OrderRepository {
  Future<Either<Failure, List<Order>>> getOrdersByUser(String userId);
}

sealed class CheckoutState {}
class CheckoutInitial extends CheckoutState {}
class CheckoutLoading extends CheckoutState {}
class CheckoutSummary extends CheckoutState {
  final Order order;
  final double subtotal;
  final double tax;
  final double total;
  CheckoutSummary({required this.order, required this.subtotal, required this.tax, required this.total});
}
class CheckoutProcessing extends CheckoutState {}
class CheckoutSuccess extends CheckoutState {
  final String orderId;
  CheckoutSuccess(this.orderId);
}
class CheckoutError extends CheckoutState {
  final String message;
  CheckoutError(this.message);
}
```

## Flujo de datos

```
CheckoutPage ──initiate──► CheckoutCubit.initiateCheckout()
                              │ emit CheckoutLoading
                              ▼
                       InitiateCheckout(repository)
                              ▼
                       CheckoutRepositoryImpl ──► crear orden + order_items en Supabase
                              ▼
                       ◄── Either.right(Order)
                              ▼
                       emit CheckoutSummary(order, subtotal, tax, total)
                              │
User toca "Pagar" ──────► CheckoutCubit.processPayment(paymentMethodId)
                              │ emit CheckoutProcessing
                              ▼
                       ProcessPayment(repository) ──► Stripe.createPaymentIntent(amount, currency)
                              │                           │
                              │                           ▼
                              │                       Stripe procesa
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         succeeded        failed         network_error
              │               │               │
              ▼               ▼               ▼
     ConfirmPayment    CheckoutError   CheckoutError
     (webhook)         "rechazado"     "verifica estado"
              │
              ▼
     actualizar estado → pagado
     vaciar carrito
     descontar stock
              │
              ▼
     CheckoutSuccess ──► PaymentResultPage
```

## Backend Supabase
- **Tabla `orders`:** id UUID PK, user_id UUID FK → auth.users, status TEXT (pending/paid/refunded/failed), total DECIMAL, created_at TIMESTAMPTZ
- **Tabla `order_items`:** id UUID PK, order_id UUID FK → orders, product_id UUID FK → products, quantity INT, unit_price DECIMAL
- **Tabla `payments`:** id UUID PK, order_id UUID FK → orders, stripe_payment_intent_id TEXT UNIQUE, amount DECIMAL, currency TEXT, status TEXT, idempotency_key TEXT UNIQUE, created_at TIMESTAMPTZ
- **Tabla `products`:** MODIFICADA — agregar columna `stock INT NOT NULL DEFAULT 0`
- **RLS orders:** auth.uid() = user_id (lectura); admin solo lectura vía claim
- **RLS order_items:** hereda de orders
- **RLS payments:** auth.uid() = user_id (solo lectura de sus pagos)
- **RPC `decrement_stock`:** function security definer que decrementa stock atómicamente (evita race condition)
- **Edge Function:** `stripe-webhook` (verifica firma, actualiza estado)
- **Migración:** supabase/migrations/0009_payments.sql

## Boundaries
- Nunca almacenar datos de tarjeta (PCI compliance)
- Idempotency key obligatoria en cada payment intent
- Webhook siempre verificado con firma Stripe
- Stock decrementado solo al confirmar pago (no al iniciar checkout)
- Transiciones de estado válidas forzadas en la DB (CHECK constraint)
```

#### Paso 5: tasks.md

```
## 1. Dominio
- [ ] 1.1 Entity Order + OrderItem en `lib/features/checkout/domain/entities/` (REQ-001, REQ-004)
- [ ] 1.2 Entity Payment en `lib/features/checkout/domain/entities/payment.dart` (REQ-002)
- [ ] 1.3 Enum PaymentStatus en `lib/features/checkout/domain/enums/payment_status.dart` (REQ-004)
- [ ] 1.4 Interfaces CheckoutRepository + OrderRepository (REQ-001..006)
- [ ] 1.5 UseCases: InitiateCheckout, ProcessPayment, ConfirmPayment, GetOrderHistory (REQ-001..006)

## 2. Capa de datos + Backend Supabase
- [ ] 2.1 Migración SQL: tablas orders, order_items, payments + RLS + CHECK constraints (REQ-004, REQ-005)
- [ ] 2.2 RPC decrement_stock (security definer) (REQ-002)
- [ ] 2.3 Edge Function stripe-webhook (verificar firma + confirmar) (REQ-003)
- [ ] 2.4 OrderModel + PaymentModel (fromJson/toJson, snake_case) (REQ-004)
- [ ] 2.5 CheckoutRemoteDataSource (crear orden, procesar pago, confirmar) (REQ-001..003)
- [ ] 2.6 OrderRemoteDataSource (consultar historial) (REQ-005..006)
- [ ] 2.7 CheckoutRepositoryImpl (Either + Failure mapping + idempotency) (REQ-001..005)
- [ ] 2.8 OrderRepositoryImpl (historial) (REQ-005..006)

## 3. Estado y presentación
- [ ] 3.1 CheckoutState sealed (Initial, Loading, Summary, Processing, Success, Error) (REQ-001..004)
- [ ] 3.2 CheckoutCubit (initiateCheckout, processPayment) (REQ-001..004)
- [ ] 3.3 OrderHistoryCubit (getOrders) (REQ-006)
- [ ] 3.4 CheckoutPage (resumen + botón pagar) (REQ-001, REQ-002)
- [ ] 3.5 PaymentResultPage (éxito/error) (REQ-002)
- [ ] 3.6 OrderHistoryPage (lista de órdenes) (REQ-006)

## 4. Integración
- [ ] 4.1 Registro en service_locator.dart (+3)
- [ ] 4.2 Rutas en app_router.dart (+2: /checkout, /payment-result)

## 5. Tests
- [ ] 5.1 Test OrderModel + PaymentModel: roundtrip JSON (REQ-004)
- [ ] 5.2 Test CheckoutCubit: initiateCheckout, processPayment success/failure (REQ-001..004)
- [ ] 5.3 Test OrderHistoryCubit: getOrders empty/populated (REQ-006)
- [ ] 5.4 Test CheckoutPage: estados Summary, Processing, Success, Error (REQ-001..002)
- [ ] 5.5 Test webhook handler: firma válida/inválida (REQ-003)

## Trazabilidad
| Req | Tarea(s) | Test | Cubre escenario |
|-----|----------|------|-----------------|
| REQ-001 | 1.1, 1.4, 1.5, 2.5, 2.7, 3.1, 3.2, 3.4 | 5.2, 5.4 | Checkout con items + vacío |
| REQ-002 | 1.2, 1.5, 2.5, 2.7, 3.2, 3.4, 3.5 | 5.2, 5.4 | Pago exitoso + rechazado + red + doble |
| REQ-003 | 2.2, 2.3 | 5.5 | Webhook válido + firma inválida |
| REQ-004 | 1.1, 1.3, 2.1, 2.4, 3.1 | 5.1, 5.2 | Estados válidos + transición inválida |
| REQ-005 | 2.1 | 5.2 | Aislamiento RLS |
| REQ-006 | 1.5, 2.6, 2.8, 3.3, 3.6 | 5.3, 5.4 | Historial con/sin órdenes |
```

#### Paso 6: Validar y cerrar

```bash
# Puerta 1: requisitos
openspec validate

# Puerta 2: diseño
openspec validate

# Puerta 3: tareas
openspec validate
```

**Modo completo (recomendado para Compleja — mejor grano para auditar):**
```bash
/opsx-apply-change
# La IA implementa todo — MUCHO más código, audita con cuidado
# Especial atención a: idempotency, webhook firma, CHECK constraints
```

> **Modo andamiaje:** mismo comando — el agente genera el scaffold por tarea y pausa; tú implementas la parte crítica (idempotency, Failure mapping, transiciones de estado) antes de continuar con la siguiente tarea.

```bash
/opsx-verify-change
/opsx-archive-change
```

**Lo que aprendiste:** Compleja toca múltiples features existentes, tiene 6 REQs con 14 escenarios, 4 decisiones técnicas con alternativas, 20+ ficheros, y requiere atención especial a seguridad (Stripe webhook, idempotency, RLS). Las 3 puertas son necesarias porque un error en pagos es costoso.

---

## 7. Comandos OpenSpec — Referencia rápida

| Momento | Comando | Qué hace |
|---------|---------|----------|
| Explorar antes de decidir | `/opsx-explore` | IA lee codebase y sugiere opciones (no crea archivos) |
| Crear cambio (artesano) | `/opsx-new-change` | Crea esqueleto de 4 archivos |
| Crear cambio (copiloto) | `/opsx-propose add-nombre` | IA genera 4 archivos completos |
| Crear cambio (fast-forward) | `/opsx-ff-change add-nombre` | Propose + todos los artifacts en un solo paso |
| Continuar cambio existente | `/opsx-continue-change` | Reabre un cambio para iterar |
| Registrar progreso | `/opsx-update-change` | Actualiza checklist de tareas |
| Implementar (respeta el Modo de tasks.md) | `/opsx-apply-change` | andamiaje: scaffold por tarea + pausa · completo: IA escribe todo |
| Verificar contra specs | `/opsx-verify-change` | Valida código vs requisitos (solo reporte) |
| Archivar cambio | `/opsx-archive-change` | Consolida specs y archiva |
| Ver progreso de artifacts | `openspec status --change <id>` (CLI) | Checklist de qué artifacts faltan |
| Ver diffs antes de archivar | `openspec show <cambio> --diff` (CLI) | Diffs de requisitos contra specs principales |
| Ver un cambio o spec | `openspec show <item>` (CLI) | Reemplaza a `openspec change` y `openspec spec` (deprecated) |
| Validar formato | `openspec validate` (CLI) | Comprueba schemas de archivos |
| Verificar salud instalación | `openspec doctor` (CLI) | Diagnóstico de la instalación |

> **Deprecated:** `openspec change <id>` y `openspec spec <cap>` → usa `openspec show` en su lugar.

---

## Referencias

- Metodología central: [02-sdd-flutter-supabase.md](./02-sdd-flutter-supabase.md)
- Referencia de comandos: [03-openspec-guia-practica.md](./03-openspec-guia-practica.md)
- Plantilla de cambio: [04-plantilla-cambio-openspec.md](./04-plantilla-cambio-openspec.md)
- Cheat sheet: [05-referencia-rapida.md](./05-referencia-rapida.md)
- Auditoría de código: [06-auditoria-codigo-ia.md](./06-auditoria-codigo-ia.md)
- Ejemplos completos: [`ejemplos-cambios/`](./ejemplos-cambios/)
