# PARTE B -- PACKS OPCIONALES

Estos bloques **se pegan al final** del prompt, despues de que PARTE A haya
verificado. Cada uno es independiente: podes pegar uno, tres o ninguno.

**Antes de pegar uno, decide si tu proyecto lo necesita.** El problema que
resuelve este prompt es exactamente el de pegarle auth a una app sin auth. La
misma disciplina aplica aca.

| Pack | Pegalo si... |
|---|---|
| `auth` | Tu app tiene **usuarios que se registran e inician sesion**. |
| `rpc-publicas` | Tu backend expone datos a un **visitante sin sesion**. |
| `storage` | Subis archivos: avatares, imagenes, adjuntos. |
| `observability` | Necesitas ver errores de produccion. |

El nucleo ya cubre el caso "backend privado, solo usuarios de la app": eso es
`auth` y nada mas.

---

## PACK: auth

> **Este pack es el mas grande y el mas facil de pegar de mas.** Si tu app no
> tiene usuarios, no lo pegues. Un `/login` generado que nadie usa es codigo que
> nadie borra.

Genera **todo lo siguiente, en este orden**. El orden importa: cada paso depende
del anterior.

### P1. Migration: tabla de perfil

`supabase/migrations/00002_create_profiles.sql`

```sql
-- Perfil del usuario. Una fila por usuario de auth.users.
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  -- NOT NULL DEFAULT: agregar una columna NOT NULL sin default rompe a los
  -- clientes viejos que no la lei todavia.
  full_name text not null default '',
  phone text,
  avatar_url text,
  -- Sin esto, dos lugares siguen pidiendo que el usuario configure su idioma.
  preferred_language text not null default 'es',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table public.profiles is
  'Datos publicos del usuario. Una fila por auth.users.id.';

-- Indice por telefono: es el identificador de negocio mas consultado.
create index if not exists idx_profiles_phone
  on public.profiles (phone);

-- --- RLS ---
alter table public.profiles enable row level security;
alter table public.profiles force row level security;

-- El usuario lee su propio perfil.
create policy "Users can read own profile"
  on public.profiles for select
  to authenticated
  using (auth.uid() = id);

-- El usuario actualiza su propio perfil.
-- El `using` filtra filas visibles; el `with check` impide escribir en una fila
-- ajena. Sin el `with check`, un update pasa el `using` y escribe en cualquier id.
create policy "Users can update own profile"
  on public.profiles for update
  to authenticated
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Nadie inserta desde el cliente: el alta la hace el trigger de abajo.
-- Nadie borra desde el cliente: se borra en cascada con auth.users.
```

**El `with check` es la parte que se olvida.** Es la diferencia entre "el usuario
puede editar su perfil" y "el usuario puede editar cualquier perfil, incluyendo
el nombre de otro usuario". Sin `with check`, un `update ... where true` alcanza.

### P2. Trigger: perfil al registrarse

`supabase/migrations/00003_profile_on_signup.sql`

```sql
-- Crea la fila de perfil cuando se crea el usuario.
--
-- El trigger, y no la app, es el que garantiza que toda fila de auth.users tenga
-- perfil. Si lo hace la app, un signup desde otro cliente, o un usuario creado
-- desde el dashboard, queda sin perfil.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
  set search_path = ''
as $$
begin
  insert into public.profiles (id, full_name, phone)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'full_name', ''),
    new.raw_user_meta_data ->> 'phone'
  )
  on conflict (id) do nothing;

  return new;
end;
$$;

-- trigger insert on auth.users
create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute function public.handle_new_user();

-- updated_at automatico.
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create trigger profiles_set_updated_at
  before update on public.profiles
  for each row
  execute function public.set_updated_at();
```

> `set search_path = ''` en `handle_new_user`: sin eso, la funcion busca tablas en
> el `search_path` de quien la dispara. Con `search_path = ''` hay que calificar
> (`public.profiles`), que es lo que hace el cuerpo. Es lo unico que impide que
> alguien con `CREATE` en un schema secuestre la funcion.

### P3. Tests pgTAP de la parte de auth

`supabase/tests/002_profiles_test.sql`

```sql
begin;

select plan(8);

-- Variables de estado para los tres roles del test.
\gset

-- ARRANGE: dos usuarios reales.
select test_helpers.create_user('dueno@example.com') as owner_id \gset
select test_helpers.create_user('otro@example.com') as other_id \gset

-- El trigger creo los perfiles.
select is(
  (select count(*) from public.profiles),
  2::bigint,
  'el trigger creo un perfil por usuario'
);

select is(
  (select full_name from public.profiles where id = :'owner_id'),
  'Test User',
  'el trigger copio full_name del metadata'
);

-- Un segundo signup no duplica.
select is(
  (select count(*) from public.profiles where id = :'owner_id'),
  1::bigint,
  'el perfil es uno por usuario'
);

-- RLS: el anon no lee nada.
select is_empty(
  (select id from public.profiles where id = :'owner_id')::text[],
  'anon no puede leer perfiles'
);

-- RLS: un authenticated no lee el perfil de otro.
select throws_ok(
  $$select test_helpers.as_user(:'other_id',
      'select id from public.profiles where id = ''' || :'owner_id' || '''')
  $$,
  'insufficient privilege',
  'un usuario no puede leer el perfil de otro'
);

-- RLS: un authenticated si lee el suyo.
select lives_ok(
  format(
    $$select test_helpers.as_user(%L,
        'select id from public.profiles where id = %L') $$,
    :'owner_id', :'owner_id'
  ),
  'un usuario puede leer su propio perfil'
);

-- El `with check` bloquea escribir en un perfil ajeno.
select throws_ok(
  format(
    $$select test_helpers.as_user(%L,
        $$update public.profiles set full_name = 'secuestrado'
          where id = %L$$) $$,
    :'other_id', :'owner_id'
  ),
  'insufficient privilege',
  'un usuario no puede actualizar el perfil de otro'
);

-- Las columnas NOT NULL rechazan null.
select throws_ok(
  format(
    $$select test_helpers.as_user(%L,
        $$update public.profiles set preferred_language = null
          where id = %L$$) $$,
    :'owner_id', :'owner_id'
  ),
  'null value in column "preferred_language"',
  'preferred_language no acepta null'
);

select * from finish();
rollback;
```

> **El test que importa es el del `with check`.** Los otros siete pueden pasar con
> el `with check` ausente. Ese es exactamente el punto: RLS necesita los dos
> predicados, y probarlos por separado es obligatorio.

### P4. `config.toml`: la parte de auth que faltaba

Agrega a `[auth]`:

```toml
[auth]
enabled = true
# En produccion, esto va en true. En developing false evita el correo.
site_url = "http://127.0.0.1:3000"
additional_redirect_urls = ["http://127.0.0.1:3000/auth/callback"]
jwt_expiry = 3600
enable_refresh_token_rotation = true
refresh_token_reuse_interval = 10

[auth.email]
enable_signup = true
# CAMBIAR A true en produccion. En false, cualquiera puede usar cualquier correo.
enable_confirmations = true
secure_password_change = true

[auth.sms]
enable_signup = false
enable_confirmations = false

# Sin OAuth. Agregar el bloque de cada provider solo si el proyecto lo usa:
# un provider configurado y no usado es una superficie de ataque de mas.
```

### P5. Flutter: `CurrentUserSupabase`

**Reemplaza** `lib/core/session/current_user_stub.dart` por:

```dart
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/session/current_user.dart';

/// Identidad respaldada por Supabase Auth.
///
/// Implementa el mismo contrato que `CurrentUserStub`. La diferencia es de donde
/// viene el dato: aca, de la sesion de Supabase.
///
/// **Por que `userId` es nullable y no `String`:** porque `supabase.auth
/// .currentUser` es `User?`. Un getter que fuerza el no-null con `!` convierte
/// un "no hay sesion" en un crash. La nulabilidad es la senal de que hay que
/// manejar el caso sin usuario, y esa senal tiene que estar en el tipo.
///
/// `@LazySingleton(as: CurrentUser)` es la misma anotación que tenia el stub:
/// no hay que "cambiar el registro" en `service_locator.dart`, porque ese
/// archivo nunca supo de la identidad.
@LazySingleton(as: CurrentUser)
class CurrentUserSupabase implements CurrentUser {
  CurrentUserSupabase({required SupabaseClient supabase})
      : _supabase = supabase;

  final SupabaseClient _supabase;

  @override
  String? get userId => _supabase.auth.currentUser?.id;

  @override
  bool get isSignedIn => _supabase.auth.currentUser != null;
}
```

**Borra** `lib/core/session/current_user_stub.dart`. Y borra su test.

> **Lo que verifica que lo hayas borrado:** si quedan las dos anotaciones, hay
> dos registros de `CurrentUser` y el arranque falla con
> `CurrentUser is already registered`. Es un error ruidoso a proposito: mejor
> que el doble registro silencioso que tendrias con la cascada manual.

### P6. Flutter: stream de estado de auth

`lib/core/services/auth_state_monitor.dart`

```dart
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:{{NOMBRE_PROYECTO}}/features/auth/domain/entities/user_entity.dart';

/// Eventos de sesion, en el vocabulario del dominio.
///
/// Existe para que `core/` no dependa de `gotrue.AuthChangeEvent`. Si el
/// `AppRouter` importara el enum de gotrue, cambiar de proveedor de auth seria
/// reescribir el router entero. Con este enum, cambiar de proveedor es cambiar
/// este archivo.
enum AuthMonitorEvent {
  signedIn,
  signedOut,
  tokenRefreshed,
  userUpdated,
  initialSession,
  passwordRecovery,
  /// Cualquier evento que no cae en los anteriores.
  other,
}

/// Un evento, con el usuario si lo hay.
class AuthMonitorData {
  const AuthMonitorData({required this.event, this.user});

  final AuthMonitorEvent event;

  /// Null en `signedOut`. No opcional en `signedIn`: ahi siempre hay usuario.
  final UserEntity? user;
}

/// Fuente de eventos de sesion.
abstract class AuthStateMonitor {
  Stream<AuthMonitorData> get onAuthStateChange;

  void dispose();
}

/// `@LazySingleton(as:)`: es una sola suscripcion broadcast a gotrue para toda
/// la app. Dos instancias emitirian los eventos dos veces.
@LazySingleton(as: AuthStateMonitor)
class SupabaseAuthStateMonitor implements AuthStateMonitor {
  SupabaseAuthStateMonitor({required SupabaseClient supabase})
      : _client = supabase;

  final SupabaseClient _client;

  StreamSubscription<AuthState>? _subscription;
  final StreamController<AuthMonitorData> _controller =
      StreamController<AuthMonitorData>.broadcast();

  @override
  Stream<AuthMonitorData> get onAuthStateChange {
    // Suscribirse de forma perezosa: el stream es broadcast, y varios listeners
    // comparten una sola suscripcion a gotrue. Suscribirse en el constructor
    // abriria el canal aunque nadie escuchara.
    _subscription ??= _client.auth.onAuthStateChange.listen(
      _handle,
      onError: (Object error) => _controller.addError(error),
    );
    return _controller.stream;
  }

  void _handle(AuthState state) {
    _controller.add(
      AuthMonitorData(
        event: _mapEvent(state.event),
        user: state.session?.user == null
            ? null
            : UserEntity(
                id: state.session!.user!.id,
                email: state.session!.user!.email ?? '',
                fullName: state.session!.user!.userMetadata?['full_name']
                        as String? ??
                    '',
                emailConfirmed: state.session!.user!.emailConfirmedAt != null,
              ),
      ),
    );
  }

  AuthMonitorEvent _mapEvent(AuthChangeEvent event) {
    return switch (event) {
      AuthChangeEvent.signedIn => AuthMonitorEvent.signedIn,
      AuthChangeEvent.signedOut => AuthMonitorEvent.signedOut,
      AuthChangeEvent.tokenRefreshed => AuthMonitorEvent.tokenRefreshed,
      AuthChangeEvent.userUpdated => AuthMonitorEvent.userUpdated,
      AuthChangeEvent.initialSession => AuthMonitorEvent.initialSession,
      AuthChangeEvent.passwordRecovery => AuthMonitorEvent.passwordRecovery,
      // `signIn` y `userConfirmationSent` no tienen equivalente propio. Si
      // alguno importa, agregalo al enum explicitamente. Dejar `other` y no
      // decidir ahora es mejor que adivinar mal.
      _ => AuthMonitorEvent.other,
    };
  }

  @override
  void dispose() {
    _subscription?.cancel();
    _controller.close();
  }
}
```

No hay nada que registrar en `service_locator.dart`: la anotación
`@LazySingleton(as: AuthStateMonitor)` de la caja anterior ya lo hizo.

```bash
make gen
```

### P7. Flutter: la feature `auth`

Estructura completa:

```
lib/features/auth/
├── data/
│   ├── datasources/
│   │   └── auth_remote_data_source.dart
│   ├── models/
│   │   └── user_model.dart
│   └── repositories/
│       └── auth_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── user_entity.dart
│   ├── repositories/
│   │   └── auth_repository.dart
│   └── usecases/
│       ├── sign_in_usecase.dart
│       ├── sign_up_usecase.dart
│       ├── sign_out_usecase.dart
│       ├── get_current_user_usecase.dart
│       └── reset_password_usecase.dart
└── presentation/
    ├── cubit/
    │   ├── auth_cubit.dart
    │   └── auth_state.dart
    ├── pages/
    │   ├── login_page.dart
    │   ├── register_page.dart
    │   └── forgot_password_page.dart
    └── widgets/
        └── auth_form_card.dart
```

Cada clase de la lista de arriba **que se resuelve desde DI** lleva su
anotación. El mapa completo, para no tener que recordarlo:

| Archivo | Clase | Anotación |
|---|---|---|
| `data/datasources/auth_remote_data_source.dart` | `AuthRemoteDataSourceImpl` | `@LazySingleton(as: AuthRemoteDataSource)` |
| `data/repositories/auth_repository_impl.dart` | `AuthRepositoryImpl` | `@LazySingleton(as: AuthRepository)` |
| `domain/usecases/sign_in_usecase.dart` (+ `sign_up_usecase`, `sign_out_usecase`, `get_current_user_usecase`, `reset_password_usecase`) | el use case de cada archivo | `@lazySingleton` |
| `presentation/cubit/auth_cubit.dart` | `AuthCubit` | `@lazySingleton` (es global, ver P10) |

No se anotan los abstractos (`AuthRemoteDataSource`, `AuthRepository`), la
entidad, el model ni los `params`: no son clases que se resuelven, son tipos
que viajan por argumentos.

Si te olvidas una anotación, el error aparece recien al correr la app
(`AuthRepositoryImpl is not registered`), porque el `service_locator.dart` ya no
tiene una lista que te obligue a completar. Por eso el `make gen` +
`flutter analyze` del P12 no es opcional.

**`domain/entities/user_entity.dart`**

```dart
import 'package:equatable/equatable.dart';

class UserEntity extends Equatable {
  const UserEntity({
    required this.id,
    required this.email,
    required this.fullName,
    required this.emailConfirmed,
  });

  final String id;
  final String email;
  final String fullName;
  final bool emailConfirmed;

  @override
  List<Object?> get props => [id, email, fullName, emailConfirmed];
}
```

**`domain/repositories/auth_repository.dart`**

```dart
import 'package:fpdart/fpdart.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/error/failures.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/auth/domain/entities/user_entity.dart';

abstract class AuthRepository {
  /// El usuario actual, o `Left` si no hay sesion.
  Future<Either<Failure, UserEntity?>> getCurrentUser();

  Future<Either<Failure, UserEntity>> signIn({
    required String email,
    required String password,
  });

  Future<Either<Failure, UserEntity>> signUp({
    required String email,
    required String password,
    required String fullName,
  });

  Future<Either<Failure, Unit>> signOut();

  Future<Either<Failure, Unit>> resetPassword(String email);
}
```

**`data/datasources/auth_remote_data_source.dart`**

```dart
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:{{NOMBRE_PROYECTO}}/core/error/exceptions.dart';
import 'package:{{NOMBRE_PROYECTO}}/features/auth/data/models/user_model.dart';

abstract class AuthRemoteDataSource {
  Future<UserModel?> getCurrentUser();
  Future<UserModel> signIn({required String email, required String password});
  Future<UserModel> signUp({
    required String email,
    required String password,
    required String fullName,
  });
  Future<void> signOut();
  Future<void> resetPassword(String email);
}

/// El `SupabaseClient` lo inyecta el `@module`; nadie pasa
/// `Supabase.instance.client` a mano.
@LazySingleton(as: AuthRemoteDataSource)
class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  AuthRemoteDataSourceImpl({required this.supabase});

  final SupabaseClient supabase;

  @override
  Future<UserModel?> getCurrentUser() async {
    try {
      return UserModel.fromUser(supabase.auth.currentUser);
    } catch (e) {
      throw ServerException(message: 'get_current_user_error: $e');
    }
  }

  @override
  Future<UserModel> signIn({
    required String email,
    required String password,
  }) async {
    try {
      final response = await supabase.auth.signInWithPassword(
        email: email,
        password: password,
      );

      final user = response.user;
      if (user == null) {
        throw ServerException(message: 'sign_in_no_user');
      }

      return UserModel.fromUser(user);
    } on AuthException catch (e) {
      // El mensaje crudo de Supabase va como esta, en el mensaje de la
      // Exception. Lo traduce ErrorHandler en la capa de arriba. Si lo
      // traducieras aca, el repositorio y el cubit verian texto de UI.
      throw AuthException(message: e.message);
    }
  }

  @override
  Future<UserModel> signUp({
    required String email,
    required String password,
    required String fullName,
  }) async {
    try {
      final response = await supabase.auth.signUp(
        email: email,
        password: password,
        data: {'full_name': fullName},
        emailRedirectTo: '${AppConfig.siteUrl}/auth/callback',
      );

      final user = response.user;
      if (user == null) {
        throw ServerException(message: 'sign_up_no_user');
      }

      return UserModel.fromUser(user);
    } on AuthException catch (e) {
      throw AuthException(message: e.message);
    }
  }

  @override
  Future<void> signOut() async {
    try {
      await supabase.auth.signOut();
    } on AuthException catch (e) {
      throw AuthException(message: e.message);
    }
  }

  @override
  Future<void> resetPassword(String email) async {
    try {
      await supabase.auth.resetPasswordForEmail(
        email,
        redirectTo: '${AppConfig.siteUrl}/auth/callback',
      );
    } on AuthException catch (e) {
      throw AuthException(message: e.message);
    }
  }
}
```

**Falta el import de `AppConfig`** (`core/config/app_config.dart`) en el datasource.
Sumalo.

**`core/error/exceptions.dart`** -- agregar `AuthException`:

```dart
class AuthException implements Exception {
  const AuthException({required this.message});

  final String message;

  @override
  String toString() => 'AuthException($message)';
}
```

**`core/error/failures.dart`** -- agregar `AuthFailure`:

```dart
class AuthFailure extends Failure {
  const AuthFailure({super.message = 'Authentication failure', super.code});
}
```

Y **agregar el case al switch de `ErrorHandler.forFailure`**, que sin esto tira
un `switch` no exhaustivo:

```dart
      AuthFailure() => 'Tu sesion expiro. Volve a iniciar sesion',
```

**`presentation/cubit/auth_state.dart`** y **`auth_cubit.dart`**: el cubit se
suscribe al `AuthStateMonitor` y expone el estado. El esqueleto:

```dart
part 'auth_state.dart';

/// `@lazySingleton`, **no** `@injectable`: `AuthCubit` es global. `main()` hace
/// `sl<AuthCubit>().checkSession()` y despues `Bootstrap` lo cuelga con
/// `.value(value: sl<AuthCubit>())`. Con `@injectable` serian dos instancias:
/// el resultado del `checkSession()` quedaria en una que nadie mira.
///
/// Es la excepcion a la regla "los cubits van con `@injectable`": aplica a los
/// cubits de pantalla, que se crean con `BlocProvider(create: ...)`. Un cubit
/// de ambito de app, provisto una sola vez, es un singleton.
@lazySingleton
class AuthCubit extends Cubit<AuthState> {
  AuthCubit({
    required SignInUseCase signIn,
    required SignUpUseCase signUp,
    required SignOutUseCase signOut,
    required GetCurrentUserUseCase getCurrentUser,
    required AuthStateMonitor authStateMonitor,
  })  : _signIn = signIn,
        _signUp = signUp,
        _signOut = signOut,
        _getCurrentUser = getCurrentUser,
        _authStateMonitor = authStateMonitor,
        super(const AuthChecking()) {
    _subscription = _authStateMonitor.onAuthStateChange.listen(
      _onAuthEvent,
      onError: (Object error) => emit(AuthError(_messageOf(error))),
    );
  }

  final SignInUseCase _signIn;
  final SignUpUseCase _signUp;
  final SignOutUseCase _signOut;
  final GetCurrentUserUseCase _getCurrentUser;
  final AuthStateMonitor _authStateMonitor;

  StreamSubscription<AuthMonitorData>? _subscription;

  @override
  Future<void> close() async {
    await _subscription?.cancel();
    _authStateMonitor.dispose();
    return super.close();
  }

  void _onAuthEvent(AuthMonitorData data) {
    switch (data.event) {
      case AuthMonitorEvent.signedIn:
        final user = data.user;
        if (user != null) emit(AuthAuthenticated(user));
      case AuthMonitorEvent.signedOut:
        emit(const AuthUnauthenticated());
      case AuthMonitorEvent.passwordRecovery:
        emit(const AuthPasswordRecovery());
      case AuthMonitorEvent.initialSession:
        // No hace falta emitir nada: el redirect maneja la pantalla de inicio.
        break;
      case AuthMonitorEvent.tokenRefreshed:
      case AuthMonitorEvent.userUpdated:
      case AuthMonitorEvent.other:
        break;
    }
  }

  Future<void> checkSession() async {
    final result = await _getCurrentUser();
    result.fold(
      (failure) => emit(AuthError(failure.message)),
      (user) => user == null
          ? emit(const AuthUnauthenticated())
          : emit(AuthAuthenticated(user)),
    );
  }

  Future<void> signIn({
    required String email,
    required String password,
  }) async {
    emit(const AuthLoading());
    final result = await _signIn(
      SignInUseCaseParams(email: email, password: password),
    );
    result.fold(
      (failure) => emit(AuthError(failure.message)),
      // El estado autenticado lo emite `_onAuthEvent` cuando llega el evento de
      // Supabase, no aca. Emitirlo aca y volver a emitirlo desde el stream
      // produce un rebuild de mas.
      (_) {},
    );
  }

  Future<void> signOut() async {
    emit(const AuthLoading());
    final result = await _signOut();
    result.fold((failure) => emit(AuthError(failure.message)), (_) {});
  }
}
```

**Sobre el `(_) {}` en el `fold`:** un `fold` con la rama del `Right` vacia parece
raro y por eso hay que justificarlo. La alternativa —emitir aca
`AuthAuthenticated(user)`— duplica el estado con el del stream. El patron correcto
es: **el stream es la unica fuente de verdad del estado de sesion; las acciones
solo reportan errores.**

**`presentation/pages/login_page.dart`**, `register_page.dart` y
`forgot_password_page.dart`: pantallas con `AppTextField`, `AppButton`,
`SnackbarHelper` y `BlocConsumer`. Mismo patron de cada pagina del slice de
ejemplo. **TODO:** agregar el link "olvidé mi contraseña" y el de "crear cuenta".

> **Sobre la comparacion de errores en strings.** Es tempting hacer
> `if (failure.message == 'email_not_confirmed')`. **No lo hagas.** El mensaje es
> un contrato de gotrue: cambia entre versiones y no esta tipado. Compará el
> **tipo** del `Failure` (`AuthFailure` vs `ServerFailure`) o un **enum** propio,
> nunca el texto. Ver `## PACK: auth`, paso P8, y el Apendice C, punto 6.

### P8. Flutter: `error_code` en vez de comparar strings

Si tu UI necesita distinguir "correo sin confirmar" de "contraseña incorrecta",
agrega un enum al dominio y un campo `code` que lo transporta:

```dart
// core/error/failure_codes.dart
enum FailureCode { emailNotConfirmed, invalidCredentials, rateLimited, unknown }
```

```dart
// En el repositorio, mapea el mensaje crudo al code una sola vez:
on AuthException catch (e) {
  return Left(
    AuthFailure(message: e.message, code: mapAuthErrorToCode(e.message)),
  );
}
```

El cubit y la vista comparan `FailureCode`, no strings. El mensaje crudo queda
interno de `data`.

### P9. Flutter: `redirect` en el router

**Reemplaza** el `AppRouter` de la FASE 3.16 por este:

```dart
class AppRouter {
  AppRouter({required this.authCubit});

  final AuthCubit authCubit;

  static const String splash = '/';
  static const String splashName = 'splash';
  static const String login = '/login';
  static const String loginName = 'login';
  static const String register = '/register';
  static const String registerName = 'register';
  static const String forgotPassword = '/forgot-password';
  static const String forgotPasswordName = 'forgot_password';
  static const String home = '/home';
  static const String homeName = 'home';

  static final List<RouteBase> routes = [
    GoRoute(
      path: splash,
      name: splashName,
      builder: (context, state) => const SplashPage(),
    ),
    GoRoute(
      path: login,
      name: loginName,
      builder: (context, state) => const LoginPage(),
    ),
    // ... register, forgotPassword, home
  ];

  GoRouter router() {
    return GoRouter(
      initialLocation: splash,
      routes: routes,
      // Sin esto, el router no reacciona a un cambio de sesion. El usuario
      // inicia sesion, el login sigue montado, y el redirect nunca corre.
      refreshListenable: _RouterRefreshStream([authCubit.stream]),
      redirect: (context, state) => computeRedirect(
        authCubit.state,
        state.matchedLocation,
      ),
      errorBuilder: (context, state) =>
          _PageNotFound(uri: state.uri.toString()),
    );
  }

  /// La logica de redirect, como funcion pura y testeable.
  ///
  /// Separarla del `GoRouter` es lo que permite testear los casos de navegacion
  /// sin montar un widget. `visibleForTesting` no es decoracion: marca que esta
  /// expuesta por testing y no por uso.
  @visibleForTesting
  static FutureOr<String?> computeRedirect(
    AuthState authState,
    String location,
  ) {
    final isOnSplash = location == splash;
    final isOnAuthRoute = _authRoutes.any((r) => location.startsWith(r));

    // --- Splash ---
    // Mientras no sepamos si hay sesion, no decidir. Es lo unico que la
    // pantalla de splash justifica: sin este estado, no hay a quien esperar.
    if (authState is AuthChecking || authState is AuthInitial) {
      return isOnSplash ? null : splash;
    }

    // --- Sin sesion ---
    if (authState is AuthUnauthenticated) {
      return isOnSplash || isOnAuthRoute ? null : login;
    }

    // --- Con sesion ---
    if (authState is AuthAuthenticated) {
      // Recuperacion de contrasena: el usuario llego desde un link de email.
      // Va primero porque `AuthAuthenticated` y `AuthPasswordRecovery` pueden
      // coexistir en una implementacion futura.
      if (authState is AuthAuthenticatedWithRecovery) {
        return isOnAuthRoute ? null : forgotPassword;
      }

      if (isOnSplash || isOnAuthRoute) return home;
    }

    return null;
  }

  static const List<String> _authRoutes = [login, register, forgotPassword];
}

/// Puente de `Stream` a `ChangeNotifier`.
///
/// GoRouter necesita un `Listenable` para `refreshListenable`, y `Cubit` es un
/// `Stream`. Este adapter es la pieza que hace que el redirect se reevalue.
class _RouterRefreshStream extends ChangeNotifier {
  _RouterRefreshStream(List<Stream<dynamic>> streams) {
    notifyListeners();
    for (final stream in streams) {
      _subscriptions.add(
        stream.asBroadcastStream().listen((_) => notifyListeners()),
      );
    }
  }

  final List<StreamSubscription<dynamic>> _subscriptions = [];

  @override
  void dispose() {
    for (final subscription in _subscriptions) {
      subscription.cancel();
    }
    super.dispose();
  }
}
```

### P10. Flutter: `main.dart` con la sesion

**No hay bloques de DI que agregar.** Las anotaciones de P7 (`@lazySingleton`
en los use cases y en `AuthCubit`, `@LazySingleton(as: ...)` en el datasource y
el repositorio) ya registraron `auth`; el `AuthStateMonitor` lo hizo P6. Corre:

```bash
make gen
```

Si `service_locator.config.dart` no contiene un `gh.lazySingleton<AuthCubit>`
nuevo, te faltó alguna anotación de la tabla de P7.

Agrega el `checkSession()` al arranque y el `AuthCubit` al `MultiBlocProvider`.

En `main()`, **despues** de `configureDependencies()`:

```dart
  // 6. Session. Antes de runApp: si arrancamos sin saber si hay sesion, el
  //    router muestra el splash, el splash dispara checkSession(), y el usuario
  //    ve un frame de la app antes del login.
  await sl<AuthCubit>().checkSession();
```

Las tres llamadas siguientes resuelven **la misma instancia** de `AuthCubit`,
porque es `@lazySingleton`. Con `@injectable` cada llamada daria un cubit nuevo
y el estado del `checkSession()` no lo veria nadie.

En `Bootstrap.build()`, el `AuthCubit` **si** es global (el router lo necesita):

```dart
      providers: [
        BlocProvider<AuthCubit>.value(value: sl<AuthCubit>()),
      ],
```

Y el router se construye con el cubit:

```dart
        routerConfig: AppRouter(authCubit: sl<AuthCubit>()).router(),
```

### P11. Web: auth con `middleware.ts`

**`apps/web/middleware.ts`**

```typescript
import { createServerClient } from '@supabase/ssr';
import { NextResponse, type NextRequest } from 'next/server';

/**
 * Rutas que no requieren sesion.
 *
 * `matcher` es una regex contra el path. Excluir `/auth`, los assets y los
 * archivos con extension. Sin la exclusion de extensiones, `/favicon.ico` pasa
 * por el middleware y cada icono hace una llamada a Supabase.
 */
const PUBLIC_ROUTES = ['/auth', '/login', '/register'];

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          response = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            response.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  // **La parte que importa.** `getUser()` valida el JWT contra el servidor de
  // Auth y refresca la sesion si hace falta. `getSession()` solo lee la cookie y
  // NO la valida: un JWT forjado con cualquier firma pasa, y el codigo que
  // confia en el para autorizar, permite el acceso.
  //
  // El costo es una llamada de red por request. Es el precio de no confiar en un
  // token sin verificar, y vale pagarlo.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const path = request.nextUrl.pathname;
  const isPublicRoute = PUBLIC_ROUTES.some((route) => path.startsWith(route));

  if (!user && !isPublicRoute) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = '/login';
    loginUrl.searchParams.set('next', path);
    return NextResponse.redirect(loginUrl);
  }

  // Usuario logueado abriendo /login: mandarlo a la app, no al loop.
  if (user && isPublicRoute) {
    const homeUrl = request.nextUrl.clone();
    homeUrl.pathname = '/';
    homeUrl.searchParams.delete('next');
    return NextResponse.redirect(homeUrl);
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Todo excepto:
     *  - _next/static, _next/image (assets de Next)
     *  - favicon.ico y los .svg
     *  - archivos con extension (api/auth/callback debe correr sin sesion)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
```

**`apps/web/app/login/actions.ts`**

```typescript
'use server';

import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export type LoginState =
  | { status: 'idle' }
  | { status: 'error'; message: string }
  | { status: 'success' };

/**
 * Login con email y contrasena.
 *
 * Es una Server Action y no un Route Handler porque se llama desde un `<form>`
 * con `useActionState`: corre en el servidor, escribe cookies, y el error vuelve
 * en la respuesta sin exponer la publishable key en el cliente.
 */
export async function login(
  _prev: LoginState,
  formData: FormData,
): Promise<LoginState> {
  const email = formData.get('email');
  const password = formData.get('password');
  const next = formData.get('next');

  // Validacion en el servidor. El `required` del HTML es UX, no seguridad: el
  // cliente puede mandar cualquier cosa.
  if (typeof email !== 'string' || !email.includes('@')) {
    return { status: 'error', message: 'Correo invalido' };
  }
  if (typeof password !== 'string' || password.length < 6) {
    return { status: 'error', message: 'La contrasena es muy corta' };
  }

  const supabase = await createClient();

  const { error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    // Un unico mensaje para credenciales invalidas y para usuario inexistente.
    // Distinguirlos confirma a un atacante que una casilla tiene cuenta.
    return { status: 'error', message: 'Correo o contrasena incorrectos' };
  }

  // Redirect seguro: `next` viene del cliente, es entrada no confiable.
  // Sin esta validacion, `?next=https://sitio-malicioso.com` convierte el login
  // en un redirector abierto.
  const safeNext =
    typeof next === 'string' && next.startsWith('/') && !next.startsWith('//')
      ? next
      : '/';

  redirect(safeNext);
}
```

**`apps/web/app/auth/callback/route.ts`**

```typescript
import { createClient } from '@/lib/supabase/server';
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Callback de OAuth y de confirmacion de correo.
 *
 * Un Route Handler y no una pagina: no renderiza UI, solo intercambia el codigo
 * por una sesion y redirige. Es la unica parte del flujo de auth que necesita ser
 * un endpoint.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = new URL(request.url);
  const code = searchParams.get('code');
  const next = searchParams.get('next') ?? '/';

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);

    if (!error) {
      const safeNext =
        next.startsWith('/') && !next.startsWith('//') ? next : '/';
      return NextResponse.redirect(`${origin}${safeNext}`);
    }
  }

  // Sin `code` o con error: volver al login con un motivo, no a un 500.
  return NextResponse.redirect(
    `${origin}/login?error=auth_failed`,
  );
}
```

Y el `layout.tsx` de la web ahora puede leer la sesion:

```tsx
import { createClient } from '@/lib/supabase/server';
import { redirect } from 'next/navigation';

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // El middleware ya redirige. Este es el segundo filtro, para el caso en que
  // `matcher` no cubra la ruta.
  if (!user) {
    redirect('/login');
  }

  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
```

> **El `layout.tsx` no deberia redirigir** si la web tiene paginas publicas (la
> landing, el catalogo). Con redirect en el layout, las paginas publicas dejan de
> existir. Con la sesion en el layout y el `redirect` en el middleware, las
> paginas publicas siguen publicas. Borra el `redirect` del layout si tu web tiene
> rutas publicas.

### P12. Verificacion del pack

```bash
cd supabase
supabase db reset
supabase test db        # los 8 tests de profiles deben pasar

cd ../apps/mobile
make l10n && make gen && make analyze && make test
flutter run
```

Checklist manual:

- [ ] Registrarse con un correo nuevo crea una fila en `profiles`.
- [ ] Un segundo registro con el mismo correo da error.
- [ ] El trigger corrio con `full_name` desde el metadata.
- [ ] `flutter run`: muestra splash, redirige a `/login`.
- [ ] Iniciar sesion lleva a `/home`.
- [ ] Cerrar sesion vuelve a `/login`.
- [ ] Rotar el dispositivo en `/login` no rompe nada.
- [ ] La web: `/` sin sesion redirige a `/login?next=/`.
- [ ] La web: logueado, `/login` redirige a `/`.
- [ ] La web: `?next=https://ejemplo.com` NO redirige afuera.
- [ ] `make git-verify` sigue pasando: ningun `.env` trackeado.

---

## PACK: rpc-publicas

Para cuando tu backend expone datos a **visitantes sin sesion**. Es el patron de
una web publica con catalogo: anon key, RLS de lectura, y funciones
`security definer` para lo que necesita varias tablas.

### R1. La RPC

```sql
-- supabase/migrations/00004_rpc_public_catalog.sql

-- RPC publica de lectura.
--
-- Tres cosas la hacen segura, y las tres son necesarias:
--
-- 1. `security definer`: el `anon` no tiene permiso de SELECT sobre las tablas
--    internas, pero si puede ejecutar la funcion.
-- 2. `set search_path = ''`: sin esto, la funcion resuelve nombres por el
--    `search_path` de quien la llama. Un atacante que cree un schema con el
--    nombre de una tabla interna ejecuta su codigo dentro de esta funcion, con
--    los permisos de esta funcion. Es un takeover.
-- 3. `revoke execute from public`: sin esto, cualquier rol puede llamarla,
--    incluidos los que no deberían.
--
-- La regla general: toda funcion `security definer` lleva `set search_path = ''`
-- y califica **todas** las tablas con el esquema. Sin excepcion.
create or replace function public.get_public_catalog()
returns table (
  id uuid,
  title text,
  subtitle text,
  price_cents integer,
  published_at timestamptz
)
language sql
stable
security definer
  set search_path = ''
as $$
  select
    c.id,
    c.title,
    c.subtitle,
    c.price_cents,
    c.published_at
  from public.catalog_items c
  where c.status = 'published'
    and c.published_at <= now()
  order by c.published_at desc;
$$;

-- El default de Postgres es permitir execute a PUBLIC. Decidir a quien.
revoke execute on function public.get_public_catalog() from public;
grant execute on function public.get_public_catalog() to anon, authenticated;
```

### R2. El test que verifica que la RPC no filtra

```sql
-- supabase/tests/003_rpc_public_catalog_test.sql
begin;

select plan(5);

select test_helpers.create_user('seller@example.com') as seller_id \gset
select test_helpers.create_user('buyer@example.com') as buyer_id \gset

-- ARRANGE: un item publicado y uno en borrador.
insert into public.catalog_items (id, title, status, published_at)
values
  ('11111111-1111-1111-1111-111111111111', 'Publicado', 'published', now()),
  ('22222222-2222-2222-2222-222222222222', 'Borrador', 'draft', now());

-- El anon puede leer la RPC.
select lives_ok(
  $$select public.get_public_catalog()$$,
  'la RPC es ejecutable por anon'
);

-- Pero solo ve lo publicado.
select is(
  (select count(*) from public.get_public_catalog()),
  1::bigint,
  'la RPC solo devuelve items publicados'
);

-- Y no el borrador.
select is_empty(
  (select id from public.get_public_catalog()
    where id = '22222222-2222-2222-2222-222222222222')::text[],
  'un item en borrador no aparece en la RPC'
);

-- La RPC no deja ver las tablas internas directamente.
select throws_ok(
  $$select test_helpers.as_anon(
      'select * from public.catalog_items')
  $$,
  'insufficient privilege',
  'anon no puede leer la tabla interna, solo la RPC'
);

-- search_path acotado: la funcion declara el setting.
select ok(
  coalesce(
    (select array_to_string(proconfig, ',') from pg_proc
      where proname = 'get_public_catalog'),
    ''
  ) like '%search_path=%',
  'la RPC declara set search_path'
);

select * from finish();
rollback;
```

### R3. El cliente

En la web, la pagina publica llama la RPC:

```tsx
const { data, error } = await supabase.rpc('get_public_catalog');
```

En mobile, el datasource:

```dart
  @override
  Future<List<CatalogModel>> getPublished() async {
    try {
      final response = await supabase.rpc<List<dynamic>>(
        'get_public_catalog',
      );
      return response
          .cast<Map<String, dynamic>>()
          .map(CatalogModel.fromJson)
          .toList();
    } on FunctionException catch (e) {
      // Una RPC que tira una exception de Postgres llega como FunctionException.
      // El `detail` suele traer el mensaje de Postgres, que puede contener
      // nombres de tablas y columnas. No lo muestres al usuario sin filtrar.
      throw ServerException(
        message: 'rpc_get_public_catalog_error',
        statusCode: 500,
      );
    }
  }
```

> **El `catch (FunctionException)` con mensaje generico es a proposito.** El
> `e.details` de una exception de Postgres puede incluir el SQL que fallo, con
> nombres de tablas y a veces valores. Va al log del servidor, no al `Failure`
> que ve el usuario. `ErrorHandler` traduce `'rpc_..._error'` a texto presentable.

### R4. Verificacion

```bash
supabase db reset && supabase test db

# Con la publishable key, desde el navegador:
curl 'http://127.0.0.1:54321/rest/v1/rpc/get_public_catalog' \
  -H 'apikey: TU_PUBLISHABLE_KEY' \
  -H 'Content-Type: application/json'
```

Checklist:

- [ ] La RPC responde con la publishable key.
- [ ] No responde con la secret key desde el cliente (no debe estar disponible).
- [ ] Un item en borrador no aparece.
- [ ] Un item de otro `owner_id` no aparece en una RPC con filtro por dueno.
- [ ] La tabla interna no es legible directamente por `anon`.

---

## PACK: storage

Para archivos subidos por usuarios: avatares, imagenes, adjuntos.

### S1. Buckets

```sql
-- supabase/migrations/00005_storage_buckets.sql

-- Bucket de archivos publicos.
--
-- `public = true` significa que la URL es de lectura sin permisos. Es correcto
-- para imagenes de perfil y archivos que no tienen nada confidencial. Para un
-- adjunto que solo el dueno debe ver: `public = false` y descarga por Server
-- Action con `createSignedUrl`.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'avatars',
  'avatars',
  true,
  5242880,                              -- 5 MB
  array['image/png', 'image/jpeg', 'image/webp']
)
on conflict (id) do nothing;

-- Un bucket privado para lo que no debe ser publico.
insert into storage.buckets (id, name, public, file_size_limit)
values (
  'private-docs',
  'private-docs',
  false,
  10485760                              -- 10 MB
)
on conflict (id) do nothing;

-- Policies de storage. Son policies como cualquier otra: RLS tambien aplica a
-- las tablas de storage, y por eso funcionan los `auth.uid()`.
create policy "Anyone can read avatars"
  on storage.objects for select
  using (bucket_id = 'avatars');

-- El nombre del archivo es el id del usuario: un usuario no sube por otro.
create policy "Users can upload own avatar"
  on storage.objects for insert
  to authenticated
  with check (
    bucket_id = 'avatars'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

create policy "Users can update own avatar"
  on storage.objects for update
  to authenticated
  using (bucket_id = 'avatars' and owner_id = auth.uid()::text)
  with check (bucket_id = 'avatars' and owner_id = auth.uid()::text);

create policy "Users can delete own avatar"
  on storage.objects for delete
  to authenticated
  using (bucket_id = 'avatars' and owner_id = auth.uid()::text);

-- El bucket privado: solo el dueno.
create policy "Users can read own docs"
  on storage.objects for select
  to authenticated
  using (bucket_id = 'private-docs' and owner_id = auth.uid()::text);

create policy "Users can write own docs"
  on storage.objects for insert
  to authenticated
  with check (bucket_id = 'private-docs' and owner_id = auth.uid()::text);
```

> **`owner_id` viene del JWT, no del `path`.** El `(storage.foldername(name))[1]
> = auth.uid()` funciona mientras la app ponga el id en el path. `owner_id` lo
> setea Supabase y no lo puede manipular el cliente. Si podés usar `owner_id`,
> usalo.
>
> **El `with check` en el `insert`** es lo que impide subir al bucket de otro: sin
> el, el `using` no aplica al insert.

### S2. Flutter: el datasource

```dart
// lib/core/data/local/../features/<tu_feature>/data/datasources/<tu>_remote_data_source.dart
import 'dart:typed_data';

import 'package:supabase_flutter/supabase_flutter.dart';

abstract class UploadDataSource {
  Future<String> uploadAvatar({
    required Uint8List bytes,
    required String fileName,
    required String mimeType,
  });

  Future<void> deleteAvatar(String path);

  Future<String> getSignedUrl(String path);
}

class UploadDataSourceImpl implements UploadDataSource {
  UploadDataSourceImpl({required this.supabase, required this.currentUser});

  final SupabaseClient supabase;
  final CurrentUser currentUser;

  @override
  Future<String> uploadAvatar({
    required Uint8List bytes,
    required String fileName,
    required String mimeType,
  }) async {
    // Prefijar con el id del usuario: hace que la policy de storage por path
    // funcione, y que listar el bucket por prefijo traiga los archivos de una
    // sola persona.
    final userId = currentUser.userId;
    if (userId == null) {
      throw ServerException(message: 'upload_no_user');
    }

    final path = '$userId/$fileName';

    // 1. Subir con `uploadBinary`, no `upload` con File: en mobile el archivo
    //    puede venir de la galeria sin estar en disco.
    final upload = await supabase.storage
        .from('avatars')
        .uploadBinary(path, bytes, fileOptions: FileOptions(
          contentType: mimeType,
          upsert: true,
        ));

    // 2. El path **no** es la URL. Sin este paso, la app guarda un path y
    //    despues intenta renderizarlo como si fuera una URL: 404.
    final publicUrl = supabase.storage.from('avatars').getPublicUrl(path);

    return publicUrl;
  }

  @override
  Future<void> deleteAvatar(String path) async {
    await supabase.storage.from('avatars').remove([path]);
  }

  @override
  Future<String> getSignedUrl(String path) async {
    // URL firmada, con expiracion corta. Para un bucket privado.
    final url = supabase.storage.from('private-docs').createSignedUrl(
          path,
          const Duration(minutes: 5),
        );
    return url;
  }
}
```

> **Los dos errores que casi siempre aparecen:**
>
> 1. **Confundir `path` con `publicUrl`.** `upload` devuelve el path. La URL es
>    `getPublicUrl(path)`. Sin la conversion, el avatar guardado no carga.
> 2. **Duplicar al re-subir sin `upsert: true`.** Sin eso, cada cambio de avatar
>    crea un archivo nuevo y el bucket crece sin limite. Con `upsert`, se
>    reemplaza.

### S3. Verificacion

```bash
supabase db reset && supabase test db
```

Checklist:

- [ ] `anon` no sube nada.
- [ ] Un `authenticated` sube a su propia carpeta.
- [ ] Un `authenticated` **no** sube a la carpeta de otro (probar con otro JWT).
- [ ] Re-subir el mismo archivo no crea un segundo.
- [ ] La URL guardada en el perfil carga la imagen.
- [ ] Un archivo de 6 MB en `avatars` es rechazado por `file_size_limit`.
- [ ] Un `.exe` es rechazado por `allowed_mime_types`.

---

## PACK: observability

Sentry. Solo tiene sentido si el proyecto va a produccion.

### O1. Flutter

Agrega `sentry_flutter: ^9.28.0` a `pubspec.yaml`, en `dependencies`.

```dart
// main.dart
import 'package:sentry_flutter/sentry_flutter.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await dotenv.load(fileName: '.env');

  // Sentry antes que todo lo demas: si `runApp` tira, tiene que reportarse.
  //
  // Condicional: sin DSN, no se inicializa. Asi el proyecto funciona sin
  // configuracion y no manda datos a ningun lado.
  if (AppConfig.sentryDsn.isNotEmpty) {
    await SentryFlutter.init(
      (options) => options
        ..dsn = AppConfig.sentryDsn
        ..tracesSampleRate = 0.1
        ..release = AppConfig.sentryRelease
        ..environment = kReleaseMode ? 'production' : 'development'
        // Errores que no son bugs y no deberian generar ruido.
        ..ignoreErrors(
          on: (error, stack) =>
              error is SocketException ||
              error is TimeoutException ||
              error is HttpException,
        ),
    );
  }

  // ...
}
```

> **Sentry Dart no necesita Firebase.** Ni `firebase_core`, ni
> `google-services.json`, ni `GoogleService-Info.plist`. Es un error comun que
> viene de la documentacion de Sentry para iOS, que si usa Crashlytics. Lo unico
> que hace falta es la dependencia y el `init`.

En `pubspec.yaml`, agregar a los assets:

```yaml
  assets:
    - .env
```

Y **una excepcion en el `.gitignore`**, porque los symbol files si se commitean
(Sentry los usa para leer el archivo fuente):

```gitignore
# NO ignorar: apps/mobile/build/symbols/
# Sentry los necesita para mapear un stack trace ofuscado al fuente real.
```

### O2. Navegacion instrumentada

Sin esto, Sentry te dice **que** fallo pero no **desde donde se llego**:

```dart
GoRouter router() {
  return GoRouter(
    observer: SentryNavigatorObserver(),
    // ...
  );
}

/// Breadcrumbs de navegacion.
///
/// Sin esto, un crash en el checkout no deja rastro de las pantallas que
/// antecedieron al error, y reproducirlo es adivinar.
class SentryNavigatorObserver extends NavigatorObserver {
  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);
    _tag('navigation.push', previousRoute?.settings.name, route.settings.name);
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPop(route, previousRoute);
    _tag('navigation.pop', route.settings.name, previousRoute?.settings.name);
  }

  @override
  void didReplace({Route<dynamic>? newRoute, Route<dynamic>? oldRoute}) {
    super.didReplace(newRoute: newRoute, oldRoute: oldRoute);
    _tag('navigation.replace', oldRoute?.settings.name, newRoute?.settings.name);
  }

  void _tag(String action, String? from, String? to) {
    if (from == null && to == null) return;
    Sentry.addBreadcrumb(
      Breadcrumb(
        message: '$from -> $to',
        category: 'navigation',
        data: {'action': action},
        // Sin esto, mil navegaciones llenan el limite de 100 breadcrumbs y
        // borran los del error.
        level: SentryLevel.info,
      ),
    );
  }
}
```

### O3. Web

```bash
npm install --prefix apps/web @sentry/nextjs
```

```typescript
// apps/web/instrumentation.ts
import * as Sentry from '@sentry/nextjs';

if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    tracesSampleRate: 0.1,
    environment: process.env.NODE_ENV,
  });
}
```

Registrarla en `next.config.ts`:

```typescript
import withSentryConfig from '@sentry/nextjs';

const nextConfig: NextConfig = { /* ... */ };

export default withSentryConfig(nextConfig, {
  // Los source maps suben al build, no en runtime: subirlos en cada deploy
  // llena el quota de Sentry y tarda.
  silent: true,
  widenClientFileUpload: true,
});
```

### O4. Verificacion

```bash
make -C apps/mobile run-prod   # con SENTRY_DSN en el .env
```

Checklist:

- [ ] Sin `SENTRY_DSN`, la app arranca igual y no reporta nada.
- [ ] Con `SENTRY_DSN`, un crash deliberado aparece en Sentry.
- [ ] El release de Sentry coincide con `AppInfo.versionString`.
- [ ] Navegar por 5 pantallas y crashear muestra las 5 en los breadcrumbs.
- [ ] Los errores de red conocidos (`SocketException`, `TimeoutException`,
      `HttpException`) no llegan a Sentry.

---

