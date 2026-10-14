## FASE 3 -- Core de Flutter `apps/mobile/`

### 3.1 Estructura de `apps/mobile/`

```
apps/mobile/
├── lib/
│   ├── main.dart
│   ├── core/
│   │   ├── common/
│   │   ├── config/
│   │   ├── constants/
│   │   ├── data/local/
│   │   ├── di/
│   │   ├── error/
│   │   ├── network/
│   │   ├── routing/
│   │   ├── services/
│   │   ├── session/
│   │   ├── theme/
│   │   ├── utils/
│   │   └── widgets/
│   ├── features/
│   │   └── <FEATURE_EJEMPLO>/        <- FASE 4
│   └── l10n/
│       ├── arb/
│       ├── gen/                     <- gitignored
│       └── l10n.dart
├── test/
│   ├── core/
│   ├── features/
│   ├── fixtures/
│   └── helpers/
├── assets/
├── android/
├── ios/
├── analysis_options.yaml
├── l10n.yaml
├── pubspec.yaml
├── .env.example
├── .env
├── Makefile
└── README.md
```

Los directorios de plataforma (`android/`, `ios/`) salen de `flutter create`. **No
los modifiques** en este prompt: se resuelven en la FASE 5 con los flavors.

> **VERIFICAR 3.1**

```bash
cd apps/mobile
flutter create --project-name {{NOMBRE_PROYECTO}} --org {{ORG_GITHUB}} --platforms=android,ios .
```

### 3.2 `pubspec.yaml`

Lista **cerrada** de dependencias. Nada de lo que este aqui genera codigo salvo
Isar.

```yaml
name: {{NOMBRE_PROYECTO}}
description: "{{NOMBRE_MOSTRABLE}}"
version: {{VERSION_INICIAL}}
publish_to: 'none'

environment:
  sdk: ^3.11.0
  flutter: ^3.41.0

dependencies:
  # --- Estado y presentacion ---
  flutter:
    sdk: flutter
  flutter_bloc: ^9.1.1
  bloc: ^9.2.1
  equatable: ^2.0.7
  fpdart: ^1.2.0

  # --- Navegacion y DI ---
  go_router: ^14.8.1
  # ^8.3.0 es el piso que pide `injectable` (>=8.3.0 <10.0.0).
  get_it: ^8.3.0
  injectable: ^2.7.1

  # --- Supabase ---
  supabase_flutter: ^2.12.4

  # --- Almacenamiento local ---
  # isar_community, no isar: el paquete isar original esta sin mantenimiento
  # desde 2023 y la comunidad mantiene el fork con fixes de compilacion en
  # las versiones nuevas de Flutter. Fijate en la major, no en la minor.
  isar_community: ^3.3.2
  isar_community_flutter_libs: ^3.3.2
  path_provider: ^2.1.1

  # --- Config ---
  flutter_dotenv: ^5.2.1

  # --- IDs ---
  # Genera los ids que crea el cliente. El backend los genera si tenes
  # colisiones entre dispositivos offline.
  uuid: ^4.5.1

  # --- Red / plataforma ---
  http: ^1.6.0
  internet_connection_checker_plus: ^2.9.1+2
  package_info_plus: ^8.3.0
  url_launcher: ^6.3.0
  intl: ^0.20.2

  # --- Iconos de launcher (genera recursos, no codigo Dart) ---
  flutter_launcher_icons: ^0.14.4

  flutter_localizations:
    sdk: flutter
  cupertino_icons: ^1.0.8

dev_dependencies:
  flutter_test:
    sdk: flutter

  # --- Analisis estatico ---
  very_good_analysis: ^10.2.0
  bloc_lint: ^0.3.6

  # --- Tests ---
  bloc_test: ^10.0.0
  mocktail: ^1.0.5

  # --- Codegen: Isar y DI (ver ADR 0002) ---
  # Fijos, no con `^`: isar_community_generator 3.3.2 pide analyzer <11.0.0 y
  # la 3.x de injectable_generator pide SDK >=3.12.0. Bajo Dart 3.11 solo
  # resuelve esta combinacion. Si subis de Flutter, revisalas juntas.
  build_runner: ^2.4.7
  isar_community_generator: ^3.3.2
  injectable_generator: ^2.12.1

flutter:
  # Necesario para que flutter genere las localizaciones en cada `flutter run`.
  generate: true
  uses-material-design: true
  assets:
    # El .env va como asset: flutter_dotenv lo lee del bundle.
    - .env

flutter_launcher_icons:
  android: true
  ios: true
  image_path: 'assets/app_icon.png'
```

**Lo que NO esta y por que:**

| Ausente | Motivo |
|---|---|
| `riverpod` como contenedor | GetIt + `injectable` ya cubre lo mismo sin un segundo sistema de estado. Ver ADR 0002 |
| `freezed` + `freezed_annotation` | Los estados son clases `Equatable` escritas a mano |
| `json_serializable` | Los modelos usan `fromJson`/`toJson` explicitos |
| `dartz` | `Either` viene de `fpdart` |
| `hive`, `shared_preferences` | Isar cubre el cache |
| `mockito` | `mocktail` alcanza y no necesita codegen |
| `cupertino_icons` en dev | Es una dependencia real, va en `dependencies` |

> **VERIFICAR 3.2**

```bash
flutter pub get
flutter pub deps --style=compact | head -40
```

Si falla una version, ajustala al rango disponible mas cercano y **anotalo** en
el reporte. No cambies el paquete.

### 3.3 `analysis_options.yaml`

```yaml
include:
  - package:very_good_analysis/analysis_options.yaml
  - package:bloc_lint/recommended.yaml

analyzer:
  exclude:
    - lib/l10n/gen/**
    - "**/*.g.dart"
    # El config de DI es codigo generado. No lo lints: lo que importa es que
    # este actualizado, y eso lo verifica la FASE 6 con `git diff --exit-code`.
    - "**/*.config.dart"
    - build/**
    - android/**
    - ios/**
  errors:
    # very_good_analysis es estricto en reglas que estorban a una app real.
    # Cada excepcion esta justificada al lado.
    one_member_abstracts: ignore          # las abstracciones de una sola pieza son el punto
    avoid_types_as_parameter_names: ignore
    avoid_redundant_argument_values: ignore
    always_put_required_named_parameters_first: ignore
    prefer_const_constructors: ignore
    sort_constructors_first: ignore
    sort_pub_dependencies: ignore
    discarded_futures: ignore             # bloc_test y BuildContext lo necesitan
    always_use_package_imports: ignore    # los part/part of no pueden usar package:
    avoid_dynamic_calls: ignore
    deprecated_member_use: ignore

linter:
  rules:
    public_member_api_docs: false
```

**Por que `always_use_package_imports: ignore`:** los `part of` de los pares
cubit/state no pueden referenciar `package:`. Si el linter esta activo, cada
`part` es una excepcion manual. Desactivarlo y aplicar la regla a mano (todos los
imports reales usan `package:`, ver `AGENTS.md`) es mas limpio que 20
excepciones.

> **VERIFICAR 3.3**

```bash
flutter analyze   # todavia no hay codigo, debe dar 0 problemas
```

### 3.4 `l10n.yaml` y los archivos ARB

```yaml
# l10n.yaml
arb-dir: lib/l10n/arb
template-arb-file: app_es.arb
output-localization-file: app_localizations.dart
output-dir: lib/l10n/gen
nullable-getter: false
synthetic-package: false
```

> **Por que `synthetic-package: false`:** sin esto, la salida va a
> `flutter_gen/` y hay que importarla con un `// ignore:` deprecado. Con la
> salida dentro de `lib/`, el import es normal y el directorio se puede
> gitignorar sin que el build se rompa.

**`lib/l10n/arb/app_es.arb`** (template, español). Las claves son de la app, no de
un contador de ejemplo:

```json
{
  "@@locale": "es",

  "appTitle": "{{NOMBRE_MOSTRABLE}}",
  "@appTitle": { "description": "Nombre de la app, mostrado en el launcher y en la barra de titulo" },

  "exampleTitle": "Ejemplo",
  "@exampleTitle": { "description": "Titulo de la pantalla de ejemplo, que se borra con el slice" },

  "exampleEmpty": "Todavia no hay nada aca",
  "@exampleEmpty": { "description": "Estado vacio de la pantalla de ejemplo" },
  "exampleEmptyHint": "Agrega un elemento para empezar.",
  "@exampleEmptyHint": { "description": "Ayuda bajo el estado vacio" },
  "exampleAdd": "Agregar",
  "@exampleAdd": { "description": "Boton para crear un elemento de ejemplo" },
  "exampleTitleFieldLabel": "Titulo",
  "@exampleTitleFieldLabel": { "description": "Etiqueta del campo de texto del formulario" },
  "exampleTitleFieldHint": "Escribi algo",
  "@exampleTitleFieldHint": { "description": "Placeholder del campo de texto" },
  "exampleTitleRequired": "El titulo no puede estar vacio",
  "@exampleTitleRequired": { "description": "Error de validacion del campo titulo" },
  "exampleDelete": "Eliminar",
  "@exampleDelete": { "description": "Boton para eliminar un elemento" },
  "exampleDetail": "Detalle",
  "@exampleDetail": { "description": "Boton para abrir el detalle de un elemento" },
  "exampleCreated": "Elemento creado",
  "@exampleCreated": { "description": "Mensaje de confirmacion tras crear" },
  "exampleDeleted": "Elemento eliminado",
  "@exampleDeleted": { "description": "Mensaje de confirmacion tras eliminar" },
  "exampleConfirmDeleteTitle": "Eliminar este elemento?",
  "@exampleConfirmDeleteTitle": { "description": "Titulo del dialogo de confirmacion" },
  "exampleConfirmDeleteBody": "Esta accion no se puede deshacer.",
  "@exampleConfirmDeleteBody": { "description": "Cuerpo del dialogo de confirmacion" },
  "exampleCancel": "Cancelar",
  "@exampleCancel": { "description": "Boton de cancelar generico" },

  "errorGeneric": "Algo salio mal. Proba de nuevo.",
  "@errorGeneric": { "description": "Mensaje de error generico, cuando no sabemos que paso" },
  "errorNetwork": "Sin conexion a internet. Revisa tu red.",
  "@errorNetwork": { "description": "Error de falta de conexion" },
  "errorServer": "El servidor respondio con un error.",
  "@errorServer": { "description": "Error del servidor, sin detalle tecnico" },
  "errorServerStatus": "Error del servidor ({status})",
  "@errorServerStatus": {
    "description": "Error del servidor con el codigo HTTP",
    "placeholders": { "status": { "type": "int" } }
  },
  "errorCache": "No pudimos leer los datos guardados.",
  "@errorCache": { "description": "Error de cache local" },
  "errorValidation": "Revisa los datos que cargaste.",
  "@errorValidation": { "description": "Error de validacion" },

  "retry": "Reintentar",
  "@retry": { "description": "Boton de reintento tras un error" },
  "loading": "Cargando...",
  "@loading": { "description": "Texto mientras carga contenido" },
  "emptyStateTitle": "Nada por aca",
  "@emptyStateTitle": { "description": "Titulo generico de estado vacio" },
  "pageNotFoundTitle": "Pagina no encontrada",
  "@pageNotFoundTitle": { "description": "Titulo de la pantalla 404 del router" },
  "pageNotFoundBody": "El enlace que seguiste no existe o fue movido.",
  "@pageNotFoundBody": { "description": "Cuerpo de la pantalla 404" },
  "goHome": "Ir al inicio",
  "@goHome": { "description": "Boton para volver al inicio desde la 404" },
  "dismiss": "Cerrar",
  "@dismiss": { "description": "Boton para cerrar un dialogo o snackbar" }
}
```

**`lib/l10n/arb/app_en.arb`** (traduccion). Mismas claves, en ingles:

```json
{
  "@@locale": "en",

  "appTitle": "{{NOMBRE_MOSTRABLE}}",

  "exampleTitle": "Example",
  "exampleEmpty": "Nothing here yet",
  "exampleEmptyHint": "Add an item to get started.",
  "exampleAdd": "Add",
  "exampleTitleFieldLabel": "Title",
  "exampleTitleFieldHint": "Write something",
  "exampleTitleRequired": "Title cannot be empty",
  "exampleDelete": "Delete",
  "exampleDetail": "Details",
  "exampleCreated": "Item created",
  "exampleDeleted": "Item deleted",
  "exampleConfirmDeleteTitle": "Delete this item?",
  "exampleConfirmDeleteBody": "This action cannot be undone.",
  "exampleCancel": "Cancel",

  "errorGeneric": "Something went wrong. Please try again.",
  "errorNetwork": "No internet connection. Check your network.",
  "errorServer": "The server returned an error.",
  "errorServerStatus": "Server error ({status})",
  "errorCache": "Could not read the locally stored data.",
  "errorValidation": "Check the data you entered.",

  "retry": "Retry",
  "loading": "Loading...",
  "emptyStateTitle": "Nothing here",
  "pageNotFoundTitle": "Page not found",
  "pageNotFoundBody": "The link you followed does not exist or has moved.",
  "goHome": "Go home",
  "dismiss": "Dismiss"
}
```

**`lib/l10n/l10n.dart`** (barrel + extension):

```dart
import 'package:flutter/widgets.dart';
import 'package:{{NOMBRE_PROYECTO}}/l10n/gen/app_localizations.dart';

export 'package:{{NOMBRE_PROYECTO}}/l10n/gen/app_localizations.dart';

/// Acceso corto a las localizaciones: `context.l10n.exampleAdd`.
extension AppLocalizationsX on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this);
}
```

> **Sobre por que el template es `es` y no `en`:** el ARB template define los tipos
> y las claves. Si el proyecto es en español, español como template evita que
> falte una traduccion en el idioma principal.

> **VERIFICAR 3.4**

```bash
flutter gen-l10n
ls lib/l10n/gen/
grep -c '":' lib/l10n/arb/app_es.arb lib/l10n/arb/app_en.arb   # deben coincidir
```

### 3.5 `lib/main.dart`

Sin autenticacion, sin splash de sesion, sin espera de nada que no tenga que ver
con el arranque de la app.

```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/config/app_config.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/constants/constants.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/di/service_locator.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/routing/app_router.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/theme/app_theme.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/utils/app_info.dart';
import 'package:{{NOMBRE_PROYECTO}}/l10n/l10n.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 1. Variables de entorno. Va primero: todo lo demas las lee.
  await dotenv.load(fileName: '.env');

  // 2. Orientation y status bar. La UI es vertical en las dos plataformas.
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    systemNavigationBarColor: Colors.white,
    systemNavigationBarIconBrightness: Brightness.dark,
  ));

  // 3. Supabase. Va antes que configureDependencies() porque el modulo de DI
  //    lee Supabase.instance.client al resolver los datasources.
  //    El nucleo solo lo inicializa. NO llama a auth: este prompt no genera
  //    autenticacion. Ver `## PACK: auth`.
  await Supabase.initialize(
    url: AppConfig.supabaseUrl,
    anonKey: AppConfig.supabasePublishableKey,
  );

  // 4. DI. Arranca Isar (@preResolve en el modulo) y registra todo lo que
  //    encontro `make gen` en las anotaciones de cada clase.
  await configureDependencies();

  // 5. Metadata de la app (version, build). La usa el chequeo de updates.
  await AppInfo.init();

  runApp(const Bootstrap());
}

/// Construye el arbol de providers globales y levanta la app.
///
/// Se separa de `main()` para que un test pueda construir el mismo arbol con
/// doubles en lugar de singletons reales.
class Bootstrap extends StatelessWidget {
  const Bootstrap({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      // TODO: registrar aqui los cubits de alcance global (los que no son de
      // una sola pantalla). Cada uno con BlocProvider<T>.value(value: sl<T>()).
      //
      // La regla: un cubit va aca si lo necesitan dos o mas ramas del router.
      // Si lo necesita una sola pantalla, va en el BlocProvider de esa pagina,
      // con `create:`, no con `.value`.
      providers: const <SingleChildWidget>[],

      child: MaterialApp.router(
        title: AppConstants.appName,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        localizationsDelegates: AppLocalizations.localizationsDelegates,
        supportedLocales: AppLocalizations.supportedLocales,
        routerConfig: AppRouter().router(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
```

> **Sobre `AppRouter().router()`:** `AppRouter` construye un `GoRouter` nuevo en
> cada llamada a `router()`, no lo guarda como campo. Si lo guardara, recrear el
> router seria imposible sin reiniciar la app entera.
>
> **Sobre `MultiBlocProvider` con lista vacia:** es intencional. El slice de
> ejemplo (FASE 4) se provee en su propia pagina, no globalmente. Cuando agregues
> tu primer cubit global, la lista deja de estar vacia y la estructura queda
> probada.

Imports faltantes arriba: agregalos en el archivo generado, en este orden:

```dart
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:provider/single_child_widget.dart';
```

> Si `provider` no esta en `pubspec.yaml`, entonces `MultiBlocProvider` con lista
> vacia no necesita el tipo explicito. En ese caso **borrá** el
> `<SingleChildWidget>` y el import, y deja `providers: const [],`. No agregues
> una dependencia nueva por esto.

### 3.6 `apps/mobile/.env.example` y `.env`

**`.env.example`:**

```bash
# ==============================================================
#  Plantilla. Copiala a .env: `make env-local`.
#  NUNCA commitees .env.
# ==============================================================

# --- Supabase ---
# Valores que imprime `supabase start` en tu maquina.
SUPABASE_URL=http://127.0.0.1:54321

# La publishable key es publica por diseno: viaja en el bundle de la app.
# Solo protege lo que las policies RLS protegen. Empieza con
# sb_publishable_...
SUPABASE_PUBLISHABLE_KEY=sb_publishable_TU_CLAVE_PUBLISHABLE_AQUI

# --- Sitio ---
# Debe coincidir con el redirect de Auth configurado en Supabase.
# El nucleo no lo usa para auth; lo usa para links del backend.
SITE_URL=http://127.0.0.1:3000

# --- Opcional ---
# Sentry. Vacio = la app no reporta nada. Ver `## PACK: observability`.
SENTRY_DSN=
SENTRY_RELEASE=
```

**`.env`:** generalo con los valores que salio de `supabase start`. Si no lo tenes
todavia, generalo con placeholders identicos a los del `.env.example` y anotalo en
el reporte. **Nunca inventes una URL que parezca real.**

> **VERIFICAR 3.6**

```bash
cd apps/mobile
cp .env.example .env
grep -q 'sb_publishable_' .env && echo "placeholder presente: completar con supabase start"
```

### 3.7 `core/error/` -- el contrato de errores

Dos archivos. Nada mas. Esta forma exacta la copian todos los repositorios.

**`lib/core/error/failures.dart`**

```dart
import 'package:equatable/equatable.dart';

/// Falla de negocio: algo que ya se sabe que salio mal.
///
/// Los `Failure` no se loguean ni se muestran crudos. Son de la capa de
/// presentacion, que los convierte en texto con `ErrorHandler` o con l10n.
abstract class Failure extends Equatable {
  const Failure({
    required this.message,
    this.code,
  });

  /// Texto listo para mostrar. En ingles: la capa de presentacion o el
  /// `ErrorHandler` lo traduce.
  final String message;

  /// Codigo de negocio opcional. `statusCode` es de la Exception, no del Failure.
  final int? code;

  @override
  List<Object?> get props => [message, code];
}

class ServerFailure extends Failure {
  const ServerFailure({super.message = 'Something went wrong', super.code});
}

class NetworkFailure extends Failure {
  const NetworkFailure({super.message = 'No internet connection', super.code});
}

class CacheFailure extends Failure {
  const CacheFailure({super.message = 'Cache failure', super.code});
}

class ValidationFailure extends Failure {
  const ValidationFailure({super.message = 'Validation failure', super.code});
}
```

> **Nota sobre `AuthFailure`.** Un proyecto con autenticacion necesita un
> `AuthFailure`. **Este nucleo no lo incluye**: incluirlo seria asumir que hay
> sesiones. El `## PACK: auth` lo agrega con su firma `message`.

> **Dos campos, no uno.** `Failure` lleva `code` y `ServerException` lleva
> `statusCode`. Es deliberado: el codigo HTTP es un detalle del transporte, el
> `code` de negocio es del dominio. Mezclarlos hace que la capa de presentacion
> termine mirando codigos HTTP para decidir que mostrar.

**`lib/core/error/exceptions.dart`**

```dart
/// Excepcion de infraestructura: algo que fallo al hablar con algo.
///
/// La capa `data` las lanza. La capa `domain` nunca las ve: el repositorio las
/// traduce a `Failure`.
class ServerException implements Exception {
  const ServerException({
    required this.message,
    this.statusCode,
  });

  final String message;
  final int? statusCode;

  @override
  String toString() => 'ServerException($message, statusCode: $statusCode)';
}

class NetworkException implements Exception {
  const NetworkException({required this.message});

  final String message;

  @override
  String toString() => 'NetworkException($message)';
}

class CacheException implements Exception {
  const CacheException({required this.message});

  final String message;

  @override
  String toString() => 'CacheException($message)';
}

class ValidationException implements Exception {
  const ValidationException({required this.message});

  final String message;

  @override
  String toString() => 'ValidationException($message)';
}
```

### 3.8 `core/common/usecase.dart`

```dart
import 'package:equatable/equatable.dart';
import 'package:fpdart/fpdart.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';

/// Params de un use case sin argumentos.
///
/// Se usa `NoParams()` y no un valor nulo para que el constructor del use case
/// quede uniforme: `GetRafflesUseCase(this._repo)`, `SignInUseCase(this._repo)`.
class NoParams extends Equatable {
  const NoParams();

  @override
  List<Object?> get props => const [];
}

/// Un caso de uso. Devuelve `Either<Failure, T>`: o falla, o tiene exito.
///
/// Que devuelva `Either` en vez de `Future<T>` no es estilo. Obliga a decidir en
/// tiempo de compilacion que pasa con el error, y no a olvidarse en cada
/// `await`. Un `Future<T>` que tambien puede fallar es indistinguible de uno que
/// no falla.
abstract class UseCase<Type, Params> {
  Future<Either<Failure, Type>> call(Params params);
}

/// Variante sin parametros. Separada para no obligar a `call(NoParams())`.
abstract class NoParamsUseCase<Type> {
  Future<Either<Failure, Type>> call();
}
```

> **Por que `fpdart` y no `dartz`:** `dartz` esta sin mantenimiento desde 2023.
> `fpdart` es actively maintained, soporta Dart 3 completo, y su API es igual
> (`Either`, `Left`, `Right`, `fold`). El unico cambio al migrar de un proyecto
> viejo: `dartz` tiene `fold` con `(L left, R right)`, `fpdart` tambien. Practica
> la misma.

### 3.9 `core/config/app_config.dart` y `core/constants/constants.dart`

**`lib/core/config/app_config.dart`**

```dart
import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Configuracion leida del `.env`.
///
/// Todo son getters estaticos perezosos: leer un getter no toca `dotenv`, solo
/// cuando se lo usa. Asi se puede llamar a `AppConfig.algo` antes o despues de
/// `dotenv.load()` sin romper.
///
/// Regla: todo acceso al `.env` pasa por aca. Ningun `dotenv.env['X']` suelto
/// en el codigo. Un unico punto de lectura es un unico punto de auditar.
class AppConfig {
  const AppConfig._();

  // --- Supabase ---
  static String get supabaseUrl => dotenv.env['SUPABASE_URL'] ?? '';

  /// La publishable key (sb_publishable_...). Publica por diseno.
  static String get supabasePublishableKey =>
      dotenv.env['SUPABASE_PUBLISHABLE_KEY'] ?? '';

  // --- Sitio ---
  static String get siteUrl => dotenv.env['SITE_URL'] ?? 'http://127.0.0.1:3000';

  // --- Opcional: observabilidad ---
  // Vacio significa "no instalar". Ver `## PACK: observability`.
  static String get sentryDsn => dotenv.env['SENTRY_DSN'] ?? '';
  static String get sentryRelease => dotenv.env['SENTRY_RELEASE'] ?? '';

  /// Verifica que las variables criticas tengan valor.
  ///
  /// Llamarlo en `main()` antes de `Supabase.initialize`. Un string vacio en la
  /// URL de Supabase produce un error de red thirty minutos despues, en el primer
  /// request real, no en el arranque. Fallar aca es fallar en el momento util.
  static List<String> validate() {
    final missing = <String>[];
    if (supabaseUrl.isEmpty) missing.add('SUPABASE_URL');
    if (supabasePublishableKey.isEmpty) missing.add('SUPABASE_PUBLISHABLE_KEY');
    return missing;
  }
}
```

**`lib/core/constants/constants.dart`**

Solo constantes que son hechos sobre la app, no configuracion. Si el valor cambia
por entorno, va en `AppConfig`, no aca.

```dart
/// Constantes de la aplicacion.
///
/// Aqui van hechos, no configuracion: el nombre de la app, los timeouts, los
/// limites de paginado. Lo que varia por entorno va en `AppConfig`.
class AppConstants {
  const AppConstants._();

  static const String appName = '{{NOMBRE_MOSTRABLE}}';
  static const String appVersion = '{{VERSION_INICIAL}}';

  // --- Red ---
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 30);

  // --- Paginacion ---
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;

  // --- Cache ---
  static const Duration cacheTtl = Duration(days: 30);

  // --- Storage (Isar) ---
  static const String isarName = '{{NOMBRE_PROYECTO}}';

  // --- Rutas ---
  static const String assetsPath = 'assets';
  static const String imagePath = '$assetsPath/images';
}
```

> **Por que `AppConfig` y no leer `dotenv` en cada lado:** con lecturas sueltas,
> `grep SUPABASE_URL` devuelve cinco lugares y cambiar el nombre de una variable
> es buscar en todo el proyecto. Con `AppConfig`, es un archivo.

### 3.10 `core/network/network_info.dart`

```dart
import 'package:injectable/injectable.dart';
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart';

/// Estado de la conexion de red.
///
/// Vive en `core` y no en `features/` porque lo consultan todos los repositorios.
/// Un repositorio que hace `if (await networkInfo.isConnected)` no necesita saber
/// que la conexion se mide con `internet_connection_checker_plus`.
abstract class NetworkInfo {
  Future<bool> get isConnected;
}

/// `@LazySingleton(as:)` dice: "cuando algo pida un `NetworkInfo`, dale un
/// `NetworkInfoImpl`". El `_connectionChecker` lo inyecta GetIt desde el
/// `@module`; nadie lo pasa a mano.
@LazySingleton(as: NetworkInfo)
class NetworkInfoImpl implements NetworkInfo {
  NetworkInfoImpl(this._connectionChecker);

  final InternetConnection _connectionChecker;

  @override
  Future<bool> get isConnected => _connectionChecker.hasConnection;
}
```

> **Por que una abstraccion de tres lineas:** el repositorio depende de
> `NetworkInfo`, no del paquete. Los tests pueden inyectar un fake con una linea
> (`class FakeNetworkInfo implements NetworkInfo { ... }`) en lugar de mockear una
> plataforma con canales de method calls.

### 3.11 `core/utils/` -- utilerias transversales

**`lib/core/utils/error_handler.dart`**

Traduce los mensajes crudos de los proveedores a texto presentable, y deja
registrado que mensaje va con que error.

```dart
import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';

/// Traduce errores a texto que se pueda mostrar.
///
/// Existe por una razon concreta: los proveedores de infraestructura tiran
/// strings en ingles que no significan nada para el usuario ("JWT expired",
/// "relation does not exist"). Este archivo es el unico lugar donde se decide
/// que se le muestra a la persona.
///
/// **Y el problema que resuelve de verdad:** sin esto, cada repositorio escribe
/// `e.message` directo a la UI, y el texto crudo se escapa a produccion.
///
/// El nucleo lo incluye porque no tiene nada de auth: es util para cualquier
/// proyecto. Si tu app tiene l10n completo, preferi `Failure` con un `type`
/// enumerado y traduzi con l10n. Ver el Apendice C, punto 4.
class ErrorHandler {
  const ErrorHandler._();

  // ------------------------------------------------------------------
  //  Mensajes exactos del proveedor. De proposito literales: si cambia el
  //  mensaje, falla el lookup y caemos en la traduccion heuristica.
  // ------------------------------------------------------------------

  static const Map<String, String> _supabaseErrorMessages = {
    'Invalid login credentials': 'Correo o contrasena incorrectos',
    'Email not confirmed': 'Tu correo todavia no esta confirmado',
    'User already registered': 'Ya existe una cuenta con ese correo',
    'Password should be at least 6 characters':
        'La contrasena debe tener al menos 6 caracteres',
    'Rate limit exceeded': 'Demasiados intentos. Espera un momento',
    'JWT expired': 'Tu sesion expiro. Volve a iniciar sesion',
    'JWT invalid': 'Tu sesion no es valida. Volve a iniciar sesion',
    'new password should be different from the old password':
        'La contrasena nueva debe ser distinta de la anterior',
    'unable to validate email address': 'El correo no tiene un formato valido',
    'request timed out': 'La solicitud tardo demasiado. Proba de nuevo',
    'Failed to fetch': 'No pudimos conectarnos. Revisa tu red',
  };

  static const Map<String, String> _networkErrorMessages = {
    'Network Failure': 'Sin conexion a internet',
    'No internet connection': 'Sin conexion a internet',
    'SocketException': 'Sin conexion a internet',
    'TimeoutException': 'La solicitud tardo demasiado',
  };

  static const Map<String, String> _genericErrorMessages = {
    'Something went wrong': 'Algo salio mal. Proba de nuevo',
    'Unhandled exception': 'Algo salio mal. Proba de nuevo',
    'Bad state': 'Algo salio mal. Proba de nuevo',
  };

  // ------------------------------------------------------------------
  //  API
  // ------------------------------------------------------------------

  /// Traduce por coincidencia exacta.
  static String translate(String errorMessage) {
    return _supabaseErrorMessages[errorMessage] ??
        _networkErrorMessages[errorMessage] ??
        _genericErrorMessages[errorMessage] ??
        _fallback(errorMessage);
  }

  /// Traduce un `Failure` al mensaje que se muestra.
  ///
  /// El `switch` sobre el tipo, no sobre el string: si el repositorio cambia
  /// el mensaje de un `ServerFailure`, la traduccion sigue funcionando.
  static String forFailure(Failure failure) {
    return switch (failure) {
      ServerFailure() => translate(failure.message),
      NetworkFailure() => 'Sin conexion a internet. Revisa tu red',
      CacheFailure() => 'No pudimos leer los datos guardados',
      ValidationFailure() => 'Revisa los datos que cargaste',
    };
  }

  static String forNetworkError() => 'Sin conexion a internet. Revisa tu red';

  static String forServerError([int? statusCode]) {
    if (statusCode == null) return 'El servidor respondio con un error';
    return 'El servidor respondio con un error ($statusCode)';
  }

  static String forCacheError([String? message]) =>
      message == null ? 'No pudimos leer los datos guardados' : translate(message);

  static String forUnknownError() => 'Algo salio mal. Proba de nuevo';

  // ------------------------------------------------------------------
  //  Heuristicas, para cuando el mensaje no coincide exacto
  // ------------------------------------------------------------------

  static String _fallback(String errorMessage) {
    final lower = errorMessage.toLowerCase();
    if (lower.contains('timeout')) return 'La solicitud tardo demasiado';
    if (lower.contains('socket') || lower.contains('connection')) {
      return 'Sin conexion a internet';
    }
    if (lower.contains('expired')) return 'Tu sesion expiro. Volve a iniciar sesion';
    if (lower.contains('unique') || lower.contains('duplicate')) {
      return 'Ese registro ya existe';
    }
    if (lower.contains('violates')) return 'La operacion viola una restriccion';
    if (lower.contains('permission denied')) {
      return 'No tenes permiso para hacer eso';
    }
    return 'Algo salio mal. Proba de nuevo';
  }
}
```

> **El problema real de este archivo, y su unico riesgo:** el mensaje crudo de
> un proveedor es un contrato no documentado. Cuando Supabase lo cambie, el
> lookup falla, cae en `_fallback`, y el usuario ve "Algo salio mal" en vez de
> "Tu sesion expiro". No se rompe, pero se pierde precision en silencio.
>
> Mitigacion: los tests de este archivo fijan los strings. Cuando Supabase los
> cambie, los tests avisan.
>
> **El riesgo mayor es peor:** si en algun momento un mensaje crudo contiene datos
> del servidor (un id, un nombre de columna con datos de otra persona), esto lo
> muestra al usuario. `_fallback` devuelve texto generico justamente para
> acotar eso. Nunca reescribas esto para que muestre el error crudo.
>
> **Por que el mapa tiene strings de auth en un proyecto sin auth.** porque
> `supabase_flutter` esta en el stack pase lo que pase, y los mensajes de Auth
> son los mas numerosos y los mas propensos a aparecer. Son entradas muertas en
> un proyecto sin usuarios, y el costo de tenerlas es cero: un lookup que nunca
> se dispara. Quitarlas cuando no haya auth es opcional; dejarlas es mas simple
> que mantener dos versiones del archivo.

**`lib/core/utils/snackbar_helper.dart`**

```dart
import 'package:flutter/material.dart';

import 'package:{{NOMBRE_PROYECTO}}/l10n/l10n.dart';

/// Snackbars consistentes.
///
/// Existe para que ninguna pantalla escriba `ScaffoldMessenger.of(context)
/// .showSnackBar(...)` a mano. Cada una seria una fuente distinta de copy y de
/// duracion.
class SnackbarHelper {
  const SnackbarHelper._();

  static void showSuccess(BuildContext context, String message) {
    _show(context, message, isError: false);
  }

  static void showError(BuildContext context, String message) {
    _show(context, message, isError: true);
  }

  static void showFailure(BuildContext context, Object failure) {
    _show(context, ErrorHandler.forFailure(failure as Failure),
        isError: true);
  }

  static void _show(
    BuildContext context,
    String message, {
    required bool isError,
  }) {
    final messenger = ScaffoldMessenger.of(context);
    messenger.hideCurrentSnackBar();
    messenger.showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        backgroundColor:
            isError ? Theme.of(context).colorScheme.error : null,
        duration: Duration(seconds: isError ? 5 : 3),
      ),
    );
  }
}
```

> **Falta el import de `ErrorHandler` y de `Failure` en el archivo real.** Son
> `package:{{NOMBRE_PROYECTO}}/core/utils/error_handler.dart` y
> `package:{{NOMBRE_PROYECTO}}/core/error/failures.dart`. No los dejes como nota.

**`lib/core/utils/validators.dart`**

```dart
/// Validadores de formulario.
///
/// Reutilizables y con mensaje via l10n. Un `validator` devuelve `String?`: el
/// texto de error, o `null` si esta bien.
class Validators {
  const Validators._();

  static String? required(String? value, {String? fieldName}) {
    if (value == null || value.trim().isEmpty) {
      return fieldName == null
          ? 'Este campo es obligatorio'
          : '$fieldName es obligatorio';
    }
    return null;
  }

  static String? minLength(
    String? value,
    int min, {
    String? fieldName,
  }) {
    if (value == null || value.trim().length < min) {
      return fieldName == null
          ? 'Tiene que tener al menos $min caracteres'
          : '$fieldName tiene que tener al menos $min caracteres';
    }
    return null;
  }

  static String? maxLength(
    String? value,
    int max, {
    String? fieldName,
  }) {
    if (value != null && value.trim().length > max) {
      return fieldName == null
          ? 'No puede pasar de $max caracteres'
          : '$fieldName no puede pasar de $max caracteres';
    }
    return null;
  }

  static String? email(String? value) {
    if (value == null || value.isEmpty) return 'El correo es obligatorio';
    // Expresion deliberadamente laxa: el unico validador de correo que vale
    // es el que manda el correo. Aca solo se filtran los casos evidentes.
    final pattern = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');
    if (!pattern.hasMatch(value.trim())) return 'El correo no es valido';
    return null;
  }

  /// Ejecuta una lista de validadores y devuelve el primer error.
  ///
  /// `null` si todos pasan.
  static String? compose(List<String? Function()> validators) {
    for (final validate in validators) {
      final error = validate();
      if (error != null) return error;
    }
    return null;
  }
}
```

> **Por que `compose` y no encadenar `??`:** con dos validadores,
> `Validators.required(a) ?? Validators.email(a)` funciona, pero con cinco es una
> linea de 200 caracteres y el orden de la operacion `??` es dificil de leer.
> `compose` hace el loop explicito.

**`lib/core/utils/app_info.dart`**

```dart
import 'package:package_info_plus/package_info_plus.dart';

/// Metadata de la app, leida de la plataforma.
///
/// Vive en `utils` y no en `config` porque no viene del `.env`: lo da el
/// binario. Sirve para mostrar la version y para comparar contra una version
/// remota.
class AppInfo {
  const AppInfo._();

  static late final String version;
  static late final String buildNumber;

  static Future<void> init() async {
    final info = await PackageInfo.fromPlatform();
    version = info.version;
    buildNumber = info.buildNumber;
  }

  static String get versionString => '$version+$buildNumber';
}
```

### 3.12 `core/data/local/` -- cache local

Isar arranca **desde `core`, no desde cada feature.** Es la pieza que suele
generar duplicacion: si el cache es global a la app, su servicio y sus schemas
son globales a la app. Cada feature aporta su datasource local, no su base de
datos.

**`lib/core/data/local/isar_service.dart`**

```dart
import 'package:{{NOMBRE_PROYECTO}}/core/constants/constants.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/data/local/isar_models/cached_entry.dart';
import 'package:isar_community/isar.dart';
import 'package:path_provider/path_provider.dart';

/// Bootstrap de Isar.
///
/// Un unico `Isar.open` para toda la app, con todos los schemas centralizados.
/// Agregar una coleccion implica: sumar el `@Collection` en `isar_models/`, sumar
/// su `*Schema` a la lista de abajo, y correr `make gen`.
///
/// Por que una lista central de schemas y no un descubrimiento automatico:
/// el orden de apertura importa cuando hay indices cruzados, y una lista
/// explicita deja ese orden a la vista. El costo es editar dos lugares cuando
/// agregas una coleccion; el beneficio es no tener un `build_runner` que
/// descubra schemas.
class IsarService {
  IsarService._();

  static Isar? _instance;

  /// Instancia abierta. Lanza si se llama antes de `initialize()`.
  ///
  /// Que sea `late` en vez de nullable obliga a que el orden de arranque este
  /// bien, en vez de fallar en el primer uso con un null check.
  static Isar get instance {
    final instance = _instance;
    if (instance == null) {
      throw StateError(
        'Isar no inicializado. Corre configureDependencies() en main(): '
        'el modulo de DI lo abre con @preResolve.',
      );
    }
    return instance;
  }

  static bool get isInitialized => _instance != null;

  static Future<void> initialize() async {
    if (_instance != null) return;

    final directory = await getApplicationDocumentsDirectory();
    _instance = await Isar.open(
      [
        CachedEntrySchema,
        // TODO: sumar aca los schemas de cada feature, en orden.
      ],
      directory: directory.path,
      name: AppConstants.isarName,
    );
  }

  /// Cierra la instancia. Usado en tests y en el apagado controlado.
  static Future<void> close() async {
    await _instance?.close();
    _instance = null;
  }

  /// Borra todo el contenido. No borra el archivo.
  static Future<void> clear() async {
    final instance = instance;
    await instance.writeTxn(() async {
      await instance.clear();
    });
  }
}
```

**`lib/core/data/local/isar_models/cached_entry.dart`**

El nucleo trae **una** coleccion generica. No es un cache de negocio: es la que
usa el slice de ejemplo (FASE 4) y la que sirve de plantilla para las reales.

```dart
import 'package:isar_community/isar.dart';

part 'cached_entry.g.dart';

/// Entrada de cache con TTL.
///
/// Plantilla para las colecciones reales. Tres cosas que toda coleccion de cache
/// necesita y que es facil olvidar:
///
/// 1. `@Index(unique: true)` sobre la clave natural. Sin el, el cache duplica
///    filas en cada escritura y `where()` devuelveUnexpectedamente varias.
/// 2. `cachedAt` y `expiresAt`. Un cache sin TTL es una fuente de datos
///   obsoleta: el usuario ve algo que el backend ya cambio.
/// 3. Un `key` compuesto string, no un id autogenerado. El id de Isar sirve para
///    la fila, la clave natural sirve para deduplicar.
@Collection()
class CachedEntry {
  CachedEntry({
    required this.key,
    required this.payload,
    this.expiresAt,
  });

  /// Clave natural. Unica por indice.
  @Index(unique: true)
  String key;

  /// Contenido serializado. JSON string, no Map: Isar no indexa Map y un Map
  /// obliga a migrar el schema cada vez que la forma del dato cambia.
  String payload;

  DateTime? cachedAt;

  /// Si es `null`, no expira. Chequear antes de leer:
  /// `entry.expiresAt == null || entry.expiresAt!.isAfter(DateTime.now())`.
  DateTime? expiresAt;
}
```

> **Sobre por que `payload` es un `String` y no un `Map`:** Isar soporta `Map`
> pero el campo no es indexable y cambiar la forma del dato obliga a una
> migracion. Un JSON string es opaco, no migra nunca, y para un cache es
> exactamente lo que queres. El precio es pagar `jsonDecode` en cada lectura, que
> en un cache de lectura rapida es irrelevante.

### 3.13 `core/session/` -- la identidad, declarada y vacia

Esta es la pieza central del prompt. Lee el codigo y despues la nota.

**`lib/core/session/current_user.dart`**

```dart
/// La identidad de quien esta usando la app.
///
/// **Por que esto existe y esta vacio.** Muchisimas apps no tienen usuarios: una
/// app de notas, un lector de RSS, una calculadora de gastos. Otras los tienen.
/// Si el bootstrap te genera la pantalla de login, el router con redirect y la
/// tabla `profiles`, le estas resolviendo a la app una pregunta que el dueno del
/// proyecto todavia no se hizo. Y compila, asi que el error aparece meses
/// despues.
///
/// La solucion es no tener la pregunta en el nucleo. Este archivo declara *que*
/// es la identidad, sin decir *de donde* viene. Un proyecto sin usuarios la
/// implementa con el stub de abajo y nunca lo piensa de nuevo. Un proyecto con
/// usuarios pega el `## PACK: auth` y reemplaza el stub.
///
/// Los repositorios preguntan por `userId`. Si vuelve `null`, significa "esta
/// operacion necesita un usuario y no hay". Eso sirve igual para una app publica
/// (donde `null` es el estado normal y se responde con una consulta sin filtro)
/// que para una app privada.
///
/// **La regla de dependencia:** las features consultan esta abstraccion, nunca
/// `features/<algo>/` directamente. Si una feature importa la feature de auth
/// para preguntar quien es el usuario, la dependencia se invierte: `auth` deja de
/// poder usar `core`.
abstract class CurrentUser {
  /// Id del usuario actual, o `null` si no hay ninguno.
  String? get userId;

  /// Si hay un usuario. Equivale a `userId != null`, pero disponible para codigo
  /// de presentacion que quiere leer el nombre sin el `!=`.
  bool get isSignedIn => userId != null;

  /// Para invalidar caches o forzar una relectura cuando la identidad cambia.
  ///
  /// El nucleo no lo usa: no hay streams de sesion. Si tu proyecto tiene auth y
  /// este metodo no hace nada, borralo en vez de dejarlo como no-op.
  // TODO: si tu app tiene identidad observable (login/logout), implementá
  // refresh() acá y notificá a los que escuchen.
}
```

**`lib/core/session/current_user_stub.dart`**

```dart
import 'package:injectable/injectable.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/session/current_user.dart';

/// Implementacion para apps sin usuarios.
///
/// Es el registro por defecto del bootstrap. `userId` es siempre `null`, asi que
/// cualquier repositorio que lo pida recibe "no hay usuario" y responde con su
/// camino de lectura publica.
///
/// **Esto no es scaffolding para borrar a la fuerza.** Es una implementacion
/// completa y correcta del contrato "esta app no tiene identidad". Si tu app no
/// tiene usuarios, este archivo se queda.
///
/// La anotación es la declaracion de registro: no hay una linea en otro archivo
/// que diga "para `CurrentUser`, usa `CurrentUserStub`". Si tu proyecto **si**
/// tiene usuarios, borra este archivo y pegá el `## PACK: auth`, que trae
/// `CurrentUserSupabase` con la misma anotación. El `## PACK: auth` te avisa si
/// quedan las dos anotaciones a la vez: serian dos registros del mismo tipo.
@LazySingleton(as: CurrentUser)
class CurrentUserStub implements CurrentUser {
  const CurrentUserStub();

  @override
  String? get userId => null;

  @override
  bool get isSignedIn => false;
}
```

> **Nota:** el texto de la clase dice `CurrentUserStub`. Si tu proyecto **si**
> tiene usuarios, este archivo no aplica: borralo y usá el `## PACK: auth`.

**Lo que este prompt NO genera, y por que.** Ninguno de estos archivos existe en
la salida del bootstrap:

| No se genera | Motivo |
|---|---|
| `user_session_impl.dart` que lee `Supabase.instance.client.auth` | Asume que hay sesiones |
| La tabla `profiles` | Asume un modelo de datos de usuarios |
| El trigger `on auth.users insert` | Idem |
| El enum `AuthMonitorEvent` y su stream | Asume que el login emite eventos |
| `AuthCubit` | Asume una feature de login |

Los cuatro van en `## PACK: auth`. Ese bloque los mete todos juntos y en el orden
correcto, con las migraciones y el `config.toml` incluidos.

### 3.14 `core/di/` -- el punto de entrada de la DI

`injectable` + `get_it`. Las decisiones de registro viven **en cada clase**, con
una anotación. `build_runner` las convierte en llamadas a GetIt. Este directorio
tiene dos archivos y ninguno contiene registros.

**`lib/core/di/service_locator.dart`**

```dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/di/service_locator.config.dart';

/// El contenedor de dependencias.
///
/// `final sl = GetIt.instance` es el atajo global. Todo el proyecto usa `sl`:
/// las paginas (`BlocProvider(create: (_) => sl<XCubit>())`), `main()` y los
/// tests que necesiten una instancia real.
final GetIt sl = GetIt.instance;

/// Registra todas las dependencias.
///
/// **No escribas el registro a mano.** Cada clase se anota donde vive:
///
/// - `@lazySingleton` -- una sola instancia para la app (use cases, servicios).
/// - `@LazySingleton(as: X)` -- la abstracta `X` se resuelve a esta concreta
///   (datasources, repositories).
/// - `@injectable` -- `factory`, una instancia por request. **Cubits de
///   pantalla.** Un cubit global de `Bootstrap` va `@lazySingleton`: dos
///   `sl<XCubit>()` darian dos instancias distintas.
/// - `@module` -- clases de terceros que no puedo anotar. Va en
///   `external_module.dart`.
///
/// y `make gen` escribe el cuerpo en `service_locator.config.dart`.
///
/// **`service_locator.config.dart` se commitea.** Si lo regeneras y queda un
/// diff, es que alguien anoto algo sin correr `make gen`; CI lo detecta con
/// `git diff --exit-code`.
///
/// Por que `injectable` y no una cascada manual: ver
/// `docs/adr/0002-getit-injectable.md`.
@InjectableInit(
  initializerName: 'init',
  // `false` = el config generado usa imports `package:` como todo `lib/`.
  // Si fuera `true` (el default), el config tendria imports relativos y seria
  // la unica excepcion a la regla 7 del prompt.
  preferRelativeImports: false,
)
Future<void> configureDependencies() async {
  // Isar arranca adentro del modulo (@preResolve), no aca: `init()` espera el
  // modulo antes de registrar el resto, y todo lo demas es sincrono.
  await sl.init();
}
```

> **Por que `sl` sigue siendo `sl`:** el alias no cambia, solo cambia quien
> escribe el registro. `main()`, las paginas y los tests siguen haciendo
> `sl<XCubit>()`; el `.config.dart` detras resuelve.

**`lib/core/di/external_module.dart`** -- lo que no puedo anotar

```dart
import 'package:http/http.dart' as http;
import 'package:injectable/injectable.dart';
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart';
import 'package:isar_community/isar.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/data/local/isar_service.dart';

/// Dependencias de terceros: clases que no llevan anotaciones nuestras porque
/// no son nuestras. Un `@module` es la traduccion de un `registerLazySingleton`
/// manual, pero declarado al lado del resto de la DI.
///
/// **Por que registrar `SupabaseClient` si `Supabase.instance` ya es un
/// singleton:** el modulo no crea un cliente nuevo, devuelve la misma
/// instancia de la libreria. Hay una sola verdad (`Supabase.instance.client`);
/// GetIt solo guarda la referencia para poder inyectarla por tipo en los
/// constructores. Antes de registrar, el getter no se ejecuta: `main()`
/// llama a `Supabase.initialize()` antes de `configureDependencies()`.
@module
abstract class ExternalModule {
  /// El unico init asincrono de la app.
  ///
  /// `@preResolve` hace que `init()` espere este Future antes de registrar
  /// el resto. Sin eso, el primer `sl<Isar>()` llegaria antes de abrir la base.
  @preResolve
  Future<Isar> get isar async {
    await IsarService.initialize();
    return IsarService.instance;
  }

  @lazySingleton
  InternetConnection get internetConnection =>
      InternetConnection.createInstance();

  @lazySingleton
  http.Client get httpClient => http.Client();

  @lazySingleton
  SupabaseClient get supabaseClient => Supabase.instance.client;
}
```

> **Por que `InternetConnection.createInstance()` y no
> `newInstance`:** `internet_connection_checker_plus` 2.9.1+2 no tiene
> `newInstance`; `createInstance` es el constructor de fabrica real.

**Como registrar algo nuevo, en tres lineas:** anotá la clase, y corré
`make gen`. Ejemplos:

```dart
@lazySingleton                     // una instancia para toda la app
class AnalyticsService { ... }

@LazySingleton(as: UserRepository) // la abstracta se resuelve a esta
class UserRepositoryImpl implements UserRepository { ... }

@injectable                        // cubit: una instancia por pantalla
class SettingsCubit extends Cubit<SettingsState> { ... }
```

> **Nunca `@lazySingleton` en un cubit de pantalla.** Un cubit singleton
> sobrevive al `dispose()` de su pantalla y fuga estado entre dos visitas al
> mismo flujo. La unica excepcion es un cubit de ambito de app, provisto una
> sola vez en `MultiBlocProvider` con `.value` (ver P10 del `## PACK: auth`).

### 3.15 `core/services/cache_manager.dart`

```dart
import 'package:injectable/injectable.dart';

/// Registro de funciones que vacian caches.
///
/// El problema que resuelve: el logout tiene que limpiar el cache, pero el
/// `cache_manager` no puede conocer a cada datasource local sin un import
/// circular (los datasources importan `di`, `di` importa `cache_manager`).
///
/// La solucion es el patron de registro: cada datasource se inyecta con este
/// manager y se registra desde su propio constructor, y el manager solo guarda
/// closures. Ningun ciclo de imports.
///
/// `@lazySingleton` en vez de `@injectable`: tiene que haber UNA sola lista de
/// cleaners. Dos instancias registrarian dos mitades y el `clearAll()` limpiaria
/// la mitad del cache.
@lazySingleton
class CacheManager {
  final List<Future<void> Function()> _clearers = [];

  /// Registra una funcion de limpieza.
  ///
  /// Llamar **en el constructor** del datasource local, no en `main()`:
  /// en el constructor, el datasource ya existe y el orden de registracion
  /// importa.
  void register(Future<void> Function() clear) {
    _clearers.add(clear);
  }

  /// Ejecuta todos los cleaners en paralelo.
  Future<void> clearAll() async {
    await Future.wait(_clearers.map((clear) => clear()));
  }

  /// Para tests.
  int get registeredCount => _clearers.length;
}
```

### 3.16 `core/routing/app_router.dart`

**Sin `redirect`. Sin `refreshListenable`. Sin `splash`.**

Un `redirect` de autenticacion es la forma mas comun de que un bootstrap te
resuelva una pregunta que no le hiciste. El nucleo enruta, y nada mas.

```dart
import 'package:flutter/material.dart';
import 'package:fpdart/fpdart.dart';
import 'package:go_router/go_router.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/session/current_user.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/{{FEATURE_EJEMPLO}}/presentation/pages/{{FEATURE_EJEMPLO}}_page.dart';
import 'package:{{NOMBRE_PROYECTO}}/l10n/l10n.dart';

/// El router de la app.
///
/// `router()` es un **metodo**, no un campo. Devuelve un `GoRouter` nuevo en cada
/// llamada. Si fuera un campo, la unica forma de cambiar el router seria
/// reconstruir la app entera.
///
/// ## Lo que este router NO tiene, y por que
///
/// Un bootstrap que genera auth mete aca tres cosas: un `redirect` que manda a
/// `/login` si no hay sesion, un `refreshListenable` para reaccionar a cambios de
/// sesion, y una ruta `/splash` que espera a que la sesion cargue. Son tres
/// piezas que solo tienen sentido si hay usuarios.
///
/// Sin usuarios, el `redirect` no tiene nada que evaluar y la pantalla de splash
/// solo alarga el arranque.
///
/// Si tu app **si** tiene usuarios, pegá el `## PACK: auth`: ese bloque agrega
/// el `redirect`, el `refreshListenable` y el bridge al cubit de auth, y lo
/// muestra en un unico lugar en vez de repartirlo.
class AppRouter {
  AppRouter(this._currentUser);

  final CurrentUser _currentUser;

  // --- Rutas ---
  // Cada ruta es un par: el path y el nombre con nombre, para no repetir
  // strings en el codigo que navega.
  static const String home = '/';
  static const String homeName = 'home';
  static const String exampleDetail = '/{{FEATURE_EJEMPLO}}/:id';
  static const String exampleDetailName = '{{FEATURE_EJEMPLO}}_detail';

  /// `static final`, no `const`: `GoRoute` no es const-constructible.
  static final List<RouteBase> routes = [
    GoRoute(
      path: home,
      name: homeName,
      builder: (context, state) => const {{DART_NOMBRE_CLASE}}Page(),
    ),
    GoRoute(
      path: exampleDetail,
      name: exampleDetailName,
      builder: (context, state) => {{DART_NOMBRE_CLASE}}DetailPage(
        // TODO: la clase del ejemplo define `id`. Cuando agregues features
        // reales, cambialo por tu tipo de entidad.
        id: state.pathParameters['id'] ?? '',
      ),
    ),
  ];

  /// Construye el router.
  ///
  /// El nucleo no tiene `redirect` ni `refreshListenable`. El pack de auth los
  /// agrega.
  GoRouter router() {
    return GoRouter(
      initialLocation: home,
      routes: routes,
      errorBuilder: (context, state) => const _PageNotFound(),
    );
  }

  /// Redireccion.
  ///
  /// Vacia a proposito, y es `Either<bool, String>` para que el dia que la
  /// necesites, el tipo ya sea el correcto en vez de cambiar la firma de un
  /// metodo que fifty archivos usan.
  ///
  /// TODO: si tu app tiene identidad, implementa aca la logica de navegacion
  /// por sesion y cambiala en `router()` por `redirect: redirect`. Ver
  /// `## PACK: auth`, que trae la implementacion completa.
  Either<bool, String> redirect(String location) {
    return const Left(false);
  }
}

/// 404. La pantalla que muestra `errorBuilder`.
///
/// Usa `state.uri` en el mensaje para que el error sea accionable: si el
/// developpega en un link roto, la ruta exacta queda en la UI y no en un
/// `print` que nadie lee.
class _PageNotFound extends StatelessWidget {
  const _PageNotFound({required this.uri});

  final String uri;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.pageNotFoundTitle)),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.explore_off_outlined, size: 56),
              const SizedBox(height: 16),
              Text(l10n.pageNotFoundBody, textAlign: TextAlign.center),
              const SizedBox(height: 8),
              Text(
                uri,
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: () => context.go(home),
                child: Text(l10n.goHome),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

Y en `router()`, el `errorBuilder` necesita recibir el estado:

```dart
      errorBuilder: (context, state) => _PageNotFound(uri: state.uri.toString()),
```

> **Sobre `Either<bool, String>` como firma de `redirect`:** un `redirect` de GoRouter
> devuelve `FutureOr<String?>`. Si el nucleo lo expone como `Either<bool, String>`
> —"redirigir a home" o "redirigir a esta ruta"—, el dia que se use, la logica
> ya tiene el tipo correcto. El costo es un `fold` en la llamada. Un nucleo que
> noopinion sobre identidad tampoco deberia opinion sobre la firma de `redirect`.

### 3.17 `core/theme/app_theme.dart`

```dart
import 'package:flutter/material.dart';

/// Temas de la app.
///
/// Un solo archivo con los dos modos. Los colores viven en `ColorScheme` con
/// `fromSeed`, no como colores sueltos: cambiar el tema es cambiar un seed, no
/// buscar 40 hex.
///
/// Los widgets de `core/widgets/` **no** tienen colores propios. Usan
/// `Theme.of(context).colorScheme`. Un `AppButton` con `color: Colors.blue`
/// dentro no se puede tematizar.
class AppTheme {
  const AppTheme._();

  /// Color semilla. Cambiar esto cambia toda la paleta.
  static const Color _seedColor = Color(0xFF3B5BDB);

  static ThemeData get lightTheme => _build(Brightness.light);

  static ThemeData get darkTheme => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: _seedColor,
      brightness: brightness,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: colorScheme.surface,
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 1,
        backgroundColor: colorScheme.surface,
        foregroundColor: colorScheme.onSurface,
        titleTextStyle: TextStyle(
          color: colorScheme.onSurface,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: colorScheme.surfaceContainerLow,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: EdgeInsets.zero,
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: colorScheme.surfaceContainerHighest,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colorScheme.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: colorScheme.error),
        ),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 14,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          minimumSize: const Size(0, 44),
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(8),
        ),
      ),
      dividerTheme: DividerThemeData(
        color: colorScheme.outlineVariant,
        space: 1,
        thickness: 1,
      ),
      listTileTheme: const ListTileThemeData(
        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      ),
      textTheme: const TextTheme(
        headlineMedium: TextStyle(fontSize: 26, fontWeight: FontWeight.w700),
        titleLarge: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
        titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
        bodyLarge: TextStyle(fontSize: 16, height: 1.4),
        bodyMedium: TextStyle(fontSize: 14, height: 1.4),
        bodySmall: TextStyle(fontSize: 12),
      ),
    );
  }
}
```

### 3.18 `core/widgets/` -- el arsenal base

Siete widgets. Todos **sin color propio**, todos usando `Theme.of(context)` y
l10n. Si un widget de `core` necesita un string, sale de `context.l10n`, nunca de
un literal: un literal en `core` es un string que no se puede traducir.

`app_button.dart`:

```dart
import 'package:flutter/material.dart';

enum AppButtonVariant { primary, secondary, tertiary, danger }

/// Boton de la app.
///
/// Variantes explicitas en vez de estilos sueltos: `AppButtonVariant.primary` es
/// legible en el call site, `color: Colors.blue` deja el significado en el
/// color, que es justo lo que no sobrevive al dark mode.
class AppButton extends StatelessWidget {
  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.isLoading = false,
    this.variant = AppButtonVariant.primary,
    this.icon,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final AppButtonVariant variant;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final isDisabled = onPressed == null || isLoading;

    final child = isLoading
        ? const SizedBox(
            height: 20,
            width: 20,
            child: CircularProgressIndicator(strokeWidth: 2),
          )
        : Text(label);

    return switch (variant) {
      AppButtonVariant.primary => FilledButton(
          onPressed: isDisabled ? null : onPressed,
          child: child,
        ),
      AppButtonVariant.secondary => OutlinedButton(
          onPressed: isDisabled ? null : onPressed,
          child: child,
        ),
      AppButtonVariant.tertiary => TextButton(
          onPressed: isDisabled ? null : onPressed,
          child: child,
        ),
      AppButtonVariant.danger => FilledButton(
          onPressed: isDisabled ? null : onPressed,
          style: FilledButton.styleFrom(
            backgroundColor: scheme.error,
            foregroundColor: scheme.onError,
          ),
          child: child,
        ),
    };
  }
}
```

`app_card.dart`:

```dart
import 'package:flutter/material.dart';

/// Contenedor con padding, borde y sombra consistentes.
///
/// Envuelve contenido arbitrario. Un `Card` de Material por pantalla produce
/// margenes y radios distintos en cada una.
class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    required this.child,
    this.onTap,
    this.padding = const EdgeInsets.all(16),
  });

  final Widget child;
  final VoidCallback? onTap;
  final EdgeInsetsGeometry padding;

  @override
  Widget build(BuildContext context) {
    final content = Container(
      width: double.infinity,
      padding: padding,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surfaceContainerLow,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: Theme.of(context).colorScheme.outlineVariant,
        ),
      ),
      child: child,
    );

    if (onTap == null) return content;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: content,
      ),
    );
  }
}
```

`app_text_field.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Campo de texto con los estilos de la app.
///
/// Los `TextInputFormatter` van como parametro, no adentro: un campo de codigo
/// postal, uno de email y uno de tarjeta tienen reglas distintas, y meterlas en
/// el widget obliga a un `if` por caso.
class AppTextField extends StatelessWidget {
  const AppTextField({
    super.key,
    required this.label,
    this.controller,
    this.hint,
    this.validator,
    this.onChanged,
    this.keyboardType,
    this.textInputAction,
    this.inputFormatters,
    this.obscureText = false,
    this.enabled = true,
    this.maxLines = 1,
    this.autofocus = false,
  });

  final String label;
  final TextEditingController? controller;
  final String? hint;
  final String? Function(String?)? validator;
  final ValueChanged<String>? onChanged;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final List<TextInputFormatter>? inputFormatters;
  final bool obscureText;
  final bool enabled;
  final int maxLines;
  final bool autofocus;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      validator: validator,
      onChanged: onChanged,
      keyboardType: keyboardType,
      textInputAction: textInputAction,
      inputFormatters: inputFormatters,
      obscureText: obscureText,
      enabled: enabled,
      maxLines: obscureText ? 1 : maxLines,
      autofocus: autofocus,
      autovalidateMode: AutovalidateMode.onUserInteraction,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
      ),
    );
  }
}
```

`empty_state.dart`:

```dart
import 'package:flutter/material.dart';

import 'package:{{NOMBRE_PROYECTO}}/l10n/l10n.dart';

/// Estado vacio.
///
/// Existe porque "no hay nada aca" es un estado de primera clase, no un caso
/// borde. Un `Center(child: Text('...'))` en cada pantalla produce cinco textos
/// distintos para lo mismo.
class EmptyState extends StatelessWidget {
  const EmptyState({
    super.key,
    required this.message,
    this.title,
    this.actionLabel,
    this.onAction,
    this.icon = Icons.inbox_outlined,
  });

  /// Titulo. Si es `null`, sale de l10n. Un string hardcodeado aca es un string
  /// que no se traduce.
  final String? title;

  /// Mensaje que explica por que esta vacio. Este si es obligatorio: un estado
  /// vacio sin explicacion no le dice al usuario que hacer.
  final String message;

  final String? actionLabel;
  final VoidCallback? onAction;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 56,
              color: Theme.of(context).colorScheme.outline,
            ),
            const SizedBox(height: 16),
            Text(
              title ?? l10n.emptyStateTitle,
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.outline,
                  ),
              textAlign: TextAlign.center,
            ),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 24),
              AppButton(
                label: actionLabel!,
                onPressed: onAction,
                variant: AppButtonVariant.secondary,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

`error_view.dart`:

```dart
import 'package:flutter/material.dart';

import 'package:{{NOMBRE_PROYECTO}}/l10n/l10n.dart';

/// Vista de error con reintento.
///
/// El cubit expone `Failure`, la vista muestra texto. Un error que obliga a
/// arrancar la app no sirve.
class ErrorView extends StatelessWidget {
  const ErrorView({
    super.key,
    required this.message,
    this.onRetry,
    this.icon = Icons.error_outline,
  });

  final String message;
  final VoidCallback? onRetry;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              size: 56,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              AppButton(
                label: l10n.retry,
                onPressed: onRetry,
                variant: AppButtonVariant.secondary,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

`loading_indicator.dart`:

```dart
import 'package:flutter/material.dart';

/// Indicador de carga centrado.
///
/// Para carga de pantalla completa. Para carga dentro de un boton, `AppButton`
/// ya lo tiene. Para carga de una seccion sin bloquear la pantalla, un
/// `LinearProgressIndicator` en la parte de arriba del Scaffold.
class LoadingIndicator extends StatelessWidget {
  const LoadingIndicator({super.key, this.label});

  final String? label;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          if (label != null) ...[
            const SizedBox(height: 16),
            Text(label!, style: Theme.of(context).textTheme.bodyMedium),
          ],
        ],
      ),
    );
  }
}
```

`skeleton.dart`:

```dart
import 'package:flutter/material.dart';

/// Placeholder de carga.
///
/// Un `CircularProgressIndicator` en medio de una lista oculta el layout y hace
/// que la pantalla salte cuando llega el contenido. El skeleton reserva el lugar.
///
/// El `shimmer` esta a proposito en el nucleo porque no necesita dependencias
/// externas: una animacion de gradiente con `AnimatedBuilder`.
class Skeleton extends StatefulWidget {
  const Skeleton({
    super.key,
    this.width,
    this.height = 16,
    this.borderRadius = 8,
  });

  final double? width;
  final double height;
  final double borderRadius;

  @override
  State<Skeleton> createState() => _SkeletonState();
}

class _SkeletonState extends State<Skeleton>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1200),
  )..repeat(reverse: true);

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Container(
          width: widget.width,
          height: widget.height,
          decoration: BoxDecoration(
            color: Color.lerp(
              scheme.surfaceContainerHighest,
              scheme.surfaceContainerLow,
              _controller.value,
            ),
            borderRadius: BorderRadius.circular(widget.borderRadius),
          ),
        );
      },
    );
  }
}

/// Lista de N skeletons. Para el estado de carga de una lista.
class SkeletonList extends StatelessWidget {
  const SkeletonList({super.key, this.count = 5, this.itemHeight = 72});

  final int count;
  final double itemHeight;

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: count,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Skeleton(width: 200, height: 18),
            const SizedBox(height: 8),
            Skeleton(height: itemHeight - 34),
          ],
        );
      },
    );
  }
}
```

`pull_to_refresh_wrapper.dart`:

```dart
import 'package:flutter/material.dart';

/// RefreshIndicator con padding consistente.
///
/// Envuelve cualquier `ListView`/`GridView` y aplica el padding y el physics
/// correctos. Sin esto, cada pantalla con pull-to-refresh reinventa los tres
/// parametros, y uno de ellos siempre queda mal.
class PullToRefreshWrapper extends StatelessWidget {
  const PullToRefreshWrapper({
    super.key,
    required this.onRefresh,
    required this.child,
    this.edgeOffset = 0.0,
  });

  final Future<void> Function() onRefresh;
  final Widget child;

  /// Cuanto se desplaza la lista al hacer pull, para que un header quede
  /// visible. 0 = comportamiento normal.
  final double edgeOffset;

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      edgeOffset: edgeOffset,
      child: NotificationListener<ScrollNotification>(
        onNotification: (notification) {
          if (notification is OverscrollNotification) {
            // Overscroll comportamiento de Material antes de 3.10; el
            // parpadeo en iOS. Forzar el de Android.
            notification.overscroll = 0;
          }
          return false;
        },
        child: child,
      ),
    );
  }
}
```

> **VERIFICAR 3.18**

```bash
flutter gen-l10n
flutter analyze
# Debe dar: No issues found!
```

### 3.19 Tests de `core`

`test/core/` espeja `lib/core/`. Mismos nombres de carpeta. Once archivos.

**`test/helpers/fixture_reader.dart`**

```dart
import 'dart:convert';
import 'dart:io';

/// Lee un JSON de `test/fixtures/`.
///
/// Lanza con el nombre del archivo faltante, no con un
/// `FormatException` de `readAsStringSync`. El nombre del archivo es la
/// informacion que te dice que test fallo.
String fixture(String name) {
  final file = File('test/fixtures/$name.json');
  if (!file.existsSync()) {
    throw StateError('Fixture no encontrada: test/fixtures/$name.json');
  }
  return file.readAsStringSync();
}

Map<String, dynamic> fixtureAsMap(String name) {
  final decoded = jsonDecode(fixture(name));
  if (decoded is! Map<String, dynamic>) {
    throw StateError('El fixture $name.json no es un objeto JSON');
  }
  return decoded;
}

List<dynamic> fixtureAsList(String name) {
  final decoded = jsonDecode(fixture(name));
  if (decoded is! List) {
    throw StateError('El fixture $name.json no es una lista JSON');
  }
  return decoded;
}
```

**`test/core/error/failures_test.dart`**

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';

void main() {
  group('Failure', () {
    test('dos failures con el mismo message y code son iguales', () {
      // ARRANGE
      const a = ServerFailure(message: 'error', code: 500);
      const b = ServerFailure(message: 'error', code: 500);

      // ASSERT
      expect(a, equals(b));
    });

    test('cambiar el message las hace distintas', () {
      // ARRANGE
      const a = ServerFailure(message: 'a');
      const b = ServerFailure(message: 'b');

      // ASSERT
      expect(a, isNot(equals(b)));
    });

    test('cada subclase conserva su message por defecto', () {
      // ASSERT
      expect(const ServerFailure().message, 'Something went wrong');
      expect(const NetworkFailure().message, 'No internet connection');
      expect(const CacheFailure().message, 'Cache failure');
      expect(const ValidationFailure().message, 'Validation failure');
    });

    test('los code por defecto son null, no cero', () {
      // ASSERT
      expect(const ServerFailure().code, isNull);
    });
  });

  group('Jerarquia', () {
    test('todas las subclases de Failure son Failure', () {
      // ASSERT
      expect(const ServerFailure(), isA<Failure>());
      expect(const NetworkFailure(), isA<Failure>());
      expect(const CacheFailure(), isA<Failure>());
      expect(const ValidationFailure(), isA<Failure>());
    });
  });
}
```

**`test/core/error/exceptions_test.dart`**

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/exceptions.dart';

void main() {
  group('Exceptions', () {
    test('ServerException lleva statusCode opcional', () {
      // ARRANGE
      const withStatus = ServerException(message: 'boom', statusCode: 500);
      const withoutStatus = ServerException(message: 'boom');

      // ASSERT
      expect(withStatus.statusCode, 500);
      expect(withoutStatus.statusCode, isNull);
    });

    test('todas son Exception', () {
      // ASSERT
      expect(const ServerException(message: 'a'), isA<Exception>());
      expect(const NetworkException(message: 'a'), isA<Exception>());
      expect(const CacheException(message: 'a'), isA<Exception>());
      expect(const ValidationException(message: 'a'), isA<Exception>());
    });

    test('el toString de ServerException incluye el status', () {
      // ASSERT
      expect(
        const ServerException(message: 'boom', statusCode: 503).toString(),
        contains('503'),
      );
    });
  });
}
```

**`test/core/session/current_user_stub_test.dart`** — el test que **verifica que el
nucleo no asume identidad:**

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/session/current_user.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/session/current_user_stub.dart';

void main() {
  group('CurrentUserStub', () {
    const stub = CurrentUserStub();

    test('userId es siempre null', () {
      // ASSERT
      expect(stub.userId, isNull);
    });

    test('isSignedIn es false', () {
      // ASSERT
      expect(stub.isSignedIn, isFalse);
    });

    test('isSignedIn es coherente con userId', () {
      // ASSERT
      // El default de la interfaz dice `userId != null`. Con el stub siempre
      // null, tiene que dar false. Si alguien rompe esa relacion, el router
      // manda a donde no debe.
      expect(stub.isSignedIn, equals(stub.userId != null));
    });

    test('es una implementacion valida de CurrentUser', () {
      // ASSERT
      expect(stub, isA<CurrentUser>());
    });
  });
}
```

**`test/core/common/usecase_test.dart`**

```dart
import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/common/usecase.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';

/// Use case de mentira para probar la abstraccion.
class _GetThings extends UseCase<List<String>, NoParams> {
  @override
  Future<Either<Failure, List<String>>> call(NoParams params) async {
    return const Right(['a', 'b']);
  }
}

class _FailingUseCase extends UseCase<List<String>, NoParams> {
  @override
  Future<Either<Failure, List<String>>> call(NoParams params) async {
    return const Left(ServerFailure(message: 'boom'));
  }
}

void main() {
  group('NoParams', () {
    test('dos NoParams son iguales', () {
      // ASSERT
      expect(const NoParams(), equals(const NoParams()));
    });
  });

  group('UseCase', () {
    test('propaga el Right', () async {
      // ARRANGE
      final useCase = _GetThings();

      // ACT
      final result = await useCase(const NoParams());

      // ASSERT
      expect(result, isA<Right<Failure, List<String>>>());
      expect(result.getOrNull(), ['a', 'b']);
    });

    test('propaga el Left', () async {
      // ARRANGE
      final useCase = _FailingUseCase();

      // ACT
      final result = await useCase(const NoParams());

      // ASSERT
      expect(result, isA<Left<Failure, List<String>>>());
      expect(result.getOrNull(), isNull);
    });
  });
}
```

**`test/core/utils/error_handler_test.dart`** — el test que **fija los strings
crudos del proveedor**, que es la unica defensa contra que cambien en silencio:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/utils/error_handler.dart';

void main() {
  group('ErrorHandler.translate', () {
    test('traduce los mensajes exactos de Supabase', () {
      // ASSERT
      expect(
        ErrorHandler.translate('Invalid login credentials'),
        'Correo o contrasena incorrectos',
      );
      expect(
        ErrorHandler.translate('Email not confirmed'),
        'Tu correo todavia no esta confirmado',
      );
    });

    test('cae en la heuristica cuando el mensaje no coincide exacto', () {
      // ASSERT
      expect(
        ErrorHandler.translate('Request to /api timed out after 30s'),
        contains('tardo'),
      );
    });

    test('nunca devuelve el mensaje crudo', () {
      // ASSERT
      // El motivo de existir del archivo: el texto crudo de un proveedor es un
      // contrato no documentado que puede incluir datos internos. La UI no
      // deberia ver nunca algo que no pase por el mapa.
      const raw = 'connection to server at 10.0.0.5:5432 refused';
      expect(ErrorHandler.translate(raw), isNot(raw));
    });

    test('un mensaje desconocido cae en generico, no en crudo', () {
      // ASSERT
      expect(
        ErrorHandler.translate('xz-9917 unexpected token'),
        'Algo salio mal. Proba de nuevo',
      );
    });
  });

  group('ErrorHandler.forFailure', () {
    test('cada tipo de Failure tiene su mensaje', () {
      // ASSERT
      expect(
        ErrorHandler.forFailure(const NetworkFailure()),
        'Sin conexion a internet. Revisa tu red',
      );
      expect(
        ErrorHandler.forFailure(const CacheFailure()),
        'No pudimos leer los datos guardados',
      );
      expect(
        ErrorHandler.forFailure(const ValidationFailure()),
        'Revisa los datos que cargaste',
      );
    });

    test('ServerFailure se traduce por su message', () {
      // ASSERT
      expect(
        ErrorHandler.forFailure(const ServerFailure(message: 'Email not confirmed')),
        'Tu correo todavia no esta confirmado',
      );
    });
  });
}
```

**`test/core/utils/validators_test.dart`**

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/utils/validators.dart';

void main() {
  group('Validators.required', () {
    test('rechaza null, vacio y solo espacios', () {
      // ASSERT
      expect(Validators.required(null), isNotNull);
      expect(Validators.required(''), isNotNull);
      expect(Validators.required('   '), isNotNull);
    });

    test('acepta texto con contenido', () {
      // ASSERT
      expect(Validators.required('hola'), isNull);
    });
  });

  group('Validators.email', () {
    test('acepta formatos razonable', () {
      // ASSERT
      expect(Validators.email('a@b.co'), isNull);
      expect(Validators.email('nombre.apellido@dominio.com'), isNull);
    });

    test('rechaza formatos imposibles', () {
      // ASSERT
      expect(Validators.email('sin-arroba'), isNotNull);
      expect(Validators.email('a@b'), isNotNull);
      expect(Validators.email('a b@c.com'), isNotNull);
      expect(Validators.email(''), isNotNull);
    });
  });

  group('Validators.compose', () {
    test('devuelve el primer error', () {
      // ASSERT
      final result = Validators.compose([
        () => null,
        () => 'el segundo falla',
        () => 'el tercero tambien',
      ]);
      expect(result, 'el segundo falla');
    });

    test('devuelve null si todos pasan', () {
      // ASSERT
      expect(Validators.compose([() => null, () => null]), isNull);
    });
  });

  group('length', () {
    test('minLength y maxLength respetan el limite', () {
      // ASSERT
      expect(Validators.minLength('ab', 3), isNotNull);
      expect(Validators.minLength('abc', 3), isNull);
      expect(Validators.maxLength('abcd', 3), isNotNull);
      expect(Validators.maxLength('abc', 3), isNull);
    });
  });
}
```

**`test/core/theme/app_theme_test.dart`**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/theme/app_theme.dart';

void main() {
  group('AppTheme', () {
    test('lightTheme y darkTheme usan Material 3', () {
      // ASSERT
      expect(AppTheme.lightTheme.useMaterial3, isTrue);
      expect(AppTheme.darkTheme.useMaterial3, isTrue);
    });

    test('la seed es la misma en los dos temas', () {
      // ASSERT
      // Misma seed garantiza coherencia entre light y dark. Si divergen, un
      // color primario distinto entre modos es una fuente de bug visual.
      expect(
        AppTheme.lightTheme.colorScheme.primary,
        AppTheme.darkTheme.colorScheme.primary,
      );
    });

    test('la brightness de cada tema es la correcta', () {
      // ASSERT
      expect(AppTheme.lightTheme.colorScheme.brightness, Brightness.light);
      expect(AppTheme.darkTheme.colorScheme.brightness, Brightness.dark);
    });

    test('los slots del ColorScheme no colisionan', () {
      // ARRANGE
      final scheme = AppTheme.lightTheme.colorScheme;

      // ASSERT
      // Slots sin definir o iguales entre si : NullCheckError o texto
      // invisible, en la pantalla equivocada. Aca falla al arrancar.
      expect(scheme.primary, isNot(equals(scheme.surface)));
      expect(scheme.error, isNot(equals(scheme.primary)));
      expect(scheme.onSurface, isNotNull);
    });
  });
}
```

**`test/core/widgets/`** -- un test por widget. Todos usan el patron
`pumpWidget` + `find.byType`. Los 7 archivos son cortos; generá el patron con
este ejemplo y replicálo:

```dart
// test/core/widgets/app_button_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/theme/app_theme.dart';
import 'package:{{NOMBRE_PROYECTO}}/core/widgets/app_button.dart';

Widget _wrap(Widget child) => MaterialApp(
      theme: AppTheme.lightTheme,
      home: Scaffold(body: Center(child: child)),
    );

void main() {
  group('AppButton', () {
    testWidgets('muestra el label', (tester) async {
      // ARRANGE
      const button = AppButton(label: 'Guardar');

      // ACT
      await tester.pumpWidget(_wrap(button));

      // ASSERT
      expect(find.text('Guardar'), findsOneWidget);
      expect(find.byType(FilledButton), findsOneWidget);
    });

    testWidgets('onPressed null lo deja deshabilitado', (tester) async {
      // ARRANGE
      const button = AppButton(label: 'Guardar');

      // ACT
      await tester.pumpWidget(_wrap(button));
      final widget = tester.widget<FilledButton>(find.byType(FilledButton));

      // ASSERT
      expect(widget.onPressed, isNull);
    });

    testWidgets('isLoading muestra un indicador, no el label',
        (tester) async {
      // ARRANGE
      const button = AppButton(label: 'Guardar', isLoading: true);

      // ACT
      await tester.pumpWidget(_wrap(button));

      // ASSERT
      expect(find.text('Guardar'), findsNothing);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('onPressed se dispara al tocar', (tester) async {
      // ARRANGE
      var taps = 0;
      await tester.pumpWidget(
        _wrap(AppButton(label: 'Guardar', onPressed: () => taps++)),
      );

      // ACT
      await tester.tap(find.byType(FilledButton));

      // ASSERT
      expect(taps, 1);
    });

    testWidgets('cada variante produce el boton correcto', (tester) async {
      // ARRANGE & ACT
      for (final variant in AppButtonVariant.values) {
        await tester.pumpWidget(
          _wrap(AppButton(label: 'X', variant: variant)),
        );

        // ASSERT
        expect(tester.takeException(), isNull);
      }
    });
  });
}
```

Genera tambien `app_card_test.dart`, `app_text_field_test.dart`,
`empty_state_test.dart`, `error_view_test.dart`, `loading_indicator_test.dart` y
`pull_to_refresh_wrapper_test.dart` con el mismo patron. Para `empty_state` y
`error_view`, inicializá las traducciones en el test:

```dart
// Al principio de esos dos tests, dentro de setUp():
await tester.pumpWidget(
  MaterialApp(
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    supportedLocales: AppLocalizations.supportedLocales,
    home: const Scaffold(body: EmptyState(message: 'Nada por aca')),
  ),
);
```

> **VERIFICAR 3.19**

```bash
flutter analyze
flutter test test/core/
```

---

