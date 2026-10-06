---
name: clean-arch-component
description: Generate individual Clean Architecture components (entity, model, usecase, cubit+state, datasource, repository, repository_impl, page) for an existing feature. Pages use the listener_builder / builder / form patterns. Only generates structure — never implementation bodies.
---

# clean-arch-component — Scaffold de componente individual

Genera un archivo individual para una feature ya existente. Útil cuando necesitas añadir un usecase nuevo, un modelo, o un cubit a una feature que ya tiene su estructura base.

## Componentes disponibles

| Tipo | Genera | Depende de |
|---|---|---|
| `entity` | Entity con Equatable + copyWith + props | Fields |
| `model` | Model con fromJson/toJson + fromEntity/toEntity | Entity existente |
| `usecase` | UseCase + Params | Repository existente |
| `cubit` | Cubit + State (ambos archivos) | Usecases existentes |
| `datasource` | DataSource abstract + impl | SupabaseClient |
| `repository` | Repository abstract interface | Entity existente |
| `repository_impl` | Repository implementation | DataSource + Repository interface |
| `page` | Página conectada al cubit (listener_builder / builder / form) | Cubit existente |

## Input requerido

- **feature_name**: nombre de la feature (snake_case)
- **component_type**: tipo de componente a generar
- **fields**: lista de campos (solo para entity/model)
- **operation**: nombre de la operación (solo para usecase, ej: `get`, `create`, `delete`)
- **page_name**: nombre de la página (solo para page, ej: `list`, `detail`, `edit`)
- **pattern_type**: patrón de la página (solo para page: `listener_builder`, `builder`, `form`)

## Templates

> **Anotaciones DI:** los templates que son registros (usecase, cubit, datasource impl, repository_impl) llevan su anotación (`@lazySingleton`, `@injectable`, `@LazySingleton(as:)`). El registro lo escribe `make gen` en `service_locator.config.dart` — no se toca `service_locator.dart`. Entity, Model, interface de Repository y Params **nunca** se anotan: son tipos de datos o contratos, no registros.

### Entity

```dart
import 'package:equatable/equatable.dart';

class {Feature} extends Equatable {
  const {Feature}({
{fields_required_ctor}
  });

{fields_declarations}

  {Feature} copyWith({
{fields_copywith_params}
  }) {
    return {Feature}(
{fields_copywith_body}
    );
  }

  @override
  List<Object?> get props => [{fields_props}];
}
```

### Model

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

### Usecase

```dart
import 'package:fpdart/fpdart.dart';
import 'package:equatable/equatable.dart';
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

### Cubit + State

```dart
// {feature}_cubit.dart
import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';
import 'package:{app_name}/core/common/usecase.dart';
import 'package:{app_name}/features/{feature}/domain/entities/{feature}.dart';
import 'package:{app_name}/features/{feature}/domain/usecases/get_{feature}s.dart';
import 'package:{app_name}/features/{feature}/domain/usecases/get_{feature}.dart';

part '{feature}_state.dart';

/// `@injectable` genera un `factory`: cada pantalla que pida el cubit recibe
/// una instancia nueva. **Nunca `@lazySingleton` en un cubit de pantalla.**
@injectable
class {Feature}Cubit extends Cubit<{Feature}State> {
  final Get{Feature}s _get{Feature}s;
  final Get{Feature} _get{Feature};

  {Feature}Cubit({
    required Get{Feature}s get{Feature}s,
    required Get{Feature} get{Feature},
  })  : _get{Feature}s = get{Feature}s,
        _get{Feature} = get{Feature},
        super({Feature}Initial());

  Future<void> load{Feature}s() async {
    emit({Feature}Loading());
    // TODO: implement
    // final result = await _get{Feature}s(NoParams());
    // result.fold(
    //   (failure) => emit({Feature}Error(failure.message)),
    //   ({feature}s) => emit({Feature}sLoaded({feature}s)),
    // );
  }

  Future<void> load{Feature}(String id) async {
    emit({Feature}Loading());
    // TODO: implement
    // final result = await _get{Feature}(Get{Feature}Params(id: id));
    // result.fold(
    //   (failure) => emit({Feature}Error(failure.message)),
    //   ({feature}) => emit({Feature}Loaded({feature})),
    // );
  }

  void clearError() {
    // TODO: optional — emit a copy of previous loaded state without error
    // if (state is {Feature}Error) {
    //   final previous = (state as {Feature}Error).previousState;
    //   if (previous != null) emit(previous as {Feature}State);
    // }
  }
}
```

```dart
// {feature}_state.dart
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

### DataSource

```dart
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:{app_name}/core/error/exceptions.dart';
import 'package:{app_name}/features/{feature}/data/models/{feature}_model.dart';

abstract class {Feature}RemoteDataSource {
  Future<List<{Feature}Model>> getAll();
  Future<{Feature}Model> getById(String id);
}

/// `@LazySingleton(as:)`: cuando algo pida `{Feature}RemoteDataSource`, se
/// resuelve a esta concreta. `make gen` escribe el registro.
@LazySingleton(as: {Feature}RemoteDataSource)
class {Feature}RemoteDataSourceImpl implements {Feature}RemoteDataSource {
  final SupabaseClient _supabase;

  {Feature}RemoteDataSourceImpl({required SupabaseClient supabase})
      : _supabase = supabase;

  @override
  Future<List<{Feature}Model>> getAll() async {
    throw UnimplementedError('getAll');
  }

  @override
  Future<{Feature}Model> getById(String id) async {
    throw UnimplementedError('getById');
  }
}
```

### Repository Interface

```dart
import 'package:fpdart/fpdart.dart';
import 'package:{app_name}/core/error/failures.dart';
import 'package:{app_name}/features/{feature}/domain/entities/{feature}.dart';

abstract class {Feature}Repository {
  Future<Either<Failure, List<{Feature}>>> getAll();
  Future<Either<Failure, {Feature}>> getById(String id);
  Future<Either<Failure, void>> create({Feature} {feature});
  Future<Either<Failure, void>> update({Feature} {feature});
  Future<Either<Failure, void>> delete(String id);
}
```

### Repository Implementation

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

  @override
  Future<Either<Failure, List<{Feature}>>> getAll() async {
    // TODO: implement
    // try {
    //   final models = await remoteDataSource.getAll();
    //   return Right(models.map((m) => m.toEntity()).toList());
    // } on ServerException catch (e) {
    //   return Left(ServerFailure(e.message));
    // } on CacheException catch (e) {
    //   return Left(CacheFailure(e.message));
    // }
    throw UnimplementedError('getAll');
  }

  @override
  Future<Either<Failure, {Feature}>> getById(String id) async {
    // TODO: implement
    throw UnimplementedError('getById');
  }

  @override
  Future<Either<Failure, void>> create({Feature} {feature}) async {
    // TODO: implement
    throw UnimplementedError('create');
  }

  @override
  Future<Either<Failure, void>> update({Feature} {feature}) async {
    // TODO: implement
    throw UnimplementedError('update');
  }

  @override
  Future<Either<Failure, void>> delete(String id) async {
    // TODO: implement
    throw UnimplementedError('delete');
  }
}
```

### Page

Genera `lib/features/{feature}/presentation/pages/{feature}_{page_name}_page.dart` conectada al cubit existente.

Los templates de página viven en `clean-arch-feature` (sección **"Templates de página"**) y se reutilizan aquí tal cual — fuente única, no duplicar:

| pattern_type | Template a usar (en clean-arch-feature) | Placeholders |
|---|---|---|
| `listener_builder` | Pattern listener_builder (default) | `{Feature}{PageName}Page`, `BlocListener` + `BlocBuilder` |
| `builder` | Pattern builder | `{Feature}{PageName}Page`, solo `BlocBuilder` |
| `form` | Pattern form | `{Feature}{PageName}Page`, `Form` + `GlobalKey<FormState>` |

Reglas de naming:
- Clase: `{Feature}{PageName}Page` (ej: `OrderDetailPage`)
- Archivo: `{feature}_{page_name}_page.dart` — usar plural de la feature solo si `page_name` es `list` (ej: `orders_list_page.dart`)
- Si el cubit no tiene el método `load{Feature}s()` para la página `list`, ajustar el método invocado al que exista

## Workflow

1. Preguntar al usuario: feature_name, component_type, y params específicos del tipo
2. Verificar que la carpeta `features/{feature}/` existe (avisar si no)
3. Generar el archivo usando el template correspondiente
4. Para `page`: cargar el template desde `clean-arch-feature` según `pattern_type`; verificar que el cubit exista y que use los estados que el template referencia
5. No generar bodies de métodos — usar `throw UnimplementedError()` o `// TODO: implement`
6. Si el componente lleva anotación DI (usecase, cubit, datasource, repository_impl): el registro aparece al correr `make gen` — recordar que `service_locator.config.dart` se commitea y nunca se edita a mano
7. Mostrar la ruta del archivo creado y recordar conectar la página en el router (`go-route-scaffold`)
