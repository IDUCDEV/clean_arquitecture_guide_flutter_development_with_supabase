## FASE 4 -- El slice vertical descartable

### 4.1 Para que existe esta fase

Un bootstrap que genera solo `core/` no esta verificado. Si el agente escribio
cuatrocientas lineas de `core/` que compilan, pero los errores aparecen en como se
conectan las piezas entre si, el proyecto arranca roto y el error aparece cuando
la primera feature real este a medio hacer.

Esta fase genera **una feature completa de punta a punta**, con datasource en
memoria, para que al terminar se pueda correr la app y ver que anda. Y existe
tambien para poder **borrarla**: es la ultima en 3 minutos con
`make drop-feature`.

No es un ejemplo de dominio. No hay usuarios, ni pedidos, ni pagos. Hay una
entidad generica con titulo y contenido, guardada en `CachedEntry` de Isar,
accesible sin sesion.

**La regla:** si no podes borrar `features/{{FEATURE_EJEMPLO}}/` sin tocar nada mas
del proyecto, el slice esta acoplado y hay que arreglarlo antes de seguir.

### 4.2 Estructura

```
lib/features/{{FEATURE_EJEMPLO}}/
├── data/
│   ├── datasources/
│   │   └── {{FEATURE_EJEMPLO}}_local_data_source.dart
│   ├── models/
│   │   └── {{FEATURE_EJEMPLO}}_model.dart
│   └── repositories/
│       └── {{FEATURE_EJEMPLO}}_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── {{FEATURE_EJEMPLO}}_entity.dart
│   ├── repositories/
│   │   └── {{FEATURE_EJEMPLO}}_repository.dart
│   └── usecases/
│       ├── get_{{FEATURE_EJEMPLO}}s_usecase.dart
│       ├── create_{{FEATURE_EJEMPLO}}_usecase.dart
│       └── delete_{{FEATURE_EJEMPLO}}_usecase.dart
└── presentation/
    ├── cubit/
    │   ├── {{FEATURE_EJEMPLO}}_cubit.dart
    │   └── {{FEATURE_EJEMPLO}}_state.dart
    ├── pages/
    │   ├── {{FEATURE_EJEMPLO}}_page.dart
    │   └── {{FEATURE_EJEMPLO}}_detail_page.dart
    └── widgets/
        └── {{FEATURE_EJEMPLO}}_tile.dart
```

Y los tests, espejando:

```
test/features/{{FEATURE_EJEMPLO}}/
├── data/
│   ├── datasources/{{FEATURE_EJEMPLO}}_local_data_source_test.dart
│   ├── models/{{FEATURE_EJEMPLO}}_model_test.dart
│   └── repositories/{{FEATURE_EJEMPLO}}_repository_impl_test.dart
├── domain/usecases/
│   ├── get_{{FEATURE_EJEMPLO}}s_usecase_test.dart
│   ├── create_{{FEATURE_EJEMPLO}}_usecase_test.dart
│   └── delete_{{FEATURE_EJEMPLO}}_usecase_test.dart
└── presentation/
    ├── cubit/{{FEATURE_EJEMPLO}}_cubit_test.dart
    └── pages/{{FEATURE_EJEMPLO}}_page_test.dart
```

Y un fixture:

```
test/fixtures/{{FEATURE_EJEMPLO}}.json
```

### 4.3 Dominio

**`lib/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart`**

```dart
import 'package:equatable/equatable.dart';

/// Entidad de dominio.
///
/// Sin `json`, sin anotaciones, sin `fromJson`. Una entidad es el concepto; su
/// representacion en JSON es responsabilidad del model, en la capa de datos.
class {{DART_NOMBRE_CLASE}}Entity extends Equatable {
  const {{DART_NOMBRE_CLASE}}Entity({
    required this.id,
    required this.title,
    required this.body,
    required this.createdAt,
  });

  final String id;
  final String title;
  final String body;
  final DateTime createdAt;

  @override
  List<Object?> get props => [id, title, body, createdAt];
}
```

**`lib/features/{{FEATURE_EJEMPLO}}/domain/repositories/{{FEATURE_EJEMPLO}}_repository.dart`**

```dart
import 'package:fpdart/fpdart.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart';

/// Contrato del repositorio.
///
/// La capa `domain` define la interfaz; `data` la implementa. Un use case depende
/// de esta abstraccion, nunca de la implementacion, asi que se puede testear sin
/// Isar ni Supabase.
abstract class {{DART_NOMBRE_CLASE}}Repository {
  Future<Either<Failure, List<{{DART_NOMBRE_CLASE}}Entity>>> getAll();

  Future<Either<Failure, {{DART_NOMBRE_CLASE}}Entity>> getById(String id);

  Future<Either<Failure, {{DART_NOMBRE_CLASE}}Entity>> create({
    required String title,
    required String body,
  });

  Future<Either<Failure, Unit>> delete(String id);
}
```

> `Unit` (de `fpdart`) y no `void`: `Either<Failure, void>` no se puede componer
> con `fold` ni con `doOnRight` sin castear. `Unit` es el valor de "salio bien y
> no hay nada que devolver".

**`get_{{FEATURE_EJEMPLO}}s_usecase.dart`**, **`create_{{FEATURE_EJEMPLO}}_usecase.dart`** y
**`delete_{{FEATURE_EJEMPLO}}_usecase.dart`** -- tres use cases, mismo patron. El primero
completo, los otros dos con el mismo esqueleto:

```dart
import 'package:injectable/injectable.dart';
import 'package:fpdart/fpdart.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/common/usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/repositories/{{FEATURE_EJEMPLO}}_repository.dart';

/// Obtiene todos los elementos.
///
/// Notar que el use case **no** tiene try/catch ni logica de red. Toda la
/// traduccion Exception -> Failure vive en el repositorio. Un use case con
/// `try {}` alrededor de la llamada al repositorio seria codigo muerto: el
/// repositorio nunca deja escapar una excepcion.
///
/// `@lazySingleton`: el use case no tiene estado, asi que una instancia para
/// toda la app alcanza. Los bloques de `CreateUseCase` y `DeleteUseCase` abajo no repiten
/// imports: cada uno de sus archivos arranca con
/// `import 'package:injectable/injectable.dart';`.
@lazySingleton
class Get{{DART_NOMBRE_PLURAL}}UseCase extends NoParamsUseCase<
    List<{{DART_NOMBRE_CLASE}}Entity>> {
  Get{{DART_NOMBRE_PLURAL}}UseCase(this._repository);

  final {{DART_NOMBRE_CLASE}}Repository _repository;

  @override
  Future<Either<Failure, List<{{DART_NOMBRE_CLASE}}Entity>>> call() {
    return _repository.getAll();
  }
}
```

```dart
@lazySingleton
class Create{{DART_NOMBRE_CLASE}}UseCase extends UseCase<
    {{DART_NOMBRE_CLASE}}Entity, Create{{DART_NOMBRE_CLASE}}UseCaseParams> {
  Create{{DART_NOMBRE_CLASE}}UseCase(this._repository);

  final {{DART_NOMBRE_CLASE}}Repository _repository;

  @override
  Future<Either<Failure, {{DART_NOMBRE_CLASE}}Entity>> call(
    Create{{DART_NOMBRE_CLASE}}UseCaseParams params,
  ) {
    return _repository.create(title: params.title, body: params.body);
  }
}

/// Params de `Create{{DART_NOMBRE_CLASE}}UseCase`.
///
/// `const`-able y `Equatable`, en el mismo archivo que el use case. Si sus
/// parametros no son primitivos, `registerFallbackValue` en los tests de cubit.
class Create{{DART_NOMBRE_CLASE}}UseCaseParams extends Equatable {
  const Create{{DART_NOMBRE_CLASE}}UseCaseParams({
    required this.title,
    required this.body,
  });

  final String title;
  final String body;

  @override
  List<Object?> get props => [title, body];
}
```

```dart
@lazySingleton
class Delete{{DART_NOMBRE_CLASE}}UseCase extends UseCase<Unit, String> {
  Delete{{DART_NOMBRE_CLASE}}UseCase(this._repository);

  final {{DART_NOMBRE_CLASE}}Repository _repository;

  @override
  Future<Either<Failure, Unit>> call(String id) {
    return _repository.delete(id);
  }
}
```

### 4.4 Capa de datos

**`{{FEATURE_EJEMPLO}}_local_data_source.dart`** -- sobre Isar, sin backend:

```dart
import 'dart:convert';

import 'package:injectable/injectable.dart';
import 'package:isar_community/isar.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/constants/constants.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/data/local/isar_service.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/exceptions.dart';

/// Acceso a la cache local de los elementos.
///
/// **Por que Isar y no Supabase a proposito:** este datasource existe para
/// verificar el cableado completo (DI -> data -> domain -> presentation) sin
/// depender de una tabla que todavia no existe. Cuando sumes tu primer backend
/// real, agregá `{{FEATURE_EJEMPLO}}_remote_data_source.dart` al lado y hacé que
/// el repositorio lea de los dos.
abstract class {{DART_NOMBRE_CLASE}}LocalDataSource {
  Future<List<Map<String, dynamic>>> getAll();
  Future<Map<String, dynamic>?> getById(String id);
  Future<Map<String, dynamic>> save({
    required String id,
    required String title,
    required String body,
  });
  Future<void> delete(String id);
}

/// `@LazySingleton(as:)`: esta concreta es la que resuelve cuando algo pide un
/// `{{DART_NOMBRE_CLASE}}LocalDataSource`. El `Isar` sale del `@module`.
@LazySingleton(as: {{DART_NOMBRE_CLASE}}LocalDataSource)
class {{DART_NOMBRE_CLASE}}LocalDataSourceImpl
    implements {{DART_NOMBRE_CLASE}}LocalDataSource {
  {{DART_NOMBRE_CLASE}}LocalDataSourceImpl(this._isar);

  final Isar _isar;

  /// Prefijo de namespace. Sin esto, el `where().findAll()` de esta feature
  /// devolveria **todas** las entradas de la app, de todas las features. El
  /// prefijo es lo que hace posible una unica coleccion compartida.
  static const String _prefix = '{{FEATURE_EJEMPLO}}:';

  String _key(String id) => '$_prefix$id';

  @override
  Future<List<Map<String, dynamic>>> getAll() async {
    try {
      final entries = await _isar.cachedEntrys
          .filter()
          .keyStartsWith(_prefix)
          .findAll();

      return entries
          .map((entry) => jsonDecode(entry.payload) as Map<String, dynamic>)
          .toList();
    } on IsarError catch (e) {
      // El prefijo en el mensaje no es para el usuario: es para el log. El
      // repositorio lo traduce.
      throw CacheException(message: 'cache_read_error: $e');
    }
  }

  @override
  Future<Map<String, dynamic>?> getById(String id) async {
    try {
      final entry = await _isar.cachedEntrys.get(_key(id));
      if (entry == null) return null;
      if (_isExpired(entry)) {
        await delete(id);
        return null;
      }
      return jsonDecode(entry.payload) as Map<String, dynamic>;
    } on IsarError catch (e) {
      throw CacheException(message: 'cache_read_error: $e');
    }
  }

  @override
  Future<Map<String, dynamic>> save({
    required String id,
    required String title,
    required String body,
  }) async {
    final payload = <String, dynamic>{
      'id': id,
      'title': title,
      'body': body,
      'createdAt': DateTime.now().toIso8601String(),
    };

    try {
      await _isar.writeTxn(() async {
        await _isar.cachedEntrys.put(
          CachedEntry(
            key: _key(id),
            payload: jsonEncode(payload),
            cachedAt: DateTime.now(),
            expiresAt: DateTime.now().add(AppConstants.cacheTtl),
          ),
        );
      });
    } on IsarError catch (e) {
      throw CacheException(message: 'cache_write_error: $e');
    }

    return payload;
  }

  @override
  Future<void> delete(String id) async {
    try {
      await _isar.writeTxn(() async {
        await _isar.cachedEntrys.delete(_key(id));
      });
    } on IsarError catch (e) {
      throw CacheException(message: 'cache_write_error: $e');
    }
  }

  static bool _isExpired(CachedEntry entry) {
    final expiresAt = entry.expiresAt;
    return expiresAt != null && expiresAt.isBefore(DateTime.now());
  }
}
```

**`{{FEATURE_EJEMPLO}}_model.dart`**

```dart
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart';

/// De JSON a entidad.
///
/// Los nombres de campo del JSON se repiten explicitos en el `fromJson`. No
/// usar un mapper generico: cuando el backend cambia un nombre, el error tiene
/// que aparecer en este archivo, no en el `.g.dart` generado.
class {{DART_NOMBRE_CLASE}}Model {
  const {{DART_NOMBRE_CLASE}}Model({
    required this.id,
    required this.title,
    required this.body,
    required this.createdAt,
  });

  factory {{DART_NOMBRE_CLASE}}Model.fromJson(Map<String, dynamic> json) {
    return {{DART_NOMBRE_CLASE}}Model(
      id: json['id'] as String,
      title: json['title'] as String,
      body: json['body'] as String? ?? '',
      // `createdAt` viene como ISO 8601 string desde Supabase. Si viene null o
      // con otro formato, el `as` revienta con un TypeError que no dice que
      // campo fue. Por eso el parseo explicito con fallback.
      createdAt: DateTime.tryParse(json['created_at'] as String? ?? '') ??
          DateTime.fromMillisecondsSinceEpoch(0),
    );
  }

  final String id;
  final String title;
  final String body;
  final DateTime createdAt;

  {{DART_NOMBRE_CLASE}}Entity toEntity() {
    return {{DART_NOMBRE_CLASE}}Entity(
      id: id,
      title: title,
      body: body,
      createdAt: createdAt,
    );
  }
}
```

**`{{FEATURE_EJEMPLO}}_repository_impl.dart`** -- el archivo donde vive el mapeo:

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:uuid/uuid.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/error/exceptions.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/network/network_info.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/session/current_user.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/data/datasources/{{FEATURE_EJEMPLO}}_local_data_source.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/data/models/{{FEATURE_EJEMPLO}}_model.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/repositories/{{FEATURE_EJEMPLO}}_repository.dart';

/// `@LazySingleton(as: XRepository)`: es el registro. El `localDataSource`,
/// `networkInfo` y `currentUser` los inyecta GetIt por tipo -- nadie pasa nada
/// a mano, y `CurrentUser` resuelve al stub del nucleo (o al de auth, si
/// pegaste el pack).
@LazySingleton(as: {{DART_NOMBRE_CLASE}}Repository)
class {{DART_NOMBRE_CLASE}}RepositoryImpl implements {{DART_NOMBRE_CLASE}}Repository {
  {{DART_NOMBRE_CLASE}}RepositoryImpl({
    required {{DART_NOMBRE_CLASE}}LocalDataSource localDataSource,
    required NetworkInfo networkInfo,
    required CurrentUser currentUser,
  })  : _localDataSource = localDataSource,
        _networkInfo = networkInfo,
        _currentUser = currentUser;

  final {{DART_NOMBRE_CLASE}}LocalDataSource _localDataSource;
  final NetworkInfo _networkInfo;
  final CurrentUser _currentUser;

  static const Uuid _uuid = Uuid();

  @override
  Future<Either<Failure, List<{{DART_NOMBRE_CLASE}}Entity>>> getAll() async {
    try {
      final rows = await _localDataSource.getAll();
      return Right(
        rows.map((row) => {{DART_NOMBRE_CLASE}}Model.fromJson(row).toEntity()).toList(),
      );
    } on CacheException catch (e) {
      return Left(CacheFailure(message: e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, code: e.statusCode));
    }
  }

  @override
  Future<Either<Failure, {{DART_NOMBRE_CLASE}}Entity>> getById(String id) async {
    try {
      final row = await _localDataSource.getById(id);
      if (row == null) {
        return const Left(ServerFailure(message: 'Not found'));
      }
      return Right({{DART_NOMBRE_CLASE}}Model.fromJson(row).toEntity());
    } on CacheException catch (e) {
      return Left(CacheFailure(message: e.message));
    }
  }

  @override
  Future<Either<Failure, {{DART_NOMBRE_CLASE}}Entity>> create({
    required String title,
    required String body,
  }) async {
    try {
      final row = await _localDataSource.save(
        id: _uuid.v4(),
        title: title,
        body: body,
      );
      return Right({{DART_NOMBRE_CLASE}}Model.fromJson(row).toEntity());
    } on CacheException catch (e) {
      return Left(CacheFailure(message: e.message));
    }
  }

  @override
  Future<Either<Failure, Unit>> delete(String id) async {
    try {
      await _localDataSource.delete(id);
      return const Right(unit);
    } on CacheException catch (e) {
      return Left(CacheFailure(message: e.message));
    }
  }
}
```

> **Tres cosas que este repositorio tiene y la mayoria no:**
>
> 1. **`CurrentUser` inyectado y sin usar.** Es deliberado: el repositorio ya
>    depende de la abstraccion de identidad, asi que el dia que la operacion la
>    necesite ya esta el cable. Borralo cuando te llame de mas.
> 2. **Sin `if (await _networkInfo.isConnected)`.** No hay red en este datasource.
>    El guard va en el repositorio que habla con Supabase, no en todos.
> 3. **Sin try/catch generico.** Cada `on` es especifico. Un `on Object catch (e)`
>    al final convierte un `TypeError` de un bug de mapeo en un
>    `ServerFailure('type 'Null' is not a subtype of type 'String'')` que el
>    usuario ve como "Algo salio mal". Los bugs de programacion tienen que ser
>    exceptions que rompen los tests, no failures que se muestran.

### 4.5 Presentacion

**`{{FEATURE_EJEMPLO}}_state.dart`** -- `part of`, `sealed`, `final`:

```dart
part of '{{FEATURE_EJEMPLO}}_cubit.dart';

sealed class {{DART_NOMBRE_CLASE}}State extends Equatable {
  const {{DART_NOMBRE_CLASE}}State();

  @override
  List<Object?> get props => const [];
}

final class {{DART_NOMBRE_CLASE}}Initial extends {{DART_NOMBRE_CLASE}}State {
  const {{DART_NOMBRE_CLASE}}Initial();
}

final class {{DART_NOMBRE_CLASE}}Loading extends {{DART_NOMBRE_CLASE}}State {
  const {{DART_NOMBRE_CLASE}}Loading();
}

final class {{DART_NOMBRE_CLASE}}Loaded extends {{DART_NOMBRE_CLASE}}State {
  const {{DART_NOMBRE_CLASE}}Loaded(this.items);

  final List<{{DART_NOMBRE_CLASE}}Entity> items;

  @override
  List<Object?> get props => [items];
}

/// Estado de error.
///
/// `message` es un `String`, no un `Failure`. La presentacion muestra texto; si
/// el estado lleva el `Failure`, cada widget tiene que saber convertirlo, y esa
/// conversion se duplica en cada pantalla.
final class {{DART_NOMBRE_CLASE}}Error extends {{DART_NOMBRE_CLASE}}State {
  const {{DART_NOMBRE_CLASE}}Error(this.message);

  final String message;

  @override
  List<Object?> get props => [message];
}

/// Indica que una accion termino bien y hay que reordenar.
///
/// Sin este estado, "crear" no puede distinguir "no se creo nada todavia" de
/// "se creo y hay que recargar". Es un estado explicito de un campo
/// `bool`, no un `showSnackbar` desde el cubit.
final class {{DART_NOMBRE_CLASE}}ActionSuccess extends {{DART_NOMBRE_CLASE}}State {
  const {{DART_NOMBRE_CLASE}}ActionSuccess(this.action);

  final {{DART_NOMBRE_CLASE}}Action action;

  @override
  List<Object?> get props => [action];
}

enum {{DART_NOMBRE_CLASE}}Action { created, deleted }
```

**`{{FEATURE_EJEMPLO}}_cubit.dart`**

```dart
import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/common/usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/usecases/create_{{FEATURE_EJEMPLO}}_usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/usecases/delete_{{FEATURE_EJEMPLO}}_usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/usecases/get_{{FEATURE_EJEMPLO}}s_usecase.dart';

part '{{FEATURE_EJEMPLO}}_state.dart';

/// `@injectable` genera un `factory`, no un `lazySingleton`: cada pantalla que
/// hace `sl<XCubit>()` recibe una instancia nueva con su estado limpio. Si
/// fuera lazySingleton, el estado de la visita anterior sobreviviria al
/// `dispose()` de la pantalla.
@injectable
class {{DART_NOMBRE_CLASE}}Cubit extends Cubit<{{DART_NOMBRE_CLASE}}State> {
  {{DART_NOMBRE_CLASE}}Cubit({
    required Get{{DART_NOMBRE_PLURAL}}UseCase get{{DART_NOMBRE_PLURAL}},
    required Create{{DART_NOMBRE_CLASE}}UseCase create{{DART_NOMBRE_CLASE}},
    required Delete{{DART_NOMBRE_CLASE}}UseCase delete{{DART_NOMBRE_CLASE}},
  })  : _getAll = get{{DART_NOMBRE_PLURAL}},
        _create = create{{DART_NOMBRE_CLASE}},
        _delete = delete{{DART_NOMBRE_CLASE}},
        super(const {{DART_NOMBRE_CLASE}}Initial());

  final Get{{DART_NOMBRE_PLURAL}}UseCase _getAll;
  final Create{{DART_NOMBRE_CLASE}}UseCase _create;
  final Delete{{DART_NOMBRE_CLASE}}UseCase _delete;

  Future<void> load() async {
    emit(const {{DART_NOMBRE_CLASE}}Loading());

    final result = await _getAll();

    // fold, no match. `match` de fpdart tira si el valor es null; aca el tipo
    // del Right no es nullable, asi que fold es la eleccion correcta y mas
    // explicita.
    result.fold(
      (failure) => emit({{DART_NOMBRE_CLASE}}Error(failure.message)),
      (items) => emit({{DART_NOMBRE_CLASE}}Loaded(items)),
    );
  }

  Future<void> create({
    required String title,
    required String body,
  }) async {
    final result = await _create(
      Create{{DART_NOMBRE_CLASE}}UseCaseParams(title: title, body: body),
    );

    result.fold(
      (failure) => emit({{DART_NOMBRE_CLASE}}Error(failure.message)),
      // TODO: este slice no crea remoto todavia. Si tu backend asigna el id y
      // otros campos, relee el elemento creado desde el repositorio en vez de
      // usar el resultado del create.
      (_) => emit(const {{DART_NOMBRE_CLASE}}ActionSuccess(
        {{DART_NOMBRE_CLASE}}Action.created,
      )),
    );
  }

  Future<void> delete(String id) async {
    final result = await _delete(id);

    result.fold(
      (failure) => emit({{DART_NOMBRE_CLASE}}Error(failure.message)),
      (_) => emit(const {{DART_NOMBRE_CLASE}}ActionSuccess(
        {{DART_NOMBRE_CLASE}}Action.deleted,
      )),
    );
  }

  /// Vuelve al estado inicial.
  ///
  /// Necesario cuando un `ActionSuccess` o un `Error` se queda en pantalla y el
  /// usuario quiere recargar: sin esto, el `BlocBuilder` no se vuelve a
  /// disparar porque el estado no cambio.
  void reset() => emit(const {{DART_NOMBRE_CLASE}}Initial());
}
```

**`{{FEATURE_EJEMPLO}}_tile.dart`** -- widget de fila:

```dart
import 'package:flutter/material.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/theme/app_theme.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart';

/// Fila de la lista.
///
/// Formatea la fecha aca, no en la pagina. Si el formato vive en la pagina, cada
/// lista nueva reimprime la misma cadena de `DateFormat`.
class {{DART_NOMBRE_CLASE}}Tile extends StatelessWidget {
  const {{DART_NOMBRE_CLASE}}Tile({
    super.key,
    required this.item,
    required this.onTap,
    required this.onDelete,
  });

  final {{DART_NOMBRE_CLASE}}Entity item;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  /// Formatea la fecha en el locale activo.
  ///
  /// Va como metodo estatico con `BuildContext` porque `intl` necesita el locale
  /// para decidir el orden de los componentes. Un `DateFormat` en un `static
  /// final` se construye una vez, en el primer acceso, con un locale que
  /// todavia no se sabe.
  ///
  /// Si esto tira `LocaleDataException`, falta `initializeDateFormatting` para
  /// ese locale. Flutter lo hace solo cuando el `MaterialApp` declara
  /// `localizationsDelegates`.
  static String _formatDate(BuildContext context, DateTime date) {
    final locale = Localizations.localeOf(context).toString();
    return DateFormat.yMMMd(locale).format(date);
  }

```dart
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return AppCard(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      onTap: onTap,
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.title, style: theme.textTheme.titleMedium),
                const SizedBox(height: 4),
                Text(
                  _formatDate(context, item.createdAt),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.outline,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: onDelete,
            icon: const Icon(Icons.delete_outline),
            tooltip: l10n.exampleDelete,
            color: theme.colorScheme.error,
          ),
        ],
      ),
    );
  }
}
```

Los imports que necesita el archivo: `flutter/material.dart`,
`intl/intl.dart`, `app_card.dart`, la entidad y `l10n/l10n.dart`.

**`{{FEATURE_EJEMPLO}}_page.dart`** -- la pantalla principal:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/routing/app_router.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/utils/snackbar_helper.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/widgets/app_button.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/widgets/empty_state.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/widgets/error_view.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/widgets/loading_indicator.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/widgets/pull_to_refresh_wrapper.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/widgets/skeleton.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/presentation/cubit/{{FEATURE_EJEMPLO}}_cubit.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/presentation/widgets/{{FEATURE_EJEMPLO}}_tile.dart';
import 'package:{{NOMBRE_PROYECTO}}/l10n/l10n.dart';

class {{DART_NOMBRE_CLASE}}Page extends StatelessWidget {
  const {{DART_NOMBRE_CLASE}}Page({super.key});

  @override
  Widget build(BuildContext context) {
    // El cubit se provee aca, con `create:`, no globalmente en `main.dart`.
    //
    // La regla: global si lo necesitan dos o mas ramas del router; local si lo
    // necesita una sola pantalla. Este solo lo necesita esta, asi que va local.
    // Cada `read` de la pantalla arranca con un cubit nuevo, sin estado
    // compartido de la sesion anterior.
    return BlocProvider(
      create: (context) => sl<{{DART_NOMBRE_CLASE}}Cubit>()..load(),
      child: const _{{DART_NOMBRE_CLASE}}View(),
    );
  }
}

class _{{DART_NOMBRE_CLASE}}View extends StatefulWidget {
  const _{{DART_NOMBRE_CLASE}}View();

  @override
  State<_{{DART_NOMBRE_CLASE}}View> createState() => _{{DART_NOMBRE_CLASE}}ViewState();
}

class _{{DART_NOMBRE_CLASE}}ViewState extends State<_{{DART_NOMBRE_CLASE}}View> {
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _bodyController = TextEditingController();

  @override
  void dispose() {
    // Todo controller creado en `build` o en `initState` se disposea. Un
    // controller sin dispose es una fuga de memoria y un warning del analyzer
    // en el siguiente `flutter analyze`.
    _titleController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return BlocConsumer<{{DART_NOMBRE_CLASE}}Cubit, {{DART_NOMBRE_CLASE}}State>(
      // Cuando hay side-effects: solo una vez por estado, y despues de pintar.
      listenWhen: (previous, current) => current != previous,
      listener: (context, state) {
        // El feedback (snackbar) va en `listener`, nunca en `build`. Si va en
        // `build`, el snackbar reaparece cada vez que se reconstruye la
        // pantalla, o con cada scroll.
        if (state is {{DART_NOMBRE_CLASE}}ActionSuccess) {
          switch (state.action) {
            case {{DART_NOMBRE_CLASE}}Action.created:
              SnackbarHelper.showSuccess(context, l10n.exampleCreated);
              _clearForm();
            case {{DART_NOMBRE_CLASE}}Action.deleted:
              SnackbarHelper.showSuccess(context, l10n.exampleDeleted);
          }
          context.read<{{DART_NOMBRE_CLASE}}Cubit>().reset();
          return;
        }
        if (state is {{DART_NOMBRE_CLASE}}Error) {
          SnackbarHelper.showError(context, state.message);
          context.read<{{DART_NOMBRE_CLASE}}Cubit>().reset();
        }
      },
      builder: (context, state) {
        return Scaffold(
          appBar: AppBar(
            title: Text(l10n.exampleTitle),
            actions: [
              IconButton(
                onPressed: () => _showCreateSheet(context),
                icon: const Icon(Icons.add),
                tooltip: l10n.exampleAdd,
              ),
            ],
          ),
          body: switch (state) {
            {{DART_NOMBRE_CLASE}}Initial() || {{DART_NOMBRE_CLASE}}Loading() =>
              const LoadingIndicator(),
            {{DART_NOMBRE_CLASE}}Loaded(:final items) when items.isEmpty =>
              EmptyState(message: l10n.exampleEmptyHint),
            {{DART_NOMBRE_CLASE}}Loaded(:final items) => _List(items: items),
            {{DART_NOMBRE_CLASE}}Error(:final message) => ErrorView(
                message: message,
                onRetry: () => context.read<{{DART_NOMBRE_CLASE}}Cubit>().load(),
              ),
            {{DART_NOMBRE_CLASE}}ActionSuccess() => const LoadingIndicator(),
          },
        );
      },
    );
  }

  void _clearForm() {
    _titleController.clear();
    _bodyController.clear();
  }

  Future<void> _showCreateSheet(BuildContext context) async {
    // TODO: reemplazar el Dialog por un `showModalBottomSheet` con el formulario
    // completo. Se deja como Dialog para que el slice sea de una sola pantalla
    // y se borre rapido.
    final l10n = context.l10n;

    final title = await showDialog<String>(
      context: context,
      builder: (context) => _CreateDialog(
        titleController: _titleController,
        bodyController: _bodyController,
        titleLabel: l10n.exampleTitleFieldLabel,
        hint: l10n.exampleTitleFieldHint,
        cancelLabel: l10n.exampleCancel,
        submitLabel: l10n.exampleAdd,
      ),
    );

    if (title == null || title.isEmpty || !context.mounted) return;

    await context.read<{{DART_NOMBRE_CLASE}}Cubit>().create(
          title: title,
          body: _bodyController.text,
        );
  }
}

class _List extends StatelessWidget {
  const _List({required this.items});

  final List<{{DART_NOMBRE_CLASE}}Entity> items;

  @override
  Widget build(BuildContext context) {
    return PullToRefreshWrapper(
      onRefresh: () async {
        await context.read<{{DART_NOMBRE_CLASE}}Cubit>().load();
      },
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (context, index) {
          final item = items[index];
          return {{DART_NOMBRE_CLASE}}Tile(
            item: item,
            onTap: () => context.pushNamed(
              AppRouter.exampleDetailName,
              pathParameters: {'id': item.id},
            ),
            onDelete: () => _confirmDelete(context, item.id),
          );
        },
      ),
    );
  }

  Future<void> _confirmDelete(BuildContext context, String id) async {
    final l10n = context.l10n;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.exampleConfirmDeleteTitle),
        content: Text(l10n.exampleConfirmDeleteBody),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: Text(l10n.exampleCancel),
          ),
          AppButton(
            label: l10n.exampleDelete,
            variant: AppButtonVariant.danger,
            onPressed: () => Navigator.of(context).pop(true),
          ),
        ],
      ),
    );

    if (confirmed != true || !context.mounted) return;
    await context.read<{{DART_NOMBRE_CLASE}}Cubit>().delete(id);
  }
}

class _CreateDialog extends StatelessWidget {
  const _CreateDialog({
    required this.titleController,
    required this.bodyController,
    required this.titleLabel,
    required this.hint,
    required this.cancelLabel,
    required this.submitLabel,
  });

  final TextEditingController titleController;
  final TextEditingController bodyController;
  final String titleLabel;
  final String hint;
  final String cancelLabel;
  final String submitLabel;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(titleLabel),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AppTextField(
            label: titleLabel,
            hint: hint,
            controller: titleController,
            autofocus: true,
          ),
          const SizedBox(height: 12),
          AppTextField(
            label: hint,
            controller: bodyController,
            maxLines: 3,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(cancelLabel),
        ),
        AppButton(
          label: submitLabel,
          onPressed: () => Navigator.of(context).pop(titleController.text),
        ),
      ],
    );
  }
}
```

Imports que faltan en el archivo de la pagina: `core/di/service_locator.dart`
(para `sl`), `core/widgets/app_text_field.dart`, `intl/intl.dart` (para
`DateFormat` en el tile) y la entidad en el tile.

**`{{FEATURE_EJEMPLO}}_detail_page.dart`**

```dart
import 'package:flutter/material.dart';

import 'package:{{NOMBRE_PROYECTO}}/l10n/l10n.dart';

/// Detalle de un elemento.
class {{DART_NOMBRE_CLASE}}DetailPage extends StatelessWidget {
  const {{DART_NOMBRE_CLASE}}DetailPage({super.key, required this.id});

  /// El id viene de `state.pathParameters['id']` en el router.
  final String id;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    // TODO: reemplazar por el use case `Get{{DART_NOMBRE_CLASE}}ById` cuando
    // exista. El slice de ejemplo no trae un use case de detalle para no
    // inflar el ejemplo con un quinto archivo.
    return Scaffold(
      appBar: AppBar(title: Text(l10n.exampleDetail)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(id, style: Theme.of(context).textTheme.bodyMedium),
        ),
      ),
    );
  }
}
```

### 4.6 Registro en la DI

Ya esta: **la seccion anterior ya lo hizo.** Las anotaciones de las cinco clases
son el registro completo.

| Clase | Anotación | GetIt la registra como |
|---|---|---|
| `{{DART_NOMBRE_CLASE}}LocalDataSourceImpl` | `@LazySingleton(as: ...LocalDataSource)` | lazySingleton de la abstracta |
| `{{DART_NOMBRE_CLASE}}RepositoryImpl` | `@LazySingleton(as: ...Repository)` | lazySingleton de la abstracta |
| `Get{{DART_NOMBRE_PLURAL}}UseCase`, `Create{{DART_NOMBRE_CLASE}}UseCase`, `Delete{{DART_NOMBRE_CLASE}}UseCase` | `@lazySingleton` | una instancia para la app |
| `{{DART_NOMBRE_CLASE}}Cubit` | `@injectable` | `factory`, una por pantalla |

Lo que **si** hay que hacer:

```bash
make gen    # service_locator.config.dart ahora conoce las cinco clases
make check
```

`service_locator.dart` no se toca. Ese archivo ya no tiene un `// TODO:
registrar aca los...` que reemplazar: no tiene la lista.

> **Por que `@injectable` y no `@lazySingleton` en el cubit:** `injectable`
> genera `factory`. Un `lazySingleton` de cubit es la misma instancia para toda
> la app: si la pantalla se reconstruye al rotar, el estado sobrevive y el
> `dispose` nunca se llama. Fuga.
>
> **Lo que no se anota:** la entidad, el model y los `params`. No son
> dependencias, son tipos que viajan por los argumentos. Anotarlos registraria
> algo que nadie pide.

### 4.7 Fixture

`test/fixtures/{{FEATURE_EJEMPLO}}.json`:

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Primer elemento",
    "body": "Cuerpo del primer elemento de prueba",
    "created_at": "2026-10-01T12:00:00.000Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Segundo elemento",
    "body": "Cuerpo del segundo elemento de prueba",
    "created_at": "2026-10-02T09:30:00.000Z"
  }
]
```

> **`created_at` en snake_case, `createdAt` en Dart.** El `fromJson` lee
> `json['created_at']`. La conversion pasa por el model, que es el unico lugar
> que conoce los dos mundos.

> **VERIFICAR FASE 4**

```bash
flutter gen-l10n
dart run build_runner build --delete-conflicting-outputs   # cached_entry.g.dart + service_locator.config.dart
flutter analyze
flutter test test/features/
flutter run
```

La app debe mostrar la lista vacia, poder agregar un elemento, verlo aparecer,
poder eliminarlo, y navegar al detalle. Sin errores en consola.

### 4.8 Tests de la feature

Nueve archivos. Mismo patron en todos; generá los que falten siguiendo este.

Mocks **a nivel de archivo, fuera de `main()`**:

```dart
// test/features/{{FEATURE_EJEMPLO}}/domain/usecases/get_{{FEATURE_EJEMPLO}}s_usecase_test.dart
import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/common/usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/entities/{{FEATURE_EJEMPLO}}_entity.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/repositories/{{FEATURE_EJEMPLO}}_repository.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/usecases/get_{{FEATURE_EJEMPLO}}s_usecase.dart';

class Mock{{DART_NOMBRE_CLASE}}Repository extends Mock
    implements {{DART_NOMBRE_CLASE}}Repository {}

/// Datos de prueba. Prefijo `t` de test.
final tEntity = {{DART_NOMBRE_CLASE}}Entity(
  id: 'id-1',
  title: 'Titulo',
  body: 'Cuerpo',
  createdAt: DateTime.utc(2026, 10, 1),
);

void main() {
  late Mock{{DART_NOMBRE_CLASE}}Repository mockRepository;
  late Get{{DART_NOMBRE_PLURAL}}UseCase useCase;

  setUp(() {
    mockRepository = Mock{{DART_NOMBRE_CLASE}}Repository();
    useCase = Get{{DART_NOMBRE_PLURAL}}UseCase(mockRepository);
  });

  test('debe devolver la lista cuando la operacion es exitosa', () async {
    // ARRANGE
    when(() => mockRepository.getAll())
        .thenAnswer((_) async => Right([tEntity]));

    // ACT
    final result = await useCase();

    // ASSERT
    expect(result, isA<Right<Failure, List<{{DART_NOMBRE_CLASE}}Entity>>>());
    expect(result.getOrNull(), [tEntity]);
  });

  test('debe devolver la failure cuando el repositorio falla', () async {
    // ARRANGE
    const tFailure = ServerFailure(message: 'boom');
    when(() => mockRepository.getAll())
        .thenAnswer((_) async => const Left(tFailure));

    // ACT
    final result = await useCase();

    // ASSERT
    expect(result, isA<Left<Failure, List<{{DART_NOMBRE_CLASE}}Entity>>>());
    expect(result.getOrNull(), isNull);
  });

  test('debe delegar en getAll sin parametros', () async {
    // ARRANGE
    when(() => mockRepository.getAll())
        .thenAnswer((_) async => const Right([]));

    // ACT
    await useCase();

    // ASSERT
    verify(() => mockRepository.getAll()).called(1);
  });
}
```

**Test del cubit** con `blocTest` (sin comentarios AAA: se usan las claves):

```dart
// test/features/{{FEATURE_EJEMPLO}}/presentation/cubit/{{FEATURE_EJEMPLO}}_cubit_test.dart
import 'package:bloc_test/bloc_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/usecases/create_{{FEATURE_EJEMPLO}}_usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/usecases/delete_{{FEATURE_EJEMPLO}}_usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/domain/usecases/get_{{FEATURE_EJEMPLO}}s_usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/presentation/cubit/{{FEATURE_EJEMPLO}}_cubit.dart';

class MockGet{{DART_NOMBRE_PLURAL}}UseCase extends Mock
    implements Get{{DART_NOMBRE_PLURAL}}UseCase {}
class MockCreate{{DART_NOMBRE_CLASE}}UseCase extends Mock
    implements Create{{DART_NOMBRE_CLASE}}UseCase {}
class MockDelete{{DART_NOMBRE_CLASE}}UseCase extends Mock
    implements Delete{{DART_NOMBRE_CLASE}}UseCase {}

void main() {
  late MockGet{{DART_NOMBRE_PLURAL}}UseCase mockGetAll;
  late MockCreate{{DART_NOMBRE_CLASE}}UseCase mockCreate;
  late MockDelete{{DART_NOMBRE_CLASE}}UseCase mockDelete;
  late {{DART_NOMBRE_CLASE}}Cubit cubit;

  setUpAll(() {
    // Obligatorio: los Params no son primitivos, y mocktail necesita una
    // instancia de referencia para saber compararlos en `when`. Sin esto, el
    // test tira en runtime, no en compilacion.
    registerFallbackValue(
      const Create{{DART_NOMBRE_CLASE}}UseCaseParams(title: '', body: ''),
    );
  });

  setUp(() {
    mockGetAll = MockGet{{DART_NOMBRE_PLURAL}}UseCase();
    mockCreate = MockCreate{{DART_NOMBRE_CLASE}}UseCase();
    mockDelete = MockDelete{{DART_NOMBRE_CLASE}}UseCase();
    cubit = {{DART_NOMBRE_CLASE}}Cubit(
      get{{DART_NOMBRE_PLURAL}}: mockGetAll,
      create{{DART_NOMBRE_CLASE}}: mockCreate,
      delete{{DART_NOMBRE_CLASE}}: mockDelete,
    );
  });

  tearDown(() => cubit.close());

  group('load', () {
    blocTest<{{DART_NOMBRE_CLASE}}Cubit, {{DART_NOMBRE_CLASE}}State>(
      'load success emits [Loading, Loaded]',
      setUp: () {
        when(() => mockGetAll()).thenAnswer((_) async => const Right([]));
      },
      build: () => cubit,
      act: (cubit) => cubit.load(),
      expect: () => [
        isA<{{DART_NOMBRE_CLASE}}Loading>(),
        isA<{{DART_NOMBRE_CLASE}}Loaded>(),
      ],
    );

    blocTest<{{DART_NOMBRE_CLASE}}Cubit, {{DART_NOMBRE_CLASE}}State>(
      'load failure emits [Loading, Error]',
      setUp: () {
        when(() => mockGetAll())
            .thenAnswer((_) async => const Left(ServerFailure(message: 'boom')));
      },
      build: () => cubit,
      act: (cubit) => cubit.load(),
      expect: () => [
        isA<{{DART_NOMBRE_CLASE}}Loading>(),
        isA<{{DART_NOMBRE_CLASE}}Error>().having(
          (state) => state.message,
          'message',
          'boom',
        ),
      ],
    );
  });

  group('create', () {
    blocTest<{{DART_NOMBRE_CLASE}}Cubit, {{DART_NOMBRE_CLASE}}State>(
      'create success emits [ActionSuccess]',
      setUp: () {
        when(() => mockCreate(any()))
            .thenAnswer((_) async => Right(tEntity));
      },
      build: () => cubit,
      act: (cubit) => cubit.create(title: 'a', body: 'b'),
      expect: () => [
        isA<{{DART_NOMBRE_CLASE}}ActionSuccess>()
            .having((s) => s.action, 'action', {{DART_NOMBRE_CLASE}}Action.created),
      ],
      verify: (_) {
        verify(() => mockCreate(
          const Create{{DART_NOMBRE_CLASE}}UseCaseParams(title: 'a', body: 'b'),
        )).called(1);
      },
    );
  });

  group('reset', () {
    blocTest<{{DART_NOMBRE_CLASE}}Cubit, {{DART_NOMBRE_CLASE}}State>(
      'reset emits Initial',
      build: () => cubit,
      seed: () => {{DART_NOMBRE_CLASE}}Error('boom'),
      act: (cubit) => cubit.reset(),
      expect: () => [isA<{{DART_NOMBRE_CLASE}}Initial>()],
    );
  });
}
```

**Test del datasource con Isar real** -- el unico test de la suite que necesita un
backend de verdad. Usa el Isar in-memory, que existe justamente para esto:

```dart
// test/features/{{FEATURE_EJEMPLO}}/data/datasources/{{FEATURE_EJEMPLO}}_local_data_source_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:isar_community/isar.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/data/local/isar_models/cached_entry.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/data/datasources/{{FEATURE_EJEMPLO}}_local_data_source.dart';

void main() {
  late Isar isar;
  late {{DART_NOMBRE_CLASE}}LocalDataSourceImpl dataSource;

  setUp(() async {
    // Isar in-memory: no toca disco, no necesita path_provider, no deja rastro.
    // Es la diferencia entre un test que corre en 2 segundos y uno que corre en 30.
    isar = await Isar.open(
      [CachedEntrySchema],
      directory: '',
      name: 'test-${DateTime.now().microsecondsSinceEpoch}',
    );
    dataSource = {{DART_NOMBRE_CLASE}}LocalDataSourceImpl(isar);
  });

  tearDown(() async => isar.close(deleteFromDisk: true));

  group('save', () {
    test('devuelve el payload con id y createdAt', () async {
      // ACT
      final result = await dataSource.save(
        id: 'id-1',
        title: 'Titulo',
        body: 'Cuerpo',
      );

      // ASSERT
      expect(result['id'], 'id-1');
      expect(result['title'], 'Titulo');
      expect(result['createdAt'], isA<String>());
    });
  });

  group('getById', () {
    test('devuelve null si no existe', () async {
      // ASSERT
      expect(await dataSource.getById('nope'), isNull);
    });

    test('devuelve lo guardado', () async {
      // ARRANGE
      await dataSource.save(id: 'id-1', title: 'T', body: 'B');

      // ACT
      final result = await dataSource.getById('id-1');

      // ASSERT
      expect(result?['title'], 'T');
    });
  });

  group('aislamiento por prefijo', () {
    test('getAll no trae entradas de otra feature', () async {
      // ARRANGE
      await isar.writeTxn(() async {
        await isar.cachedEntrys.put(
          CachedEntry(key: 'otra_feature:xyz', payload: '{"id":"xyz"}'),
        );
      });
      await dataSource.save(id: 'id-1', title: 'T', body: 'B');

      // ACT
      final result = await dataSource.getAll();

      // ASSERT
      // Si este test falla, `getAll` esta devolviendo la cache entera de la app.
      // Es el bug que el prefijo evita.
      expect(result, hasLength(1));
      expect(result.first['id'], 'id-1');
    });
  });

  group('delete', () {
    test('elimina la entrada', () async {
      // ARRANGE
      await dataSource.save(id: 'id-1', title: 'T', body: 'B');

      // ACT
      await dataSource.delete('id-1');

      // ASSERT
      expect(await dataSource.getById('id-1'), isNull);
    });
  });

  group('TTL', () {
    test('una entrada expirada se trata como ausente', () async {
      // ARRANGE
      await isar.writeTxn(() async {
        await isar.cachedEntrys.put(
          CachedEntry(
            key: '{{FEATURE_EJEMPLO}}:expired',
            payload: '{"id":"expired"}',
            expiresAt: DateTime.now().subtract(const Duration(hours: 1)),
          ),
        );
      });

      // ASSERT
      // El cache no borra: "no existe". Borrar aparte es una segunda escritura
      // por cada lectura fallida.
      expect(await dataSource.getById('expired'), isNull);
    });
  });
}
```

Test del repositorio: mockea el datasource y verifica **el mapeo de excepciones**,
que es lo unico con logica propia:

```dart
// test/features/{{FEATURE_EJEMPLO}}/data/repositories/{{FEATURE_EJEMPLO}}_repository_impl_test.dart
class Mock{{DART_NOMBRE_CLASE}}LocalDataSource extends Mock
    implements {{DART_NOMBRE_CLASE}}LocalDataSource {}
class MockNetworkInfo extends Mock implements NetworkInfo {}
class MockCurrentUser extends Mock implements CurrentUser {}

void main() {
  late Mock{{DART_NOMBRE_CLASE}}LocalDataSource mockLocal;
  late MockNetworkInfo mockNetwork;
  late MockCurrentUser mockCurrentUser;
  late {{DART_NOMBRE_CLASE}}RepositoryImpl repository;

  setUp(() {
    mockLocal = Mock{{DART_NOMBRE_CLASE}}LocalDataSource();
    mockNetwork = MockNetworkInfo();
    mockCurrentUser = MockCurrentUser();
    repository = {{DART_NOMBRE_CLASE}}RepositoryImpl(
      localDataSource: mockLocal,
      networkInfo: mockNetwork,
      currentUser: mockCurrentUser,
    );
  });

  test('getAll devuelve las entidades cuando el datasource responde', () async {
    // ARRANGE
    when(() => mockLocal.getAll()).thenAnswer(
      (_) async => [
        {'id': 'id-1', 'title': 'T', 'body': 'B', 'created_at': '2026-10-01T00:00:00.000Z'},
      ],
    );

    // ACT
    final result = await repository.getAll();

    // ASSERT
    expect(result.isRight(), isTrue);
    final entity = result.getOrNull()!.first;
    expect(entity.id, 'id-1');
    expect(entity.createdAt, DateTime.utc(2026, 10, 1));
  });

  test('getAll traduce CacheException a CacheFailure', () async {
    // ARRANGE
    when(() => mockLocal.getAll())
        .thenThrow(const CacheException(message: 'cache_read_error: boom'));

    // ACT
    final result = await repository.getAll();

    // ASSERT
    expect(result.isLeft(), isTrue);
    expect(result.getOrNull(), isNull);
    expect(
      (result as Left).left,
      isA<CacheFailure>().having((f) => f.message, 'message', contains('boom')),
    );
  });

  test('getById devuelve ServerFailure si no encuentra el id', () async {
    // ARRANGE
    when(() => mockLocal.getById('nope')).thenAnswer((_) async => null);

    // ACT
    final result = await repository.getById('nope');

    // ASSERT
    expect(result.isLeft(), isTrue);
  });

  test('delete devuelve Unit en el camino feliz', () async {
    // ARRANGE
    when(() => mockLocal.delete('id-1')).thenAnswer((_) async {});

    // ACT
    final result = await repository.delete('id-1');

    // ASSERT
    expect(result.isRight(), isTrue);
    verify(() => mockLocal.delete('id-1')).called(1);
  });
}
```

Test del model: **todos los casos borde del `fromJson`**, que es donde aparecen
los bugs de mapeo. El model se prueba por `fromJson`, no instanciandolo vacio:
tiene un constructor con campos requeridos, asi que los casos que importan son
los del parseo.

```dart
// test/features/{{FEATURE_EJEMPLO}}/data/models/{{FEATURE_EJEMPLO}}_model_test.dart
import 'package:flutter_test/flutter_test.dart';

import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/data/models/{{FEATURE_EJEMPLO}}_model.dart';

void main() {
  group('fromJson', () {
    test('mapea todos los campos', () {
      // ARRANGE
      final json = <String, dynamic>{
        'id': 'id-1',
        'title': 'Titulo',
        'body': 'Cuerpo',
        'created_at': '2026-10-01T12:00:00.000Z',
      };

      // ACT
      final model = {{DART_NOMBRE_CLASE}}Model.fromJson(json);

      // ASSERT
      expect(model.id, 'id-1');
      expect(model.title, 'Titulo');
      expect(model.body, 'Cuerpo');
      expect(model.createdAt, DateTime.utc(2026, 10, 1, 12));
    });

    test('body ausente queda como string vacio, no como null', () {
      // ARRANGE
      final json = <String, dynamic>{
        'id': 'id-1',
        'title': 'Titulo',
        'created_at': '2026-10-01T12:00:00.000Z',
      };

      // ACT
      final model = {{DART_NOMBRE_CLASE}}Model.fromJson(json);

      // ASSERT
      // El campo es `String`, no `String?`. Un null aca revienta en el primer
      // `Text(model.body)` de la UI.
      expect(model.body, '');
    });

    test('created_at ausente cae a epoch, no tira', () {
      // ARRANGE
      final json = <String, dynamic>{'id': 'id-1', 'title': 'T'};

      // ACT
      final model = {{DART_NOMBRE_CLASE}}Model.fromJson(json);

      // ASSERT
      expect(model.createdAt, isNotNull);
    });
  });

  group('toEntity', () {
    test('copia los campos a la entidad', () {
      // ARRANGE
      final model = {{DART_NOMBRE_CLASE}}Model.fromJson({
        'id': 'id-1',
        'title': 'T',
        'body': 'B',
        'created_at': '2026-10-01T00:00:00.000Z',
      };

      // ACT
      final entity = model.toEntity();

      // ASSERT
      expect(entity.id, model.id);
      expect(entity.createdAt, model.createdAt);
    });
  });
}
```

> Los tres use cases (`get`, `create`, `delete`) siguen el mismo patron de tres
> tests que el de arriba. Generalos cambiando los tipos. `delete` usa `String`
> como tipo de params, no un `Params` class, asi que **no** necesita
> `registerFallbackValue`.

> **VERIFICAR FASE 4 (tests)**

```bash
flutter test test/features/ --coverage
# Debe terminar con "All tests passed!" y cobertura > 0 en el slice
```

