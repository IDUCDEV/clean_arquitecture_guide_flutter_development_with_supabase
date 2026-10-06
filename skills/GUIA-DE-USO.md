# Guía de uso de las skills — Qué proveer a cada skill

Guía completa para usar las 5 skills de scaffolding. El foco es **qué inputs debes darle a cada skill** para que genere el resultado correcto.

> Para ver el resultado íntegro de cada skill y el flujo paso a paso, consulta [EJEMPLO.md](./EJEMPLO.md) (todo el ejemplo en un solo archivo).

---

## 1. Antes de empezar

### 1.1 Conceptos clave

| Concepto | Qué es | Ejemplo |
|---|---|---|
| `app_name` | Nombre del paquete en `pubspec.yaml` | `order_app` |
| `feature_name` | Nombre de la feature en snake_case | `product`, `user_profile` |
| `design_file` | Hoja de diseño markdown usada como input de la feature | `ruta/a/hoja-diseno.md` |
| `openspec_change` | Carpeta de cambio OpenSpec (proposal + specs + design + tasks) usada como input | `02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/add-cart/` |
| Naming | Archivos en snake_case, clases en UpperCamelCase | `order_model.dart`, `OrderModel` |
| Scaffolding-only | Las skills generan estructura, **nunca** lógica | `throw UnimplementedError()` |

### 1.2 Cómo se invoca

Las skills las ejecuta el asistente AI. Tienes dos formas de pedirlas:

1. **Lenguaje natural** — el asistente detecta la skill por el contexto:
   > "Crea un feature product con campos id, name, price"
2. **Invocación explícita** (más fiable):
   > "Usa la skill `clean-arch-feature` para crear..."

Si el asistente no invoca la skill correcta, pídele explícitamente el nombre.

### 1.3 Prerrequisitos del proyecto

Las skills asumen un proyecto Flutter ya inicializado con la base Clean Architecture (`lib/core/`). Ver checklist completo en [README.md](./README.md#prerrequisitos-del-proyecto). Lo esencial:

- `lib/core/common/usecase.dart`, `core/error/failures.dart`, `core/error/exceptions.dart`
- `lib/core/di/service_locator.dart` (+ `service_locator.config.dart` regenerado con `make gen`) para DI, y `lib/core/router/app_router.dart` (para rutas)
- Deps en `pubspec.yaml`: `fpdart`, `equatable`, `flutter_bloc`, `supabase_flutter`, `get_it`, `go_router`, `injectable` (+ `injectable_generator`, `build_runner` para `make gen`)

---

## 2. `clean-arch-feature` — feature completa

Genera las 4 capas de una feature nueva: `data/`, `domain/`, `presentation/` + opcionalmente Supabase, páginas y wiring.

### 2.1 Obligatorio

| Parámetro | Qué es | Formato | Ejemplo |
|---|---|---|---|
| `feature_name` | Nombre de la feature | snake_case | `product` |
| `fields` | Campos con nombre y tipo Dart | `nombre: Tipo` | `id: String`, `name: String`, `price: double`, `categoryId: String?` |
| `operations` | CRUD a generar | coma separada | `getAll, getById, create, update, delete` |

**Prompt mínimo:**

> Crea un feature `product` con campos `id: String`, `name: String`, `price: double`, `categoryId: String?`, `createdAt: DateTime` y operaciones `getAll, getById, create, update, delete`.

> **Alternativa (modo hoja de diseño):** en vez de `feature_name` + `fields` + `operations` puedes pasar un `design_file` con la hoja de diseño del módulo 02. Ver [2.6](#26-modo-hoja-de-diseño-design_file).

### 2.2 Opcional — Supabase

| Parámetro | Qué es | Formato | Ejemplo |
|---|---|---|---|
| `table_name` | Nombre de la tabla | snake_case | `products` |
| `columns` | Columnas Postgres | `nombre: tipo CONSTRAINT` | `id: uuid PK`, `user_id: uuid NOT NULL`, `status: text DEFAULT 'pending'`, `created_at: timestamptz DEFAULT now()` |

Al proveerlos se genera: model con mapeo snake_case, datasource con `_tableName` + `watchById`, y migración SQL `supabase/migrations/{timestamp}_create_{table}.sql` con RLS.

> **Importante:** `user_id` en `columns` activa las RLS policies con `auth.uid() = user_id`. Si tu tabla usa otro nombre de columna de propietario, edita la migración antes de aplicarla.

**Prompt con Supabase:**

> Crea un feature `product` con campos `id: String`, `name: String`, `price: double`, `categoryId: String?`, `createdAt: DateTime`, operaciones `getAll, getById, create, update, delete`, y conéctalo a Supabase con tabla `products` y columnas: `id: uuid PK`, `name: text NOT NULL`, `price: float8 NOT NULL`, `category_id: uuid`, `created_at: timestamptz DEFAULT now()`.

### 2.3 Opcional — páginas iniciales

| Parámetro | Qué es | Formato |
|---|---|---|
| `pages` | Páginas a generar | `[page_name:pattern_type, ...]` |

Patrones disponibles:

| Pattern | Cuándo usarlo |
|---|---|
| `listener_builder` | **Default.** Páginas con side effects (snackbars, navegación post-acción) |
| `builder` | Páginas de solo lectura, sin efectos secundarios |
| `form` | Formularios con validación y submit loading |

Regla de naming: `list` genera plural (`orders_list_page.dart`); el resto singular (`order_detail_page.dart`).

**Prompt con páginas:**

> Crea un feature `order` con campos `id: String`, `userId: String`, `total: double`, `status: String`, `createdAt: DateTime`, operaciones `getAll, getById, create, update, delete`, y páginas `[list:listener_builder, detail:builder, edit:form]`.

### 2.4 Opcional — wiring (orquestación)

| Parámetro | Qué hace |
|---|---|
| `wiring: [di]` | Delega en `di-getit-scaffold` → deja el feature anotado; `make gen` escribe el registro en `service_locator.config.dart` |
| `wiring: [router]` | Delega en `go-route-scaffold` → añade rutas a `app_router.dart` |
| `wiring: [di, router]` | Ambos en el mismo turno |

**Prompt completo (todos los parámetros):**

> Usa la skill `clean-arch-feature`. Feature `order`, campos `id: String`, `userId: String`, `total: double`, `status: String`, `createdAt: DateTime`, operaciones `getAll, getById, create, update, delete`. Supabase: tabla `orders`, columnas `id: uuid PK`, `user_id: uuid NOT NULL`, `total: float8 NOT NULL`, `status: text DEFAULT 'pending'`, `created_at: timestamptz DEFAULT now()`. Páginas `[list:listener_builder, detail:builder]`. Wiring `[di, router]`. App name `order_app`.

### 2.5 Qué te da y qué sigue

Genera (si todo se pide): entity, repository interface, model, datasource, repository_impl, 5 usecases, cubit + state, páginas, migración SQL, clases anotadas para DI (vía `di-getit-scaffold` + `make gen`) y rutas en el router.

**Lo siguiente es tuyo:** implementar los bodies (`UnimplementedError`), revisar RLS policies, ejecutar la migración, y `flutter pub get` si añadiste paquetes.

### 2.6 Modo hoja de diseño (`design_file`)

En vez de describir la feature en el prompt, la skill puede **leer la hoja de diseño** (output del análisis previo de la metodología SDD, módulo 02) y derivar todo de ahí.

| Parámetro | Qué es | Formato | Ejemplo |
|---|---|---|---|
| `design_file` | Ruta a la hoja de diseño markdown | ruta | `ruta/a/hoja-diseno.md` |

**Cómo funciona:**
- Si se provee `design_file`, se ignoran `feature_name`, `fields` y `operations`; la skill parsea el archivo y extrae archivos, entidades, usecases, contratos, tablas y páginas.
- Sección `3 · Mapeo` → qué archivos crear (y sus nombres exactos).
- Sección `2 · Diseño [E]` → campos de las entidades; los tipos se **infieren por convención** de nombre (`id`→`String`, `fecha*`→`DateTime`, `precio/total`→`double`, `cantidad`→`int`, default→`String`) y se marcan con `// TODO: verificar tipo`.
- Sección `4 · Contratos` → firmas verbatim de repository/datasource/usecases.
- Sección `6 · Backend` → tablas y RPCs para el datasource. Para la migración SQL la skill **pregunta las columnas** (el archivo no las trae); si declinas, se omite.
- Sección `2 · Diseño [R]` → reglas de negocio como `// TODO` en los usecases.
- Filas del mapeo que apunten a **otras features** (ej. `tickets/...`) no se generan: se listan como dependencias externas pendientes.
- `pages`, `wiring`, Supabase y `app_name` siguen pidiéndose igual que en modo clásico.

### 2.7 Modo cambio OpenSpec (`openspec_change`) — recomendado

El input preferido hoy es una **carpeta de cambio OpenSpec**, generada con el flujo SDD del módulo [02-SPEC-DRIVEN-DEVELOPMENT](../02-SPEC-DRIVEN-DEVELOPMENT/) (`/opsx-propose`). Ejemplos completos en [`02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/`](../02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/).

| Parámetro | Qué es | Formato | Ejemplo |
|---|---|---|---|
| `openspec_change` | Ruta a la carpeta del cambio | ruta | `02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/add-buyers/` |

**Cómo funciona:**
- Tiene prioridad sobre `design_file`; se ignoran `feature_name`, `fields` y `operations`.
- `proposal.md` → feature name (de la capacidad o carpeta `add-{feature}`) y alcance.
- `specs/*/spec.md` §ADDED Requirements → un usecase por requisito; cada body lleva `// TODO` citando el REQ y los mensajes exactos de los escenarios EARS.
- `specs/*/spec.md` §MODIFIED / §REMOVED → NO generan archivos: se listan como cambios brownfield pendientes sobre código existente.
- `design.md` §Ficheros afectados → tabla `Elemento | Capa | Archivo | Req`: los nombres de archivo se respetan verbatim.
- `design.md` §Contratos Dart clave → firmas verbatim (`Either<Failure, T>`, sealed states).
- `design.md` §Backend Supabase → tablas/RPCs para el datasource; columnas para la migración si están, si no se preguntan.
- Si `design.md` no existe (cambio Simple), se derivan los archivos desde la spec con el naming estándar.

**Prompt en modo cambio OpenSpec:**

> Usa la skill `clean-arch-feature` con `openspec_change: 02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/add-buyers/`. Páginas `[list:listener_builder]`. Wiring `[di]`. App name `raffle_app`.

---

## 3. `clean-arch-component` — pieza individual

Genera **un solo archivo** dentro de una feature existente. Útil para añadir un usecase, una página, un modelo, etc.

### 3.1 Inputs según tipo

| `component_type` | Inputs extra | Depende de |
|---|---|---|
| `entity` | `fields` | — |
| `model` | `fields` | Entity existente |
| `usecase` | `operation` (ej: `get`, `create`, `cancel`) | Repository existente |
| `cubit` | (ninguno) | Usecases existentes |
| `datasource` | (ninguno) | `SupabaseClient` |
| `repository` | (ninguno) | Entity existente |
| `repository_impl` | (ninguno) | DataSource + Repository interface |
| `page` | `page_name` (ej: `list`, `detail`, `edit`) + `pattern_type` (`listener_builder`/`builder`/`form`) | Cubit existente |

Siempre requiere `feature_name` y `component_type`.

### 3.2 Ejemplos de prompts

> Añade un usecase `cancel_order` al feature `order`.

> Añade una página `edit` al feature `order` con patrón `form`.

> Añade un `model` para el feature `order` con campos `id: String`, `total: double`.

> Añade el `repository_impl` del feature `order`.

### 3.3 Qué sigue

- Verificar que la feature exista (la skill avisa si no).
- Para `page`: recordar conectar la página en el router (`go-route-scaffold`).

---

## 4. `di-getit-scaffold` — inyección de dependencias

Mantiene el módulo GetIt. **Modo por defecto: `injectable`** (el de `PROMPT-BOOTSTRAP-MONOREPO.md` v2): cada clase se anota donde vive y `make gen` escribe el registro. Puede invocarse sola o ser orquestada desde `clean-arch-feature` (`wiring: [di]`).

### 4.1 Inputs

| Parámetro | Qué es | Formato | Ejemplo |
|---|---|---|---|
| `mode` | Estilo de DI. **Default: `injectable`** | `injectable` o `manual` | `injectable` |
| `app_name` | Nombre del paquete | snake_case | `order_app` |
| `features` | Features a registrar | YAML | (abajo) |
| `external_libs` | Librerías externas necesarias | lista | `SupabaseClient, Isar, InternetConnection, http.Client` |

**Formato `features`:**

```yaml
feature: product
external_datasources: [SupabaseClient]
remote_datasource: ProductRemoteDataSource
local_datasource: ProductLocalDataSource  # opcional
repository: ProductRepository
repository_impl: ProductRepositoryImpl
usecases: [GetProducts, GetProduct, CreateProduct, UpdateProduct, DeleteProduct]
cubit: ProductCubit
```

### 4.2 Ejemplo de prompt (modo default)

> Usa la skill `di-getit-scaffold` (modo `injectable`), app `order_app`. Registra el feature `order`: datasource `OrderRemoteDataSourceImpl` (usa `SupabaseClient`), repository `OrderRepositoryImpl`, usecases `GetOrders, GetOrder, CreateOrder, UpdateOrder, DeleteOrder`, cubit `OrderCubit`.

### 4.3 Reglas que aplica (modo `injectable`)

- Cada clase se anota donde vive; `make gen` escribe el registro en `service_locator.config.dart` (que **se commitea** y nunca se edita a mano).
- `@LazySingleton(as: X)` en datasources y repositories (impl); `@lazySingleton` en usecases y servicios; `@injectable` en cubits de pantalla; `@module` para terceros en `external_module.dart`.
- Entity, Model, interface de Repository y Params **nunca** se anotan.
- Si `external_module.dart` no existe, la skill lo crea con `SupabaseClient` (`Supabase.instance.client`), `Isar` (`@preResolve`), `InternetConnection.createInstance()` y `http.Client()`.
- Al terminar, recordar `make gen` + commitear el `.config.dart` si cambió.

> **Modo `manual` (legacy/brownfield):** solo para proyectos con cascada manual existente (v1). Orden de capas: external → core → datasources → repositories → usecases → cubits; `registerLazySingleton` para todo excepto cubits (`registerFactory`). `SupabaseClient` NO se registra: los datasources lo reciben como `Supabase.instance.client`.

---

## 5. `go-route-scaffold` — rutas GoRouter

Genera/actualiza `app_router.dart`. Puede invocarse sola o ser orquestada desde `clean-arch-feature` (`wiring: [router]`).

### 5.1 Inputs

| Parámetro | Qué es | Formato | Ejemplo |
|---|---|---|---|
| `app_name` | Nombre del paquete | snake_case | `order_app` |
| `has_auth` | Incluir redirect de auth | `true` / `false` | `true` |
| `auth_cubit` | Cubit de auth (si `has_auth`) | UpperCamelCase | `AuthCubit` |
| `auth_states` | Estado autenticado (si `has_auth`) | `authenticated: <State>` | `authenticated: AuthAuthenticated` |
| `use_sentry` | Incluir `SentryNavigatorObserver` | `true` / `false` | `false` |
| `routes` | Rutas a generar | YAML | (abajo) |

**Formato `routes`:**

```yaml
- path: /
  page: HomePage
  feature: home

- path: /products
  page: ProductsPage
  feature: product
  children:
    - path: :id
      page: ProductDetailPage
      feature: product

- path: /login
  page: LoginPage
  feature: auth
  auth_required: false
```

### 5.2 Ejemplos de prompt

**Básico (sin auth):**

> Usa la skill `go-route-scaffold`. App `order_app`, sin auth, sin Sentry. Rutas: `/` → `HomePage` (feature home), `/orders` → `OrdersListPage` (feature order) con hijo `:id` → `OrderDetailPage`.

**Con auth:**

> Usa la skill `go-route-scaffold`. App `order_app`, con auth (`AuthCubit`, estado autenticado `AuthAuthenticated`), sin Sentry. Rutas: `/login` → `LoginPage` (auth, `auth_required: false`), `/` → `HomePage`, `/orders` → `OrdersListPage` con hijo `:id` → `OrderDetailPage`.

**Con Sentry:**

> Usa la skill `go-route-scaffold`. App `order_app`, sin auth, con Sentry. Rutas: `/orders` → `OrdersListPage` con hijo `:id` → `OrderDetailPage`.

### 5.3 Qué sigue

- Descomentar los imports de páginas.
- Si usa auth: envolver `MaterialApp.router` con `MultiBlocProvider` que incluya `AuthCubit`.
- Si usa Sentry: configurar `SentryFlutter.init()` en `main.dart` con el DSN.

---

## 6. `flutter-test-generator` — tests boilerplate

Genera el archivo `_test.dart` espejando el path fuente bajo `test/`.

### 6.1 Input

**Un archivo Dart o un directorio.** Detecta la capa automáticamente por el path:

| Path en `lib/` | Test generado |
|---|---|
| `domain/entities/` | Entity (Equatable, copyWith, props) |
| `domain/usecases/` | UseCase (mock repository, `Either<Failure, T>`) |
| `data/models/` | Model (fromJson, toJson, roundtrip, entity conversion) |
| `data/datasources/` | DataSource (mock client, `ServerException`) |
| `data/repositories/` | Repository (mock datasources + network, online/offline) |
| `presentation/cubit/` (no state) | Cubit (`blocTest`, mock usecases) |
| `presentation/cubit/` (state file) | State (igualdad, props) |
| `presentation/pages/` o `widgets/` | Widget (`testWidgets`, mock `BlocProvider`) |
| `core/services/`, `core/network/` | Core service/network |

### 6.2 Dos formas de usarla

**Vía CLI directa:**

```bash
python3 skills/flutter-test-generator/generate_test.py lib/features/product/presentation/cubit/product_cubit.dart
```

**Vía asistente (recomendado):**

> Genera los tests para `product_cubit`.

> Genera los tests para todos los archivos de `lib/features/product/`.

### 6.3 Qué sigue

- Los bodies van vacíos con comentarios AAA en español — **tú** los completas.
- La skill pregunta si quieres que complete los tests; nunca lo hace sin tu autorización.
- Verifica con `flutter test <path>`.

---

## 7. Orquestación (wiring)

`clean-arch-feature` es la única skill que **orquesta** a las otras dos. Esto es lo que ocurre según pidas:

| Pides | Qué pasa |
|---|---|
| `wiring: [di]` | Genera el feature y luego invoca `di-getit-scaffold`: los componentes salen anotados; recuerda correr `make gen` |
| `wiring: [router]` | Genera el feature y luego invoca `go-route-scaffold` con las páginas generadas → actualiza `app_router.dart` |
| `wiring: [di, router]` | Ambos, en el mismo turno |
| (sin `wiring`) | No toca DI ni router. El resumen final te recuerda correr `make gen` (el feature ya sale anotado) y añadir rutas |

**Beneficio:** no duplicas inputs — describes el feature una sola vez y el wiring se propaga automáticamente.

---

## 8. Cheat-sheet — qué proveer a cada skill

| Skill | Obligatorio | Opcional | Prompt de ejemplo |
|---|---|---|---|
| `clean-arch-feature` | `feature_name` + `fields` + `operations` **o** `design_file` | Supabase (`table_name`, `columns`), `pages`, `wiring` | "Crea un feature `product` con campos `id`, `name`, `price` y operaciones CRUD..." / "Usa la skill `clean-arch-feature` con `design_file: .../disenio-feature-buyers.md`" |
| `clean-arch-component` | `feature_name`, `component_type` | `fields`, `operation`, `page_name`, `pattern_type` (según tipo) | "Añade un usecase `cancel_order` al feature `order`" |
| `di-getit-scaffold` | `mode` (default `injectable`), `app_name`, `features` | `external_libs`, `local_datasource` | "Registra el feature `product` en el service locator (injectable)" |
| `go-route-scaffold` | `app_name`, `has_auth`, `routes` | `use_sentry`, `auth_cubit`, `auth_states` | "Añade las rutas de `/orders` y `/orders/:id` al router" |
| `flutter-test-generator` | archivo o directorio `.dart` | — | "Genera los tests para `product_cubit`" |

---

## 9. Troubleshooting de inputs

| Síntoma | Causa probable | Solución |
|---|---|---|
| El código no compila por imports | Faltó el `app_name` correcto | Vuelve a pedir la skill indicando el paquete exacto de `pubspec.yaml` |
| El feature ya existe y se sobrescribe | Se pidió `clean-arch-feature` sobre una feature existente | Usa `clean-arch-component` para piezas sueltas |
| No salieron páginas | Se olvidó `pages` | Regenera con `pages` o añade páginas con `clean-arch-component` |
| No salió migración SQL | Se olvidó `table_name`/`columns` | Regenera con los datos de Supabase |
| No salió migración SQL en modo `design_file` | El archivo no trae columnas Postgres | Indica las columnas cuando la skill las pregunte (o regenera con `table_name` + `columns`) |
| Tipos inferidos incorrectos en modo `design_file` | Inferencia por convención de nombre | Revisa los `// TODO: verificar tipo` y ajusta el tipo antes de implementar |
| No se registró en DI ni router | Se omitió `wiring` | Invoca `di-getit-scaffold` y `go-route-scaffold` manualmente, y corre `make gen` |
| El modelo usa camelCase en vez de snake_case | No se dieron columnas Supabase | Para mapeo snake_case siempre se requiere `table_name` + `columns` |
| Tests generados para la capa equivocada | Path ambiguo (ej: `presentation/cubit/` con state dentro) | Indica el archivo exacto |
| El asistente no usó la skill | Detección automática falló | Pide explícitamente: "Usa la skill `clean-arch-feature`..." |
