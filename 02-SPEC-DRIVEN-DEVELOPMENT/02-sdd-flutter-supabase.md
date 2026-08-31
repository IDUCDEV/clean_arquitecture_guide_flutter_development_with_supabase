# 02 - SDD Aplicado a Flutter + Supabase

> La metodología del libro ([01-teoria-sdd.md](./01-teoria-sdd.md)) operativizada para tu stack: Flutter + Clean Architecture + BLoC/Cubit + fpdart + GetIt + GoRouter + Supabase.
>
> Este documento absorbe la metodología de diseño del módulo histórico `02-DISENIO-FEATURE` y la reescribe en terminología SDD estándar.

---

## El flujo completo

```
                    ┌─────────────────────────────────────────────┐
                    │  Paso 0 · IMPACT REPORT  (siempre primero)   │
                    └──────────────────────┬──────────────────────┘
                                           ▼
        ┌────────────────┐   Puerta 1   ┌────────────────┐
        │ FASE 1          │◄── humano ──│                 │
        │ Requisitos      │────────────►│ FASE 2          │
        │ (QUÉ construir) │             │ Diseño (CÓMO)   │
        └────────────────┘              └────────┬────────┘
                                                 │ Puerta 2 (humano)
                                                 ▼
                                        ┌────────────────┐
                                        │ FASE 3          │
                                        │ Tareas (ORDEN)  │
                                        └────────┬────────┘
                                                 │ Puerta 3 (humano)
                                                 ▼
                                        ┌────────────────┐
                                        │ FASE 4          │
                                        │ Implementación  │
                                        └────────┬────────┘
                                                 │ Revisión final + Clarity Gate
                                                 ▼
                                    openspec archive → specs vivas
```

**Regla de oro:** el agente no cruza una puerta sin aprobación humana. Corregir un requisito en la Puerta 1 cuesta minutos; corregirlo tras la implementación cuesta días.

**Herramienta:** cada fase vive en archivos concretos dentro de un *cambio* OpenSpec:

| Fase | Archivo | Contenido |
|------|---------|-----------|
| 0 + 1 | `proposal.md` | Impact Report resumido, problema, solución, alcance, actores |
| 1 (detallado) | `specs/{capacidad}/spec.md` | Requisitos EARS + escenarios, formato delta |
| 2 | `design.md` | Ficheros afectados, contratos Dart, flujo, backend Supabase, decisiones |
| 3 | `tasks.md` | Tareas atómicas agrupadas en oleadas |
| 4 | código + commits atómicos | Ejecución tarea por tarea |

Plantilla completa: [04-plantilla-cambio-openspec.md](./04-plantilla-cambio-openspec.md)

---

## Paso 0 · Impact Report (obligatorio en brownfield)

Todo proyecto real es brownfield: ya hay código. Antes de escribir UN solo requisito, analiza qué existe. *(El libro lo exige en su cap. 19; aquí está adaptado a un proyecto Clean Architecture.)*

Tres preguntas:
1. ¿Qué features existentes se ven afectadas?
2. ¿Qué puede reutilizarse (contratos, widgets, servicios, tablas)?
3. ¿Qué riesgos introduce el cambio?

Checklist específico de tu codebase:

```
[ ] Features similares: lib/features/*/  — ¿existe algo parecido? ¿patrón a copiar?
[ ] Entidades/contratos reutilizables: lib/features/*/domain/
[ ] Tablas Supabase afectadas: esquema, políticas RLS existentes
[ ] RPCs / vistas que consumen o alimentan
[ ] Registro DI: lib/core/di/service_locator.dart — ¿nuevos registros?
[ ] Rutas: lib/core/router/app_router.dart — ¿nueva pantalla? ¿guards?
[ ] Widgets/servicios compartidos: lib/core/ y lib/shared/
[ ] Convenciones: pubspec.yaml (paquetes disponibles), lints, naming
[ ] Migraciones previas: supabase/migrations/ — numeración siguiente
```

**Salida:** sección "Impacto" al inicio de `proposal.md` (5–15 líneas). Si el report revela que la feature toca 3+ dominios → proporcionalidad Compleja ([ver §Proporcionalidad](#proporcionalidad-según-complejidad)).

---

## Dos modos de crear el cambio

Toda feature nace como carpeta de cambio. Hay dos formas de llenarla, y **no son excluyentes** — puedes empezar artesano y terminar copiloto (o al revés):

| | Modo artesano (tú propones) | Modo copiloto (la IA propone) |
|---|---|---|
| Comando de arranque | `/opsx-new-change` o copiar [04-plantilla-cambio-openspec.md](./04-plantilla-cambio-openspec.md) | `/opsx-propose <nombre>` |
| Primera versión de la spec | La escribes TÚ, sin código | La redacta la IA desde tu descripción |
| Rol de la IA | Refina: busca ambigüedades, requisitos no verificables, supuestos ocultos | Propone desde cero y tú apruebas |
| Cómo refina | Conversación + `/opsx-update-change` | Conversación sobre su propia propuesta |
| Validación común | `openspec validate <cambio> --strict` + Clarity Gate | idem |
| Ideal para | Aprender, dominio crítico, diseño difícil, entrenar criterio | Velocidad, CRUD conocido, brownfield |

**Flujo del modo artesano:**

1. `/opsx-new-change` (o copia la plantilla) → esqueleto `proposal.md` + `specs/` + `design.md` + `tasks.md` listo
2. Llenas tú: proposal, requisitos EARS y design. Piensas primero — igual que se hacía con la hoja de diseño del método anterior
3. Pides revisión a la IA: *"revísame la spec: ¿qué escenario es ambiguo, qué requisito no es testeable, qué supuesto falta?"* → aplicas las mejoras con `/opsx-update-change`
4. `openspec validate <cambio> --strict`
5. Clarity Gate como prueba final: ¿otro agente, leyendo SOLO tu spec, produciría código equivalente?

Ambos modos convergen en la misma **Puerta 1**. La implementación posterior usa siempre el mismo motor —`/opsx-apply-change`—; lo único que varía es el **Modo** declarado en `tasks.md` (`andamiaje` | `completo`), independiente del modo de redacción elegido.

---

## Fase 1 · Requisitos — QUÉ construir

> Diluye los pasos **Alcance**, **Formular**, **Actorizar**, **Descomponer**, **Entidades** y **Reglas** del método anterior. Nada se pierde: cada pieza tiene su lugar exacto.

### 1.1 Historias precisas (antes "Formular")

Una historia precisa define: **actor** + **acción** + **objeto** + **propósito** + contexto.

```
❌ Vaga:    "El usuario podrá gestionar su carrito"
✅ Precisa: "Como cliente con sesión iniciada, quiero agregar productos a mi
            carrito para acumular mi pedido antes de pagar."
```

Prueba de precisión: ¿puedo escribir un test de aceptación sin preguntar nada más?

### 1.2 Actores y permisos (antes "Actorizar")

Tabla de actores con lo que pueden y NO pueden hacer. En Supabase esto mapea 1:1 a políticas RLS.

| Actor | Tipo | Puede | No puede |
|-------|------|-------|----------|
| Cliente | Primario (auth.uid()) | CRUD sus items, aplicar cupón | Ver carritos ajenos |
| Admin | Secundario (claim role) | Ver carritos abandonados | Modificar carrito ajeno |
| Inventario | Sistema interno | Validar stock vía RPC | — |

### 1.3 Alcance (antes "Paso Alcance")

Va directo a `proposal.md`: incluye / no incluye / dependencias / suposiciones / preguntas abiertas. Las preguntas abiertas se cierran ANTES de la Puerta 1 o se documentan como decisión pendiente.

### 1.4 Operaciones atómicas → requisitos dirigidos por evento (antes "Descomponer")

Enumera operaciones de una sola cosa, agrúpalas por actor, ordena dependencias. Luego **cada operación se convierte en un requisito** escrito en EARS.

### 1.5 Notación EARS (reemplaza al formato libre RN/RT/RS)

EARS elimina ambigüedad con 5 patrones. Cada requisito tiene ID único (`REQ-XXX`), nombre corto, cuerpo EARS y escenarios.

| Patrón | Plantilla | Uso típico en tu stack |
|--------|-----------|------------------------|
| Ubicuo | "El sistema DEBERÁ \<acción\>" | Reglas invariables (ej: precio unitario congelado al agregar) |
| Dirigido por evento | "CUANDO \<disparador\> EL sistema DEBERÁ \<acción\>" | Interacciones UI, eventos Cubit |
| Dirigido por estado | "MIENTRAS \<estado\> EL sistema DEBERÁ \<acción\>" | Estados del carrito (vacío, con items) |
| No deseado | "SI \<condición\> ENTONCES el sistema DEBERÁ \<respuesta\>" | Errores, validaciones, failures |
| Opcional | "DONDE \<característica\> EL sistema DEBERÁ \<acción\>" | Feature flags |

Ejemplo aplicado:

```markdown
### Requirement: Agregar producto al carrito
El cliente agregará productos validando stock y límites.

#### Scenario: Agregar producto con stock disponible
- **WHEN** el cliente agrega un producto con stock > 0
- **THEN** el sistema DEBERÁ agregarlo con cantidad 1 y congelar su precio unitario
- **AND** recalcular subtotal, impuesto y total

#### Scenario: Producto sin stock
- **IF** el stock del producto es 0
- **THEN** el sistema DEBERÁ mostrar "Producto {nombre} sin stock disponible" y no modificar el carrito

#### Scenario: Límite de items alcanzado
- **IF** el carrito ya contiene 50 productos distintos
- **THEN** el sistema DEBERÁ mostrar "Has alcanzado el límite de 50 productos"
```

> **Nota: Los escenarios EARS son tus criterios de aceptación.**
>
> Cada `#### Scenario:` en spec.md define una condición verificable que el sistema DEBERÁ cumplir. En terminología clásica de QA/BA, estos son los *acceptance criteria* de la user story. La diferencia es el formato: EARS reemplaza la prosa libre por patrones con keywords (`WHEN/THEN`, `IF/THEN`, `GIVEN/WHEN/THEN`) que eliminan ambigüedad.
>
> **Ubicación:** los criterios de aceptación viven en `spec.md`, dentro de cada requisito (`REQ-XXX`), como escenarios con caso feliz + error + bordes. Los tests (unit, widget, integration) validan estos mismos criterios.

### 1.6 Clasificación de reglas → dónde viven

Las categorías RN/RT/RS anteriores se diluyen así:

| Categoría anterior | Ahora es... | Dónde se especifica |
|--------------------|-------------|---------------------|
| RN (negocio): restricción/cálculo/validación/flujo | Requisitos EARS ubicuos/evento/no deseado | `specs/carrito/spec.md` |
| RT (técnicas) | Decisiones explícitas + requisitos de comportamiento interno | `design.md` §Decisiones |
| RS (seguridad) | Escenarios EARS + política RLS concreta | `spec.md` escenario + `design.md` §Backend |

> **Reglas de negocio: no son un documento separado.**
>
> Las reglas de negocio (antes "RN") son requisitos EARS que especifican invariantes, cálculos y validaciones. Ejemplos de mapeo:
>
> | Regla de negocio | Patrón EARS | Ubicación |
> |------------------|-------------|-----------|
> | "El precio unitario se congela al agregar al carrito" | Ubicuo (`DEBERÁ`) | `spec.md` REQ + `entity` (invariante) |
> | "Tope de descuento: 50%" | No deseado (`IF/THEN`) | `spec.md` REQ + `usecase` (validación) |
> | "Stock se descuenta al confirmar pago, no al iniciar" | Ubicuo (`DEBERÁ`) | `spec.md` REQ + `usecase` (orquestación) |
> | "RLS: cada usuario solo ve sus datos" | Aislamiento (`GIVEN/WHEN/THEN`) | `spec.md` escenario + `design.md` §Backend |
>
> **Dónde vive la implementación:** `domain/entity` (invariantes, cálculos puros) y `domain/usecases` (validaciones de negocio). **NUNCA** en `presentation` (cubit/widget).

### 1.7 Specs por componente Clean Architecture

Un mismo requisito de negocio genera requisitos derivados por capa. Especifica el comportamiento esperado de cada componente (no su implementación):

| Componente | Qué se especifica |
|------------|-------------------|
| Entity (domain) | Invariantes, cálculos puros (subtotal, impuesto), igualdad |
| Repository interface (domain) | Firma de métodos, tipo de retorno `Either<Failure, T>` |
| Model (data) | Serialización JSON ↔ entity, campos nulos, snake_case ↔ camelCase |
| DataSource (data) | Llamadas exactas a Supabase (tabla/RPC/auth), manejo de errores de red |
| Repository impl (data) | Mapeo Failure ← excepciones, aplicación de RT |
| UseCase (domain) | Orquestación única, parámetros, validaciones de entrada |
| Cubit + State (presentation) | Estados posibles (sealed class), transiciones, mensajes de error |
| Page (presentation) | Qué muestra cada estado, interacciones que disparan eventos |
| Supabase (backend) | Tablas, columnas, constraints, políticas RLS, triggers, RPC |

### 1.8 Formato delta (ADDED / MODIFIED / REMOVED)

La spec de un cambio describe **solo lo que cambia** respecto a las specs archivadas:

- `## ADDED Requirements` — capacidad nueva
- `## MODIFIED Requirements` — requisito completo reescrito que reemplaza al anterior
- `## REMOVED Requirements` — qué desaparece y por qué

Esto mantiene las specs cortas y hace el diff auditable.

**Salida de Fase 1:** `proposal.md` + `specs/{capacidad}/spec.md`

---

### 🚪 Puerta 1 — Aprobación de requisitos

```
[ ] Cada historia pasa la prueba de precisión
[ ] Todos los requisitos usan notación EARS con ID único
[ ] Los bordes están cubiertos (valores límite, vacío, negativos, expirados)
[ ] Las preguntas abiertas del alcance están cerradas o documentadas
[ ] El formato delta es correcto (ADDED/MODIFIED/REMOVED según toque)
[ ] El Impact Report justifica el alcance elegido
```

---

## Fase 2 · Diseño — CÓMO construirlo

> Diluye **Mapeo a capas**, **Contratos**, **Flujo de datos** y parte de **Backend**.

### 2.1 Ficheros afectados (antes "Mapeo")

Tabla obligatoria de `design.md`. Sin ella, el agente improvisa rutas y rompe convenciones:

| Elemento | Capa | Archivo | Regla asociada |
|----------|------|---------|----------------|
| CartItem | domain/entity | `lib/features/cart/domain/entities/cart_item.dart` | REQ-001 |
| CartRepository | domain/repository | `lib/features/cart/domain/repositories/cart_repository.dart` | REQ-002..007 |
| CartModel | data/model | `lib/features/cart/data/models/cart_model.dart` | REQ-001 |
| CartRemoteDataSource | data/datasource | `lib/features/cart/data/datasources/cart_remote_data_source.dart` | REQ-002 |
| AddItemToCart | domain/usecase | `lib/features/cart/domain/usecases/add_item_to_cart.dart` | REQ-003 |
| CartCubit / CartState | presentation | `lib/features/cart/presentation/cubit/…` | REQ-008..010 |
| CartPage | presentation | `lib/features/cart/presentation/pages/cart_page.dart` | REQ-011 |

### 2.2 Contratos Dart primero (antes "Contratos")

Escribe las interfaces ANTES de la implementación. Son la spec ejecutable del dominio:

```dart
abstract interface class CartRepository {
  Future<Either<Failure, Cart>> getCart();
  Future<Either<Failure, Unit>> addItem({required String productId, required int quantity});
  Future<Either<Failure, Unit>> removeItem({required String productId});
  Future<Either<Failure, Cart>> applyCoupon({required String code});
}
```

Estados UI como sealed class:

```dart
sealed class CartState {}
class CartInitial extends CartState {}
class CartLoading extends CartState {}
class CartLoaded extends CartState { final Cart cart; CartLoaded(this.cart); }
class CartError extends CartState { final String message; CartError(this.message); }
```

Si un contrato cambia respecto a una feature existente → requisito MODIFIED, no silencio.

### 2.3 Flujo de datos (antes "Flujo")

Documento ASCII del recorrido completo, incluidos caminos de error:

```
CartPage ──onTap──► CartCubit.addItem(productId)
                        │ emit CartLoading
                        ▼
                 AddItemToCart(repository)
                        ▼
                 CartRepositoryImpl ──► valida RN (stock, límite) local si aplica
                        ▼
                 CartRemoteDataSource.addCartItem(...)
                        │ supabase.from('cart_items').insert(...)
                        ▼
                 Supabase: INSERT con RLS (auth.uid() = user_id)
                        ▼
        ◄── Either.right(Unit) ◄── mapeo ◄── respuesta
        │
        └── Either.left(Failure) ──► CartError(message) ──► SnackBar
```

### 2.4 Backend Supabase (contrato de datos)

En `design.md` se fija ANTES de implementar:

- **Tablas**: `carts`, `cart_items`, `coupons` — columnas, tipos, FKs, constraints
- **RLS = tus antiguas RS**: cada política citada por su escenario (`auth.uid() = user_id`; admin solo lectura vía claim `role`)
- **Cálculos**: subtotal/impuesto en el cliente (entity pura) vs RPC atómico cuando hay concurrencia — decidir y anotar por qué
- **Migración**: número siguiente en `supabase/migrations/`, idempotente, nunca tocar migraciones previas

### 2.5 Decisiones explícitas + heurística sénior (antes ADRs ligeros)

Cada decisión no obvia se registra: qué se decide, alternativas descartadas, por qué. Señales de que una decisión merece registro: elegir entre dos patrones válidos, depender de un paquete nuevo, tocar seguridad, cambiar un contrato público.

Heurística sénior aplicada (qué haría un dev con años en este repo):
- Copia el patrón de la feature más parecida existente antes de inventar uno
- fpdart `Either` siempre; jamás exceptions cruzando capas de dominio
- Un UseCase = una operación; el Cubit orquesta varios
- Sin lógica de negocio en widgets ni en models

### 2.6 Diseño de interfaz (UI-UX) — archivo .pen

El diseño visual de pantallas se hace con **Pencil** (módulo `08-PENCIL/`, diseño manual, sin IA) y viaja dentro del change folder:

- **Ubicación:** `openspec/changes/<cambio>/design/<feature>-ui.pen` (JSON diffable en git, ver `08-PENCIL/08-cli-pen-format.md`)
- **Registro en `design.md` §UI-UX:** tabla `Pantalla (.pen) | Escenario REQ | Estados visibles | Notas`; los mensajes/estados EXACTOS ya viven en los escenarios EARS de la spec — aquí se mapea cada pantalla a su REQ
- **Regla de complejidad:** Simple omite el `.pen` (igual que `design.md`); Intermedia → wireframes de las pantallas clave; Compleja → mapa de pantallas por actor/escenario
- **Puerta 2 valida** que todo escenario REQ con UI visible tiene pantalla/estado diseñado ANTES de tasks.md; la Oleada 3.3 implementa contra ese `.pen` aprobado

> El principio es el del **Clarity Gate**: para UI compleja hay que capturar los supuestos visuales antes de implementar. Límite del antipatrón de **sobreespecificación**: wireframes, no pixel-árbol.

**Salida de Fase 2:** `design.md` (+ `design/*.pen` cuando aplica)

---

### 🚪 Puerta 2 — Aprobación del diseño

```
[ ] La tabla de ficheros afectados cubre TODOS los requisitos de la Puerta 1
[ ] Los contratos compilan mentalmente (firmas coherentes entre capas)
[ ] El flujo de datos cubre caminos de éxito Y de error
[ ] RLS especificada para toda tabla nueva/modificada
[ ] Ninguna decisión importante quedó implícita
[ ] Se respeta el patrón de las features existentes (o se justifica el cambio)
[ ] Cada escenario REQ visible tiene su pantalla/estado diseñado (archivo .pen)
```

---

## Fase 3 · Tareas — EN QUÉ ORDEN

> Diluye **Descomposición en tareas** y **Estimación**.

### 3.1 Anatomía de tarea atómica

Cada tarea: 1–3 ficheros, verificable en aislado, con criterios de éxito objetivos.

```markdown
- [ ] 2.1 Implementar CartModel
      Rol: experto en Flutter/Dart con Clean Architecture
      Tarea: serialización JSON↔entity para carts y cart_items
      Restricciones: freezed opcional según pubspec; snake_case desde Supabase;
                     null-safety estricta; sin lógica de negocio
      Éxito: fromJson/toJson roundtrip; tests unitarios pasan
```

### 3.2 Oleadas estándar para una feature Clean Architecture

Dentro de una oleada las tareas son independientes (paralelizables); entre oleadas hay dependencia:

```
OLEADA 1 — Dominio (independientes entre sí)
  1.1 Entity Cart/CartItem (+ invariantes)
  1.2 Interface CartRepository
  1.3 UseCases (uno por operación)

OLEADA 2 — Capa de datos + Backend Supabase
  2.1 Migración SQL tablas + RLS        ← si aplica; abre la capa: el flujo de datos es probable de inmediato
  2.2 Models (fromJson/toJson)
  2.3 RemoteDataSource
  2.4 CartRepositoryImpl

OLEADA 3 — Estado y presentación
  3.1 CartState (sealed)
  3.2 CartCubit
  3.3 CartPage + widgets

OLEADA 4 — Integración (cableado de la app)
  4.1 Registro en service_locator.dart
  4.2 Ruta en app_router.dart

OLEADA 5 — Tests
  5.1 Unit tests entidades/usecases
  5.2 Test repository impl (mock datasource) + integración contra la migración real
  5.3 Widget test página clave
```

### 3.3 Commits atómicos

1 tarea = 1 commit con mensaje convencional (`feat(cart): add CartModel with json mapping`). Beneficios: reversión granular, bisección eficaz, trazabilidad requisito→commit. Al cerrar la oleada: revisión contra la spec (no diff-and-hope).

### 3.4 Descomposición justa

Demasiado gruesa (>3 ficheros, "implementar feature") = agente improvisa.
Demasiado fina ("crear archivo", "añadir import") = ruido y pérdida de contexto.
El punto dulce: una responsabilidad verificable.

**Salida de Fase 3:** `tasks.md`

---

### 🚪 Puerta 3 — Aprobación de tareas

```
[ ] Cada requisito de la spec tiene ≥1 tarea que lo implementa
[ ] Cada tarea referencia su requisito (trazabilidad bidireccional)
[ ] Las dependencias definen el orden de oleadas correctamente
[ ] Ninguna tarea excede ~3 ficheros
[ ] Hay tareas de test para los escenarios críticos
```

---

## Fase 4 · Implementación

Un único motor —`/opsx-apply-change`— según **quién escribe el código**. El **Modo** se declara por cambio en la primera línea de `tasks.md`:

### Modo: andamiaje — scaffold IA + lógica crítica tuya

1. `/opsx-apply-change` genera scaffold por tarea (entity/model/datasource/repo/usecases/cubit/state/pages) con cuerpos `UnimplementedError()` y comentarios TODO citando el requisito, deja la casilla en `- [ ]` y pausa
2. Tú implementas las tareas siguiendo tasks.md oleada por oleada (la práctica de escribir la lógica crítica se preserva)
3. Delegación automática: DI → skill `di-getit-scaffold`, routing → skill `go-route-scaffold`

### Modo: completo — la IA escribe todo, tú verificas

1. `/opsx-apply-change` — el agente lee proposal/specs/design/tasks y ejecuta todas las tareas, commit por tarea, escribiendo el 100% del código
2. Al cierre de cada oleada auditas el resultado contra la spec
3. Checklist completo de auditoría: [06-auditoria-codigo-ia.md](./06-auditoria-codigo-ia.md)

### ¿andamiaje o completo? Matriz de decisión

| Criterio | andamiaje (tú implementas la crítica) | completo (IA escribe todo) |
|---|---|---|
| Lógica crítica: dinero, permisos, estados | ✅ entiendes cada línea que firmas | ⚠️ solo si los escenarios EARS son exhaustivos |
| CRUD, formularios, brownfield quirúrgico | posible overkill | ✅ terreno ideal |
| Estás aprendiendo el stack o el dominio | ✅ implementar ES aprender | ❌ no aprendes nada |
| Specs con supuestos ocultos (falla el Clarity Gate) | ✅ implementar te obliga a resolverlos | ❌ el error se multiplica silenciosamente |

> **Regla del libro:** puedes delegar la *escritura*, nunca la aprobación de la spec (Puerta 1) ni la verificación final (Puerta 3).

### Verificación contra spec

Al cierre de cada oleada:

| Tarea | La spec dice | El código hace | Cumple |
|-------|--------------|----------------|--------|
| 2.1 CartModel | roundtrip JSON completo | ✔ roundtrip cubierto en test | ✅ |
| 3.3 CartCubit | estados sealed + mensajes RN001/RN002 | falta mensaje RN006 | ❌ → fix |

### Clarity Gate y cierre

- **Clarity Gate:** ¿un agente distinto, con solo la spec, produciría código equivalente? Si dudas, la spec tiene supuestos ocultos → corrígela AHORA (sigue siendo barato).
- **Archive:** `openspec archive <cambio>` mueve el change folder a specs consolidadas. Las specs vivas describen el sistema ACTUAL.

---

## Boundaries del proyecto

Marco Always / Ask First / Never adaptado a Flutter + Supabase. Ajústalo a tu equipo y decláralo en la constitución del proyecto:

| Nivel | En este stack |
|-------|---------------|
| **Always** (sin preguntar) | Crear ficheros nuevos dentro de su feature; seguir patrón existente; añadir tests; formatear con dart format |
| **Ask First** | Cambiar contratos existentes (MODIFIED); añadir paquete a pubspec; crear tabla/modificar esquema; nueva ruta con guard |
| **Never** | Eliminar/reescribir migraciones previas; desactivar RLS; tocar secretos/.env; subir build.gradle/signing; borrar datos de producción |

---

## Proporcionalidad según complejidad

SDD es proporcional al riesgo. No todos los cambios necesitan las 3 puertas completas:

| Nivel | Ejemplos | Proceso mínimo |
|-------|----------|----------------|
| **Simple** | Texto UI, color, constante, renombrado local | Proposal breve → implementar directo (sin design.md) |
| **Intermedia** | Nueva pantalla CRUD sobre patrón existente | Proposal + spec + design ligero + tasks → 1 puerta combinada |
| **Compleja** | Feature nueva multi-capa, pagos, cambios de contrato, seguridad | Flujo completo con 3 puertas |

Regla práctica: si dudarías en mergearlo sin revisión de otro humano, es al menos Intermedia.

---

## Specs vivas y trazabilidad

- La spec se actualiza **en el mismo commit** que el código que cambia el comportamiento (nunca después, nunca "luego").
- Matriz de trazabilidad mínima (vive en tasks.md): requisito ↔ tarea ↔ test ↔ commit.
- Tras archive, las capacidades archivadas son la documentación viva del sistema: léelas antes de planear el próximo cambio (alimentan el siguiente Impact Report).

```
REQ-003 (spec) ──► tarea 1.3 AddItemToCart (tasks) ──► test add_item_test.dart ──► commit feat(cart): ...
```

---

## Errores comunes (anti-patrones aplicados)

| Error | Síntoma | Prevención |
|-------|---------|------------|
| Spec zombi | Código cambió, spec no | Actualizar spec en el mismo commit |
| Teatro de especificación | Docs perfectas, código que no las cumple | Puertas con checklist verificable, revisión por lotes |
| Sobreespecificación | Spec de 500 líneas para un botón | Proporcionalidad; EARS solo donde importa |
| Requisitos vagos | "debería funcionar bien" | Prueba de precisión + EARS obligatorio |
| Design omitido | Agente inventa carpetas y nombres | Tabla de ficheros afectados obligatoria |
| Tareas gigantes | "implementar feature completa" | Límite 1–3 ficheros por tarea |
| Delta mal usado | Reescribir specs enteras sin MODIFIED | Solo ADDED/MODIFIED/REMOVED según toque |
| Puertas saltadas | "ya lo apruebo mientras codeo" | El coste crece por fase; volver a la puerta más barata |

---

## Referencias

- Teoría: [01-teoria-sdd.md](./01-teoria-sdd.md) → libro oficial en `pdf/`
- Herramienta CLI: [03-openspec-guia-practica.md](./03-openspec-guia-practica.md)
- Plantilla lista para copiar: [04-plantilla-cambio-openspec.md](./04-plantilla-cambio-openspec.md)
- Cheat sheet: [05-referencia-rapida.md](./05-referencia-rapida.md)
- Ejemplos completos: [`ejemplos-cambios/`](./ejemplos-cambios/)
