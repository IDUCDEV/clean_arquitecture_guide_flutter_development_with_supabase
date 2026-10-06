---
name: clean-arch-feature
description: Generate a complete Clean Architecture feature scaffold (entity, model, datasource, repository interface + impl, usecases, cubit, state, optional pages) from a feature name + entity fields (classic mode), from a design file (design_file) following the 8-step methodology (Alcance → Diseño → Mapeo → Contratos → Flujo → Backend → Criterios → Estimación), or from an OpenSpec change folder (openspec_change: proposal.md + specs/*/spec.md con requisitos EARS en formato delta + design.md con ficheros afectados y contratos Dart + tasks.md, e.g. 02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/add-cart). Optionally includes Supabase integration (table schema → snake_case model + datasource + SQL migration), initial pages (listener_builder / builder / form patterns) and wiring orchestration (delegates DI registration to di-getit-scaffold and routing to go-route-scaffold). All method bodies are left as throw UnimplementedError() — implementation is the developer's responsibility.
---

# clean-arch-feature — Scaffold completo de feature

Genera la estructura completa de carpetas y archivos para una feature siguiendo Clean Architecture + Supabase + Cubit. Si proporcionas datos de tabla Supabase, genera además el mapeo snake_case, datasource con `SupabaseClient`, y migración SQL.

## Input requerido (modo clásico)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `feature_name` | Nombre en snake_case | `product`, `user_profile` |
| `fields` | Lista de campos con nombre y tipo Dart | `id: String`, `name: String`, `price: double`, `categoryId: String?` |
| `operations` | CRUD a generar | `getAll`, `getById`, `create`, `update`, `delete` |

> **Modo clásico.** Solo aplica si NO se provee `design_file`. Si se provee `design_file`, estos tres parámetros se ignoran y se derivan del archivo (ver [Input alternativo](#input-alternativo-hoja-de-diseño) y [Modo hoja de diseño](#modo-hoja-de-diseño--parsing-del-archivo)).

## Input alternativo (hoja de diseño)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `design_file` | Ruta a una hoja de diseño markdown que sigue el flujo de 8 pasos del módulo 02 (Alcance → Diseño → Mapeo → Contratos → Flujo → Backend → Criterios → Estimación) | `ruta/a/hoja-diseno.md` (metodología en `02-SPEC-DRIVEN-DEVELOPMENT/02-sdd-flutter-supabase.md`) |

**Si se omite:** se usa el modo clásico (`feature_name` + `fields` + `operations`).
**Si se proporciona:** se ignoran `feature_name`, `fields` y `operations`; la skill lee el archivo, lo parsea (ver [Modo hoja de diseño](#modo-hoja-de-diseño--parsing-del-archivo)) y deriva entidades, usecases, repositorios, datasource, cubit, state y páginas. `table_name`, `columns`, `pages` y `wiring` siguen siendo inputs opcionales que se piden aparte si aplican.

## Input alternativo B (cambio OpenSpec)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `openspec_change` | Ruta a una carpeta de cambio OpenSpec (`proposal.md` + `specs/*/spec.md` + `design.md` + `tasks.md`) | `02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/add-cart/` |

**Prioridad de modos:** si se provee `openspec_change` tiene prioridad sobre `design_file`; ambos tienen prioridad sobre el modo clásico.

**Si se proporciona:** se ignoran `feature_name`, `fields` y `operations`; la skill parsea la carpeta (ver [Modo cambio OpenSpec](#modo-cambio-openspec--parsing-de-la-carpeta)) y deriva los mismos artefactos. Los requisitos EARS (escenarios) se convierten en comentarios TODO citando el ID del requisito en cada usecase generado. Requisitos `MODIFIED`/`REMOVED` NO generan archivos nuevos: se listan en el resumen como cambios brownfield pendientes sobre código existente.

## Input opcional (Supabase)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `table_name` | Nombre de la tabla en Supabase (snake_case) | `orders` |
| `columns` | Columnas Postgres (nombre + tipo + constraints) | `id: uuid PK`, `user_id: uuid NOT NULL`, `status: text DEFAULT 'pending'`, `created_at: timestamptz DEFAULT now()` |

**Si se omite:** se genera el esqueleto genérico (model sin mapeo snake_case, datasource sin `_tableName`, sin migración SQL).
**Si se proporciona:** se genera model con snake_case real, datasource con `_tableName` + `watchById`, y `supabase/migrations/{timestamp}_create_{table}.sql`.

**En modo hoja de diseño:** las tablas se deducen de la sección `6 · Backend` del archivo. Como el archivo normalmente NO incluye columnas Postgres, si se desea migración SQL la skill **pregunta las columnas** al usuario antes de generarla. Si el usuario declina, se omite la migración y el resumen lo indica.

## Input opcional (páginas iniciales)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `pages` | Lista de páginas a generar con su patrón: `{page_name}:{pattern_type}` | `[list:listener_builder, detail:builder, edit:form]` |

Los patrones disponibles son `listener_builder` (default), `builder` y `form`. Ver [Templates de página](#templates-de-página).

**Si se omite:** se genera el placeholder genérico `{feature}_page.dart`.
**Si se proporciona:** se genera una página por entrada: `{feature}_{page_name}_page.dart` con el patrón indicado. El nombre del archivo usa el plural de la feature solo cuando `page_name` es `list` (ej: `orders_list_page.dart`).

**En modo hoja de diseño:** las páginas se derivan de las filas `Página` de la sección `3 · Mapeo` del archivo. El patrón se toma de `pages` si se provee; si no, se usa `listener_builder`.

## Input opcional (wiring — orquestación)

| Parámetro | Descripción | Ejemplo |
|---|---|---|
| `wiring` | Qué wiring aplicar tras generar los archivos: `[di]`, `[router]` o `[di, router]` | `[di, router]` |

Esta skill **no contiene** la lógica de DI ni de rutas: delega en las skills hermanas `di-getit-scaffold` (las clases se anotan y `make gen` escribe el registro en `service_locator.config.dart`) y `go-route-scaffold` (rutas en `app_router.dart`). Solo orquesta.

**Si se omite:** no se toca DI ni el router. Los templates dejan las clases **anotadas** igualmente; el resumen final te recuerda correr `make gen` y añadir las rutas.

## Reglas de mapeo Postgres → Dart

| Postgres | Dart | Nullable |
|---|---|---|
| `uuid` | `String` | `?` si nullable |
| `text` / `varchar` | `String` | `?` si nullable |
| `int4` / `int8` | `int` | `?` si nullable |
| `float4` / `float8` / `numeric` | `double` | `?` si nullable |
| `bool` | `bool` | `?` si nullable |
| `timestamptz` / `timestamp` | `DateTime` | `?` si nullable |
| `jsonb` | `Map<String, dynamic>` | `?` si nullable |
| `date` | `DateTime` | `?` si nullable |
| `int8[]` | `List<int>` | `?` si nullable |
| `text[]` | `List<String>` | `?` si nullable |

Snake_case en JSON/Postgres → camelCase en Dart: `created_at` → `createdAt`, `user_id` → `userId`.

## Output: estructura generada

### Sin Supabase
```
lib/features/{feature_name}/
├── data/
│   ├── datasources/
│   │   └── {feature_name}_remote_datasource.dart
│   ├── models/
│   │   └── {feature_name}_model.dart
│   └── repositories/
│       └── {feature_name}_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── {feature_name}.dart
│   ├── repositories/
│   │   └── {feature_name}_repository.dart
│   └── usecases/
│       ├── get_{feature_name}s.dart
│       ├── get_{feature_name}.dart
│       ├── create_{feature_name}.dart
│       ├── update_{feature_name}.dart
│       └── delete_{feature_name}.dart
└── presentation/
    ├── cubit/
    │   ├── {feature_name}_cubit.dart
    │   └── {feature_name}_state.dart
    └── pages/
        ├── {feature_name}_page.dart          (placeholder por defecto)
        └── {feature_name}_{page}_page.dart   (uno por entrada en `pages`)
```

### Con Supabase (archivos adicionales)
```
supabase/
└── migrations/
    └── {timestamp}_create_{table}.sql
```

Además, los archivos `model.dart` y `remote_datasource.dart` se generan con mapeo snake_case y `_tableName`.

## Modo cambio OpenSpec — parsing de la carpeta

Cuando se provee `openspec_change`, la skill parsea la carpeta del cambio (estructura en [04-plantilla-cambio-openspec.md](../../02-SPEC-DRIVEN-DEVELOPMENT/04-plantilla-cambio-openspec.md); ejemplos completos en `02-SPEC-DRIVEN-DEVELOPMENT/ejemplos-cambios/`). El parsing es **estructural por archivos y encabezados**, no por contenido literal.

| Archivo | Qué se extrae | Cómo se usa |
|---|---|---|
| `proposal.md` §What Changes / Capabilities | Nombre de feature y alcance | `feature_name` (de la capacidad o del nombre de carpeta `add-{feature}`) |
| `proposal.md` §Actores y permisos + Scope | Contexto | No genera archivos; informa el resumen |
| `specs/*/spec.md` §ADDED Requirements | `### Requirement: <nombre> (REQ-xxx)` → un UseCase por requisito operacional; escenarios `#### Scenario:` → TODOs citando REQ y mensajes exactos | Bodies como TODO con los mensajes de error literales de los escenarios |
| `specs/*/spec.md` §MODIFIED / §REMOVED Requirements | Cambios sobre código existente | NO generan archivos; se listan en el resumen final como pendientes brownfield |
| `design.md` §Ficheros afectados | Tabla `Elemento \| Capa \| Archivo \| Req` | **Fuente principal.** Mismo mapeo por fila que la tabla de artefactos del modo hoja de diseño. Nombres de archivo verbatim |
| `design.md` §Contratos Dart clave | Firmas de Repository interface y states sealed | Se usan **verbatim** (incluye `Either<Failure, T>` y sealed classes si están) |
| `design.md` §Decisions | Decisiones D1..Dn | Comentarios `// Decisión Dn:` en los archivos afectados |
| `design.md` §Backend Supabase | Tablas, RLS, RPCs | `_tableName` del datasource, RPCs en TODOs, tablas para migración |
| `design.md` §Flujo de datos | Recorrido UI→Supabase | No genera archivos; valida que cada flecha tenga artifacto |
| `tasks.md` | Oleadas y trazabilidad Req↔tarea | Orden informativo de generación; no genera código |
| `tasks.md` §Trazabilidad | Matriz Req↔tarea↔test | Anotada en el resumen para `flutter-test-generator` |

**Diferencias clave vs hoja de diseño:**
1. Los requisitos ya traen ID (`REQ-xxx`) — se citan en TODOs y resumen
2. Los escenarios EARS/GIVEN-WHEN-THEN reemplazan a la sección `7 · Criterios`
3. `MODIFIED`/`REMOVED` implican brownfield: verificar existencia antes de generar y nunca duplicar contratos existentes
4. Si `design.md` no existe (cambio Simple), derivar archivos desde los requisitos de la spec usando el naming estándar y preguntar lo ambiguo

## Modo hoja de diseño — parsing del archivo

Cuando se provee `design_file`, la skill convierte la hoja de diseño en el mismo spec que el modo clásico. El archivo esperado sigue el flujo de 8 pasos del módulo 02 (metodología en `02-SPEC-DRIVEN-DEVELOPMENT/02-sdd-flutter-supabase.md`; el formato de diseño es el heredado del módulo histórico `02-DISENIO-FEATURE`). El parsing es **estructural por encabezados de sección** (1 Alcance, 2 Diseño, 3 Mapeo, 4 Contratos, 5 Flujo, 6 Backend, 7 Criterios, 8 Estimación), no por contenido literal.

Reglas de parsing, sección por sección:

| Sección del archivo | Qué se extrae | Cómo se usa |
|---|---|---|
| `3 · Mapeo Diseño → Capas` | Tabla `Elemento \| Capa \| Archivo` → lista exacta de archivos a generar | **Fuente principal.** Cada fila → un artefacto (tabla abajo). `feature_name` = prefijo de ruta repetido en la columna Capa (ej. `buyers`) |
| `2 · Diseño [E] Entidades` | Entidades y atributos (`Entidad: attr1, attr2, ...`) | Campos de entity/model. Los tipos se infieren (ver [Inferencia de tipos](#inferencia-de-tipos)) |
| `2 · Diseño [D] Descomponer` | Operaciones atómicas por actor | Fallback para usecases si `4 · Contratos` no las define |
| `2 · Diseño [R] Reglas` | Reglas de negocio (R001…R009) | `// TODO` comentadas en el body del usecase que las valida (matriz de `7 · Criterios` o descripción) |
| `4 · Contratos` | Firmas Dart exactas de Repository (4.1), DataSource (4.2) y UseCases (4.3) | Se usan **verbatim** (qué, no cómo). Sin `Either` explícito en la hoja → envolver según el patrón estándar (Failure/Data) |
| `6 · Backend` | Tablas Supabase y RPCs | El datasource referencia RPCs en sus TODOs; nombres de tabla para `_tableName` y migración |
| `7 · Criterios` | Escenarios BDD + matriz | No genera archivos; anota qué usecases cubre. Útil después para `flutter-test-generator` |
| `1 · Alcance` y `8 · Estimación` | Contexto y tiempos | No generan archivos |

**Artefactos por fila del mapeo (columna "Elemento"):**

| La fila contiene | Template |
|---|---|
| `Entidad` | Entity (`domain/entities/{archivo}`) |
| `Operación:` | UseCase (`domain/usecases/{archivo}`) |
| `Contrato de Repo` | Repository interface (`domain/repositories/{archivo}`) |
| `Modelo` | Model (`data/models/{archivo}`) |
| `DataSource` | Remote DataSource (`data/datasources/{archivo}`) |
| `Implementación de contrato` | Repository Impl (`data/repositories/{archivo}`) |
| `Estados de UI` | Cubit + State (`presentation/cubit/{archivo}`) |
| `Página` | Página (`presentation/pages/{archivo}`) |

**Naming:** los nombres de archivo se toman **verbatim** de la columna `Archivo` (ej. `buyer_reservations_model.dart`). La clase = UpperCamelCase del stem del archivo (`buyer_reservations_model.dart` → `BuyerReservationsModel`). El cubit se nombra por la feature del prefijo (no por el nombre del archivo state).

**Dependencias externas (multi-feature):** si una fila del mapeo apunta a otra feature (ruta distinta al prefijo `feature_name`, ej. `tickets/domain/entities/ticket_entity.dart`), NO se genera: se verifica si existe en el proyecto y, si no existe, se lista en el resumen final como dependencia externa pendiente (se generará con su propia skill de feature/component).

**Migración SQL en modo diseño:** las tablas salen de `6 · Backend`. Como el archivo normalmente no incluye columnas Postgres, si se desea migración la skill **pregunta las columnas** al usuario y genera `supabase/migrations/{timestamp}_create_{table}.sql`. Si declina, se omite y el resumen lo indica.

### Inferencia de tipos

Cuando la hoja lista atributos sin tipo Dart (ej. `Comprador: id, nombre, teléfono, fechaReservaMásReciente`), la skill infiere por convención:

| Atributo (o contiene) | Tipo Dart |
|---|---|
| `id` / `*Id` (FK) | `String` |
| `fecha*`, `created*`, `updated*`, `*At`, `*Fecha` | `DateTime` |
| `precio`, `price`, `total`, `amount`, `costo` | `double` |
| `cantidad`, `quantity`, `count`, `número`, `numero` | `int` |
| `nombre`, `name`, `título`, `title`, `teléfono`, `phone`, `estado`, `status`, `email` | `String` |
| prefijo `is*` / `has*` / `bool` | `bool` |
| default | `String` |

- Los atributos inferidos llevan `// TODO: verificar tipo` en la declaración.
- Atributos en snake_case → camelCase en Dart (`fecha_reserva` → `fechaReserva`).
- Si la hoja ya trae tipos (`id: String`), se respetan.

## Templates generados

> **Anotaciones DI:** los templates emiten las anotaciones del feature (`@LazySingleton(as:)` en datasource y repository impl, `@lazySingleton` en usecases, `@injectable` en el cubit de pantalla). El registro lo escribe `make gen` en `service_locator.config.dart` — el feature **nunca** toca `service_locator.dart`. Entity, Model, interface de Repository y Params **no** se anotan: son tipos de datos o contratos, no registros.

### Entity (`domain/entities/{feature}.dart`)

```dart
import 'package:equatable/equatable.dart';

class {Feature} extends Equatable {
  const {Feature}({
    required this.id,
{fields_required_ctor}
  });

{fields_declarations}

  @override
  List<Object?> get props => [{fields_props}];

  {Feature} copyWith({
    {fields_copywith_params}
  }) {
    return {Feature}(
      {fields_copywith_body}
    );
  }

  @override
  String toString() => '{Feature}({fields_tostring})';
}
```

### Repository interface (`domain/repositories/{feature}_repository.dart`)

```dart
import 'package:fpdart/fpdart.dart';
import 'package:{app_name}/core/error/failures.dart';
import 'package:{app_name}/features/{feature}/domain/entities/{feature}.dart';

abstract class {Feature}Repository {
{methods_repository_interface}
}
```

### Model (`data/models/{feature}_model.dart`)

**Sin Supabase** (mapeo genérico):
```dart
import 'package:{app_name}/features/{feature}/domain/entities/{feature}.dart';

class {Feature}Model extends {Feature} {
  const {Feature}Model({super fields});

  factory {Feature}Model.fromJson(Map<String, dynamic> json) {
    return {Feature}Model(
{fields_fromjson}
    );
  }

  Map<String, dynamic> toJson() => {
{fields_tojson}
  };

  factory {Feature}Model.fromEntity({Feature} entity) {
    return {Feature}Model(
{fields_fromentity}
    );
  }

  {Feature} toEntity() => {Feature}(
{fields_toentity}
  );
}
```

**Con Supabase** (mapeo snake_case): igual estructura pero los placeholders `{fields_fromjson}`, `{fields_tojson}` usan claves snake_case (`user_id`, `created_at`) en lugar de camelCase.

### Remote DataSource (`data/datasources/{feature}_remote_datasource.dart`)

**Sin Supabase** (genérico):
```dart
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:{app_name}/core/error/exceptions.dart';
import 'package:{app_name}/features/{feature}/data/models/{feature}_model.dart';

abstract class {Feature}RemoteDataSource {
{methods_datasource_abstract}
}

/// `@LazySingleton(as:)`: cuando algo pida `{Feature}RemoteDataSource`, se
/// resuelve a esta concreta. `make gen` escribe el registro.
@LazySingleton(as: {Feature}RemoteDataSource)
class {Feature}RemoteDataSourceImpl implements {Feature}RemoteDataSource {
  final SupabaseClient _supabase;

  {Feature}RemoteDataSourceImpl({required SupabaseClient supabase})
      : _supabase = supabase;

{methods_datasource_impl}
}
```

**Con Supabase** (igual + `_tableName` + `watchById`):
```dart
import 'dart:async';
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:{app_name}/core/error/exceptions.dart';
import 'package:{app_name}/features/{feature}/data/models/{feature}_model.dart';

abstract class {Feature}RemoteDataSource {
{methods_datasource_abstract}
  Stream<{Feature}Model> watchById(String id);
}

/// `@LazySingleton(as:)`: cuando algo pida `{Feature}RemoteDataSource`, se
/// resuelve a esta concreta. `make gen` escribe el registro.
@LazySingleton(as: {Feature}RemoteDataSource)
class {Feature}RemoteDataSourceImpl implements {Feature}RemoteDataSource {
  final SupabaseClient _supabase;
  final String _tableName = '{table_name}';

  {Feature}RemoteDataSourceImpl({required SupabaseClient supabase})
      : _supabase = supabase;

{methods_datasource_impl}

  @override
  Stream<{Feature}Model> watchById(String id) {
    throw UnimplementedError('{Feature}RemoteDataSource.watchById');
  }
}
```

### Repository Impl (`data/repositories/{feature}_repository_impl.dart`)

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:{app_name}/core/error/failures.dart';
import 'package:{app_name}/core/error/exceptions.dart';
import 'package:{app_name}/features/{feature}/domain/entities/{feature}.dart';
import 'package:{app_name}/features/{feature}/domain/repositories/{feature}_repository.dart';
import 'package:{app_name}/features/{feature}/data/datasources/{feature}_remote_datasource.dart';

/// `@LazySingleton(as:)`: cuando algo pida `{Feature}Repository`, se resuelve
/// a esta concreta. `make gen` escribe el registro.
@LazySingleton(as: {Feature}Repository)
class {Feature}RepositoryImpl implements {Feature}Repository {
  final {Feature}RemoteDataSource remoteDataSource;

  {Feature}RepositoryImpl({required this.remoteDataSource});

{methods_repository_impl}
}
```

**Patrón esperado por método:**
```dart
// TODO: implementar. Resolver antes de escribir:
//   1) ¿Qué contrato cumple este método? (qué recibe, qué devuelve)
//   2) ¿Qué capa inferior interviene? (datasource, cache, red)
//   3) ¿Qué mapeo entity <-> model aplica?
//   4) ¿Qué puede fallar y cómo se traduce a Failure?
```

### UseCases (`domain/usecases/{action}_{feature}.dart`)

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:{app_name}/core/common/usecase.dart';
import 'package:{app_name}/core/error/failures.dart';
import 'package:{app_name}/features/{feature}/domain/entities/{feature}.dart';
import 'package:{app_name}/features/{feature}/domain/repositories/{feature}_repository.dart';

/// `@lazySingleton`: el use case no tiene estado, una instancia para la app.
/// Converso: `{Action}{Feature}Params` (abajo) NO se anota.
@lazySingleton
class {Action}{Feature} extends UseCase<{ReturnType}, {Action}{Feature}Params> {
  final {Feature}Repository repository;

  {Action}{Feature}(this.repository);

  @override
  Future<Either<Failure, {ReturnType}>> call({Action}{Feature}Params params) async {
    throw UnimplementedError('{Action}{Feature}.call');
  }
}

class {Action}{Feature}Params extends Equatable {
{params_fields}

  const {Action}{Feature}Params({params_ctor});

  @override
  List<Object?> get props => [{params_props}];
}
```

### Cubit + State (`presentation/cubit/{feature}_cubit.dart`)

```dart
import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';
import 'package:{app_name}/core/common/usecase.dart';
import 'package:{app_name}/features/{feature}/domain/entities/{feature}.dart';
import 'package:{app_name}/features/{feature}/domain/usecases/get_{feature}s.dart';
import 'package:{app_name}/features/{feature}/domain/usecases/get_{feature}.dart';
import 'package:{app_name}/features/{feature}/domain/usecases/create_{feature}.dart';
import 'package:{app_name}/features/{feature}/domain/usecases/delete_{feature}.dart';

part '{feature}_state.dart';

/// `@injectable` genera un `factory`: cada pantalla que pida el cubit recibe
/// una instancia nueva. **Nunca `@lazySingleton` en un cubit de pantalla.**
@injectable
class {Feature}Cubit extends Cubit<{Feature}State> {
  final Get{Feature}s _get{Feature}s;
  final Get{Feature} _get{Feature};
  final Create{Feature} _create{Feature};
  final Delete{Feature} _delete{Feature};

  {Feature}Cubit({
    required Get{Feature}s get{Feature}s,
    required Get{Feature} get{Feature},
    required Create{Feature} create{Feature},
    required Delete{Feature} delete{Feature},
  })  : _get{Feature}s = get{Feature}s,
        _get{Feature} = get{Feature},
        _create{Feature} = create{Feature},
        _delete{Feature} = delete{Feature},
        super({Feature}Initial());

{cubit_methods}

  void clearError() {
    // TODO: optional — emit copy of previous state without error
  }
}
```

### State (`presentation/cubit/{feature}_state.dart`)

```dart
part of '{feature}_cubit.dart';

sealed class {Feature}State extends Equatable {
  const {Feature}State();

  @override
  List<Object?> get props => [];
}

final class {Feature}Initial extends {Feature}State {}

final class {Feature}Loading extends {Feature}State {}

final class {Feature}sLoaded extends {Feature}State {
  final List<{Feature}> {feature}s;
  const {Feature}sLoaded(this.{feature}s);

  @override
  List<Object?> get props => [{feature}s];
}

final class {Feature}Loaded extends {Feature}State {
  final {Feature} {feature};
  const {Feature}Loaded(this.{feature});

  @override
  List<Object?> get props => [{feature}];
}

final class {Feature}Error extends {Feature}State {
  final String message;
  const {Feature}Error(this.message);

  @override
  List<Object?> get props => [message];
}
```

### Templates de página (solo si se proporcionó `pages`)

Patrones disponibles (coinciden con los estados del cubit generado: `{Feature}Loading`, `{Feature}sLoaded`, `{Feature}Loaded`, `{Feature}Error`):

| Pattern | Cuándo usarlo |
|---|---|
| `listener_builder` | **Default**. Cualquier página con side effects (snackbars, navegación post-acción). Usa `BlocListener` + `BlocBuilder`. |
| `builder` | Página de solo lectura sin efectos secundarios. Usa solo `BlocBuilder`. |
| `form` | Formulario con validación, controllers, submit loading. Usa `BlocListener` + `BlocBuilder`. |

#### Pattern: listener_builder — BlocListener + BlocBuilder (default)

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:{app_name}/core/services/snackbar_helper.dart';
import 'package:{app_name}/core/widgets/app_button.dart';
import 'package:{app_name}/features/{feature}/presentation/cubit/{feature}_cubit.dart';

class {Feature}{PageName}Page extends StatefulWidget {
  const {Feature}{PageName}Page({super.key});

  @override
  State<{Feature}{PageName}Page> createState() => _{Feature}{PageName}PageState();
}

class _{Feature}{PageName}PageState extends State<{Feature}{PageName}Page> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<{Feature}Cubit>().load{Feature}s();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('{PageTitle}')),
      body: BlocListener<{Feature}Cubit, {Feature}State>(
        listener: (context, state) {
          // TODO: handle side effects
          // if (state is {Feature}Loaded && state.xxxError != null) {
          //   SnackbarHelper.show(context, state.xxxError!, isSuccess: false);
          //   context.read<{Feature}Cubit>().clearXxxError();
          // }
          // if (state is {Feature}{Action}Success) {
          //   SnackbarHelper.show(context, 'Operación exitosa', isSuccess: true);
          //   context.pop();
          // }
        },
        child: BlocBuilder<{Feature}Cubit, {Feature}State>(
          builder: (context, state) {
            if (state is {Feature}Loading) {
              return const Center(child: CircularProgressIndicator());
            }
            if (state is {Feature}Error) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(state.message, overflow: TextOverflow.ellipsis),
                    const SizedBox(height: 16),
                    AppButton(
                      label: 'Reintentar',
                      onPressed: () => context.read<{Feature}Cubit>().load{Feature}s(),
                      variant: AppButtonVariant.primary,
                    ),
                  ],
                ),
              );
            }
            if (state is {Feature}sLoaded) {
              // TODO: render content
              return const Center(child: Text('Implement {Feature}{PageName} content'));
            }
            return const Center(child: CircularProgressIndicator());
          },
        ),
      ),
    );
  }

  void _refresh() {
    context.read<{Feature}Cubit>().load{Feature}s();
  }
}
```

#### Pattern: builder — BlocBuilder (solo lectura)

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:{app_name}/core/widgets/app_button.dart';
import 'package:{app_name}/features/{feature}/presentation/cubit/{feature}_cubit.dart';

class {Feature}{PageName}Page extends StatelessWidget {
  const {Feature}{PageName}Page({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('{PageTitle}')),
      body: BlocBuilder<{Feature}Cubit, {Feature}State>(
        builder: (context, state) {
          if (state is {Feature}Loading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is {Feature}Loaded) {
            // TODO: render content
            return const Center(child: Text('Implement {Feature}{PageName} content'));
          }
          if (state is {Feature}Error) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(state.message, overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 16),
                  AppButton(
                    label: 'Reintentar',
                    onPressed: () => context.read<{Feature}Cubit>().load{Feature}s(),
                    variant: AppButtonVariant.primary,
                  ),
                ],
              ),
            );
          }
          return const Center(child: CircularProgressIndicator());
        },
      ),
    );
  }
}
```

#### Pattern: form — Formulario con validación

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:{app_name}/core/services/snackbar_helper.dart';
import 'package:{app_name}/core/widgets/app_button.dart';
import 'package:{app_name}/features/{feature}/presentation/cubit/{feature}_cubit.dart';

class {Feature}{PageName}Page extends StatefulWidget {
  const {Feature}{PageName}Page({super.key});

  @override
  State<{Feature}{PageName}Page> createState() => _{Feature}{PageName}PageState();
}

class _{Feature}{PageName}PageState extends State<{Feature}{PageName}Page> {
  final _formKey = GlobalKey<FormState>();

  // TODO: declare TextEditingController for each field
  // late final TextEditingController _nameController;

  @override
  void initState() {
    super.initState();
    // TODO: initialize controllers
    // _nameController = TextEditingController(text: initialValue);
  }

  @override
  void dispose() {
    // TODO: dispose controllers
    // _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('{PageTitle}')),
      body: BlocListener<{Feature}Cubit, {Feature}State>(
        listener: (context, state) {
          // TODO: handle success / error side effects
          // if (state is {Feature}{Action}Success) {
          //   SnackbarHelper.show(context, 'Guardado exitoso', isSuccess: true);
          //   context.pop();
          // }
          // if (state is {Feature}Error) {
          //   SnackbarHelper.show(context, state.message, isSuccess: false);
          // }
        },
        child: BlocBuilder<{Feature}Cubit, {Feature}State>(
          builder: (context, state) {
            final isLoading = state is {Feature}Loading;

            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // TODO: TextFormField for each field
                    // TextFormField(
                    //   controller: _nameController,
                    //   decoration: const InputDecoration(labelText: 'Name'),
                    //   validator: (v) => v?.isEmpty == true ? 'Required' : null,
                    // ),
                    const SizedBox(height: 24),
                    AppButton(
                      label: 'Guardar',
                      onPressed: isLoading ? null : _submit,
                      variant: AppButtonVariant.primary,
                      isLoading: isLoading,
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  void _submit() {
    // TODO: implement submit
    // if (_formKey.currentState!.validate()) {
    //   context.read<{Feature}Cubit>().create{Feature}(
    //     {Feature}(
    //       name: _nameController.text,
    //       // ... more fields
    //     ),
    //   );
    // }
  }
}
```

### Migración SQL (solo si se proporcionó `table_name` + `columns`)

```
supabase/migrations/{timestamp}_create_{table}.sql
```

```sql
-- Create {table_name} table
-- Review and customize before applying

CREATE TABLE {table_name} (
{columns_sql_definitions}
);

-- Indexes
{indexes_sql}

-- Enable Row Level Security
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

-- RLS Policies (customize per business rules)
{default_rls_policies}

-- Triggers
{triggers_sql}
```

#### Default RLS policies generados

```sql
-- Allow read access to authenticated users
CREATE POLICY "Users can read {table_name}"
  ON {table_name}
  FOR SELECT
  TO authenticated
  USING (true);

-- Allow insert for authenticated users
CREATE POLICY "Users can insert {table_name}"
  ON {table_name}
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Allow update for own records
CREATE POLICY "Users can update own {table_name}"
  ON {table_name}
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);
```

## Workflow

1. Determinar el modo de entrada:
   - **Modo cambio OpenSpec** (si se proporciona `openspec_change`): parsear la carpeta con [Modo cambio OpenSpec](#modo-cambio-openspec--parsing-de-la-carpeta). Derivar feature, archivos, requisitos→usecases (con REQ en TODOs), contratos verbatim y tablas. NO preguntar `feature_name`, `fields` ni `operations`. Listar MODIFIED/REMOVED como pendientes brownfield.
   - **Modo hoja de diseño** (si se proporciona `design_file`): leer el archivo y parsearlo con [Modo hoja de diseño](#modo-hoja-de-diseño--parsing-del-archivo). Derivar feature, lista de archivos, entidades/campos (con inferencia de tipos), usecases, contratos y tablas. NO preguntar `feature_name`, `fields` ni `operations`.
   - **Modo clásico** (si no): preguntar feature name, lista de campos (nombre + tipo Dart), operaciones CRUD deseadas, y nombre del paquete (app name)
2. Preguntar opcionalmente: table_name y columnas Postgres si desea integración Supabase. En modo hoja de diseño las tablas se deducen del archivo; en modo cambio OpenSpec salen de `design.md` §Backend Supabase (si incluye columnas se usan tal cual; si no, preguntarlas solo si se desea migración)
3. Preguntar opcionalmente: páginas iniciales deseadas (`pages`) con sus patrones — si se omiten, generar el placeholder genérico (modo clásico) o las páginas del mapeo con patrón `listener_builder` (modo hoja de diseño)
4. Preguntar opcionalmente: wiring deseado (`[di]`, `[router]` o `[di, router]`)
5. Generar cada archivo siguiendo los templates de arriba
6. Si se proporcionó Supabase: generar además migración SQL con CREATE TABLE + índices + RLS
7. Si se proporcionó `pages` (o el mapeo define páginas): generar una página por entrada con el template de su patrón
8. Si se proporcionó `wiring` con `di`: invocar la skill `di-getit-scaffold` pasándole los componentes generados (datasources, repositorios, usecases, cubit, estado). Las clases ya salen **anotadas** de los templates; la skill verifica las anotaciones y `external_module.dart`, y recuerda correr `make gen`. No escribir el registro a mano — delegar.
9. Si se proporcionó `wiring` con `router`: invocar la skill `go-route-scaffold` pasándole las páginas generadas para que actualice `app_router.dart`. No escribir la lógica de rutas aquí — delegar.
10. No generar bodies de métodos — usar `throw UnimplementedError()`
11. Mostrar resumen de archivos creados al final. En modo hoja de diseño incluir además: dependencias externas pendientes (si hay) y campos con tipo inferido (`// TODO: verificar tipo`). En modo cambio OpenSpec incluir: requisitos ADDED cubiertos (REQ → usecase), requisitos MODIFIED/REMOVED pendientes brownfield, y matriz Req↔tarea si existe
12. Recordar al usuario que debe: implementar bodies, revisar RLS policies si aplica, ejecutar migración en Supabase, verificar los tipos inferidos en modo hoja de diseño, y ejecutar `flutter pub get` si añadió nuevos paquetes
