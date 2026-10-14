## FASE 1 -- Raiz del monorepo

### 1.1 Estructura de carpetas

```
{{NOMBRE_PROYECTO}}/
├── apps/
│   ├── mobile/
│   └── web/
├── supabase/
│   ├── migrations/
│   ├── tests/
│   └── functions/
├── docs/
│   ├── adr/
│   └── openspec/
├── design/
├── tools/
├── .github/
│   ├── workflows/
│   └── ISSUE_TEMPLATE/
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json.example
├── .husky/
│   └── commit-msg
├── AGENTS.md
├── CLAUDE.md
├── SECURITY.md
├── CONTRIBUTING.md
├── README.md
├── Makefile
├── .editorconfig
├── .gitignore
├── .gitattributes
├── .env.example
├── .nvmrc
├── package.json
├── package-lock.json
├── commitlint.config.js
├── dependabot.yml
└── .github/dependabot.yml
```

Genera `.gitkeep` en `docs/adr/`, `docs/openspec/`, `tools/`,
`supabase/functions/`, `.github/ISSUE_TEMPLATE/`.

### 1.2 `.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 100

[*.{dart}]
indent_size = 2
max_line_length = 90

[*.{ts,tsx,js,jsx,json,jsonc,yml,yaml}]
indent_size = 2

[*.{sql}]
indent_size = 2

[Makefile]
indent_style = tab

[*.md]
trim_trailing_whitespace = false
```

### 1.3 `.gitignore`

Un solo archivo en la raiz. Todo lo que se pueda ignorar sin romper el build.

```gitignore
# ---- Entorno ----
.env
.env.*
!.env.example

# ---- Flutter / Dart ----
**/apps/mobile/.dart_tool/
**/apps/mobile/.packages
**/apps/mobile/build/
**/apps/mobile/.flutter-plugins
**/apps/mobile/.flutter-plugins-dependencies
**/apps/mobile/lib/l10n/gen/
**/apps/mobile/coverage/
**/apps/mobile/android/.gradle/
**/apps/mobile/android/local.properties
**/apps/mobile/android/key.properties
**/apps/mobile/ios/Pods/
**/apps/mobile/ios/.symlinks/
**/apps/mobile/ios/Flutter/Flutter.framework
**/apps/mobile/ios/Flutter/Flutter.podspec
**/apps/mobile/ios/Flutter/Generated.xcconfig
**/apps/mobile/ios/Flutter/flutter_export_environment.sh
**/apps/mobile/ios/Flutter/App.framework
**/apps/mobile/ios/Flutter/ephemeral/
**/apps/mobile/macos/Flutter/ephemeral/
**/apps/mobile/linux/flutter/ephemeral/
**/apps/mobile/windows/flutter/ephemeral/

# ---- Node / Next.js ----
**/node_modules/
**/.next/
**/out/
**/build/
**/.turbo/
**/.vercel/
**/next-env.d.ts
**/*.tsbuildinfo
**/coverage/

# ---- Supabase ----
**/supabase/.branches/
**/supabase/.temp/
**/supabase/.env
**/supabase/logs/
**/supabase/volumes/
**/supabase/.debug/

# ---- Sentry ----
**/.sentryclirc
sentry-debug.log

# ---- SO / editores ----
.DS_Store
Thumbs.db
*.swp
*~
.idea/
.vscode/*
!.vscode/settings.json.example
!.vscode/extensions.json
!.vscode/launch.json

# ---- Test artifacts ----
test-results/
playwright-report/
allure-results/
```

### 1.4 `.env.example` (raiz)

> **REGLA DE ORO.** Este archivo se commitea. Solo van *placeholders*. Jamas una
> clave real, ni de prueba, ni "de ejemplo pero real".
>
> Una `service_role_key` en un archivo commiteado **saltea todas las policies RLS**.
> No es una credencial decorativa: es la llave que abre la base de datos entera.
> Si llega a un repositorio, hay que rotarla en el dashboard de Supabase y
> revisar el historial de git, no solo borrarla.

```bash
# ==============================================================
#  Plantilla de variables. Copiala a .env y completala.
#  NUNCA commitees .env. NUNCA pongas claves reales en este archivo.
# ==============================================================

# --- Supabase: cliente (van en el .env de cada app, no aca) ---
# Flutter  -> apps/mobile/.env
# Next.js -> apps/web/.env.local

# --- Supabase: solo CLI, para `supabase link` y `supabase db push` ---
# Esta linea es la UNICA que se lee desde la raiz del repo.
# En produccion usen el access token del CI, no esta variable.
SUPABASE_ACCESS_TOKEN=
SUPABASE_PROJECT_REF={{SUPABASE_PROJECT_REF}}

# --- Valores locales de `supabase start` ---
# Se completan solos la primera vez que corras `supabase start`.
SUPABASE_LOCAL_URL=http://127.0.0.1:54321
SUPABASE_LOCAL_PUBLISHABLE_KEY=sb_publishable_TU_CLAVE_PUBLISHABLE_LOCAL
SUPABASE_LOCAL_SECRET_KEY=sb_secret_TU_CLAVE_SECRETA_LOCAL

# --- Mobile: rutas ---
# SITE_URL debe coincidir con el redirect de Auth de tu proyecto Supabase.
SITE_URL=http://127.0.0.1:3000

# --- Opcional: observabilidad (vacio = no se instala Sentry) ---
SENTRY_DSN=
SENTRY_RELEASE=
```

**No generes `.env`.** Solo `.env.example`. El usuario lo copia.

### 1.5 `Makefile` (raiz)

Interfaz unica. Cualquier agente y cualquier humano pasan por aca, no por
comandos sueltos.

```makefile
# ==============================================================
#  Makefile raiz -- monorepo {{NOMBRE_PROYECTO}}
#  Herramienta: GNU Make 4.x
# ==============================================================

SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

MONOREPO_ROOT := $(shell pwd)
MOBILER := apps/mobile
WEB := apps/web
DB := supabase

# Prefijo de color, se desactiva si no hay TTY o si NO_COLOR esta seteado
ifneq ($(NO_COLOR),)
BOLD :=
else
BOLD := $(shell tput bold 2>/dev/null || true)
endif

.PHONY: help
help: ## Muestra esta ayuda
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BOLD)%-24s$(BOLD) %s\n", $$1, $$2}'

# ------------------------------------------------------------------
#  Salud
# ------------------------------------------------------------------

.PHONY: doctor
doctor: ## Verifica que las herramientas requeridas esten instaladas
	@echo "== toolchain =="
	@for tool in git make node npm flutter dart supabase psql; do \
		if command -v $$tool >/dev/null 2>&1; then \
			printf '  ok    %s\n' "$$tool"; \
		else \
			printf '  FALTA %s\n' "$$tool"; \
		fi; \
	done
	@echo "== versiones =="
	@git --version || true
	@node --version || true
	@flutter --version 2>/dev/null | head -1 || true
	@supabase --version || true

.PHONY: check
check: ## Corre analyze + tests + lint de las tres capas
	@$(MAKE) --no-print-directory -C $(DB) check
	@$(MAKE) --no-print-directory -C $(MOBILER) check
	@$(MAKE) --no-print-directory -C $(WEB) check

# ------------------------------------------------------------------
#  Base de datos
# ------------------------------------------------------------------

.PHONY: db-up
db-up: ## Levanta el stack local de Supabase (docker)
	@supabase start
	@echo ">> Copia los valores que/sw imprime en SUPABASE_LOCAL_URL y las claves."

.PHONY: db-stop
db-stop: ## Apaga el stack local
	@supabase stop

.PHONY: db-reset
db-reset: ## Borra la base local y la vuelve a construir desde cero (DESTRUCTIVO)
	@read -p "Esto borra la base local. Confirmar [y/N]: " a; [ "$$a" = y ]
	@supabase db reset

.PHONY: db-diff
db-diff: ## Genera una migration a partir de los cambios del schema local
	@supabase db diff -f nombre_del_cambio

.PHONY: db-test
db-test: ## Corre los tests de Postgres (pgTAP)
	@supabase test db

.PHONY: db-status
db-status: ## Estado del stack local
	@supabase status

# ------------------------------------------------------------------
#  Mobile
# ------------------------------------------------------------------

.PHONY: install
install: ## Instala dependencias de las tres capas (el npm de raiz cuelga los hooks de commit)
	@npm install
	@$(MAKE) --no-print-directory -C $(MOBILER) install
	@$(MAKE) --no-print-directory -C $(WEB) install

.PHONY: mobile-run
mobile-run: ## Levanta la app en el dispositivo/emulador conectado
	@$(MAKE) --no-print-directory -C $(MOBILER) run

.PHONY: mobile-analyze
mobile-analyze: ## Analiza Dart
	@$(MAKE) --no-print-directory -C $(MOBILER) analyze

.PHONY: mobile-test
mobile-test: ## Corre los tests de Dart
	@$(MAKE) --no-print-directory -C $(MOBILER) test

.PHONY: mobile-check
mobile-check: ## analyze + test de Dart (analyze primero)
	@$(MAKE) --no-print-directory -C $(MOBILER) check

# ------------------------------------------------------------------
#  Web
# ------------------------------------------------------------------

.PHONY: web-dev
web-dev: ## Levanta Next.js en modo desarrollo
	@$(MAKE) --no-print-directory -C $(WEB) dev

.PHONY: web-build
web-build: ## Build de produccion de Next.js
	@$(MAKE) --no-print-directory -C $(WEB) build

.PHONY: web-lint
web-lint: ## Lint + typecheck de TypeScript
	@$(MAKE) --no-print-directory -C $(WEB) check

# ------------------------------------------------------------------
#  Variables de entorno
# ------------------------------------------------------------------

.PHONY: env-local
env-local: ## Copia los valores de Supabase local al .env del mobile y de la web
	@$(MAKE) --no-print-directory -C $(MOBILER) env-local
	@$(MAKE) --no-print-directory -C $(WEB) env-local

.PHONY: env-usb
env-usb: ## Configura el mobile para hablar con la PC por USB (adb reverse)
	@$(MAKE) --no-print-directory -C $(MOBILER) env-usb

.PHONY: env-ip
env-ip: ## Configura el mobile para hablar con la PC por IP de LAN
	@$(MAKE) --no-print-directory -C $(MOBILER) env-ip

.PHONY: env-check
env-check: ## Verifica que los .env no tengan placeholders sin reemplazar
	@$(MAKE) --no-print-directory -C $(MOBILER) env-check
	@$(MAKE) --no-print-directory -C $(WEB) env-check

# ------------------------------------------------------------------
#  Git / limpieza
# ------------------------------------------------------------------

.PHONY: clean
clean: ## Borra artefactos de build de las tres capas
	@$(MAKE) --no-print-directory -C $(MOBILER) clean
	@$(MAKE) --no-print-directory -C $(WEB) clean
	@supabase stop --no-backup 2>/dev/null || true

.PHONY: git-verify
git-verify: ## Verifica que ningun archivo sensible este por commitear
	@if git ls-files --error-unmatch .env 2>/dev/null; then \
		echo "FALLA: .env esta trackeado. Corri esto antes de seguir."; exit 1; \
	fi
	@if git ls-files --error-unmatch '$(MOBILER)/.env' 2>/dev/null; then \
		echo "FALLA: apps/mobile/.env esta trackeado. Corri esto antes de seguir."; exit 1; \
	fi
	@echo "  ok    ningun .env trackeado"

.PHONY: git-history
git-history: ## Busca credenciales reales commiteadas en TODO el historial
	@echo "Buscando service-role / secret keys en el historial..."
	@if git log -p --all -S'sb_secret_' --oneline | head -1 | grep -q .; then \
		echo "ALERTA: hay una sb_secret_ en el historial de git."; \
		echo "       Rotala en el dashboard de Supabase YA."; \
		echo "       Borrar el archivo no alcanza: sigue en el historial."; exit 1; \
	else \
		echo "  ok    sin sb_secret_ en el historial"; \
	fi

# ------------------------------------------------------------------
#  Conventional commits
# ------------------------------------------------------------------

.PHONY: commit
commit: ## Abre el wizard de conventional commits (commitizen)
	@npm run commit

.PHONY: commitlint
commitlint: ## Valida el ultimo mensaje de commit (el hook commit-msg tambien)
	@npm run commitlint

.PHONY: prepare-husky
prepare-husky: ## Reinstala los hooks de git (husky + commit-msg)
	@npm run prepare
```

### 1.6 `README.md`

```markdown
# {{NOMBRE_PROYECTO}}

Monorepo con Flutter (mobile), Next.js (web) y Supabase (backend).

## Requisitos

- GNU Make 4+
- Flutter 3.41+ con FVM (`fvm install`)
- Node 20+ (version exacta en `.nvmrc`)
- Docker (para `supabase start`)
- Supabase CLI

Verificacion completa con `make doctor`.

## Arranque desde cero

```bash
git clone https://github.com/{{ORG_GITHUB}}/{{REPO_GITHUB}}.git
cd {{REPO_GITHUB}}
make doctor
make install
cp .env.example .env
make env-local      # despues de `make db-up`: completa SUPABASE_URL y la clave
make db-up
make db-test
make web-dev
```

Mobile: `fvm flutter run` (o `make mobile-run`).

## Estructura

| Ruta | Que hay |
|---|---|
| `apps/mobile/` | Flutter. Clean Architecture feature-first. |
| `apps/web/` | Next.js App Router. |
| `supabase/` | Postgres, migrations, tests pgTAP, Edge Functions. |
| `docs/openspec/` | Cambios especificados antes de codear. |
| `docs/adr/` | Decisiones arquitectónicas y sus porques. |

## Comandos utiles

```bash
make help        # lista todos los targets
make check       # analyze + test + lint de las tres capas
make db-diff     # genera una migration desde los cambios de schema
make git-verify  # verifica que no haya .env trackeados
make commit      # abre el wizard de conventional commits (commitizen)
make commitlint  # valida el ultimo mensaje de commit
```

## Seguridad

- `.env` jamas se commitea. Solo `.env.example`, solo placeholders.
- La `service_role_key` **saltea RLS**. Solo vive en el servidor y en el CI.
- Las claves de la app usan el formato `sb_publishable_...`.
- Reporta vulnerabilidades por el proceso de `SECURITY.md`.

## Convenciones

El detalle completo esta en `docs/adr/0001-estructura-del-monorepo.md` y en
`AGENTS.md`. Leelos antes de escribir codigo.
```

### 1.7 `AGENTS.md`

Instrucciones para agentes de IA que trabajan en el repo. Es el archivo que
hace que un agente nuevo cumpla las convenciones sin que se las repitas.

```markdown
# AGENTS.md

Instrucciones para agentes de IA. Leer completo antes de escribir codigo.

## Regla 0 -- El contrato manda

Si estas instrucciones contradicen un `// TODO:` existente, gana el `// TODO:`.
Si contradicen una instruccion explicita del usuario en el chat, gana el usuario.
No improvises para "arreglar" algo que no te pidieron.

## Como trabaja Clean Architecture aqui

El proyecto es **feature-first**. `lib/` tiene exactamente tres entradas:

```
lib/
  main.dart
  core/       infraestructura transversal
  features/   slices verticales de negocio
  l10n/
```

Regla de dependencia, en una linea:

> `presentation` conoce `domain`. `domain` no conoce nada. `data` conoce
> `domain`. `core` no importa `features`.

Si `core/` importa `features/`, la dependencia esta invertida. Es un error de
arquitectura, no un detalle de estilo.

## Nombres de archivo -- no negociar

| Concepto | Nombre exacto | Ejemplo |
|---|---|---|
| DataSource abstracto + impl | `<algo>_data_source.dart` | `raffle_remote_data_source.dart` |
| | | **dos palabras**, nunca `datasource` |
| Repositorio | `<algo>_repository.dart` / `<algo>_repository_impl.dart` | `raffle_repository_impl.dart` |
| Entidad | `<algo>_entity.dart` | `ticket_entity.dart` |
| Modelo (JSON) | `<algo>_model.dart` | `raffle_model.dart` |
| Use case | `<verbo>_<sustantivo>_usecase.dart`, **con** sufijo `usecase` | `get_raffles_usecase.dart` |
| Params de use case | `<UseCase>Params`, `const`, `extends Equatable`, mismo archivo | `GetRafflesUseCaseParams` |
| Cubit | `<feature>_cubit.dart` | `raffle_list_cubit.dart` |
| Estado | `<feature>_state.dart` como `part of` del cubit | `raffle_list_state.dart` |
| Pagina | `pages/`, **nunca** `screens/` | `presentation/pages/raffles_list_page.dart` |
| Widget de feature | `presentation/widgets/` | `presentation/widgets/raffle_card.dart` |

## Estado y cubits

- `Cubit`, nunca `Bloc`. Cero eventos.
- El estado es `part of` del cubit. Nunca `import`.
- El estado base es `sealed class ... extends Equatable` con subclases
  `class`.
- La clase del estado es el nombre del cubit + `State`. Sin sufijo en la variante:
  `RaffleListLoaded`, no `RaffleListStateLoaded`.
- Los estados de error llevan `String message`, no el objeto `Failure` entero.
  La capa de presentacion muestra texto, no tipos.

```dart
sealed class RaffleListState extends Equatable {
  const RaffleListState();
  @override
  List<Object?> get props => const [];
}

class RaffleListInitial extends RaffleListState {
  const RaffleListInitial();
}

class RaffleListError extends RaffleListState {
  const RaffleListError(this.message);
  final String message;
  @override
  List<Object?> get props => [message];
}
```

## Errores -- el unico camino valido

`Either<Failure, T>` de **fpdart** (`package:fpdart/fpdart.dart`), no dartz.
Nunca lances excepciones desde `domain`. Nunca devuelvas `Right` con datos
invalidos.

Mapeo canonico, siempre en el repositorio:

```dart
if (await networkInfo.isConnected) {
  try {
    final data = await remoteDataSource.fetch();
    return Right(data.map((m) => m.toEntity()).toList());
  } on ServerException catch (e) {
    return Left(ServerFailure(message: e.message));
  } on CacheException catch (e) {
    return Left(CacheFailure(message: e.message));
  }
}
return Left(NetworkFailure(message: ErrorHandler.forNetworkError()));
```

Firmas exactas de `core/error/`:

```dart
Failure({required String message, int? code})   // code, NO statusCode
ServerException({required String message, int? statusCode})
NetworkException({required String message})
CacheException({required String message})
ValidationException({required String message})
```

## Inyeccion de dependencias

GetIt + `injectable`, alias `sl`. Las decisiones de registro viven **en la
clase**, no en un archivo central.

```dart
final GetIt sl = GetIt.instance;

@InjectableInit(initializerName: 'init', preferRelativeImports: false)
Future<void> configureDependencies() async {
  await sl.init();
}
```

Reglas de registro:

- `@LazySingleton(as: X)` cuando una clase abstracta `X` se resuelve a una
  implementacion concreta (datasources, repositories).
- `@lazySingleton` para UseCases y servicios compartidos.
- `@injectable` para Cubits de pantalla: `injectable` genera `factory`, un cubit
  nuevo por instancia. **Nunca `@lazySingleton` en un cubit de pantalla.**
  Unica excepcion: un cubit de ambito de app, provisto una sola vez en el
  `MultiBlocProvider` de `Bootstrap` con `.value` (va `@lazySingleton`; dos
  `sl<XCubit>()` serian dos instancias distintas).
- Las clases de terceros (`Isar`, `InternetConnection`, `http.Client`,
  `SupabaseClient`) van en un `@module`. No se pueden anotar.
- El `.config.dart` se regenera con `make gen`. **Nunca** se edita a mano.
- `grep '@lazySingleton\|@injectable\|@Injectable'` responde el grafo de
  dependencias. No hace falta leer el `.config.dart`.

## Tests

`test/` replica `lib/` 1:1, mismos nombres de carpeta hasta `datasources/`.

- `mocktail`, nunca mockito. `bloc_test` para cubits. `fpdart` para `Left`/`Right`.
- Mocks a nivel de archivo, fuera de `main()`: `class MockX extends Mock implements X {}`.
- `late X mockX;` instanciado en `setUp()`.
- Prefijos: `mock*` para mocks, `t*` para datos de prueba (`tRaffle`, `tRaffleId`).
- Comentarios `// ARRANGE` / `// ACT` / `// ASSERT` en mayusculas, siempre.
- Los tests de cubit usan `blocTest` con las claves `setUp` / `build` / `act` /
  `expect` / `verify`, sin comentarios AAA.
- Fixtures JSON en `test/fixtures/`, leidos con `helpers/fixture_reader.dart`.

```dart
test('debe devolver la lista cuando la operacion es exitosa', () async {
  // ARRANGE
  when(() => mockRepository.getAll()).thenAnswer((_) async => Right(tList));

  // ACT
  final result = await useCase(const NoParams());

  // ASSERT
  expect(result, isA<Right<Failure, List<Raffle>>>());
});
```

## Git

- Commits conventional commits: `make commit` abre el wizard (commitizen). El
  hook `commit-msg` valida cada mensaje con commitlint; `make commitlint` valida
  el ultimo commit. No `--no-verify`.
- Ramas: `main` (produccion), `develop` (integracion), `feature/*`, `fix/*`, `chore/*`.
- Los `.env` nunca se commitean. `make git-verify` antes de cada push.
- Toda migration nueva requiere su test pgTAP en el mismo PR.

## Al tocar Supabase

- Toda columna con `NOT NULL DEFAULT`, para que agregar una no rompa clientes viejos.
- Toda tabla con RLS habilitado y **politicas explicitas**, aunque sea `false`.
  RLS habilitado sin politica es denegar todo: eso es intencional y esta bien.
- Toda funcion con `SECURITY DEFINER` lleva `SET search_path = ''` y califica
  **todas** las tablas con el esquema. Sin esto, un atacante con permiso de crear
  objetos puede secuestrar la funcion.
- Nunca uses la `service_role_key` desde el cliente. Jamas.

## Cuando termines

Ejecuta `make check`. Si algo falla, arreglalo. No digas "deberia funcionar".
```

### 1.8 `CLAUDE.md`

Un `include` de tres lineas. La fuente de verdad es `AGENTS.md`.

```markdown
# CLAUDE.md

Ver `AGENTS.md`. Ese archivo es la fuente de verdad de las convenciones de este
repositorio y aplica sin excepcion.

Resumen operativo:

- `make check` antes de dar por terminada cualquier tarea.
- Clean Architecture feature-first. `core/` nunca importa `features/`.
- DI con GetIt + `injectable`. El registro vive en las anotaciones de cada
  clase; `make gen` escribe el `.config.dart`.
- Tests con `mocktail` + `bloc_test`, espejando `lib/` 1:1.
- Los `.env` nunca se commitean.
```

### 1.9 `SECURITY.md`

```markdown
# Politica de seguridad

## Reportar una vulnerabilidad

**No abras un issue publico.** Enviá el detalle a {{EMAIL_CONTACTO}}.

Incluí:

1. Qué es vulnerable y dónde (archivo, ruta, endpoint).
2. Pasos para reproducirlo.
3. Impacto: qué datos o acciones queda expuestos un atacante.
4. Si ya explotaste algo, qué tocaste.

Respondemos en 72 horas con un acuse de recibo y una fecha de corrección o de
mitigación.

## Superficie de la app

| Activo | Donde vive | Que lo protege |
|---|---|---|
| Publishable key | `.env` del cliente, va en el bundle | Solo RLS. Es publica por diseno |
| Secret / service_role key | Secretos del CI y del servidor | Nunca sale del servidor. Salta RLS |
| JWT de sesion | Lo emite Supabase Auth | Caduca; no lo guardes en disco sin motivo |
| RLS de Postgres | `supabase/migrations/*.sql` | Es la unica barrera real |

## Reglas que no se negocian

1. La `service_role_key` nunca se commitea, nunca llega al cliente, nunca se
   loguea. Si aparece en un repo, **rotala**: borrarla no alcanza, sigue en el
   historial de git.
2. Toda policy de lectura publica lleva `TO anon` explicito, y una justificacion
   escrita al lado. `USING (true)` es una decision, no un default.
3. Las Edge Functions verifican el JWT del que llama. Sin excepcion.
4. Nada de datos personales de terceros en logs ni en errores de cliente.
5. Las dependencias se auditan con `make audit` (ver Makefile de la capa web).
```

### 1.10 `CONTRIBUTING.md`

```markdown
# Como contribuir

## Antes de escribir codigo

Todo cambio arranca como propuesta en `docs/openspec/<nombre-del-cambio>/`:
`proposal.md`, `design.md`, `tasks.md` y `specs/<capability>/spec.md`.
Lo revisa el equipo antes de la primera linea de implementacion.

## Rama

1. `git switch develop && git pull`
2. `git switch -c feature/mi-cambio`
3. Commits pequenos, conventional commits, sin `--no-verify`.

## Antes de abrir el PR

```bash
make check          # analyze + test + lint de las tres capas
make git-verify     # ningun .env trackeado
git push -u origin feature/mi-cambio
```

El PR describe **que** cambia y **por que**. Referencia el cambio de `openspec/`.
Los drafts se saltan el pipeline pesado: marcalo como draft si todavia no compila.

## Si tocas el schema

1. Cambia el schema con `supabase db reset` para ver el estado real.
2. `make db-diff -f nombre` genera la migration.
3. Editala a mano. Agregale **todos** los `NOT NULL DEFAULT`.
4. Escribí los tests pgTAP en `supabase/tests/` en el mismo PR.
5. Si la migration es destructiva, planificala en dos pasos: agregar nullable,
   migrar datos, agregar la constraint.
```

### 1.11 `docs/adr/0001-estructura-del-monorepo.md`

```markdown
# ADR 0001 -- Estructura del monorepo yClean Architecture feature-first

- Estado: aceptada
- Fecha: {{FECHA}}

## Contexto

Se necesita una app movil en Flutter, una web en Next.js y un backend en
Supabase, con reglas de negocio compartidas entre ambos.

## Decisiones

1. **Monorepo, no polirepo.** Los cambios que tocan schema, mobile y web a la vez
   son la norma en este producto, no la excepcion. Con repos separados, coordinar
   un cambio de contrato cuesta dias.

2. **Supabase en la raiz, no en `apps/`.** Es un servicio que comparte el ciclo de
   vida con las tres capas, y su CLI trabaja con rutas relativas a la raiz.

3. **Clean Architecture feature-first en Flutter.** Las features son slices
   verticales completas (`data` + `domain` + `presentation`). El horizontal
   (`models/`, `repositories/`, `screens/`) obliga a saltar entre carpetas para
   entender una sola feature.

4. **Clean Architecture en la capa web.** Next.js no la impone, pero el dominio se
   comparte con mobile, y tener dos estilos de dominio en el mismo repo es peor que
   tener dos.

5. **GetIt con `injectable`.** Ver ADR 0002.

6. **El nucleo no asume autenticacion.** Ver ADR 0003.

## Consecuencias

- La raiz tiene un Makefile unico. Nadie escribe comandos sueltos.
- `docs/openspec/` es la puerta de entrada a cualquier cambio.
- La suite de tests de `apps/mobile/test/` espeja `lib/` exactamente: una ruta
  teaches you where things are without reading any index.
- El registro de dependencias vive al lado de cada clase. Agregar una feature es
  anotar sus clases y correr `make gen`; no se edita `service_locator.dart`. El
  riesgo nuevo es que el `.config.dart` quede viejo si alguien olvida el `gen`
  y `make check` lo descubre.

## Alternativas descartadas

| Alternativa | Por que no |
|---|---|
| `flutter create` en la raiz, `apps/` para el resto | El paquete Dart queda raro y `flutter` mezcla los tres proyectos |
| NestJS como backend en vez de Supabase | Se pierde Auth, Storage y Realtime sin necesidad; el equipo ya conoce Postgres |
| Horizontal Clean Architecture | Cada feature exige saltar entre 5 carpetas |
| Melos para orquestar paquetes Dart | Make alcanza; una dependencia mas no se justifica |
| GetIt con registro manual (`service_locator.dart` con cascada) | 84 registros en un solo archivo: toda feature nueva lo toca y es el punto de colision del repo |
```

### 1.12 `docs/adr/0002-getit-injectable.md`

```markdown
# ADR 0002 -- GetIt con `injectable`, no registro manual

- Estado: aceptada
- Fecha: {{FECHA}}

## Contexto

GetIt es el contenedor. La pregunta es quien escribe el registro: un archivo
central con la cascada (`service_locator.dart`), o las propias clases con
anotaciones que `build_runner` convierte en codigo.

El registro manual funciona hasta que el archivo crece. En el proyecto que
inspiro esta decision el archivo tenia 84 registros y 432 lineas: toda feature
nueva lo tocaba, dos features en paralelo chocaban en el mismo diff, y el
archivo era a la vez el mapa de dependencias y su punto unico de fallo.

## Decision

`injectable` + `injectable_generator`. Cada clase anota su propia forma de
registro:

- `@LazySingleton(as: X)` cuando una abstracta `X` se resuelve a una concreta.
- `@lazySingleton` para servicios y use cases.
- `@injectable` para cubits (genera `factory`).
- `@module` para las clases de terceros que no se pueden anotar
  (`Isar`, `InternetConnection`, `http.Client`, `SupabaseClient`).

`service_locator.dart` queda como punto de entrada: declara `sl` y
`configureDependencies()`. El cuerpo real lo escribe `make gen` en
`core/di/service_locator.config.dart`.

## Consecuencias

- Agregar una feature es anotar sus clases y correr `make gen`. Nadie edita un
  archivo compartido: dos features en paralelo no chocan.
- `service_locator.config.dart` se commitea. Si queda desactualizado, el error
  aparece en `make check`, no en produccion.
- Hay dos paquetes de codegen mas y un paso mas en el ciclo `make gen`.

## Alternativas descartadas

| Alternativa | Por que no |
|---|---|
| Cascada manual en `service_locator.dart` | 84 registros, 432 lineas; todo el mundo toca el mismo archivo |
| `get_it` + `inject.dart` | Menos adoptado que `injectable` y sin ecosistema de `@module` |
| Riverpod | Otro contenedor ademas de GetIt; el codigo existente y los tests usan `sl` |

## Versiones

Bajo Dart 3.11 (Flutter 3.41) hay que fijar `injectable_generator: ^2.12.1`:
la 3.x pide SDK `>=3.12.0` y `analyzer >=10.0.0 <15.0.0` incompatible con
`isar_community_generator 3.3.2` (`analyzer <11.0.0`). La combinacion que
resuelve es `injectable: ^2.7.1` + `injectable_generator: ^2.12.1` +
`analyzer` en `[10.0.0, 11.0.0)`.
```

### 1.13 `docs/adr/0003-nucleo-sin-auth.md`

```markdown
# ADR 0003 -- El nucleo no asume autenticacion

- Estado: aceptada
- Fecha: {{FECHA}}

## Contexto

Un bootstrap que genera la pantalla de login, el `redirect` del router y la
tabla `profiles` le esta resolviendo a la app una pregunta que el dueno del
proyecto todavia no se hizo: "¿esta app tiene usuarios?". Y compila, asi que el
error aparece meses despues, cuando nadie recuerda por que estaba la pantalla
de login. Muchas apps reales no tienen usuarios: una de notas, un lector de
RSS, una calculadora de gastos.

## Decision

El nucleo declara la identidad sin decir de donde viene:
`core/session/current_user.dart` define un `CurrentUser` abstracto
(`userId` nullable, `isSignedIn`), y el bootstrap registra
`CurrentUserStub` (`@LazySingleton(as: CurrentUser)`) que devuelve `null`.

Si el proyecto tiene usuarios, se pega el `## PACK: auth` del prompt: borra el
stub, anota `CurrentUserSupabase` con la misma anotacion y agrega la feature
`auth`, el redirect del router y las migraciones de `profiles` — todos juntos,
en un solo bloque.

## Consecuencias

- Los repositorios dependen de `CurrentUser`, no de la feature de auth. Cambiar
  de proveedor de identidad no toca los repositorios.
- Un proyecto sin usuarios nunca ve codigo de login. Un proyecto con usuarios
  tiene un paso extra (pegar el pack) pagado una sola vez.

## Alternativas descartadas

| Alternativa | Por que no |
|---|---|
| Generar login + `profiles` + redirect en el bootstrap | Resuelve la pregunta de la identidad por el equipo, en vez de para el equipo |
| `UserSession` como singleton con stream | Acopla `core/` a gotrue; el router dependeria del enum de eventos |
| No tener identidad en el nucleo | Los repositorios se quedarian sin poder filtrar por usuario y lo resolverian cada uno a su manera |
```

### 1.14 Archivos de soporte de la raiz

`commitlint.config.js`:

```javascript
/** @type {import('@commitlint/config-conventional').UserConfig} */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat', // feature nueva
        'fix', // bug
        'docs', // solo documentacion
        'style', // formato, sin cambio de comportamiento
        'refactor', // reescritura sin cambio de comportamiento
        'perf', // performance
        'test', // tests
        'build', // build system, dependencias
        'ci', // CI
        'chore', // mantenimiento
        'revert', // revert
      ],
    ],
    'subject-case': [0],
    'header-max-length': [2, 'always', 100],
  },
};

`package.json` (raiz):

```json
{
  "name": "{{NOMBRE_PROYECTO}}-monorepo",
  "private": true,
  "scripts": {
    "prepare": "husky",
    "commit": "git-cz",
    "commitlint": "commitlint --edit"
  },
  "devDependencies": {
    "@commitlint/cli": "^19.0.0",
    "@commitlint/config-conventional": "^19.0.0",
    "@commitlint/cz-commitlint": "^19.0.0",
    "commitizen": "^4.3.0",
    "husky": "^9.1.0"
  },
  "config": {
    "commitizen": {
      "path": "@commitlint/cz-commitlint"
    }
  }
}
```

> `prepare` corre solo en el `npm install` local (no en `npm ci`): husky cuelga
> el hook `commit-msg` y apunta `core.hooksPath` a `.husky/_` (generado, **no**
> se commitea). `make install` ya lo dispara. El wizard usa el adapter
> `@commitlint/cz-commitlint`, asi los tipos del prompt son los del
> `commitlint.config.js`, no una lista distinta a mano.

`.husky/commit-msg`:

```
npx --no -- commitlint --edit "$1"
```

> `--no` impide que `npx` pregunte para instalar commitlint de forma global si
> faltan las dependencias locales; falla limpio, que es lo correcto cuando no
> corriste `make install`.
```

`.nvmrc`:

```
20
```

`.gitattributes`:

```gitattributes
# Normaliza line endings en todo
* text=auto eol=lf

# Archivos que deben ser binarios
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.webp binary
*.ico binary
*.ttf binary
*.otf binary
*.woff binary
*.woff2 binary
*.pdf binary
*.jar binary
*.apk binary
*.aab binary
*.zip binary

# Archivos generados por Next.js: se marcan como linguist-generated
apps/web/next-env.d.ts linguist-generated
apps/web/.next/** linguist-generated

# El lockfile de pub no mergea diferencias line a line
apps/mobile/pubspec.lock merge=binary linguist-generated
```

`dependabot.yml` (raiz) y `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: weekly, day: monday, time: '07:00' }
    open-pull-requests-limit: 5
    labels: [deps, ci]

  - package-ecosystem: npm
    directory: /apps/web
    schedule: { interval: weekly, day: monday, time: '07:00' }
    open-pull-requests-limit: 10
    groups:
      next:
        patterns: ['next', 'eslint-config-next']
        update-types: [minor, patch]
    labels: [deps, javascript]

  - package-ecosystem: pub
    directory: /apps/mobile
    schedule: { interval: weekly, day: monday, time: '07:00' }
    open-pull-requests-limit: 10
    labels: [deps, dart]
```

> **Nota sobre Dependabot y Flutter:** el ecosistema `pub` cubre `pubspec.yaml`,
> pero no `flutter_lints` ni el SDK. Eso lo vigila el pipeline de CI.

`.github/ISSUE_TEMPLATE/bug_report.yml`:

```yaml
name: Reportar un bug
description: Algo no funciona como deberia
labels: [bug]
body:
  - type: textarea
    id: que-pasa
    attributes:
      label: Que pasa
      description: Que esperabas y que paso en realidad
      placeholder: |
        Esperaba que al guardar el formulario se cerrara el modal,
        pero la app se queda cargando y vuelve al inicio.
    validations:
      required: true

  - type: textarea
    id: como-reproducir
    attributes:
      label: Pasos para reproducirlo
      placeholder: |
        1. Abrir la app
        2. Tocar en "Perfil"
        3. Tocar "Cerrar sesion"
    validations:
      required: true

  - type: dropdown
    id: capa
    attributes:
      label: En que capa
      options: [Mobile (Flutter), Web (Next.js), Backend (Supabase / SQL), CI / tooling, No estoy seguro]
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: Version de la app
      placeholder: '1.0.2+5 (main@a1b2c3d)'
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Logs o traceback
      render: shell
      description: Pegalo entreTriple backticks. Sin el traceback no hay forma de reproducirlo.
```

`.github/ISSUE_TEMPLATE/feature_request.yml`:

```yaml
name: Proponer una feature
description: Algo que el producto deberia tener
labels: [enhancement]
body:
  - type: textarea
    id: problema
    attributes:
      label: Que problema resuelve
      description: El problema concreto, no la solucion que ya tenias en mente
    validations:
      required: true

  - type: textarea
    id: propuesta
    attributes:
      label: Que propones
    validations:
      required: true

  - type: textarea
    id: alcance
    attributes:
      label: Alcance
      description: Que queda explicitamente fuera
    validations:
      required: true

  - type: textarea
    id: datos
    attributes:
      label: Que datos necesita
      description: Tablas nuevas, RPCs, cambios de RLS, migraciones
```

`.vscode/extensions.json`, `.vscode/launch.json` (se commitea) y
`.vscode/settings.json.example`:

```json
{
  "recommendations": [
    "dart-code.dart-code",
    "bradlc.vscode-tailwindcss",
    "supabase.supabase-vscode",
    "editorconfig.editorconfig",
    "esbenp.prettier-vscode"
  ]
}
```

```jsonc
// Configuraciones de depuracion. Este archivo se commitea: todos los paths son
// relativos, asi que el mismo F5 funciona en cualquier maquina.
//
// El `cwd` es lo que permite un unico `.vscode/` en la raiz del monorepo:
// Dart-Code resuelve `lib/main.dart` contra apps/mobile, y `npm run dev` contra
// apps/web. La contrapartida de este modo (un solo workspace, sin un
// *.code-workspace multi-root) es que Dart-Code trabaja contra la raiz; el
// beneficio es que el repo se abre con un F5 y todos comparten la config.
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flutter: development",
      "type": "dart",
      "request": "launch",
      "cwd": "apps/mobile",
      "program": "lib/main.dart",
      "args": ["--flavor", "development"]
    },
    {
      "name": "Flutter: production",
      "type": "dart",
      "request": "launch",
      "cwd": "apps/mobile",
      "program": "lib/main.dart",
      "args": ["--flavor", "production"]
    },
    {
      "name": "Flutter: attach",
      "type": "dart",
      "request": "attach"
    },
    {
      "name": "Next.js: server-side",
      "type": "node-terminal",
      "request": "launch",
      "cwd": "apps/web",
      "command": "npm run dev"
    }
  ]
}
```

```jsonc
// Renombrar a settings.json para que se aplique de verdad.
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" },
  // Coincide con `.editorconfig`: max_line_length = 90 para Dart.
  "dart.lineLength": 90,
  // Dart-Code detecta FVM solo si existe `.fvm/`. Si no lo hace, descomentar:
  // "dart.flutterSdkPath": ".fvm/flutter_sdk",
  "[dart]": {
    "editor.defaultFormatter": "Dart-Code.dart-code",
    "editor.rulers": [90]
  },
  "[typescript]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "[typescriptreact]": { "editor.defaultFormatter": "esbenp.prettier-vscode" },
  "files.eol": "\n"
}
```

> **Sobre `launch.json` commiteado y no como `.example`:** a diferencia de
> `settings.json`, los debug configs usan rutas relativas y son portables. No hay
> nada especifico de la maquina que ignorar, asi que el equipo comparte el mismo
> F5. `settings.json` sigue siendo `.example` porque ahi si hay preferencias
> personales.

> **VERIFICAR FASE 1**

```bash
make help        # lista los targets
make doctor      # reporta las herramientas faltantes
make git-verify  # ningun .env trackeado (si falla: .gitignore esta mal)
```

El `launch.json` no se puede verificar por linea de comandos: la unica prueba es
abrir el repo en VS Code con la extension Dart-Code y dar F5 sobre
`Flutter: development`. Si el flavor todavia no existe (eso pasa en la FASE 5.2),
`Flutter: attach` y `Next.js: server-side` sirven para el resto del bootstrap.

---

