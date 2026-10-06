# PROMPT: Generar boilerplate de proyecto Flutter con Clean Architecture + Supabase

> ⚠️ **Prompt legacy — Flutter + Supabase, sin Next.js.**
>
> Para arrancar el stack completo del repo (monorepo `apps/mobile` + `apps/web` +
> `supabase/` en la raíz) usá
> [`PROMPT-BOOTSTRAP-MONOREPO.md`](./PROMPT-BOOTSTRAP-MONOREPO.md), que además
> corrige los errores de este archivo (ver Apéndice C del nuevo).
>
> Este prompt se mantiene como **referencia de estructura Flutter**: la taxonomía
> de carpetas, los tipos de `Failure`, el shape de `UseCase` y los widgets
> genéricos siguen siendo válidos. Para arrancar un proyecto de cero, usá el nuevo.

Eres un asistente experto en Flutter y Clean Architecture. Debes generar un proyecto Flutter completo listo para empezar a desarrollar, siguiendo las fases en orden.

## Variables (reemplázalas al inicio)

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `{{project_name}}` | `my_app` | Nombre del proyecto (snake_case) |
| `{{org}}` | `com.example` | Organización/dominio inverso |
| `{{supabase_url}}` | `http://localhost:54321` | URL de Supabase |
| `{{supabase_anon_key}}` | (placeholder) | Supabase anon/public key |
| `{{flutter_version}}` | `3.29.0` | Versión de Flutter (FVM) |

## Instrucciones generales

- Crea CADA archivo listado. No saltes ninguno.
- Usa `{{variables}}` exactamente como están; serán reemplazadas después.
- No agregues lógica de negocio (no hay dominios de rifa, sorteos, pagos, etc.).
- Sigue la estructura exacta de carpetas.
- Cada `// TODO:` marca código que el desarrollador completará después.

---

## FASE 1: Inicializar proyecto + estructura de carpetas

### 1.1 Ejecuta `flutter create`

```bash
flutter create --org {{org}} --project-name {{project_name}} --platforms android,ios,web .
```

### 1.2 Crea la estructura de carpetas

```bash
# Core layer
mkdir -p lib/core/auth
mkdir -p lib/core/common
mkdir -p lib/core/di
mkdir -p lib/core/error
mkdir -p lib/core/extensions
mkdir -p lib/core/l10n
mkdir -p lib/core/network
mkdir -p lib/core/services
mkdir -p lib/core/theme
mkdir -p lib/core/utils
mkdir -p lib/core/widgets

# Features
mkdir -p lib/features/auth/data/datasources
mkdir -p lib/features/auth/data/models
mkdir -p lib/features/auth/data/repositories
mkdir -p lib/features/auth/domain/entities
mkdir -p lib/features/auth/domain/repositories
mkdir -p lib/features/auth/domain/usecases
mkdir -p lib/features/auth/presentation/cubit
mkdir -p lib/features/auth/presentation/screens
mkdir -p lib/features/auth/presentation/widgets

# Assets
mkdir -p assets/images
mkdir -p assets/fonts
mkdir -p assets/icons

# Env
mkdir -p env

# L10n
mkdir -p lib/l10n

# Test
mkdir -p test/helpers
mkdir -p test/features/auth/data/datasources
mkdir -p test/features/auth/data/repositories
mkdir -p test/features/auth/domain/usecases
mkdir -p test/features/auth/presentation/cubit
mkdir -p test/core/services

# Supabase (local)
mkdir -p supabase/migrations
mkdir -p supabase/functions
mkdir -p supabase/seed
```

### 1.3 Elimina archivos por defecto

```bash
rm -f lib/main.dart test/widget_test.dart
```

### 1.4 Configura `analysis_options.yaml`

```yaml
include: package:very_good_analysis/analysis_options.yaml

linter:
  rules:
    public_member_api_docs: false
    lines_longer_than_80_chars: false
    sort_constructors_first: true
    avoid_print: true
    prefer_single_quotes: true
    require_trailing_commas: false
    always_use_package_imports: true
    avoid_redundant_argument_values: false
    no_default_cases: false

analyzer:
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"
    - "**/*.config.dart"
    - "**/*.mocks.dart"
    - "**/*.gr.dart"
    - build/**
    - lib/l10n/**
    - "**/*.gen.dart"
  errors:
    invalid_annotation_target: ignore
  language:
    strict-casts: true
    strict-inference: true
    strict-raw-types: true
```

### 1.5 Configura `build.yaml`

```yaml
targets:
  $default:
    builders:
      json_serializable:
        options:
          any_map: true
          checked: true
          create_factory: true
          create_to_json: true
          explicit_to_json: true
          include_if_null: false
      freezed:
        options:
          generic_argument_factories: true
          run_build_runner: false
      injectable_generator:
        options:
          auto_register: true
          namespaced: false
```

### 1.6 Configura `l10n.yaml`

```yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
output-class: AppLocalizations
preferred-supported-locales:
  - en
  - es
use-deferred-loading: false
synthetic-package: false
```

### 1.7 Configura `.gitignore`

Agrega al `.gitignore` existente:

```gitignore
# Flutter generated
*.g.dart
*.freezed.dart
*.gr.dart
*.mocks.dart
*.gen.dart
**/*.config.dart

# Environment
.env
.env.local
*.env.local

# FVM
.fvm/flutter_sdk_version

# IDE
.vscode/
.idea/

# macOS
.DS_Store

# Build
build/
*.apk
*.aab
*.jks
*.keystore

# Coverage
coverage/
```

### 1.8 Crea archivo `lib/l10n/app_en.arb`

```json
{
  "@@locale": "en",
  "app_name": "My App",
  "@app_name": {
    "description": "The application name"
  },
  "ok": "OK",
  "cancel": "Cancel",
  "retry": "Retry",
  "error_generic": "Something went wrong",
  "error_network": "No internet connection",
  "error_server": "Server error, please try again later",
  "error_validation": "Please check the entered data",
  "error_auth": "Authentication error",
  "error_unknown": "An unknown error occurred",
  "loading": "Loading...",
  "empty_title": "Nothing here yet",
  "empty_message": "Content will appear here",
  "auth_sign_in": "Sign In",
  "auth_sign_up": "Sign Up",
  "auth_sign_out": "Sign Out",
  "auth_email": "Email",
  "auth_password": "Password",
  "auth_confirm_password": "Confirm password",
  "auth_email_hint": "Enter your email",
  "auth_password_hint": "Enter your password",
  "auth_email_invalid": "Invalid email",
  "auth_password_too_short": "Password must be at least 6 characters",
  "auth_passwords_dont_match": "Passwords don't match"
}
```

### 1.9 Crea archivo `lib/l10n/app_es.arb`

```json
{
  "@@locale": "es",
  "app_name": "Mi App",
  "ok": "Aceptar",
  "cancel": "Cancelar",
  "retry": "Reintentar",
  "error_generic": "Algo salió mal",
  "error_network": "Sin conexión a internet",
  "error_server": "Error del servidor, intenta más tarde",
  "error_validation": "Revisa los datos ingresados",
  "error_auth": "Error de autenticación",
  "error_unknown": "Ocurrió un error inesperado",
  "loading": "Cargando...",
  "empty_title": "Nada aquí aún",
  "empty_message": "El contenido aparecerá aquí",
  "auth_sign_in": "Iniciar sesión",
  "auth_sign_up": "Registrarse",
  "auth_sign_out": "Cerrar sesión",
  "auth_email": "Correo electrónico",
  "auth_password": "Contraseña",
  "auth_confirm_password": "Confirmar contraseña",
  "auth_email_hint": "Ingresa tu correo",
  "auth_password_hint": "Ingresa tu contraseña",
  "auth_email_invalid": "Correo inválido",
  "auth_password_too_short": "La contraseña debe tener al menos 6 caracteres",
  "auth_passwords_dont_match": "Las contraseñas no coinciden"
}
```

---

## FASE 2: `pubspec.yaml`

```yaml
name: {{project_name}}
description: A Flutter project with Clean Architecture + Supabase.
version: 1.0.0+1
publish_to: none

environment:
  sdk: ^3.7.0
  flutter: ^3.29.0

dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  intl: ^0.20.2

  # State Management
  flutter_bloc: ^9.1.0
  bloc: ^9.0.0
  equatable: ^2.0.7

  # Functional Programming
  fpdart: ^1.1.1

  # Dependency Injection
  get_it: ^8.0.3
  injectable: ^2.5.0

  # Routing
  go_router: ^14.8.1

  # Networking
  supabase_flutter: ^2.8.4
  internet_connection_checker_plus: ^2.6.1

  # Local Storage
  isar_community: ^4.0.0
  isar_community_flutter_libs: ^4.0.0

  # Utilities
  package_info_plus: ^8.3.0
  path_provider: ^2.1.5
  url_launcher: ^6.3.1
  flutter_dotenv: ^5.2.1
  shimmer: ^3.0.0

  # Serialization
  json_annotation: ^4.9.0
  freezed_annotation: ^2.4.4

dev_dependencies:
  flutter_test:
    sdk: flutter
  bloc_test: ^10.0.0
  mocktail: ^1.0.4
  very_good_analysis: ^7.0.0

  # Code Generation
  build_runner: ^2.4.15
  json_serializable: ^6.9.4
  freezed: ^2.5.8
  injectable_generator: ^2.7.0
  isar_community_generator: ^4.0.0

flutter:
  uses-material-design: true

  generate: true

  assets:
    - assets/images/
    - assets/fonts/
    - .env
    - .env.example
```

---

## FASE 3: Core Layer

### 3.1 `lib/core/error/failures.dart`

```dart
import 'package:equatable/equatable.dart';

abstract class Failure extends Equatable {
  final String message;
  final int? statusCode;

  const Failure({required this.message, this.statusCode});

  @override
  List<Object?> get props => [message, statusCode];
}

class ServerFailure extends Failure {
  const ServerFailure({super.message = 'Server failure', super.statusCode});
}

class NetworkFailure extends Failure {
  const NetworkFailure({super.message = 'No internet connection'});
}

class CacheFailure extends Failure {
  const CacheFailure({super.message = 'Cache failure'});
}

class ValidationFailure extends Failure {
  final Map<String, String>? errors;

  const ValidationFailure({
    super.message = 'Validation failed',
    this.errors,
  });

  @override
  List<Object?> get props => [message, errors];
}

class AuthFailure extends Failure {
  const AuthFailure({super.message = 'Authentication failed', super.statusCode});
}
```

### 3.2 `lib/core/error/exceptions.dart`

```dart
class ServerException implements Exception {
  final String message;
  final int? statusCode;

  const ServerException({required this.message, this.statusCode});

  @override
  String toString() => 'ServerException: $message (status: $statusCode)';
}

class NetworkException implements Exception {
  final String message;
  const NetworkException({this.message = 'No internet connection'});
}

class CacheException implements Exception {
  final String message;
  const CacheException({this.message = 'Cache error'});
}

class AuthException implements Exception {
  final String message;
  final int? statusCode;

  const AuthException({required this.message, this.statusCode});

  @override
  String toString() => 'AuthException: $message (status: $statusCode)';
}
```

### 3.3 `lib/core/common/usecase.dart`

```dart
import 'package:fpdart/src/either.dart';
import '../error/failures.dart';

abstract class UseCase<SuccessType, Params> {
  Future<Either<Failure, SuccessType>> call(Params params);
}

class NoParams {
  const NoParams();
}
```

### 3.4 `lib/core/network/network_info.dart`

```dart
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart';

abstract class NetworkInfo {
  Future<bool> get isConnected;
  Stream<bool> get onConnectivityChanged;
}

class NetworkInfoImpl implements NetworkInfo {
  final InternetConnection _connectionChecker;

  NetworkInfoImpl(this._connectionChecker);

  @override
  Future<bool> get isConnected => _connectionChecker.hasInternetAccess;

  @override
  Stream<bool> get onConnectivityChanged =>
      _connectionChecker.onStatusChange.map(
        (status) => status == InternetStatus.connected,
      );
}
```

### 3.5 `lib/core/session/user_session.dart`

```dart
abstract class UserSession {
  /// Returns the current authenticated user's ID, or null if not authenticated.
  String? get userId;

  /// Synchronous — reads from local cache without await.
  bool get isAuthenticated;
}
```

### 3.6 `lib/core/session/user_session_impl.dart`

```dart
import 'package:isar_community/isar.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'user_session.dart';
// Importar el esquema Isar de CachedUser
// import '../data/local/isar_models/cached_user.dart';

class UserSessionImpl implements UserSession {
  final Isar _isar;
  final SupabaseClient? _supabase;

  UserSessionImpl(this._isar, {SupabaseClient? supabase})
      : _supabase = supabase;

  @override
  String? get userId {
    final cached = _isar.cachedUsers.where().findFirstSync();
    return cached?.userId;
  }

  @override
  bool get isAuthenticated {
    return _isar.cachedUsers.where().countSync() > 0;
  }
}
```

### 3.7 `lib/core/di/service_locator.dart`

```dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';
import 'service_locator.config.dart';

final serviceLocator = GetIt.instance;

@InjectableInit(
  initializerName: r'$initGetIt',
  preferRelativeImports: true,
  asExtension: false,
)
Future<void> configureDependencies() async {
  await $initGetIt(serviceLocator);
}
```

<-- Opción manual (sin injectable):
    Crea `lib/core/di/injection_container.dart` y registra manualmente
    cada dependencia usando cascade notation (`..registerLazySingleton`).
    Ver `01-CLEAN-ARCHITECTURE/06-inyeccion-de-dependencias.md` para el ejemplo completo.
-->

### 3.8 `lib/core/services/cache_manager.dart`

```dart
class CacheManager {
  final List<Future<void> Function()> _clearFns = [];

  void register(Future<void> Function() clearFn) {
    _clearFns.add(clearFn);
  }

  Future<void> clearAll() async {
    await Future.wait(_clearFns.map((fn) => fn()));
  }
}
```

### 3.10 `lib/core/l10n/l10n.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

extension AppLocalizationsX on BuildContext {
  AppLocalizations get l10n => AppLocalizations.of(this)!;
}
```

### 3.11 `lib/core/theme/app_colors.dart`

```dart
import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // Primary palette
  static const Color primary = Color(0xFF6750A4);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color primaryContainer = Color(0xFFEADDFF);
  static const Color onPrimaryContainer = Color(0xFF21005D);

  // Secondary palette
  static const Color secondary = Color(0xFF625B71);
  static const Color onSecondary = Color(0xFFFFFFFF);
  static const Color secondaryContainer = Color(0xFFE8DEF8);
  static const Color onSecondaryContainer = Color(0xFF1D192B);

  // Surface & Background
  static const Color surface = Color(0xFFFFFBFE);
  static const Color onSurface = Color(0xFF1C1B1F);
  static const Color surfaceVariant = Color(0xFFE7E0EC);
  static const Color onSurfaceVariant = Color(0xFF49454F);

  // Error
  static const Color error = Color(0xFFB3261E);
  static const Color onError = Color(0xFFFFFFFF);
  static const Color errorContainer = Color(0xFFF9DEDC);
  static const Color onErrorContainer = Color(0xFF410E0B);

  // Semantic
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFFC107);
  static const Color info = Color(0xFF2196F3);
}
```

### 3.12 `lib/core/theme/app_theme.dart`

```dart
import 'package:flutter/material.dart';
import 'app_colors.dart';

class AppTheme {
  AppTheme._();

  static ThemeData get light => ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        colorScheme: ColorScheme.light(
          primary: AppColors.primary,
          onPrimary: AppColors.onPrimary,
          primaryContainer: AppColors.primaryContainer,
          onPrimaryContainer: AppColors.onPrimaryContainer,
          secondary: AppColors.secondary,
          onSecondary: AppColors.onSecondary,
          secondaryContainer: AppColors.secondaryContainer,
          onSecondaryContainer: AppColors.onSecondaryContainer,
          surface: AppColors.surface,
          onSurface: AppColors.onSurface,
          surfaceContainerHighest: AppColors.surfaceVariant,
          onSurfaceVariant: AppColors.onSurfaceVariant,
          error: AppColors.error,
          onError: AppColors.onError,
          errorContainer: AppColors.errorContainer,
          onErrorContainer: AppColors.onErrorContainer,
        ),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            minimumSize: const Size(double.infinity, 48),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      );

  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.dark(
          primary: AppColors.primaryContainer,
          onPrimary: AppColors.onPrimaryContainer,
          secondary: AppColors.secondaryContainer,
          onSecondary: AppColors.onSecondaryContainer,
          surface: const Color(0xFF1C1B1F),
          onSurface: const Color(0xFFE6E1E5),
          error: AppColors.errorContainer,
          onError: AppColors.onErrorContainer,
        ),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            minimumSize: const Size(double.infinity, 48),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      );
}
```

### 3.13 `lib/core/theme/app_spacing.dart`

```dart
class AppSpacing {
  AppSpacing._();

  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;

  static const double radiusSm = 8;
  static const double radiusMd = 12;
  static const double radiusLg = 16;
  static const double radiusXl = 24;
}
```

### 3.14 `lib/core/utils/extensions.dart`

```dart
import 'package:flutter/material.dart';

extension BuildContextX on BuildContext {
  ThemeData get theme => Theme.of(this);
  TextTheme get textTheme => theme.textTheme;
  ColorScheme get colorScheme => theme.colorScheme;
  MediaQueryData get mediaQuery => MediaQuery.of(this);
  Size get screenSize => mediaQuery.size;
  double get screenWidth => screenSize.width;
  double get screenHeight => screenSize.height;
}
```

### 3.15 `lib/core/utils/snackbar_helper.dart`

```dart
import 'package:flutter/material.dart';

enum SnackBarType { success, error, info, warning }

class SnackBarHelper {
  static void show(
    BuildContext context, {
    required String message,
    SnackBarType type = SnackBarType.info,
    Duration duration = const Duration(seconds: 3),
  }) {
    final colors = {
      SnackBarType.success: context.colorScheme.primary,
      SnackBarType.error: context.colorScheme.error,
      SnackBarType.info: context.colorScheme.secondary,
      SnackBarType.warning: AppColors.warning,
    };

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: colors[type],
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        duration: duration,
      ),
    );
  }
}
```

### 3.16 `lib/core/utils/constants.dart`

```dart
class AppConstants {
  AppConstants._();

  static const String appName = '{{project_name}}';
  static const Duration defaultTimeout = Duration(seconds: 30);
  static const int cacheExpirationHours = 24;
}
```

### 3.17 `env/.env.example`

```env
SUPABASE_URL={{supabase_url}}
SUPABASE_ANON_KEY={{supabase_anon_key}}
```

---

## FASE 4: Feature Template (Auth)

### 4.1 `lib/features/auth/domain/entities/user.dart`

```dart
import 'package:equatable/equatable.dart';

class User extends Equatable {
  final String id;
  final String email;
  final String? displayName;
  final String? photoUrl;
  final DateTime createdAt;

  const User({
    required this.id,
    required this.email,
    this.displayName,
    this.photoUrl,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [id, email, displayName, photoUrl, createdAt];
}
```

### 4.2 `lib/features/auth/domain/repositories/auth_repository.dart`

```dart
import 'package:fpdart/src/either.dart';
import '../../../../core/error/failures.dart';
import '../entities/user.dart';

abstract class AuthRepository {
  Future<Either<Failure, User>> signInWithEmailAndPassword({
    required String email,
    required String password,
  });

  Future<Either<Failure, User>> signUp({
    required String email,
    required String password,
  });

  Future<Either<Failure, void>> signOut();

  Future<Either<Failure, User?>> getCurrentUser();

  Stream<User?> get authStateChanges;
}
```

### 4.3 `lib/features/auth/domain/usecases/sign_in.dart`

```dart
import 'package:fpdart/src/either.dart';
import '../../../../core/common/usecase.dart';
import '../../../../core/error/failures.dart';
import '../entities/user.dart';
import '../repositories/auth_repository.dart';

class SignIn implements UseCase<User, SignInParams> {
  final AuthRepository _repository;

  SignIn(this._repository);

  @override
  Future<Either<Failure, User>> call(SignInParams params) {
    return _repository.signInWithEmailAndPassword(
      email: params.email,
      password: params.password,
    );
  }
}

class SignInParams {
  final String email;
  final String password;

  const SignInParams({required this.email, required this.password});
}
```

### 4.4 `lib/features/auth/domain/usecases/sign_up.dart`

```dart
import 'package:fpdart/src/either.dart';
import '../../../../core/common/usecase.dart';
import '../../../../core/error/failures.dart';
import '../entities/user.dart';
import '../repositories/auth_repository.dart';

class SignUp implements UseCase<User, SignUpParams> {
  final AuthRepository _repository;

  SignUp(this._repository);

  @override
  Future<Either<Failure, User>> call(SignUpParams params) {
    return _repository.signUp(
      email: params.email,
      password: params.password,
    );
  }
}

class SignUpParams {
  final String email;
  final String password;

  const SignUpParams({required this.email, required this.password});
}
```

### 4.5 `lib/features/auth/domain/usecases/sign_out.dart`

```dart
import 'package:fpdart/src/either.dart';
import '../../../../core/common/usecase.dart';
import '../../../../core/error/failures.dart';
import '../repositories/auth_repository.dart';

class SignOut implements UseCase<void, NoParams> {
  final AuthRepository _repository;

  SignOut(this._repository);

  @override
  Future<Either<Failure, void>> call(NoParams params) {
    return _repository.signOut();
  }
}
```

### 4.6 `lib/features/auth/data/models/user_model.dart`

```dart
import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';
import '../../domain/entities/user.dart';

part 'user_model.g.dart';

@JsonSerializable()
class UserModel extends Equatable {
  final String id;
  final String email;
  @JsonKey(name: 'display_name')
  final String? displayName;
  @JsonKey(name: 'photo_url')
  final String? photoUrl;
  @JsonKey(name: 'created_at')
  final DateTime createdAt;

  const UserModel({
    required this.id,
    required this.email,
    this.displayName,
    this.photoUrl,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) =>
      _$UserModelFromJson(json);

  Map<String, dynamic> toJson() => _$UserModelToJson(this);

  User toEntity() => User(
        id: id,
        email: email,
        displayName: displayName,
        photoUrl: photoUrl,
        createdAt: createdAt,
      );

  factory UserModel.fromEntity(User entity) => UserModel(
        id: entity.id,
        email: entity.email,
        displayName: entity.displayName,
        photoUrl: entity.photoUrl,
        createdAt: entity.createdAt,
      );

  @override
  List<Object?> get props => [id, email, displayName, photoUrl, createdAt];
}
```

### 4.7 `lib/features/auth/data/datasources/auth_remote_data_source.dart`

```dart
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../../core/error/exceptions.dart';
import '../models/user_model.dart';

abstract class AuthRemoteDataSource {
  Future<UserModel> signInWithEmailAndPassword({
    required String email,
    required String password,
  });

  Future<UserModel> signUp({
    required String email,
    required String password,
  });

  Future<void> signOut();

  Future<UserModel?> getCurrentUser();

  Stream<UserModel?> get authStateChanges;
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final SupabaseClient _supabase;

  AuthRemoteDataSourceImpl(this._supabase);

  @override
  Future<UserModel> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _supabase.auth.signInWithPassword(
        email: email,
        password: password,
      );
      final user = response.user;
      if (user == null) {
        throw const AuthException(message: 'User not found');
      }
      return UserModel(
        id: user.id,
        email: user.email ?? email,
        displayName: user.userMetadata?['display_name'] as String?,
        photoUrl: user.userMetadata?['photo_url'] as String?,
        createdAt: user.createdAt,
      );
    } on AuthException {
      rethrow;
    } catch (e) {
      throw AuthException(message: e.toString());
    }
  }

  @override
  Future<UserModel> signUp({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _supabase.auth.signUp(
        email: email,
        password: password,
      );
      final user = response.user;
      if (user == null) {
        throw const AuthException(message: 'Sign up failed');
      }
      return UserModel(
        id: user.id,
        email: user.email ?? email,
        displayName: user.userMetadata?['display_name'] as String?,
        photoUrl: user.userMetadata?['photo_url'] as String?,
        createdAt: user.createdAt,
      );
    } on AuthException {
      rethrow;
    } catch (e) {
      throw AuthException(message: e.toString());
    }
  }

  @override
  Future<void> signOut() async {
    try {
      await _supabase.auth.signOut();
    } catch (e) {
      throw AuthException(message: e.toString());
    }
  }

  @override
  Future<UserModel?> getCurrentUser() async {
    final session = _supabase.auth.currentSession;
    final user = session?.user;
    if (user == null) return null;
    return UserModel(
      id: user.id,
      email: user.email ?? '',
      displayName: user.userMetadata?['display_name'] as String?,
      photoUrl: user.userMetadata?['photo_url'] as String?,
      createdAt: user.createdAt,
    );
  }

  @override
  Stream<UserModel?> get authStateChanges {
    return _supabase.auth.onAuthStateChange.map((authState) {
      final user = authState.session?.user;
      if (user == null) return null;
      return UserModel(
        id: user.id,
        email: user.email ?? '',
        displayName: user.userMetadata?['display_name'] as String?,
        photoUrl: user.userMetadata?['photo_url'] as String?,
        createdAt: user.createdAt,
      );
    });
  }
}
```

### 4.8 `lib/features/auth/data/repositories/auth_repository_impl.dart`

```dart
import 'package:fpdart/src/either.dart';
import '../../../../core/error/exceptions.dart';
import '../../../../core/error/failures.dart';
import '../../../../core/services/cache_manager.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_local_data_source.dart';
import '../datasources/auth_remote_data_source.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final AuthLocalDataSource _localDataSource;
  final CacheManager _cacheManager;

  AuthRepositoryImpl(
    this._remoteDataSource,
    this._localDataSource,
    this._cacheManager,
  );

  @override
  bool get isLoggedIn => _localDataSource.hasCachedUser;

  @override
  Future<Either<Failure, User>> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    try {
      final userModel = await _remoteDataSource.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
      await _localDataSource.cacheUser(userModel);
      return Right(userModel.toEntity());
    } on AuthException catch (e) {
      return Left(AuthFailure(message: e.message, statusCode: e.statusCode));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, User>> signUp({
    required String email,
    required String password,
  }) async {
    try {
      final userModel = await _remoteDataSource.signUp(
        email: email,
        password: password,
      );
      await _localDataSource.cacheUser(userModel);
      return Right(userModel.toEntity());
    } on AuthException catch (e) {
      return Left(AuthFailure(message: e.message, statusCode: e.statusCode));
    } on ServerException catch (e) {
      return Left(ServerFailure(message: e.message, statusCode: e.statusCode));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, void>> signOut() async {
    try {
      await _cacheManager.clearAll();
      await _remoteDataSource.signOut();
      return const Right(null);
    } on AuthException catch (e) {
      return Left(AuthFailure(message: e.message, statusCode: e.statusCode));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, User?>> getCurrentUser() async {
    try {
      final userModel = await _remoteDataSource.getCurrentUser();
      if (userModel != null) {
        await _localDataSource.cacheUser(userModel);
      }
      return Right(userModel?.toEntity());
    } on AuthException catch (e) {
      return Left(AuthFailure(message: e.message, statusCode: e.statusCode));
    } catch (e) {
      return Left(ServerFailure(message: e.toString()));
    }
  }

  @override
  Future<Either<Failure, UserModel?>> getCachedUser() async {
    try {
      final user = await _localDataSource.getCachedUser();
      if (user != null) return Right(user);
      return Left(CacheFailure(message: 'No cached user'));
    } on CacheException catch (e) {
      return Left(CacheFailure(message: e.message));
    }
  }

  @override
  Stream<User?> get authStateChanges {
    return _remoteDataSource.authStateChanges.map(
      (userModel) => userModel?.toEntity(),
    );
  }
}
```

Also update the `auth_repository.dart` interface (4.2) to include `getCachedUser` and `isLoggedIn`:

```dart
// lib/features/auth/domain/repositories/auth_repository.dart
import 'package:fpdart/src/either.dart';
import '../../../../core/error/failures.dart';
import '../entities/user.dart';

abstract class AuthRepository {
  bool get isLoggedIn;  // Síncrono

  Future<Either<Failure, User>> signInWithEmailAndPassword({
    required String email,
    required String password,
  });

  Future<Either<Failure, User>> signUp({
    required String email,
    required String password,
  });

  Future<Either<Failure, void>> signOut();

  Future<Either<Failure, User?>> getCurrentUser();

  Future<Either<Failure, UserModel?>> getCachedUser();

  Stream<User?> get authStateChanges;
}
```

### 4.9 `lib/features/auth/presentation/cubit/auth_state.dart`

```dart
import 'package:equatable/equatable.dart';
import '../../../auth/domain/entities/user.dart';

sealed class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object?> get props => [];
}

final class AuthInitial extends AuthState {
  const AuthInitial();
}

final class AuthLoading extends AuthState {
  const AuthLoading();
}

final class Authenticated extends AuthState {
  final User user;

  const Authenticated(this.user);

  @override
  List<Object?> get props => [user];
}

final class Unauthenticated extends AuthState {
  const Unauthenticated();
}

final class AuthError extends AuthState {
  final String message;

  const AuthError(this.message);

  @override
  List<Object?> get props => [message];
}
```

### 4.10 `lib/features/auth/presentation/cubit/auth_cubit.dart`

```dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../../../core/common/usecase.dart';
import '../../domain/usecases/sign_in.dart';
import '../../domain/usecases/sign_up.dart';
import '../../domain/usecases/sign_out.dart';
import '../../domain/repositories/auth_repository.dart';
import 'auth_state.dart';

class AuthCubit extends Cubit<AuthState> {
  final SignIn _signIn;
  final SignUp _signUp;
  final SignOut _signOut;
  final AuthRepository _authRepository;

  AuthCubit({
    required SignIn signIn,
    required SignUp signUp,
    required SignOut signOut,
    required AuthRepository authRepository,
  })  : _signIn = signIn,
        _signUp = signUp,
        _signOut = signOut,
        _authRepository = authRepository,
        super(const AuthInitial());

  Future<void> checkAuthStatus() async {
    emit(const AuthLoading());
    final result = await _authRepository.getCurrentUser();
    result.fold(
      (failure) => emit(const Unauthenticated()),
      (user) {
        if (user != null) {
          emit(Authenticated(user));
        } else {
          emit(const Unauthenticated());
        }
      },
    );
  }

  Future<void> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    emit(const AuthLoading());
    final result = await _signIn(
      SignInParams(email: email, password: password),
    );
    result.fold(
      (failure) => emit(AuthError(failure.message)),
      (user) => emit(Authenticated(user)),
    );
  }

  Future<void> signUp({
    required String email,
    required String password,
  }) async {
    emit(const AuthLoading());
    final result = await _signUp(
      SignUpParams(email: email, password: password),
    );
    result.fold(
      (failure) => emit(AuthError(failure.message)),
      (user) => emit(Authenticated(user)),
    );
  }

  Future<void> signOut() async {
    emit(const AuthLoading());
    final result = await _signOut(const NoParams());
    result.fold(
      (failure) => emit(AuthError(failure.message)),
      (_) => emit(const Unauthenticated()),
    );
  }
}
```

### 4.11 `lib/features/auth/presentation/screens/auth_screen.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/l10n/l10n.dart';
import '../../../../core/utils/snackbar_helper.dart';
import '../../../../core/widgets/app_button.dart';
import '../../../../core/widgets/app_text_field.dart';
import '../cubit/auth_cubit.dart';
import '../cubit/auth_state.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLogin = true;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;

    if (_isLogin) {
      context.read<AuthCubit>().signInWithEmailAndPassword(
            email: _emailController.text.trim(),
            password: _passwordController.text,
          );
    } else {
      context.read<AuthCubit>().signUp(
            email: _emailController.text.trim(),
            password: _passwordController.text,
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;

    return Scaffold(
      appBar: AppBar(
        title: Text(_isLogin ? l10n.auth_sign_in : l10n.auth_sign_up),
      ),
      body: BlocListener<AuthCubit, AuthState>(
        listener: (context, state) {
          if (state is Authenticated) {
            context.go('/home');
          } else if (state is AuthError) {
            SnackBarHelper.show(context, message: state.message, type: SnackBarType.error);
          }
        },
        child: BlocBuilder<AuthCubit, AuthState>(
          builder: (context, state) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 48),
                    AppTextField(
                      controller: _emailController,
                      label: l10n.auth_email,
                      hint: l10n.auth_email_hint,
                      keyboardType: TextInputType.emailAddress,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return l10n.auth_email_hint;
                        }
                        if (!value.contains('@')) {
                          return l10n.auth_email_invalid;
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    AppTextField(
                      controller: _passwordController,
                      label: l10n.auth_password,
                      hint: l10n.auth_password_hint,
                      obscureText: _obscurePassword,
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscurePassword
                              ? Icons.visibility_off
                              : Icons.visibility,
                        ),
                        onPressed: () => setState(
                          () => _obscurePassword = !_obscurePassword,
                        ),
                      ),
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return l10n.auth_password_hint;
                        }
                        if (value.length < 6) {
                          return l10n.auth_password_too_short;
                        }
                        return null;
                      },
                    ),
                    if (!_isLogin) ...[
                      const SizedBox(height: 16),
                      AppTextField(
                        controller: _confirmPasswordController,
                        label: l10n.auth_confirm_password,
                        obscureText: true,
                        validator: (value) {
                          if (value != _passwordController.text) {
                            return l10n.auth_passwords_dont_match;
                          }
                          return null;
                        },
                      ),
                    ],
                    const SizedBox(height: 24),
                    AppButton(
                      onPressed: state is AuthLoading ? null : _submit,
                      isLoading: state is AuthLoading,
                      label: _isLogin
                          ? l10n.auth_sign_in
                          : l10n.auth_sign_up,
                    ),
                    const SizedBox(height: 16),
                    TextButton(
                      onPressed: () => setState(() => _isLogin = !_isLogin),
                      child: Text(
                        _isLogin
                            ? l10n.auth_sign_up
                            : l10n.auth_sign_in,
                      ),
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
}
```

---

## FASE 5: Widgets Genéricos

### 5.1 `lib/core/widgets/app_button.dart`

```dart
import 'package:flutter/material.dart';
import '../theme/app_spacing.dart';

enum AppButtonStyle { primary, secondary, outline, text, danger }

class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final bool isLoading;
  final bool fullWidth;
  final AppButtonStyle buttonStyle;
  final IconData? icon;

  const AppButton({
    super.key,
    required this.label,
    required this.onPressed,
    this.isLoading = false,
    this.fullWidth = true,
    this.buttonStyle = AppButtonStyle.primary,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final child = _buildChild(context);

    if (!fullWidth) return child;

    return SizedBox(width: double.infinity, child: child);
  }

  Widget _buildChild(BuildContext context) {
    final theme = Theme.of(context);

    switch (buttonStyle) {
      case AppButtonStyle.primary:
        return ElevatedButton(
          onPressed: onPressed,
          child: _content,
        );
      case AppButtonStyle.secondary:
        return ElevatedButton(
          onPressed: onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.secondaryContainer,
            foregroundColor: theme.colorScheme.onSecondaryContainer,
          ),
          child: _content,
        );
      case AppButtonStyle.outline:
        return OutlinedButton(
          onPressed: onPressed,
          child: _content,
        );
      case AppButtonStyle.text:
        return TextButton(
          onPressed: onPressed,
          child: _content,
        );
      case AppButtonStyle.danger:
        return ElevatedButton(
          onPressed: onPressed,
          style: ElevatedButton.styleFrom(
            backgroundColor: theme.colorScheme.error,
            foregroundColor: theme.colorScheme.onError,
          ),
          child: _content,
        );
    }
  }

  Widget get _content {
    if (isLoading) {
      return const SizedBox(
        height: 20,
        width: 20,
        child: CircularProgressIndicator(strokeWidth: 2),
      );
    }

    if (icon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 20),
          const SizedBox(width: AppSpacing.sm),
          Text(label),
        ],
      );
    }

    return Text(label);
  }
}
```

### 5.2 `lib/core/widgets/app_text_field.dart`

```dart
import 'package:flutter/material.dart';
import '../theme/app_spacing.dart';

class AppTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String? hint;
  final String? Function(String?)? validator;
  final TextInputType? keyboardType;
  final bool obscureText;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final int? maxLines;

  const AppTextField({
    super.key,
    required this.controller,
    required this.label,
    this.hint,
    this.validator,
    this.keyboardType,
    this.obscureText = false,
    this.prefixIcon,
    this.suffixIcon,
    this.maxLines = 1,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      validator: validator,
      keyboardType: keyboardType,
      obscureText: obscureText,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        prefixIcon: prefixIcon,
        suffixIcon: suffixIcon,
      ),
    );
  }
}
```

### 5.3 `lib/core/widgets/loading_indicator.dart`

```dart
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

enum LoadingStyle { spinner, shimmer, dots }

class LoadingIndicator extends StatelessWidget {
  final LoadingStyle style;
  final String? message;
  final double size;

  const LoadingIndicator({
    super.key,
    this.style = LoadingStyle.spinner,
    this.message,
    this.size = 40,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildIndicator(),
          if (message != null) ...[
            const SizedBox(height: 16),
            Text(
              message!,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildIndicator() {
    switch (style) {
      case LoadingStyle.spinner:
        return SizedBox(
          height: size,
          width: size,
          child: const CircularProgressIndicator(),
        );
      case LoadingStyle.shimmer:
        // Shimmer placeholder - requires shimmer package
        return Container(
          height: size,
          width: size,
          decoration: BoxDecoration(
            color: Colors.grey[300],
            borderRadius: BorderRadius.circular(8),
          ),
        );
      case LoadingStyle.dots:
        return const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            _Dot(delay: Duration.zero),
            _Dot(delay: Duration(milliseconds: 200)),
            _Dot(delay: Duration(milliseconds: 400)),
          ],
        );
    }
  }
}

class _Dot extends StatefulWidget {
  final Duration delay;
  const _Dot({required this.delay});

  @override
  State<_Dot> createState() => _DotState();
}

class _DotState extends State<_Dot> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _animation = Tween<double>(begin: 0.3, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    Future.delayed(widget.delay, () => _controller.repeat(reverse: true));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) => Opacity(
        opacity: _animation.value,
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 4),
          width: 12,
          height: 12,
          decoration: const BoxDecoration(
            color: AppColors.primary,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}
```

### 5.4 `lib/core/widgets/error_view.dart`

```dart
import 'package:flutter/material.dart';
import '../l10n/l10n.dart';
import '../theme/app_spacing.dart';
import 'app_button.dart';

class ErrorView extends StatelessWidget {
  final String? title;
  final String message;
  final IconData icon;
  final VoidCallback? onRetry;

  const ErrorView({
    super.key,
    this.title,
    required this.message,
    this.icon = Icons.error_outline,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 64, color: Theme.of(context).colorScheme.error),
            const SizedBox(height: AppSpacing.md),
            if (title != null) ...[
              Text(
                title!,
                style: Theme.of(context).textTheme.titleLarge,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: AppSpacing.sm),
            ],
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: AppSpacing.lg),
              AppButton(
                label: context.l10n.retry,
                onPressed: onRetry,
                buttonStyle: AppButtonStyle.outline,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

### 5.5 `lib/core/widgets/empty_state.dart`

```dart
import 'package:flutter/material.dart';
import '../l10n/l10n.dart';
import '../theme/app_spacing.dart';
import 'app_button.dart';

class EmptyState extends StatelessWidget {
  final String? title;
  final String? message;
  final IconData icon;
  final String? actionLabel;
  final VoidCallback? onAction;

  const EmptyState({
    super.key,
    this.title,
    this.message,
    this.icon = Icons.inbox_outlined,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.lg),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 64,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
            const SizedBox(height: AppSpacing.md),
            Text(
              title ?? context.l10n.empty_title,
              style: Theme.of(context).textTheme.titleLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.sm),
            Text(
              message ?? context.l10n.empty_message,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: AppSpacing.lg),
              AppButton(
                label: actionLabel!,
                onPressed: onAction,
              ),
            ],
          ],
        ),
      ),
    );
  }
}
```

### 5.6 `lib/core/widgets/app_card.dart`

```dart
import 'package:flutter/material.dart';
import '../theme/app_spacing.dart';

enum CardStyle { elevated, outlined, flat }

class AppCard extends StatelessWidget {
  final Widget child;
  final CardStyle style;
  final EdgeInsetsGeometry padding;
  final double? height;
  final VoidCallback? onTap;

  const AppCard({
    super.key,
    required this.child,
    this.style = CardStyle.elevated,
    this.padding = const EdgeInsets.all(AppSpacing.md),
    this.height,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final card = _buildCard();
    if (onTap != null) {
      return InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
        child: card,
      );
    }
    return card;
  }

  Widget _buildCard() {
    switch (style) {
      case CardStyle.elevated:
        return Card(
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          ),
          child: _buildContent(),
        );
      case CardStyle.outlined:
        return Card(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
            side: BorderSide(color: Colors.grey[300]!),
          ),
          child: _buildContent(),
        );
      case CardStyle.flat:
        return Material(
          borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
          child: _buildContent(),
        );
    }
  }

  Widget _buildContent() {
    return SizedBox(
      height: height,
      child: Padding(padding: padding, child: child),
    );
  }
}
```

### 5.7 `lib/core/widgets/pull_to_refresh_wrapper.dart`

```dart
import 'package:flutter/material.dart';

class PullToRefreshWrapper extends StatelessWidget {
  final Widget child;
  final Future<void> Function() onRefresh;
  final bool isRefreshing;

  const PullToRefreshWrapper({
    super.key,
    required this.child,
    required this.onRefresh,
    this.isRefreshing = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isRefreshing) {
      return Stack(
        children: [
          child,
          const Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: LinearProgressIndicator(),
          ),
        ],
      );
    }

    return RefreshIndicator(
      onRefresh: onRefresh,
      child: child,
    );
  }
}
```

### 5.8 `lib/core/widgets/decorated_background.dart`

```dart
import 'dart:math';
import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

class DecoratedBackground extends StatelessWidget {
  final Widget child;
  final List<Color>? gradientColors;

  const DecoratedBackground({
    super.key,
    required this.child,
    this.gradientColors,
  });

  @override
  Widget build(BuildContext context) {
    final colors = gradientColors ?? [
      AppColors.primaryContainer,
      AppColors.surface,
    ];

    return Stack(
      children: [
        Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: colors,
            ),
          ),
        ),
        Positioned(
          top: -100,
          right: -100,
          child: _DecorativeCircle(
            radius: 200,
            color: colors.first.withValues(alpha: 0.1),
          ),
        ),
        Positioned(
          bottom: -80,
          left: -80,
          child: _DecorativeCircle(
            radius: 160,
            color: colors.last.withValues(alpha: 0.1),
          ),
        ),
        SafeArea(child: child),
      ],
    );
  }
}

class _DecorativeCircle extends StatelessWidget {
  final double radius;
  final Color color;

  const _DecorativeCircle({required this.radius, required this.color});

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: pi / 4,
      child: Container(
        width: radius * 2,
        height: radius * 2,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: color,
        ),
      ),
    );
  }
}
```

### 5.9 `lib/core/widgets/auth_logo.dart`

```dart
import 'package:flutter/material.dart';

class AuthLogo extends StatelessWidget {
  final String appName;
  final double size;

  const AuthLogo({
    super.key,
    required this.appName,
    this.size = 80,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primary,
            borderRadius: BorderRadius.circular(size * 0.25),
          ),
          child: Icon(
            Icons.app_registration,
            size: size * 0.5,
            color: Theme.of(context).colorScheme.onPrimary,
          ),
        ),
        const SizedBox(height: 24),
        Text(
          appName,
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
      ],
    );
  }
}
```

---

## FASE 6: Testing

### 6.1 `test/helpers/fixture_reader.dart`

```dart
import 'dart:convert';
import 'dart:io';

Map<String, dynamic> readFixture(String name) {
  final file = File('test/fixtures/$name');
  return jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;
}

List<dynamic> readFixtureList(String name) {
  final file = File('test/fixtures/$name');
  return jsonDecode(file.readAsStringSync()) as List<dynamic>;
}

String readFixtureRaw(String name) {
  final file = File('test/fixtures/$name');
  return file.readAsStringSync();
}
```

### 6.2 `test/helpers/mock_classes.dart`

```dart
// Template for creating mock classes with mocktail
// Usage: extend or create instances as needed in your tests.

// import 'package:mocktail/mocktail.dart';
//
// class MockAuthRemoteDataSource extends Mock implements AuthRemoteDataSource {}
// class MockAuthRepository extends Mock implements AuthRepository {}
// class MockNetworkInfo extends Mock implements NetworkInfo {}
// class MockUserSession extends Mock implements UserSession {}
// class MockSupabaseClient extends Mock implements SupabaseClient {}
// class MockGoRouter extends Mock implements GoRouter {}
```

### 6.3 Test template para UseCase

Crea `test/features/auth/domain/usecases/sign_in_test.dart`:

```dart
import 'package:fpdart/src/either.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{{project_name}}/core/error/failures.dart';
import 'package:{{project_name}}/features/auth/domain/entities/user.dart';
import 'package:{{project_name}}/features/auth/domain/repositories/auth_repository.dart';
import 'package:{{project_name}}/features/auth/domain/usecases/sign_in.dart';

class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late SignIn useCase;
  late MockAuthRepository mockRepository;

  setUp(() {
    mockRepository = MockAuthRepository();
    useCase = SignIn(mockRepository);
  });

  const tUser = User(
    id: '1',
    email: 'test@test.com',
    createdAt: DateTime(0),
  );

  const tParams = SignInParams(
    email: 'test@test.com',
    password: 'password123',
  );

  test('should sign in successfully', () async {
    when(() => mockRepository.signInWithEmailAndPassword(
          email: any(named: 'email'),
          password: any(named: 'password'),
        )).thenAnswer((_) async => Right(tUser));

    final result = await useCase(tParams);

    expect(result, Right(tUser));
    verify(() => mockRepository.signInWithEmailAndPassword(
          email: tParams.email,
          password: tParams.password,
        )).called(1);
    verifyNoMoreInteractions(mockRepository);
  });

  test('should return AuthFailure on failure', () async {
    when(() => mockRepository.signInWithEmailAndPassword(
          email: any(named: 'email'),
          password: any(named: 'password'),
        )).thenAnswer((_) async => Left(
          const AuthFailure(message: 'Invalid credentials'),
        ));

    final result = await useCase(tParams);

    expect(result, Left(const AuthFailure(message: 'Invalid credentials')));
  });
}
```

### 6.4 Test template para Cubit

Crea `test/features/auth/presentation/cubit/auth_cubit_test.dart`:

```dart
import 'package:bloc_test/bloc_test.dart';
import 'package:fpdart/src/either.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{{project_name}}/core/error/failures.dart';
import 'package:{{project_name}}/features/auth/domain/entities/user.dart';
import 'package:{{project_name}}/features/auth/domain/repositories/auth_repository.dart';
import 'package:{{project_name}}/features/auth/domain/usecases/sign_in.dart';
import 'package:{{project_name}}/features/auth/domain/usecases/sign_up.dart';
import 'package:{{project_name}}/features/auth/domain/usecases/sign_out.dart';
import 'package:{{project_name}}/features/auth/presentation/cubit/auth_cubit.dart';
import 'package:{{project_name}}/features/auth/presentation/cubit/auth_state.dart';

class MockSignIn extends Mock implements SignIn {}
class MockSignUp extends Mock implements SignUp {}
class MockSignOut extends Mock implements SignOut {}
class MockAuthRepository extends Mock implements AuthRepository {}

void main() {
  late AuthCubit cubit;
  late MockSignIn mockSignIn;
  late MockSignUp mockSignUp;
  late MockSignOut mockSignOut;
  late MockAuthRepository mockAuthRepository;

  setUp(() {
    mockSignIn = MockSignIn();
    mockSignUp = MockSignUp();
    mockSignOut = MockSignOut();
    mockAuthRepository = MockAuthRepository();
    cubit = AuthCubit(
      signIn: mockSignIn,
      signUp: mockSignUp,
      signOut: mockSignOut,
      authRepository: mockAuthRepository,
    );
  });

  tearDown(() {
    cubit.close();
  });

  const tUser = User(
    id: '1',
    email: 'test@test.com',
    createdAt: DateTime(0),
  );

  group('signInWithEmailAndPassword', () {
    blocTest<AuthCubit, AuthState>(
      'emits [AuthLoading, Authenticated] on success',
      build: () {
        when(() => mockSignIn(any()))
            .thenAnswer((_) async => Right(tUser));
        return cubit;
      },
      act: (cubit) => cubit.signInWithEmailAndPassword(
        email: 'test@test.com',
        password: 'password123',
      ),
      expect: () => [
        const AuthLoading(),
        Authenticated(tUser),
      ],
    );

    blocTest<AuthCubit, AuthState>(
      'emits [AuthLoading, AuthError] on failure',
      build: () {
        when(() => mockSignIn(any()))
            .thenAnswer((_) async => Left(
              const AuthFailure(message: 'Invalid credentials'),
            ));
        return cubit;
      },
      act: (cubit) => cubit.signInWithEmailAndPassword(
        email: 'test@test.com',
        password: 'wrong',
      ),
      expect: () => [
        const AuthLoading(),
        const AuthError('Invalid credentials'),
      ],
    );
  });
}
```

### 6.5 Test template para Repository

Crea `test/features/auth/data/repositories/auth_repository_impl_test.dart`:

```dart
import 'package:fpdart/src/either.dart';
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart';
import 'package:mocktail/mocktail.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:{{project_name}}/core/error/failures.dart';
import 'package:{{project_name}}/features/auth/data/datasources/auth_remote_data_source.dart';
import 'package:{{project_name}}/features/auth/data/models/user_model.dart';
import 'package:{{project_name}}/features/auth/data/repositories/auth_repository_impl.dart';
import 'package:{{project_name}}/features/auth/domain/entities/user.dart';

class MockAuthRemoteDataSource extends Mock implements AuthRemoteDataSource {}
class MockInternetConnection extends Mock implements InternetConnection {}

void main() {
  late AuthRepositoryImpl repository;
  late MockAuthRemoteDataSource mockDataSource;
  late MockInternetConnection mockNetworkInfo;

  setUp(() {
    mockDataSource = MockAuthRemoteDataSource();
    mockNetworkInfo = MockInternetConnection();
    repository = AuthRepositoryImpl(mockDataSource, mockNetworkInfo);
  });

  const tUserModel = UserModel(
    id: '1',
    email: 'test@test.com',
    createdAt: DateTime(0),
  );

  const tUser = User(
    id: '1',
    email: 'test@test.com',
    createdAt: DateTime(0),
  );

  group('signInWithEmailAndPassword', () {
    test('should return User on success', () async {
      when(() => mockDataSource.signInWithEmailAndPassword(
            email: any(named: 'email'),
            password: any(named: 'password'),
          )).thenAnswer((_) async => tUserModel);

      final result = await repository.signInWithEmailAndPassword(
        email: 'test@test.com',
        password: 'password123',
      );

      expect(result, Right(tUser));
    });

    test('should return AuthFailure on AuthException', () async {
      when(() => mockDataSource.signInWithEmailAndPassword(
            email: any(named: 'email'),
            password: any(named: 'password'),
          )).thenThrow(const AuthException(message: 'Invalid'));

      final result = await repository.signInWithEmailAndPassword(
        email: 'test@test.com',
        password: 'wrong',
      );

      expect(result, Left(const AuthFailure(message: 'Invalid')));
    });
  });
}
```

### 6.6 Crea carpeta de fixtures

```bash
mkdir -p test/fixtures
```

Crea `test/fixtures/user.json`:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "display_name": "Test User",
  "photo_url": "https://example.com/avatar.png",
  "created_at": "2024-01-01T00:00:00.000Z"
}
```

---

## FASE 7: Tooling

### 7.1 Crea `Makefile`

```makefile
.PHONY: setup codegen codegen-watch analyze test build-aab build-apk clean format

# Project setup
setup:
	flutter pub get
	flutter gen-l10n
	dart run build_runner build --delete-conflicting-outputs

# Code generation
codegen:
	dart run build_runner build --delete-conflicting-outputs

codegen-watch:
	dart run build_runner watch --delete-conflicting-outputs

# Static analysis
analyze:
	flutter analyze

# Testing
test:
	flutter test --coverage

# Build
build-aab:
	flutter build appbundle --release

build-apk:
	flutter build apk --release

# Utilities
clean:
	flutter clean
	flutter pub get

format:
	dart format .
```

### 7.2 Configura Husky + lint-staged

Crea `.husky/pre-commit`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged
```

Crea `.husky/commit-msg`:

```bash
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx --no -- commitlint --edit "$1"
```

Crea `commitlint.config.js`:

```js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'docs',
        'style',
        'refactor',
        'perf',
        'test',
        'build',
        'ci',
        'chore',
        'revert',
      ],
    ],
  },
};
```

Agrega al `package.json`:

```json
{
  "name": "{{project_name}}",
  "private": true,
  "scripts": {
    "prepare": "husky"
  },
  "lint-staged": {
    "*.dart": [
      "dart format --fix",
      "flutter analyze --fatal-infos"
    ]
  },
  "devDependencies": {
    "@commitlint/cli": "^19.0.0",
    "@commitlint/config-conventional": "^19.0.0",
    "husky": "^9.0.0",
    "lint-staged": "^15.0.0"
  }
}
```

### 7.3 Configura FVM

Crea `.fvm/flutter_sdk_version`:

```
{{flutter_version}}
```

### 7.4 Configura VS Code

Crea `.vscode/settings.json`:

```json
{
  "dart.flutterSdkPath": ".fvm/flutter_sdk_version",
  "dart.runPubGetOnPubspecChanges": true,
  "[dart]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit"
    }
  },
  "search.exclude": {
    "**/.fvm": true,
    "**/*.g.dart": true,
    "**/*.freezed.dart": true,
    "**/*.gr.dart": true,
    "**/*.mocks.dart": true,
    "**/*.gen.dart": true
  },
  "files.exclude": {
    "**/.fvm": true
  }
}
```

Crea `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "dart-code.flutter",
    "dart-code.dart-code",
    "blaxout.flutter-bloc",
    "nash.awesome-flutter-snippets",
    "bierner.markdown-mermaid"
  ]
}
```

### 7.5 Configura CI/CD

Crea `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '{{flutter_version}}'
      - run: flutter pub get
      - run: flutter analyze

  test:
    needs: analyze
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '{{flutter_version}}'
      - run: flutter pub get
      - run: flutter test --coverage
      - uses: codecov/codecov-action@v4
        with:
          token: \${{ secrets.CODECOV_TOKEN }}
          file: coverage/lcov.info

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '{{flutter_version}}'
      - run: flutter pub get
      - run: flutter build apk --release
```

Crea `.github/workflows/pr-title-lint.yml`:

```yaml
name: PR Title Lint

on:
  pull_request:
    types: [opened, edited, synchronize]

jobs:
  lint-pr-title:
    runs-on: ubuntu-latest
    steps:
      - uses: aslafy-z/conventional-pr-title-action@v3
        with:
          preset: conventionalcommits
        env:
          GITHUB_TOKEN: \${{ secrets.GITHUB_TOKEN }}
```

---

## FASE 8: Post-generation

Ejecuta estos comandos **al final** para verificar y preparar el proyecto:

```bash
# 1. Verificar estructura
ls -la lib/core/
ls -la lib/features/auth/

# 2. Obtener dependencias
flutter pub get

# 3. Generar archivos .g.dart y .freezed.dart
dart run build_runner build --delete-conflicting-outputs

# 4. Verificar que no haya errores de análisis
flutter analyze

# 5. Ejecutar tests
flutter test

# 6. Copiar env example
cp env/.env.example .env

# 7. Inicializar git
git init
git add .
git commit -m "chore: initial scaffold with Clean Architecture + Supabase"

# 8. Configurar FVM (opcional)
# dart pub global activate fvm
# fvm use {{flutter_version}}
```

---

## Resumen del proyecto generado

```
{{project_name}}/
├── lib/
│   ├── core/
│   │   ├── auth/          # UserSession (abstract + Supabase impl)
│   │   ├── common/        # UseCase base + NoParams
│   │   ├── di/            # service_locator (GetIt + Injectable)
│   │   ├── error/         # Failures + Exceptions
│   │   ├── extensions/    # BuildContext extensions
│   │   ├── l10n/          # Localization helpers
│   │   ├── network/       # NetworkInfo
│   │   ├── services/      # CacheManager (abstract + Isar impl)
│   │   ├── theme/         # AppColors, AppTheme, AppSpacing
│   │   ├── utils/         # Constants, Extensions, SnackBarHelper
│   │   └── widgets/       # 9 widgets genéricos
│   ├── features/
│   │   └── auth/          # Auth feature completa
│   │       ├── data/      # datasources, models, repositories
│   │       ├── domain/    # entities, repositories, usecases
│   │       └── presentation/ # cubit, screens, widgets
│   └── l10n/              # ARB files (en + es)
├── test/
│   ├── helpers/           # fixture_reader, mock templates
│   ├── fixtures/          # JSON test data
│   └── features/auth/     # Tests para cada capa
├── supabase/              # Directorio listo para config
├── .github/workflows/     # CI + PR title lint
├── .husky/                # Git hooks
├── Makefile
├── commitlint.config.js
├── analysis_options.yaml
├── build.yaml
└── l10n.yaml
```

**Listo para desarrollar.** Solo reemplaza `{{variables}}`, completa los `// TODO:`, agrega tus features de negocio y configura Supabase.
