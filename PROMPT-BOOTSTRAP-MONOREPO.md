# PROMPT: Bootstrap de monorepo Flutter + Supabase + Next.js

> **Estado:** vigente · **Sustituye a:** [`PROMPT-SCAFFOLD.md`](./PROMPT-SCAFFOLD.md) (Flutter unicamente, Next.js inexistente)
> **Ultima revision:** 2026-10-05

---

## Que es este documento

Un prompt de una sola pasada para que un agente de IA genere un proyecto nuevo y
vacio con este stack:

```
{{NOMBRE_PROYECTO}}/
├── apps/mobile/       Flutter 3.41 · Clean Architecture feature-first · Cubit · GetIt
├── apps/web/          Next.js 16 App Router · React 19 · Tailwind v4 · TypeScript
└── supabase/          Postgres · pgTAP · RLS
```

Tres caracteristicas de este prompt que lo diferencian de un "generame un scaffold":

1. **No inventa dominio.** No hay sorteos, pagos ni rifas. Hay un slice vertical
   descartable llamado `example` que existe solo para verificar el cableado. Se borra
   con un comando.
2. **No asume autenticacion.** El nucleo no menciona login ni usuarios ni sesiones.
   La identidad es una abstraccion neutra y vacia. Si tu proyecto tiene usuarios,
   pegas el bloque `## PACK: auth` de la PARTE B.
3. **Todo cuerpo de funcion es un `// TODO:` explicito.** Si el prompt promete un
   stub, el stub tiene que decir `// TODO:`. Nunca scaffolding silencioso.

---

## Variables

Sustituye antes de ejecutar. El agente debe preguntarte por las que no estes
definidas en la linea `Valor por defecto`.

| Variable | Default | Notas |
|---|---|---|
| `{{NOMBRE_PROYECTO}}` | `mi_app` | snake_case. Es el nombre del paquete Dart (`package:{{NOMBRE_PROYECTO}}/`) |
| `{{NOMBRE_MOSTRABLE}}` | `Mi App` | Visible en la app y en la web |
| `{{ORG_GITHUB}}` | `tu-usuario` | Sin `https://`, sin `@` |
| `{{REPO_GITHUB}}` | `{{NOMBRE_PROYECTO}}` | |
| `{{PUERTO_WEB}}` | `3000` | |
| `{{FEATURE_EJEMPLO}}` | `example` | Slice vertical descartable. Sin mayusculas, sin guiones |
| `{{VERSION_INICIAL}}` | `0.1.0+1` | Version de `pubspec.yaml` |
| `{{DART_NOMBRE_CLASE}}` | `Ejemplo` | Clase de dominio derivada de `{{FEATURE_EJEMPLO}}` |
| `{{SUPABASE_PROJECT_REF}}` | `tu-ref-de-proyecto` | Solo para `supabase link`. El resto funciona con `supabase start` local |
| `{{EMAIL_CONTACTO}}` | `tu@email.com` | Aparece en `SECURITY.md` |
| `{{SENTRY_DSN}}` | *(vacio)* | Si queda vacio, la observabilidad no se instala. Ver `## PACK: observability` |

---

## Contrato de ejecucion

Lee esto antes de generar nada. Es lo unico que no es negociable.

### Reglas duras

1. **Una fase a la vez.** No avances de fase hasta que `make verify` (FASE 8) pase.
   Si una fase falla, arreglala. No sigas adelante.
2. **Nada de placeholders silenciosos.** Cada metodo sin implementar lleva
   `// TODO: <que hacer>`. Si inventas un nombre de dominio, es un error: las
   entidades del slice `example` son las unicas entidades de ejemplo.
3. **Nada de codigo generado que no se use.** `build_runner` genera dos cosas y
   nada mas: los `.g.dart` de Isar y el `.config.dart` de DI. Sin `freezed`, sin
   `json_serializable`. Si el `.config.dart` quedo viejo, `make gen` lo arregla;
   no lo edites a mano.
4. **No crees features de ejemplo con dominio de negocio.** El unico slice vertical
   que se genera es `{{FEATURE_EJEMPLO}}`, con datasource en memoria. Nada de
   usuarios, pedidos, pagos, ni post-its.
5. **No generes autenticacion.** Ni pantalla de login, ni `/login` en el router, ni
   tabla `profiles`, ni trigger sobre `auth.users`, ni `[auth]` en `config.toml`, ni
   `middleware.ts` en Next.js, ni Server Action de login. Si crees que hace falta,
   agregá una nota al final del reporte y seguí.
6. **Un archivo, una responsabilidad.** Si el prompt dice "un archivo", no lo
   combines aunque te parezca mas limpio.
7. **Imports siempre con `package:`.** Nunca imports relativos en `lib/`. Excepcion
   unica: los `part` / `part of` de los pares cubit/state.
8. **No inventes dependencias.** La lista de `pubspec.yaml` y de `package.json` es
   cerrada. Si necesitás otra, la anotas en el reporte final, no la agregás.
9. **Reportá al final.** Al terminar, lista en Markdown: archivos creados, archivos
   omitidos con el motivo, decisiones donde el prompt era ambiguo, y los `// TODO:`
   que quedaron, agrupados por archivo.

### Lo que este prompt NO genera

Decilo explicitamente en el reporte final, para que quede escrito:

- Modulos de plataforma Android/iOS completos (solo `flutter create`).
- Google Play / App Store signing, `Info.plist` de permisos, `Podfile`, Gradle.
- Assets binarios (fuentes, imagenes). El `.gitkeep` y nada mas.
- Tests end-to-end reales. Los tests unitarios si, y deben pasar.

---

## Orden de ejecucion

```
PARTE A -- ESTRUCTURA (verificable con `flutter analyze`)
  FASE 1  Raiz del monorepo
  FASE 2  Backend supabase/
  FASE 3  Core de Flutter apps/mobile/lib/core/
  FASE 4  Slice vertical descartable apps/mobile/lib/features/
  FASE 5  Tooling (Makefile, l10n, scripts)
  FASE 6  CI
  FASE 7  Web Next.js (anonima)
  FASE 8  Verificacion

PARTE B -- PACKS OPCIONALES (pegar solo los que apliquen)
  ## PACK: auth
  ## PACK: rpc-publicas
  ## PACK: storage
  ## PACK: observability
```

PARTE A es autonome. Al terminar tenes un proyecto que compila, que pasa
`flutter analyze` sin warnings, con tests verdes y una web que levanta, y **sin
una sola linea de autenticacion**.

PARTE B son bloques independientes. Cada uno se pega al final del prompt y se
ejecuta despues de que PARTE A verifico. No dependen entre si.

---

# PARTE A -- ESTRUCTURA

## Instrucciones generales para el agente

- Escribi los archivos en el orden de las fases. No generes la FASE 5 antes que la 3.
- Cuando el prompt muestre un bloque de codigo, es **literal**. No lo "mejores",
  no le cambies los nombres, no lo acortes.
- Cuando el prompt muestre un bloque con `# ...` es pseudocodigo: reemplazalo.
- Al final de cada fase, corré el comando de verificacion de esa fase (esta
  marcado con `> VERIFICAR`). Si falla, corregi antes de avanzar.
- No imprimas el contenido de los archivos que generaste en la conversacion. Si
  el usuario los pide, los mostras despues.

---

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

## FASE 2 -- Backend `supabase/`

El backend arranca **vacio a proposito**. Sin tablas de ejemplo, sin policies de
ejemplo, sin seed de datos de negocio. Lo unico que hay es la maquinaria para que
`supabase db test` funcione y para que la primera migration real sea facil.

### 2.1 Estructura

```
supabase/
├── config.toml
├── migrations/
│   └── README.md
├── tests/
│   ├── 000_helpers.sql
│   └── 001_schema_basico_test.sql
├── functions/
│   └── .gitkeep
└── seed.sql
```

### 2.2 `supabase/config.toml`

Genera el archivo **completo y valido** que produce `supabase init`, pero
**editado** en estos puntos:

1. **`[auth]` reducido a lo minimo.** Sin `enable_signup`, sin templates, sin SMS.
   Sin providers. Si tu proyecto tiene auth, el `## PACK: auth` agrega lo que
   corresponda. El nucleo no decide eso por vos.
2. **`[db.pooler]`** con connection strings explicitos.
3. **`[api]`** con `schemas = ["public", "graphql_public"]` y `extra_search_path`
   acotado a `"public", "extensions"`.
4. **`[analytics]`** desactivado: no queres telemetria de uso de un proyecto de
   simulacion.
5. **`[db.seed]`** apuntando a `seed.sql`.
6. **`[auth.email]`** con confirmaciones **desactivadas** por defecto, para que
   developing sea rapido. El pack de auth lo revierte en produccion.

```toml
# supabase/config.toml
# Archivo completo. Generado con `supabase init` y editado a mano.
project_id = "{{NOMBRE_PROYECTO}}"

[api]
enabled = true
port = 54321
schemas = ["public", "graphql_public"]
extra_search_path = ["public", "extensions"]
max_rows = 1000

[db]
port = 54322
shadow_port = 54320
major_version = 17

[db.pooler]
enabled = true
port = 54329
pool_mode = "transaction"
default_pool_size = 20
max_client_conn = 100

[realtime]
enabled = true

[studio]
enabled = true
port = 54323
api_url = "http://127.0.0.1"

[inbucket]
enabled = true
port = 54324

[storage]
enabled = true
file_size_limit = '50MiB'

[auth]
# El nucleo NO define un modelo de autenticacion.
# Ver `## PACK: auth` para los ajustes de email, providers y redirect URLs.
enabled = true

[auth.email]
enable_signup = true
enable_confirmations = false          # developing: sin correos. Produccion: true.
double_confirm_changes = true
secure_password_change = false
max_frequency = "1s"
otp_length = 6
otp_expiry = 3600

[auth.email.template]
subject = "Confirmá tu correo"
content = """<!DOCTYPE html><html><body>
  <h2>Confirmá tu correo</h2>
  <p>Entrá a {{ .ConfirmationURL }} para confirmar tu cuenta de {{ .SiteName }}.</p>
</body></html>"""

[analytics]
enabled = false

[db.seed]
enabled = true
sql_paths = ["./seed.sql"]
```

### 2.3 `supabase/migrations/README.md`

Este archivo es el **contrato de las migrations**. La CLI ignora los `.md`, asi que
convive con los `.sql` sin problema.

````markdown
# Migrations

Todo cambio de schema entra por aca, versionado, y en el mismo PR que su test.

## Nombre

```
<ordinal_5_digitos>_<nombre_en_snake_case>.sql
```

El ordinal es un contador monotonico de 5 digitos, **no una fecha**:

```
00001_create_profiles.sql
00002_create_raffles.sql
00003_create_tickets.sql
00004_fix_tickets_rls.sql
```

Por que no `YYYYMMDDHHMMSS_`:

- Un timestamp codifica una fecha, no un orden. `20260101120000` y
  `20260101093000` se aplican en orden alfabetico aunque el segundo sea posterior.
- Con dos ramas abiertas, dos personas eligen el mismo timestamp.
- Con ordinal se ve el holes: si falta el `00007`, se nota de un vistazo.

Cuando apliques dos migrations a la vez, sumale los numeros y borra el hueco
despues. Los huecos se llenan; reescribir el historial no.

## Flujo

```bash
# 1. Cambiá el schema mirandolo de verdad
supabase db reset

# 2. Diff contra la base de producción -> genera el archivo por vos
supabase db diff -f nombre_del_cambio

# 3. Editalo a mano. La parte importante es esta:

#    a) TODA columna nueva lleva NOT NULL DEFAULT.
#       Agregar una columna NOT NULL sin default rompe a todos los clientes
#       viejos que no laLei todavia.
#    b) Todo index nuevo va en la misma migration que la tabla o columna.
#    c) Toda columna que se consulta filtrada lleva su index. Sin index, un
#       `WHERE` sobre una tabla grande es un seq scan.
#    d) Los cambios destructivos van en dos pasos: agregar nullable, migrar,
#       agregar la constraint. Nunca en un solo deploy.

# 4. Los tests, en supabase/tests/, en el mismo PR
```

## Reglas de seguridad

Estas no son sugerencias. Una migration las puede violar en un `npm run db:push`
a las 18 de un viernes.

1. **RLS habilitado y policies explicitas en toda tabla.** RLS habilitado sin
   policy es denegar todo. Eso esta bien como punto de partida, pero entonces
   escribilo en un comentario para que el siguiente dev entienda que es
   intencional y no un olvido.

2. **Las policies nombradas en ingles, consistentes.**

   ```
   Anyone can read public raffles
   Authenticated can create own raffles
   Owners can update own raffles
   Owners can delete own raffles
   ```

   El prefijo del actor, luego la accion, luego el alcance. Cuando alguien lea
   `pg_policies` y vea `Anyone can view buyers`, la palabra `buyers` ya dice que
   hay que mirar.

3. **Toda policy tiene un `TO` explicito.** `USING (true)` sin `TO anon` es una
   invitation a que alguien agregue la fila equivocada al lado. Si la lectura es
   realmente publica:

   ```sql
   create policy "Anyone can read public raffles"
     on raffles for select
     to anon
     using (status = 'published');
   ```

   Con la justificacion escrita al lado. `USING (true)` es una decision
   consciente, jamas un default.

4. **RLS no aplica a los owners.** Postgres ignora RLS para el owner de la tabla,
   salvo que la tabla sea `FORCE ROW LEVEL SECURITY`. Si el service role o el
   postgres owner necesita que las policies se apliquen, la tabla va con:

   ```sql
   alter table raffles force row level security;
   ```

5. **`SECURITY DEFINER` siempre con `search_path` acotado.**

   ```sql
   create or replace function public.get_public_raffles()
   returns setof public.raffles
   language plpgsql
   security definer
   set search_path = ''
   as $$
   begin
     return query select * from public.raffles where status = 'published';
   end;
   $$;
   ```

   Sin `set search_path = ''`, la funcion busca tablas en el `search_path` del
   que la llama. Un atacante que pueda crear un schema con el mismo nombre que
   una de tus tablas ejecuta su codigo dentro de tu funcion, con tus permisos.

6. **`grant execute` acotado.** Una funcion `security definer` es ejecutable por
   cualquiera que tenga el permiso por default. Decidi a quien:

   ```sql
   revoke execute on function public.get_public_raffles() from public;
   grant  execute on function public.get_public_raffles() to anon, authenticated;
   ```

7. **Nunca la `service_role_key` desde el cliente.** Ni en un `.env` del mobile,
   ni en `.env.local` de la web, ni en un `NEXT_PUBLIC_`. Salta todas las
   policies. Si esta en un repo, rotala en el dashboard.

## Tests

Cada migration va acompanada de su test pgTAP:

- **Feliz:** el caso que tiene que funcionar.
- **RLS:** el `anon` no lee lo que no debe, el `authenticated` ajeno tampoco, y el
  dueno si.
- **Constraints:** la columna `NOT NULL` rechaza `null`.

Un test de RLS que verifica solo el camino feliz no verifica RLS.

```bash
supabase test db
```

## Seeds

`seed.sql` corre despues de cada `supabase db reset`. Sirve para datos de
desarrollo, no de produccion. Si necesita datos semilla fijos, van en el `.env`,
no hardcodeados.
````

### 2.4 `supabase/tests/000_helpers.sql`

Helpers compartidos por todos los tests. pgTAP se ejecuta como superusuario, asi
que los tests necesitan **simular** los roles reales para que la prueba signifique
algo.

```sql
-- Helpers compartidos por la suite pgTAP.
-- pgTAP corre como superusuario, y el superusuario ignora RLS.
-- Para que un test de RLS pruebe algo, hay que:set role explicitamente.

create schema if not exists test_helpers;

-- Crea un usuario de auth real y devuelve su id.
-- No lo inventamos: si el id no existe en auth.users, `auth.uid()` devuelve null
-- y el test pasa por razones equivocadas.
create or replace function test_helpers.create_user(
  p_email text default 'test@example.com'
) returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id uuid;
begin
  v_id := gen_random_uuid();
  insert into auth.users (
    instance_id, id, aud, role, email, encrypted_password,
    email_confirmed_at, created_at, updated_at, raw_app_meta_data, raw_user_meta_data
  ) values (
    '00000000-0000-0000-0000-000000000000', v_id, 'authenticated', 'authenticated',
    p_email, crypt('password123', gen_salt('bf')),
    now(), now(), now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    '{"full_name":"Test User"}'::jsonb
  );
  return v_id;
end;
$$;

-- Corre un bloque con el rol de la publishable key (visitante sin sesion).
create or replace function test_helpers.as_anon(p_sql text)
returns void language plpgsql as $$
begin
  set local role anon;
  execute p_sql;
end;
$$;

-- Corre un bloque como un usuario autenticado.
create or replace function test_helpers.as_user(p_user_id uuid, p_sql text)
returns void language plpgsql as $$
begin
  set local role authenticated;
  set local request.jwt.claim.sub = p_user_id::text;
  execute p_sql;
end;
$$;

-- Corre un bloque como el dueno de una fila (RLS forceada).
create or replace function test_helpers.as_owner(p_user_id uuid, p_sql text)
returns void language plpgsql as $$
begin
  set local role authenticated;
  set local request.jwt.claim.sub = p_user_id::text;
  execute p_sql;
end;
$$;
```

### 2.5 `supabase/tests/001_schema_basico_test.sql`

Un unico test que verifica lo unico que hay: que el schema carga, que RLS esta
habilitado donde tiene que estar, y que las funciones usan `search_path` acotado.
Es el **andamiaje** sobre el que van a crecer los tests de las features reales.

```sql
-- Test base del schema. Verifica las invariantes que tiene que cumplir
-- TODA tabla y TODA funcion del proyecto, mas las de seguridad.
begin;

select plan(7);

-- ------------------------------------------------------------------
--  1. La extension pgcrypto esta disponible
--    crypt() y gen_salt() se usan en triggers y en el helper de usuarios.
-- ------------------------------------------------------------------
select has_function('public', 'crypt', ARRAY['text', 'text'],
  'pgcrypto esta instalada (crypt)');

select has_function('public', 'gen_salt', ARRAY['text'],
  'pgcrypto esta instalada (gen_salt)');

select has_function('public', 'gen_random_uuid', ARRAY[],
  'gen_random_uuid esta disponible');

-- ------------------------------------------------------------------
--  2. Ninguna tabla se dejo sin RLS
--    Un select a pg_tables debe dar cero filas. Si el proyecto ya tiene
--    tablas, este test falla y por ahi: alguien agrego una sin RLS.
-- ------------------------------------------------------------------
select is_empty(
  (
    select c.relname::text
    from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public'
      and c.relkind = 'r'
      and not c.relrowsecurity
  )::text[],
  'toda tabla de public tiene row level security habilitado'
);

-- ------------------------------------------------------------------
--  3. Ninguna policy es USING (true) sin justificar
--    Las policies publicas legitimas declaran to anon + un comentario.
--    Este test no prohibe el acceso publico: obliga a que sea explicito.
-- ------------------------------------------------------------------
select is_empty(
  (
    select policyname::text
    from pg_policies
    where schemaname = 'public'
      and qual = 'true'
      and coalesce(roles::text, '') not like '%anon%'
  )::text[],
  'toda policy USING (true) declara TO anon explicitamente'
);

-- ------------------------------------------------------------------
--  4. Toda funcion security definer tiene search_path acotado
--    El fallo aca es explotable: sin esto, un atacante con CREATE en el
--    schema puede secuestrar la funcion.
-- ------------------------------------------------------------------
select is_empty(
  (
    select p.proname::text
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.prosecdef
      and coalesce(
            array_to_string(p.proconfig, ','),
            ''
          ) not like '%search_path=%'
  )::text[],
  'toda funcion SECURITY DEFINER tiene SET search_path'
);

-- ------------------------------------------------------------------
--  5. Los helpers de test quedaron disponibles
-- ------------------------------------------------------------------
select has_function('test_helpers', 'create_user', ARRAY['text'],
  'el helper create_user existe');

select has_function('test_helpers', 'as_anon', ARRAY['text'],
  'el helper as_anon existe');

-- ------------------------------------------------------------------
--  6. Coherencia de migraciones
-- ------------------------------------------------------------------
select ok(
  (select count(*) > 0 from supabase_migrations.schema_migrations),
  'hay al menos una migration aplicada'
);

select * from finish();
rollback;
```

### 2.6 `supabase/seed.sql`

Vacio a proposito, con la guia de lo que va ahi.

```sql
-- Datos de semilla. Corre despues de cada `supabase db reset`.
--
-- Solo para desarrollo. Si esto llegara a produccion, seria un incidente.
--
-- Que va aca:
--   * fixtures minimos para que la UI se pueda desarrollar sin backend real
--   * usuarios de prueba con `test_helpers.create_user()`
--   * catalogs de apoyo (paises, estados, tipos)
--
-- Que NO va aca:
--   * datos de negocio de prueba que envecinen las policies RLS
--   * ninguna clave, ni token, ni service_role_key
--   * nada que dependa del ambiente: todo tiene que ser identico en local
--     y en el CI, o los tests dejan de ser reproducibles
--
-- Formato recomendado para datos fijos:
--
--   insert into public.countries (code, name) values
--     ('VE', 'Venezuela'),
--     ('CO', 'Colombia')
--   on conflict (code) do nothing;

select 1;
```

> **VERIFICAR FASE 2**

```bash
supabase start
supabase db reset
supabase test db        # los 7 tests del andamiaje deben pasar
```

Si el test #2 (`toda tabla de public tiene RLS`) falla: hay una tabla sin RLS.
Ese es exactamente el bug que el test existe para encontrar.

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

## FASE 5 -- Tooling

### 5.1 `apps/mobile/Makefile`

Todos los targets de la raiz delegan aca. Sin logica duplicada.

```makefile
SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

FEATURE ?= example
FLAVOR  ?= development

# Usa FVM si esta disponible; si no, el flutter del PATH.
FVM := $(shell command -v fvm 2>/dev/null)
FLUTTER := $(if $(FVM),$(FVM) flutter,flutter)
DART := $(if $(FVM),$(FVM) dart,dart)

.PHONY: help
help: ## Muestra esta ayuda
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# --- Ciclo basico ---
.PHONY: install
install: ## Instala dependencias
	$(FLUTTER) pub get

.PHONY: gen
gen: ## Genera los .g.dart de Isar y el .config.dart de DI
	$(DART) run build_runner build --delete-conflicting-outputs

.PHONY: l10n
l10n: ## Genera las localizaciones
	$(FLUTTER) gen-l10n

.PHONY: analyze
analyze: ## Analiza Dart
	$(FLUTTER) analyze

.PHONY: format
format: ## Formatea el codigo
	$(DART) format lib test

.PHONY: test
test: ## Corre los tests
	$(FLUTTER) test

.PHONY: coverage
coverage: ## Corre los tests con cobertura y abre el resumen
	$(FLUTTER) test --coverage
	@genhtml coverage/lcov.info -o coverage/html 2>/dev/null \
		&& echo "Cobertura en coverage/html/index.html" \
		|| echo "genhtml no esta instalado. Abrí coverage/lcov.info"

.PHONY: check
check: analyze test ## analyze + test
	@echo "ok: mobile"

.PHONY: clean
clean: ## Borra artefactos de build
	$(FLUTTER) clean

# --- Correr ---
.PHONY: run
run: ## Corre la app con el flavor de desarrollo
	$(FLUTTER) run --flavor development

.PHONY: run-prod
run-prod: ## Corre la app con el flavor de produccion (con Sentry)
	$(FLUTTER) run --flavor production

.PHONY: run-release
run-release: ## Build de release del flavor de produccion
	$(FLUTTER) build apk --release --flavor production

# --- Variables de entorno ---
# Por que `env-usb` y `env-ip`: el emulador y los dispositivos reales llegan al
# host por rutas distintas. En USB, `127.0.0.1` del dispositivo NO es la PC.
# `adb reverse` lo arregla sin cambiar la URL.

.PHONY: env-local
env-local: ## Copia los valores locales de Supabase al .env
	@echo "Copiando .env.example a .env"
	@cp .env.example .env
	@$(MAKE) --no-print-directory env-check

.PHONY: env-usb
env-usb: ## Configura el .env para hablar con la PC por USB
	@echo "== adb reverse =="
	@adb reverse tcp:54321 tcp:54321
	@sed -i.bak 's|^SUPABASE_URL=.*|SUPABASE_URL=http://127.0.0.1:54321|' .env
	@rm -f .env.bak
	@$(MAKE) --no-print-directory env-check
	@echo "Listo. La app va a hablar con la PC por el cable USB."

.PHONY: env-ip
env-ip: ## Configura el .env para hablar con la PC por IP de LAN
	@read -p "IP de la PC en la LAN (ej 192.168.1.10): " ip; \
	[ -n "$$ip" ] || { echo "Falta la IP"; exit 1; }
	@sed -i.bak "s|^SUPABASE_URL=.*|SUPABASE_URL=http://$$ip:54321|" .env
	@rm -f .env.bak
	@$(MAKE) --no-print-directory env-check
	@echo "Listo. Verifica que el firewall deje pasar el 54321 y que la PC y el"
	@echo "dispositivo esten en la misma red."

.PHONY: env-prod
env-prod: ## Copia .env.production a .env (build de release)
	@test -f .env.production || { echo "Falta .env.production"; exit 1; }
	@cp .env.production .env
	@echo "Ojo: apuntando a produccion. Verificá antes de correr."

.PHONY: env-check
env-check: ## Verifica que el .env no tenga placeholders sin reemplazar
	@if grep -q 'TU_CLAVE_PUBLISHABLE_AQUI' .env 2>/dev/null; then \
		echo "FALLA: la publishable key sigue siendo el placeholder."; \
		echo "       Corré 'supabase start' y copia el valor real."; exit 1; \
	fi
	@if grep -q '^SUPABASE_URL=$$' .env 2>/dev/null; then \
		echo "FALLA: SUPABASE_URL vacia."; exit 1; \
	fi
	@echo "  ok    .env parece completo"

# --- Bajar feature de ejemplo ---
# El slice de ejemplo existe para verificar el cableado. Cuando ya verificaste,
# esto lo saca: codigo, tests, fixture, claves l10n, anotaciones de DI y rutas
# del router. Si algo queda colgando, `flutter analyze` lo dice.
.PHONY: drop-feature
drop-feature: ## Borra el slice de ejemplo (FEATURE=example)
	@echo "Vas a borrar features/$(FEATURE)/ y sus tests."
	@read -p "Confirmar [y/N]: " a; [ "$$a" = y ]
	@rm -rf lib/features/$(FEATURE) test/features/$(FEATURE)
	@rm -f test/fixtures/$(FEATURE).json
	@echo "Ahora:"
	@echo "  1. Sacá la ruta de <FEATURE> de app_router.dart"
	@echo "  2. Sacá las claves <FEATURE>* de lib/l10n/arb/app_*.arb"
	@echo "  3. Cambiá el home del router a tu pantalla real"
	@echo "  4. make gen && make l10n && make analyze"
	@echo ""
	@echo "El paso 4 es el que verifica que no quedo nada colgando: si las"
	@echo "anotaciones de <FEATURE> sobrevivieron al borrado, el analyze falla."
```

> **Por que `drop-feature` pide confirmacion interactiva:** es
> `rm -rf` sobre una carpeta que el usuario eligio. Un `make drop-feature` sin
> argumentos que borre lo que hay, en un repo con diez features, es un incidente.

### 5.2 Flavor de build

Un solo `flavor`, no tres. `development` y `production` alcanza: agregar un flavor
por ambiente multiplica por N la matriz de builds sin agregar informacion.

**`android/app/build.gradle.kts`** -- agregar el bloque `flavorDimensions` dentro
de `android { }`:

```kotlin
flavorDimensions += "env"

productFlavors {
    create("development") {
        dimension = "env"
        applicationIdSuffix = ".dev"
        // El sufijo permite instalar dev y prod en el mismo dispositivo sin
        // desinstalarse. Sin el, develops sobreescribe la app real del tester.
        versionNameSuffix = "-dev"
        resValue("string", "app_name", "{{NOMBRE_MOSTRABLE}} Dev")
    }
    create("production") {
        dimension = "env"
        resValue("string", "app_name", "{{NOMBRE_MOSTRABLE}}")
    }
}
```

> En iOS el equivalente es un esquema en el proyecto de Xcode (`Runner` >
> `Product` > `Scheme` > `Edit Scheme` > `Run` > `Build` > `Define Run
> Configurations`). No lo generes desde el prompt: `ios/` requiere Xcode y no se
> puede verificar en Linux. Dejalo como TODO en el `README.md` de mobile.

**`apps/mobile/README.md`**

```markdown
# {{NOMBRE_PROYECTO}} (mobile)

## Requisitos

- Flutter 3.41+ (recomendado via FVM: `fvm install && fvm use`)
- Un emulador, o un dispositivo con USB debugging

## Arranque

```bash
make install          # pub get
make l10n             # genera AppLocalizations
make gen              # genera los .g.dart de Isar y el .config.dart de DI

# 1. Levanta Supabase desde la raiz del monorepo: make db-up
# 2. Configura el .env segun como llegues al backend:
make env-local        # emulador en la misma maquina
make env-usb          # dispositivo por cable
make env-ip           # dispositivo por WiFi

make run              # flavor development
```

## Comandos

| Target | Que hace |
|---|---|
| `make check` | `analyze` + `test` |
| `make coverage` | Tests con cobertura + resumen HTML |
| `make format` | Formatea `lib/` y `test/` |
| `make run-prod` | Corre con flavor production (activa Sentry si hay DSN) |
| `make run-release` | APK de release |
| `make env-check` | Verifica que el `.env` no tenga placeholders |
| `make drop-feature` | Borra el slice de ejemplo |

## Pendientes de configurar a mano

- [ ] **iOS flavors.** Crear los esquemas `development` y `production` en Xcode:
      `Runner` > `Product` > `Scheme` > `Edit Scheme` > `Run` >
      `Build` > `Define Run Configurations`.
- [ ] **Iconos.** Correr `dart run flutter_launcher_icons` con un
      `assets/app_icon.png` real (1024x1024, sin canal alfa).
- [ ] **Firmado.** `android/key.properties` y el certificado de iOS. Ver
      `SECURITY.md`.
- [ ] **Permisos.** `android/app/src/main/AndroidManifest.xml`: camara, ubicacion,
      contactos, segun lo que use la app. Cada permiso pedido sin usar es una
      razon para que el usuario la desinstale.
- [ ] **Deep links.** Configurar el associated domains en iOS y el intent filter
      en Android si la app se abre desde URLs.

## Por que el slice de ejemplo esta

`features/example/` existe para verificar que DI, routing, l10n, Isar y tests
estan cableados de punta a punta. Una vez verificado, se borra con
`make drop-feature`.

Si no podes borrarlo sin tocar nada mas del proyecto, hay acoplamiento. Ese es
el bug que el slice sirve para encontrar.
```

### 5.3 `.fvmrc` y `.fvm/fvm_config.json`

```json
{
  "flutter": "3.41.0"
}
```

> Un `.fvmrc` con la version exacta. Sin el, dos developers en el mismo repo
> compilan con SDKs distintos y el error aparece como un warning del analyzer que
> nadie busca.

---

## FASE 6 -- CI

Cuatro workflows.

### 6.0 Decision pendiente: pinear las acciones por SHA

Las acciones de este prompt van con **tags** (`actions/checkout@v4`), no con
SHAs. Es una decision consciente de arranque, y hay que dejarla escrita:

**Por que tags y no SHA.** Una etiqueta `v4` es mutable: el maintainer la mueve y
tu workflow corre codigo distinto sin que tu repo cambie. El estandar de
OpenSSF Scorecard para CI/CD es pinear por SHA completo, con el tag en un
comentario:

```yaml
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

**Por que no lo hago aca.** Porque no puedo verificar los SHAs desde este prompt,
y un SHA inventado rompe el CI en el primer push. Un `@v4` que funciona es mejor
que un `@<sha-falso>` que no.

**Que hacer antes de poner esto en produccion.** Para cada `uses:` del proyecto:

```bash
# 1. Ver el SHA detras del tag
gh api repos/actions/checkout/git/ref/tags/v4 --jq '.object.sha'

# 2. Reemplazar
#    actions/checkout@v4
#    -> actions/checkout@<SHA> # v4.2.2

# 3. Verificar que Scorecard este conforme
gh api repos/{{ORG_GITHUB}}/{{REPO_GITHUB}}/contents/.github/workflows
```

Y agregar Dependabot, que ya esta configurado en la FASE 1 y abre los PRs de
actualizacion de esas acciones: es el mecanismo que hace mantenible el pineado.

> **El riesgo concreto del tag, para tener el Tamano del problema:** si alguien
> compromete la cuenta del owner de `actions/checkout`, el tag `v4` que la
> app tuya referencia apunta al codigo comprometido, y ese codigo corre con los
> permisos de tu workflow. Si ese workflow tiene `secrets`, tambien.
>
> **Prioridad:** este riesgo importa mas en repos publicos que en privados, y
> mucho mas si los workflows tienen permisos de escritura. Con
> `permissions: contents: read` y secrets de deploy en un ambiente protegido, el
> tag es aceptable como estado inicial. No lo es en un repo que despliega a
> produccion con un solo click.

### 6.1 `.github/workflows/mobile.yml`

```yaml
name: Mobile

on:
  pull_request:
    paths:
      - 'apps/mobile/**'
      - 'supabase/**'
      - '.github/workflows/mobile.yml'
  push:
    branches: [main, develop]
    paths:
      - 'apps/mobile/**'
      - 'supabase/**'

concurrency:
  # Cancela el run anterior del mismo PR. Sin esto, cada push deja un workflow
  # corriendo y el PR tiene cinco checks en cola.
  group: mobile-${{ github.ref }}
  cancel-in-progress: true

defaults:
  run:
    working-directory: apps/mobile

jobs:
  analyze-and-test:
    name: Analyze y tests
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
          channel: stable
          cache: true

      - name: Instalar dependencias
        run: flutter pub get

      - name: Generar localizaciones
        run: flutter gen-l10n

      - name: Generar codigo (Isar + DI)
        run: dart run build_runner build --delete-conflicting-outputs

      - name: Verificar que el codigo generado esta commiteado
        # Si el .config.dart quedo viejo (alguien anoto una clase y no corro
        # `make gen`), este paso falla y el diff te muestra el registro faltante.
        run: git diff --exit-code -- '*.g.dart' '*.config.dart'

      - name: Analyze
        run: flutter analyze --fatal-infos --fatal-warnings

      - name: Tests con cobertura
        run: flutter test --coverage --reporter=expanded

      - name: Subir cobertura
        uses: actions/upload-artifact@v4
        with:
          name: mobile-coverage
          path: apps/mobile/coverage/lcov.info
          retention-days: 7

  format:
    name: Formato
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
          channel: stable
      - name: Verificar formato
        run: dart format --output=none --set-exit-if-changed lib test
```

> `--fatal-infos --fatal-warnings`: sin eso, el paso pasa aunque haya advertencias
> y la calidad depende de que alguien mire el log. Un lint que nadie ve es un
> lint que nadie cumple.

### 6.2 `.github/workflows/db.yml`

```yaml
name: Base de datos

on:
  pull_request:
    paths: ['supabase/**']
  push:
    branches: [main, develop]
    paths: ['supabase/**']

concurrency:
  group: db-${{ github.ref }}
  cancel-in-progress: true

defaults:
  run:
    working-directory: supabase

jobs:
  tests:
    name: pgTAP
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: supabase/setup-cli@v1
        with:
          version: latest

      # El CI no usa Docker-in-Docker: el stack corre como servicios del runner.
      # Es mas rapido y menos fragil que `supabase start` adentro de un contenedor.
      - name: Levantar Postgres
        run: |
          docker compose -f supabase/docker-compose.yml -f supabase/docker-compose.test.yml up -d db
          for i in $(seq 1 30); do
            if pg_isready -h 127.0.0.1 -p 5432 -U postgres; then break; fi
            echo "Esperando Postgres... ($i)"
            sleep 2
          done

      - name: Correr tests pgTAP
        run: supabase test db --workdir supabase
        env:
          POSTGRES_HOST: 127.0.0.1
          POSTGRES_PORT: 5432
          POSTGRES_DB: postgres
          POSTGRES_PASSWORD: postgres_password

  lint:
    name: Formato de SQL
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: sqlfluff/sqlfluff-action@v3
        with:
          # Un .sqlfluff minimo. Las reglas no-default de SQLFluff son
          # discutibles; lo unico innegociable es el indent y el fin de linea.
          sqlfluff: |
            [sqlfluff]
            dialect = postgres
            max_line_length = 100
            [sqlfluff:indentation]
            tab_space_size = 2
```

### 6.3 `.github/workflows/web.yml`

```yaml
name: Web

on:
  pull_request:
    paths: ['apps/web/**', 'package.json']
  push:
    branches: [main, develop]
    paths: ['apps/web/**']

concurrency:
  group: web-${{ github.ref }}
  cancel-in-progress: true

defaults:
  run:
    working-directory: apps/web

jobs:
  check:
    name: Lint, types y build
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
          cache: npm
          cache-dependency-path: apps/web/package-lock.json

      - name: Instalar dependencias
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Typecheck
        run: npm run typecheck

      - name: Tests
        run: npm run test -- --ci

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_SUPABASE_URL: ${{ vars.SUPABASE_URL }}
          NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: ${{ vars.SUPABASE_PUBLISHABLE_KEY }}

      # Los `NEXT_PUBLIC_*` se hornean en el bundle en tiempo de build, asi que
      # tienen que estar disponibles en este paso y no solo en el deploy.
```

### 6.4 `.github/workflows/security.yml`

```yaml
name: Seguridad

on:
  pull_request:
  push:
    branches: [main, develop]
  schedule:
    # Lunes 03:17 UTC. Numero impar a proposito: evita que todos los Dependabot
    # del mundo corran a las 00:00 y saturen los runners.
    - cron: '17 3 * * 1'

permissions:
  contents: read

jobs:
  audit-npm:
    name: npm audit
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version-file: .nvmrc
      - run: npm ci --prefix apps/web
      - run: npm audit --prefix apps/web --audit-level=high

  audit-dart:
    name: dart pub outdated
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.41.0'
      - name: Verificar que el SDK no quedo atras
        run: flutter pub outdated --no-dev-dependencies

  secrets:
    name: Buscar credenciales en el repositorio
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Buscar sb_secret_ en el historial
        run: |
          # Una service_role_key en el historial de git es un incidente, no un
          # warning. Bajar el archivo no la saca del historial: hay que
          # rotarla en el dashboard de Supabase.
          if git log -p --all -S'sb_secret_' --oneline | head -1 | grep -q .; then
            echo "::error::Hay una sb_secret_ en el historial. Rotala YA."
            exit 1
          fi
          echo "ok: sin sb_secret_ en el historial"

      - name: Verificar que ningun .env este trackeado
        run: |
          if git ls-files | grep -E '(^|/)\.env$' ; then
            echo "::error::Hay un .env trackeado."
            exit 1
          fi
          echo "ok: ningun .env trackeado"

      - name: gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # require: hace fallar el job si hay hallazgos, en vez de solo
          # reportarlos. Un escaner que informa sin cortar no cambia nada.
          # Requiere que el repo sea publico para el informe gratis; en
          # privado, falla hasta que se configure la licencia.
```

## FASE 7 -- Web Next.js (anonima)

### 7.1 Por que esta fase no tiene auth

La web del nucleo es **publica y anonima**. Sin `middleware.ts`, sin Server Action
de login, sin `getUser()` en el layout, sin cookies de sesion.

Es el mismo criterio que en mobile: un bootstrap que genera un login te resuelve
una pregunta que el proyecto todavia no se hizo. Si tu web necesita usuarios, el
`## PACK: auth` agrega el `middleware.ts` y las Server Actions.

El nucleo si demuestra el patron correcto de Next.js + Supabase, que es el que
importa: **cliente para el navegador, servidor para render y para datos.**

### 7.2 Estructura

```
apps/web/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   └── error.tsx
├── lib/
│   ├── supabase/
│   │   ├── client.ts
│   │   └── server.ts
│   └── utils.ts
├── components/
│   └── ui/
│       └── card.tsx
├── public/
├── .env.example
├── .env.local
├── eslint.config.mjs
├── next.config.ts
├── package.json
├── package-lock.json
├── postcss.config.mjs
├── tsconfig.json
├── Makefile
└── README.md
```

**Sin `src/`.** Next.js usa el directorio raiz por defecto y agregar `src/` por
costumbre produce un `tsconfig` con dos roots y un alias que apunta al lugar
equivocado.

### 7.3 `package.json`

```json
{
  "name": "{{NOMBRE_PROYECTO}}-web",
  "version": "{{VERSION_INICIAL}}",
  "private": true,
  "engines": {
    "node": ">=20"
  },
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint --max-warnings=0",
    "typecheck": "tsc --noEmit",
    "test": "vitest",
    "audit": "npm audit --audit-level=high"
  },
  "dependencies": {
    "@supabase/ssr": "^0.5.2",
    "@supabase/supabase-js": "^2.47.10",
    "next": "16.2.6",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.1.0",
    "@types/node": "^22.10.2",
    "@types/react": "^19.0.2",
    "@types/react-dom": "^19.0.2",
    "@vitejs/plugin-react": "^4.3.4",
    "eslint": "^9.17.0",
    "eslint-config-next": "16.2.6",
    "jsdom": "^25.0.1",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/postcss": "^4.0.0",
    "typescript": "^5.7.2",
    "vitest": "^2.1.8"
  }
}
```

> **Version exacta en `next` y `eslint-config-next`.** El rango `^16.2.6` en `next`
> deja que un minor rompa el build un martes. Next es estricto con las
> personalizaciones de webpack y las deprecaciones entre minors son reales. Fijalo
> y dejalo mover con Dependabot, que abre el PR.

> **Tailwind v4, CSS-first.** No hay `tailwind.config.js`. La configuracion vive en
> `globals.css` con `@theme`. Es la forma que la v4 proyecta, y agregar un
> `tailwind.config.ts` a un proyecto v4 es mezclar dos sistemas de configuracion.

### 7.4 `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

> **`@/*` apunta a la raiz, no a `./src/*`.** Sin `src/`, el alias es `./*`. Es
> menos elegante de escribir y evita el error de mover un archivo a `src/` y que
> el alias deje de resolver.

### 7.5 `next.config.ts`

```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,

  // No filtrar `NEXT_PUBLIC_SUPABASE_*` en los logs del servidor: con
  // `poweredByHeader: false` y este filtro, el log no dice que backend estas
  // usando. El log de acceso va al servidor de observabilidad, no a la consola
  // del contenedor.
  logging: {
    fetches: { fullUrl: false },
  },

  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
        ],
      },
    ];
  },
};

export default nextConfig;
```

### 7.6 El patron Supabase: dos clientes

Este es el nucleo del patron y lo unico que hay que Internalizar de la capa web.

```typescript
// lib/supabase/client.ts
'use client';

import { createBrowserClient } from '@supabase/ssr';

/**
 * Cliente de Supabase para el navegador.
 *
 * El prefijo 'use client' es lo que lo convierte en un Client Component. Sin el,
 * Next lo trata como Server Component y tira al usar un hook.
 *
 * `createBrowserClient` **memoriza** el cliente en el scope del modulo. Por eso
 * `const supabase = createBrowserClient(...)` a nivel de archivo y no dentro del
 * componente: dentro del componente se crea uno nuevo en cada render, y cada uno
 * abre su propia conexion Realtime.
 */
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
  );
}
```

```typescript
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

/**
 * Cliente de Supabase para el servidor.
 *
 * Las cookies se escriben en un Server Action o en un Route Handler, no durante
 * el render. Por eso `getAll`/`setAll` en vez de `get`/`set`: si Supabase refresca
 * el token durante el render, `setAll` lo tira y el render falla.
 */
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // En Server Components, `cookies().set` tira: son read-only. Es
            // esperado cuando el refresh del token ocurre durante el render.
            // El error se ignora a proposito, porque la sesion se va a refrescar
            // en el proximo Server Action. Un `throw` aca deja la pagina en
            // blanco.
          }
        },
      },
    },
  );
}
```

> **Por que dos archivos y no uno con una bandera:** el import de
> `createBrowserClient` arrastra codigo de navegador a un modulo que corre en
> Node. Separarlos hace que el error sea visible en el momento del import y no
> en el primer click.

### 7.7 `app/layout.tsx`, `page.tsx`, `globals.css`

```tsx
// app/layout.tsx
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '{{NOMBRE_MOSTRABLE}}',
  description: 'Descripcion del producto, en una linea.',
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
```

```tsx
// app/page.tsx
import { createClient } from '@/lib/supabase/server';

/**
 * Landing publica.
 *
 * `createClient()` sin sesion: es una pagina anonima y usa el rol `anon`, con las
 * policies RLS de lectura publica. Si la pagina necesita datos privados, ver
 * `## PACK: auth`.
 */
export default async function Home() {
  const supabase = await createClient();

  const { data, error } = await supabase.rpc('get_public_entries');

  if (error) {
    // El error va al log del servidor. Al visitante le llega la pagina sin datos,
    // no un stack trace con el nombre de la funcion SQL.
    console.error('Error cargando entradas publicas:', error.message);
  }

  const entries = data ?? [];

  return (
    <main className="mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-bold">{{NOMBRE_MOSTRABLE}}</h1>
      <p className="mt-2 text-zinc-600">
        Descripcion del producto, en una linea.
      </p>

      <section className="mt-12">
        <h2 className="text-xl font-semibold">Entradas publicas</h2>

        {entries.length === 0 ? (
          <p className="mt-4 text-zinc-500">
            Todavia no hay nada. Corré `supabase db reset` con datos de semilla.
          </p>
        ) : (
          <ul className="mt-4 space-y-2">
            {entries.map((entry) => (
              <li
                key={entry.id}
                className="rounded-lg border border-zinc-200 p-4"
              >
                {entry.title}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
```

> **La RPC `get_public_entries` no existe todavia.** El nucleo no genera schema de
> negocio. Para que la web compile y renderice, generá esta migration minima en
> `supabase/migrations/00001_public_entries.sql`:
>
> ```sql
> -- Entradas publicas de lectura.
> create table if not exists public.public_entries (
>   id uuid primary key default gen_random_uuid(),
>   title text not null,
>   created_at timestamptz not null default now()
> );
>
> alter table public.public_entries enable row level security;
>
> -- RLS habilitado y sin policies = denegar todo. Vamos a agregar la de lectura.
> create policy "Anyone can read public entries"
>   on public.public_entries for select
>   to anon, authenticated
>   using (true);
>
> -- RPC de lectura. security definer con search_path acotado: sin esto, un
> -- atacante con CREATE en el schema puede ejecutar su codigo dentro de la
> -- funcion con los permisos de la funcion. Ver supabase/migrations/README.md.
> create or replace function public.get_public_entries()
> returns setof public.public_entries
> language sql
> security definer
>   set search_path = ''
> as $$
>   select * from public.public_entries order by created_at desc;
> $$;
>
> revoke execute on function public.get_public_entries() from public;
> grant execute on function public.get_public_entries() to anon, authenticated;
> ```
>
> **Sobre `using (true)`:** esta es **una de las dos** unicas lugares del bootstrap
> donde la lectura anonima es abierta. Es correcto para contenido que es publico
> por definicion, y por eso el nombre de la policy dice `public_entries` y no
> algo con datos personales. Si tu tabla tiene datos de terceros, la policy va
> con filtro. Ver `## PACK: rpc-publicas`.
>
> Agrega el test pgTAP correspondiente en `supabase/tests/002_public_entries_test.sql`:
> que el `anon` lee, que el `authenticated` lee, y que un `service_role` puede
> escribir mientras el `anon` no.

```css
/* app/globals.css */
@import 'tailwindcss';

@theme {
  /* Tailwind v4 es CSS-first: los tokens se definen aca, no en un
     tailwind.config.js. `--color-*` genera las utilidades `bg-*`, `text-*`,
     etc. automaticamente. */
  --color-brand-50: oklch(0.97 0.02 260);
  --color-brand-500: oklch(0.62 0.19 260);
  --color-brand-600: oklch(0.55 0.20 260);
  --color-brand-900: oklch(0.28 0.09 260);
}

/* Reset minimo. Tailwind v4 ya trae su preflight. */
@layer base {
  body {
    @apply bg-white text-zinc-900 antialiased;
  }
}
```

```tsx
// app/error.tsx
'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="mx-auto max-w-2xl px-4 py-24 text-center">
      <h1 className="text-2xl font-bold">Algo salio mal</h1>
      <p className="mt-3 text-zinc-600">
        Vimos el problema. Proba de nuevo.
      </p>

      {/* El digest corre en produccion y sirve para buscar el error en el
          servidor de observabilidad. Es lo unico del error que se puede mostrar. */}
      {error.digest && (
        <p className="mt-2 font-mono text-xs text-zinc-400">
          Referencia: {error.digest}
        </p>
      )}

      <button
        onClick={reset}
        className="mt-6 rounded-lg bg-brand-600 px-4 py-2 text-white"
      >
        Reintentar
      </button>
    </main>
  );
}
```

### 7.8 `lib/utils.ts`, `components/ui/card.tsx`

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx';

/** Concatena clases condicionales. `clsx` se llama `cva` en algunos proyectos. */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
```

> Este archivo necesita la dependencia `clsx`. Agregala al `package.json` de la
> web en el bloque de dependencias:
>
> ```json
> "clsx": "^2.1.1",
> ```

```tsx
// components/ui/card.tsx
import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export function Card({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'rounded-lg border border-zinc-200 bg-white p-4 shadow-sm',
        className,
      )}
    >
      {children}
    </div>
  );
}
```

### 7.9 `.env.example` y `.env.local` de la web

```bash
# Copiala a .env.local. NUNCA commitees .env.local.
#
# NEXT_PUBLIC_* se hornea en el bundle en tiempo de build: queda visible para
# cualquiera que abra las devtools. Es correcto para la publishable key.
# Lo que jamas va aca es la secret key.

NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_TU_CLAVE_PUBLISHABLE_AQUI
```

`.env.local` con los mismos valores de `supabase start`.

### 7.10 `eslint.config.mjs`, `postcss.config.mjs`, test de web

```javascript
// eslint.config.mjs
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';

const compat = new FlatCompat({
  baseDirectory: dirname(fileURLToPath(import.meta.url)),
});

export default [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      '@typescript-eslint/no-unused-vars': 'error',
      '@typescript-eslint/consistent-type-imports': 'error',
    },
  },
];
```

```javascript
// postcss.config.mjs
const config = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
};

export default config;
```

```typescript
// vitest.config.ts
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts'],
    include: ['**/*.{test,spec}.{ts,tsx}'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./', import.meta.url)),
    },
  },
});
```

```typescript
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
```

```tsx
// components/ui/card.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Card } from '@/components/ui/card';

describe('Card', () => {
  it('renderiza sus hijos', () => {
    // ARRANGE & ACT
    render(
      <Card>
        <p>Contenido</p>
      </Card>,
    );

    // ASSERT
    expect(screen.getByText('Contenido')).toBeInTheDocument();
  });

  it('aplica las clases que le pasan', () => {
    // ARRANGE & ACT
    const { container } = render(
      <Card className="p-8">
        <p>Contenido</p>
      </Card>,
    );

    // ASSERT
    expect(container.firstChild).toHaveClass('p-8');
  });
});
```

### 7.11 `apps/web/Makefile` y `README.md`

```makefile
SHELL := /usr/bin/env bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

.PHONY: help
help: ## Muestra esta ayuda
	@grep -hE '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

.PHONY: install
install: ## Instala dependencias
	npm ci

.PHONY: dev
dev: ## Levanta el servidor de desarrollo
	npm run dev

.PHONY: build
build: ## Build de produccion
	npm run build

.PHONY: start
start: ## Sirve el build de produccion
	npm run start

.PHONY: lint
lint: ## ESLint
	npm run lint

.PHONY: typecheck
typecheck: ## Chequeo de tipos
	npm run typecheck

.PHONY: test
test: ## Tests unitarios
	npm run test

.PHONY: check
check: lint typecheck test ## lint + typecheck + test
	@echo "ok: web"

.PHONY: audit
audit: ## npm audit con nivel high
	npm run audit

.PHONY: env-local
env-local: ## Copia .env.example a .env.local
	@cp .env.example .env.local
	@$(MAKE) --no-print-directory env-check

.PHONY: env-check
env-check: ## Verifica que .env.local tenga valores
	@if grep -q 'TU_CLAVE_PUBLISHABLE_AQUI' .env.local 2>/dev/null; then \
		echo "FALLA: la publishable key sigue siendo el placeholder."; exit 1; \
	fi
	@echo "  ok    .env.local parece completo"

.PHONY: clean
clean: ## Borra .next y node_modules
	rm -rf .next node_modules
```

```markdown
# {{NOMBRE_PROYECTO}} (web)

## Requisitos

- Node 20+ (`nvm use`)
- Supabase local corriendo (ver `make db-up` en la raiz)

## Arranque

```bash
make install
make env-local
make dev        # http://localhost:{{PUERTO_WEB}}
```

## Estructura

```
app/          rutas del App Router. Un archivo por ruta.
lib/supabase/ los dos clientes. Ver abajo.
components/   componentes de UI sin logica de datos.
```

## El patron de Supabase

Dos clientes, y la diferencia es **cuando se ejecuta**:

| Archivo | Donde corre | Para que |
|---|---|---|
| `lib/supabase/client.ts` | Navegador (Client Component) | Eventos del usuario: formularios, Realtime |
| `lib/supabase/server.ts` | Node (Server Component, Action, Route Handler) | Render y lectura de datos |

Reglas:

1. `createClient()` de `server.ts` es `async` porque usa `cookies()`.
2. `createClient()` de `client.ts` se llama **a nivel de modulo**, no dentro del
   componente. Adentro se crea uno nuevo en cada render.
3. Las cookies se escriben solo desde Server Actions y Route Handlers, nunca
   durante el render.
4. `NEXT_PUBLIC_*` queda en el bundle. Jamas la secret key.

## Variables

| Variable | Donde | Visible |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | bundle | si |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | bundle | si |
| `SUPABASE_SERVICE_ROLE_KEY` | servidor | **no** |

La publishable key es publica por diseno: viaja en el bundle y lo unico que
protege son las policies RLS. La secret key saltea RLS y jamas va en el cliente.

## Pendientes

- [ ] **Auth en la web.** La web del bootstrap es publica. Si necesita sesiones,
      ver `## PACK: auth` en `PROMPT-BOOTSTRAP-MONOREPO.md`.
- [ ] **Deploy.** Configurar Vercel o el host que corresponda, con las
      variables de `NEXT_PUBLIC_*` en los settings del proyecto.
- [ ] **Dominio y HTTPS.** Configurar los redirect URLs de Auth si se agrega
      auth.
- [ ] **Imagenes y OG metadata.** `metadataBase` y `openGraph` para compartir
      links en redes.
```

> **VERIFICAR FASE 7**

```bash
cd apps/web
make install
cp .env.example .env.local
npm run lint
npm run typecheck
npm run test -- --run
npm run build
npm run start &
curl -s http://localhost:{{PUERTO_WEB}} | grep -q 'Entradas publicas' && echo "ok: la landing renderiza"
```

---

## FASE 8 -- Verificacion final

### 8.1 Checklist

Corre esto en orden. Cada item es un comando, no una opinion.

```bash
# 1. Herramientas
make doctor

# 2. Nada sensible trackeado
make git-verify
make git-history

# 3. Base de datos
supabase start
supabase db reset
supabase test db

# 4. Mobile
make -C apps/mobile install
make -C apps/mobile l10n
make -C apps/mobile gen
make -C apps/mobile analyze          # 0 problemas, 0 warnings
make -C apps/mobile test             # todos pasan
make -C apps/mobile format           # formatea; despues analyze de nuevo

# 5. Web
make -C apps/web install
make -C apps/web lint
make -C apps/web typecheck
make -C apps/web test
make -C apps/web build

# 6. Todo junto
make check
```

### 8.2 Los cinco tests que tienen que existir

Si falta alguno, el bootstrap esta incompleto:

1. **`test/core/session/current_user_stub_test.dart`** -- verifica que el stub
   devuelve `null`. Si falla, el nucleo asumio identidad en algun lado.
2. **`test/core/error/failures_test.dart`** -- verifica las firmas exactas de
   `Failure`. Si falla, hay una segunda definicion en otro archivo.
3. **`test/core/utils/error_handler_test.dart`** -- fija los strings del
   proveedor. Es la unica defensa contra que cambien en silencio.
4. **`test/features/.../{{FEATURE_EJEMPLO}}_cubit_test.dart`** -- verifica
   `[Loading, Loaded]` y `[Loading, Error]`. Si falla, la maquina de estados no
   esta completa.
5. **`supabase/tests/001_schema_basico_test.sql`** -- verifica que no hay tablas
   sin RLS y que no hay funciones `security definer` sin `search_path`. Si
   falla, hay un problema de seguridad en el schema.

### 8.3 El grep que verifica que no hay auth

```bash
# Debe dar 0 resultados (o solo las menciones explicitas de este prompt).
cd apps/mobile
grep -rn "login\|signIn\|sign_in\|password\|currentUser\|authState\|UserSession" \
  lib/ --include="*.dart" | grep -v "^\s*//"

# Y en la web:
cd apps/web
grep -rn "middleware\|'use server'\|signIn\|signOut\|auth.getUser\|auth.getSession" \
  app/ lib/ --include="*.ts" --include="*.tsx"

# Y en el backend:
cd supabase
grep -n "auth\." migrations/*.sql   # solo el helper de test_helpers.create_user
```

> Si alguno devuelve resultados, el nucleo genero autenticacion que no estaba
> pedida. Borrala antes de seguir.

### 8.4 Reporte final

El agente cierra con un reporte en Markdown, sin pegar codigo generado:

```markdown
# Bootstrap completo

## Archivos creados

| Capa | Cantidad |
|---|---|
| Raiz | 18 |
| supabase/ | 4 |
| apps/mobile/lib/core/ | 24 |
| apps/mobile/lib/features/ | 15 |
| apps/mobile/test/ | 25 |
| apps/web/ | 22 |
| .github/workflows/ | 4 |

## Archivos omitidos

| Archivo | Motivo |
|---|---|

## Decisiones donde el prompt era ambiguo

1. ...
2. ...

## TODO: que quedo sin implementar

Por capa, con la ruta del archivo. **No con una linea agregada a un reporte.**
Estos TODO van *dentro* de los archivos, y aca solo se listan.

## Verificacion

| Comando | Resultado |
|---|---|
| `make -C apps/mobile analyze` | 0 problemas |
| `make -C apps/mobile test` | N tests, todos pasan |
| `supabase test db` | 7 tests, todos pasan |
| `make -C apps/web lint` | sin errores |
| `make -C apps/web typecheck` | sin errores |
| `make -C apps/web build` | ok |

## Packs disponibles

Ninguno aplicado. Este proyecto **no tiene autenticacion**.

Para agregarla despues: pegar el bloque `## PACK: auth` del final de
`PROMPT-BOOTSTRAP-MONOREPO.md`.

## Pendientes manuales

Los que requieren una herramienta que no esta en este entorno: firma de
release, flavors de iOS, deploy de la web, configuracion de Sentry.
```

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

# APENDICES

## Apéndice A -- Arbol completo generado

```
{{NOMBRE_PROYECTO}}/
│
├── apps/mobile/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── core/
│   │   │   ├── common/usecase.dart
│   │   │   ├── config/app_config.dart
│   │   │   ├── constants/constants.dart
│   │   │   ├── data/local/
│   │   │   │   ├── isar_service.dart
│   │   │   │   └── isar_models/cached_entry.dart (+ .g.dart)
│   │   │   ├── di/{service_locator,external_module}.dart (+ .config.dart)
│   │   │   ├── error/{failures,exceptions}.dart
│   │   │   ├── network/network_info.dart
│   │   │   ├── routing/app_router.dart
│   │   │   ├── services/cache_manager.dart
│   │   │   ├── session/{current_user,current_user_stub}.dart
│   │   │   ├── theme/app_theme.dart
│   │   │   ├── utils/{app_info,error_handler,snackbar_helper,validators}.dart
│   │   │   └── widgets/
│   │   │       ├── app_button.dart
│   │   │       ├── app_card.dart
│   │   │       ├── app_text_field.dart
│   │   │       ├── empty_state.dart
│   │   │       ├── error_view.dart
│   │   │       ├── loading_indicator.dart
│   │   │       ├── pull_to_refresh_wrapper.dart
│   │   │       └── skeleton.dart
│   │   ├── features/{{FEATURE_EJEMPLO}}/
│   │   │   ├── data/
│   │   │   │   ├── datasources/{{FEATURE_EJEMPLO}}_local_data_source.dart
│   │   │   │   ├── models/{{FEATURE_EJEMPLO}}_model.dart
│   │   │   │   └── repositories/{{FEATURE_EJEMPLO}}_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entities/{{FEATURE_EJEMPLO}}_entity.dart
│   │   │   │   ├── repositories/{{FEATURE_EJEMPLO}}_repository.dart
│   │   │   │   └── usecases/
│   │   │   │       ├── create_{{FEATURE_EJEMPLO}}_usecase.dart
│   │   │   │       ├── delete_{{FEATURE_EJEMPLO}}_usecase.dart
│   │   │   │       └── get_{{FEATURE_EJEMPLO}}s_usecase.dart
│   │   │   └── presentation/
│   │   │       ├── cubit/
│   │   │       │   ├── {{FEATURE_EJEMPLO}}_cubit.dart
│   │   │       │   └── {{FEATURE_EJEMPLO}}_state.dart
│   │   │       ├── pages/
│   │   │       │   ├── {{FEATURE_EJEMPLO}}_detail_page.dart
│   │   │       │   └── {{FEATURE_EJEMPLO}}_page.dart
│   │   │       └── widgets/{{FEATURE_EJEMPLO}}_tile.dart
│   │   └── l10n/
│   │       ├── arb/{app_es.arb,app_en.arb}
│   │       ├── gen/                                   (gitignored)
│   │       └── l10n.dart
│   ├── test/
│   │   ├── core/
│   │   │   ├── common/usecase_test.dart
│   │   │   ├── error/{exceptions_test,failures_test}.dart
│   │   │   ├── session/current_user_stub_test.dart
│   │   │   ├── theme/app_theme_test.dart
│   │   │   ├── utils/{error_handler_test,validators_test}.dart
│   │   │   └── widgets/  (7 archivos, uno por widget)
│   │   ├── features/{{FEATURE_EJEMPLO}}/
│   │   │   ├── data/
│   │   │   │   ├── datasources/..._local_data_source_test.dart
│   │   │   │   ├── models/..._model_test.dart
│   │   │   │   └── repositories/..._repository_impl_test.dart
│   │   │   ├── domain/usecases/  (3 archivos)
│   │   │   └── presentation/
│   │   │       ├── cubit/..._cubit_test.dart
│   │   │       └── pages/..._page_test.dart
│   │   ├── fixtures/{{FEATURE_EJEMPLO}}.json
│   │   └── helpers/fixture_reader.dart
│   ├── assets/
│   ├── android/ ios/
│   ├── .env .env.example
│   ├── .fvmrc .fvm/fvm_config.json
│   ├── analysis_options.yaml
│   ├── l10n.yaml
│   ├── pubspec.yaml
│   ├── Makefile
│   └── README.md
│
├── apps/web/
│   ├── app/
│   │   ├── error.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── lib/
│   │   ├── supabase/{client,server}.ts
│   │   └── utils.ts
│   ├── components/ui/{card.tsx,card.test.tsx}
│   ├── public/
│   ├── .env.local .env.example
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── tsconfig.json
│   ├── vitest.config.ts vitest.setup.ts
│   ├── Makefile
│   └── README.md
│
├── supabase/
│   ├── config.toml
│   ├── migrations/
│   │   ├── README.md
│   │   ├── 00001_public_entries.sql
│   │   └── 00002_create_profiles.sql      (si pegaste PACK: auth)
│   ├── tests/
│   │   ├── 000_helpers.sql
│   │   ├── 001_schema_basico_test.sql
│   │   ├── 002_profiles_test.sql         (si pegaste PACK: auth)
│   │   └── 003_rpc_public_catalog_test.sql(si pegaste PACK: rpc-publicas)
│   ├── functions/.gitkeep
│   └── seed.sql
│
├── docs/
│   ├── adr/0001-estructura-del-monorepo.md
│   └── openspec/.gitkeep
│
├── tools/.gitkeep
├── .github/
│   ├── ISSUE_TEMPLATE/{bug_report,feature_request}.yml
│   └── workflows/{mobile,db,web,security}.yml
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json.example
├── AGENTS.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── README.md
├── SECURITY.md
├── Makefile
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .nvmrc
├── commitlint.config.js
└── dependabot.yml
```

## Apéndice B -- Tabla de convenciones

Referencia rapida. Todo lo que hay aca estaavecitado en `AGENTS.md`; esta la
version completa con el por que.

### Flutter

| Concepto | Convencion | Por que |
|---|---|---|
| Organizacion | Feature-first: `features/<f>/{data,domain,presentation}` | Un cambio de negocio no hace saltar entre 5 carpetas |
| `lib/` | 3 entradas: `main.dart`, `core/`, `features/` | Si `lib/` tiene `models/` sueltas, se vuelve horizontal |
| Dependencia | `presentation -> domain <- data`; `core` no importa `features` | Un `core` que importa una feature es un ciclo |
| Imports | Siempre `package:` | Un import relativo se rompe al mover el archivo |
| Presentacion | `pages/`, `widgets/`, `utils/`, `cubit/` | Consistencia; `screens/` y `pages/` conviven mal |
| DataSource | `datasources/`, archivo `<algo>_data_source.dart` | **Dos palabras.** La forma de una palabra se ve en codigo viejo ajeno |
| Repositorio | `<algo>_repository.dart` + `_impl.dart` | El `Impl` separado del contrato, para poder mockear |
| Entidad | `<algo>_entity.dart` | Marca visual de "esto es dominio puro" |
| Modelo | `<algo>_model.dart`, `fromJson`/`toJson` explicitos | Sin `json_serializable`: el `.g.dart` esconde el mapeo |
| Use case | `<verbo>_<sustantivo>_usecase.dart`, con sufijo `usecase` | `sign_in_usecase.dart` y no `sign_in.dart` |
| Params | `<UseCase>Params`, `const`, `Equatable`, mismo archivo | Vive junto al use case que lo consume |
| Cubit | `Cubit`, nunca `Bloc` | Menos ceremonia para el 90% de las pantallas |
| Estado | `part of` del cubit, `sealed` + `final class` | El cubit tiene el estado sin importar el archivo |
| Variantes | `XCubit -> XState`, variantes `XLoaded` sin sufijo `State` | `RaffleListLoaded`, no `RaffleListStateLoaded` |
| Error | `XError(String message)` | La UI muestra texto, no tipos |
| `Either` | `package:fpdart/fpdart.dart` | `dartz` sin mantenimiento |
| Dependencias | GetIt + `injectable`, alias `sl` | El registro vive al lado de cada clase, no en un archivo compartido. Ver ADR 0002 |
| Registros | `@lazySingleton` en data/domain; `@injectable` (factory) en cubits de pantalla | Un cubit singleton fuga al rotar |
| Codegen de DI | `service_locator.config.dart` commiteado y regenerado con `make gen` | Si lo regeneras y hay diff, alguien anoto algo y no corro `make gen` |
| `SupabaseClient` | Se inyecta desde el `@module`, con `Supabase.instance.client` | GetIt guarda la referencia; la fuente unica sigue siendo la libreria |
| Env | `flutter_dotenv`, todo acceso via `AppConfig` | Un punto de lectura de credenciales, no veinte |
| Config | `AppConfig` (del `.env`) vs `AppConstants` (hechos) | Lo que varia por entorno se separa de lo que no |
| Cache | Isar community, arranque en `core/data/local/` | El cache es global; sus schemas tambien |
| TTL | `cachedAt` + `expiresAt` en toda coleccion | Un cache sin TTL es una fuente de datos obsoleta |
| Namespaces | Prefijo por feature en la clave del cache | Una coleccion compartida sin prefijo devuelve todo |
| Lint | `very_good_analysis` + `bloc_lint`, con la lista de `ignore` | Cada excepcion justificada al lado |
| Tests | `mocktail` + `bloc_test`, espejando `lib/` | Una ruta a un test te dice donde esta el codigo |
| Fixtures | JSON en `test/fixtures/` + `fixture_reader.dart` | El path del fixture va en el error |
| AAA | `// ARRANGE` / `// ACT` / `// ASSERT`, en mayusculas | Legible de un vistazo, sin depender del IDE |
| Prefijos de test | `mock*` para mocks, `t*` para datos | Se distingue el doble del dato real |
| Deprecaciones | El SDK exacto en `.fvmrc`, no `^3.11.0` | Dos personas con SDK distinto, bugs distintos |

### Backend

| Concepto | Convencion | Por que |
|---|---|---|
| Nombre de migration | `00001_nombre.sql`, ordinal de 5 digitos | Un timestamp no ordena; el ordinal deja ver los huecos |
| Nombre de policy | `<Actor> can <accion> <alcance>` | `Anyone can read public raffles` se lee solo |
| `TO` en la policy | Siempre explicito | `USING (true)` sin `to anon` es un invitation a equivocarse |
| RLS | Habilitada en **toda** tabla | RLS sin policy es denegar todo, y eso es una decision |
| `force row level security` | En tablas donde el owner no debe saltarse las policies | Sin esto, el owner ve todo |
| `security definer` | Siempre con `set search_path = ''` + esquemas calificados | Sin eso, la funcion es secuestrable |
| `grant execute` | `revoke from public` y `grant` a quien corresponda | El default de Postgres es permitir a todos |
| Columns nuevas | `NOT NULL DEFAULT`, siempre | Agregar una NOT NULL sin default rompe clientes viejos |
| Tests | pgTAP, en el mismo PR que la migration | Una migration sin test entra y no vuelve |
| Test de RLS | Feliz + `anon` + ajeno + dueno | Un test de RLS que solo prueba el camino feliz no prueba RLS |
| Secrets | La secret key nunca en el cliente | Salta RLS |

### Web

| Concepto | Convencion | Por que |
|---|---|---|
| Directorio | `app/`, `lib/`, `components/`, sin `src/` | El default de Next; `src/` es costumbre, no necesidad |
| Alias | `@/* -> ./*` | Sin `src/`, el alias apunta a la raiz |
| Versiones | `next` y `eslint-config-next` con version exacta | Un minor de Next rompe builds sin avisar |
| Supabase | `client.ts` (navegador) y `server.ts` (Node), dos archivos | El error aparece en el import, no en el primer click |
| Cliente de browser | `createBrowserClient()` a **nivel de modulo** | Adentro del componente se crea uno por render |
| Sesion en el servidor | `await cookies()`, `getAll`/`setAll` | Durante el render son read-only; por eso el `try/catch` |
| Verificacion de sesion | `auth.getUser()`, **nunca** `getSession()` | `getSession()` no valida el JWT. Es la diferencia entre verificar y confiar |
| Mutaciones | Server Actions (`'use server'`), no Route Handlers | Formularios sin logica de cliente ni exposure de claves |
| `next` en redirects | Validar que empieza con `/` y no con `//` | Sin eso, el login es un redirector abierto |
| Tailwind | v4 CSS-first con `@theme` | Un `tailwind.config.js` en v4 mezcla dos sistemas |
| Fontes | `next/font`, nunca `<link>` a una CDN | Sin request extra y sin CLS |
| Seguridad | Headers en `next.config.ts` | Centralizado, no disperso por componente |

## Apéndice C -- Decisiones de diseño, con sus contras

Cada seccion explica por que se eligio algo y que se pierde. Las partes "que se
pierde" son las que hay que leer antes de decidir que el tradeoff vale.

### 1. `injectable`, no registro manual

**Se elige:** anotaciones en cada clase + `service_locator.config.dart`
generado. `service_locator.dart` solo declara `sl` y `configureDependencies()`.

**Gana:** el registro vive al lado de la clase que se registra. Agregar una
feature es anotar cinco clases y correr `make gen`; nadie toca un archivo que
todas las features comparten, asi que dos features en paralelo no chocan en el
mismo diff. Cuando la abstracta cambia de implementacion, el cambio es de una
linea en la clase, no de un closure en un archivo de 400. Y el `@module` da un
lugar declarado para lo externo (`Isar`, `SupabaseClient`, `http.Client`) que la
cascada manual repartia entre comentarios.

**Se pierde:**

- Un archivo mas commiteado (`service_locator.config.dart`) que puede quedar
  viejo. Si alguien anota una clase y no corre `make gen`, el error no es de
  compilacion: aparece al primer resolve, con un `X is not registered`. Por eso
  CI regenera y hace `git diff --exit-code`.
- `grep sl<` deja de ser el mapa de dependencias. El mapa ahora es
  `grep '@lazySingleton\|@injectable\|@LazySingleton'` sobre `lib/`.
- Dos paquetes de codegen mas, con un rango de resolucion ajustado:
  `injectable_generator` y `isar_community_generator` se pelean por `analyzer`
  (ver ADR 0002, Versiones). Subir de Flutter obliga a revisar los dos juntos.
- Anotar cada clase. Es mecanico, pero es codigo que hay que escribir.

**Cuando cambiar:** a `inject.dart` si el codegen se vuelve lento o si queres
un grafo verificado en compile time. A registro manual si el proyecto se
congela y nadie va a agregar features: sin cambios, no hay nada que regenerar.

### 2. El nucleo no asume autenticacion

**Se elige:** identidad declarada y vacia (`CurrentUser` + `CurrentUserStub`),
auth en un pack aparte.

**Gana:** el nucleo sirve para una app con usuarios y para una sin ellos. La
pregunta "esta app tiene usuarios" la responde el dueno del proyecto, no el
bootstrap. Un `/login` generado compila, asi que el error aparecia meses despues,
cuando nadie recordaba por que estaba.

**Se pierde:** un proyecto con auth necesita dos pasos (pegar el pack) y un
archivo que borrar (`current_user_stub.dart`). Es un paso extra para el caso
comun.

**Por que no importa tanto:** el caso comun **es** con auth. La friccion esta en
la copia del prompt, una vez. El costo del error, en cambio, lo paga el que
herede el proyecto en un ano, y paga porque el codigo estaba bien.

### 3. Un slice vertical descartable

**Se elige:** `features/example/` con datasource en memoria y `make
drop-feature`.

**Gana:** al terminar la PARTE A, el proyecto esta verificado de punta a punta: DI,
router, l10n, Isar, cubit, Either, tests y el ciclo completo de una operacion. El
slice existe para poder borrar el acoplamiento: si no podes borrarlo sin tocar
nada mas, hay un problema, y lo encontraste en el momento de borrar y no tres
meses despues.

**Se pierde:** ~15 archivos que no van a ser codigo de producto. Y el `// TODO:`
del datasource de red queda como recordatorio de algo que quizas nunca
implementes.

**Alternativa descartada:** generar solo `core/` y dejar el slice en la
documentacion. El proyecto queda "limpio" y sin verificar hasta la primera
feature real, que es donde aparecen los errores de cableado.

### 4. `ErrorHandler` con strings, no l10n de errores

**Se elige:** un mapa de strings del proveedor a texto en español.

**Gana:** resuelve el problema mas comun de una app con l10n: el mensaje crudo de
Supabase ("Invalid login credentials") nunca llega a la UI. Y funciona sin
tener l10n implementado.

**Se pierde:** dos cosas.

1. **Los mensajes del proveedor son un contrato no documentado.** Cuando
   Supabase los cambia, el lookup falla, cae en `_fallback`, y el usuario ve
   "Algo salio mal" en vez de un mensaje util. Los tests del archivo son la unica
   defensa: cuando el string cambia, el test falla. Sin tests, el archivo
   degrada en silencio.

2. **Es la razon por la que el l10n puede quedarse sin implementar.** Con un
   traductor de errores funcionando, nadie siente la falta de ARB. Y con el
   tiempo aparecen strings en espanol en tres lugares (`ErrorHandler`,
   `AppConstants`, y literals en los cubits) que ya no se traducen.

**La migracion, si la hacia falta:** agregar un enum `FailureCode` al dominio,
mapear el string crudo al code **una vez** en el repositorio, y dejar el mensaje
para el usuario en el ARB. El string crudo deja de cruzar la frontera de `data`.
El pack de auth, paso P8, ya trae la forma de hacerlo.

### 5. `Failure` con `code` y `ServerException` con `statusCode`

**Se elige:** dos campos, en dos capas.

**Gana:** el codigo HTTP es un detalle del transporte; el `code` de negocio es
del dominio. El `Failure` que ve la UI lleva lo que la UI necesita.

**Se pierde:** hay que leer dos campos en vez de uno, y es facilollars. Cuando el
mensaje que se muestra necesita el status HTTP, hay que pasarlo a mano del
`ServerException` al `ServerFailure`.

**No confundir:** son cosas distintas. Un 404 de una RPC y un 404 de "este
elemento no existe en tu cuenta" son el mismo status con codigos distintos.

### 6. Comparar errores por `code`, no por mensaje

**Se elige:** comparar el tipo del `Failure` o un enum propio.

**Gana:** el mensaje de gotrue no esta tipado y cambia entre versiones. Un
`failure.message == 'email_not_confirmed'` compila, funciona hoy, y se rompe
cuando una dependencia actualiza.

**Se pierde:** hay que agregar el enum y el mapeo. Un `==` a un string es una
linea; el enum son quince.

### 7. RLS habilitado sin policies = denegar todo

**Se elige:** toda tabla nueva empieza con RLS habilitado y sin policies.

**Gana:** el default es seguro. Una tabla recien creada es privada hasta que
alguien decide abrirla, y esa decision queda escrita en el diff. Al reves —sin
RLS hasta que la agregues—, el default es expuesto.

**Se pierde:** un desarrollador nuevo ve "no puedo leer mi tabla" y no entiende
por que. El `001_schema_basico_test.sql` y el comentario en el README de
migrations existen por eso.

### 8. `SECURITY DEFINER` con `search_path` acotado

**Se elige:** `set search_path = ''` con todos los nombres calificados.

**Gana:** sin esto, la funcion resuelve nombres por el `search_path` de quien la
llama. Un atacante con `CREATE` en un schema pone un objeto con el nombre de
vuestra tabla interna y ejecuta su codigo dentro de la funcion, con los permisos
de la funcion. Es un takeover, no una fuga de datos.

**Se pierde:** verbosidad. `public.catalogo_items` en vez de `catalogo_items`, en
cada query de la funcion.

### 9. El `catch` especifico en el repositorio

**Se elige:** `on CacheException catch`, `on ServerException catch`, sin
`on Object catch` al final.

**Gana:** un `TypeError` de un bug de mapeo se rompe en los tests en vez de
aparecer al usuario como "Algo salio mal. Tipo 'Null' no es un subtipo de
'String'".

**Se pierde:** una excepcion no prevista sube hasta el borde de la app y la
mata. Es el comportamiento correcto: una excepcion no prevista es un bug, y un
bug deberia ser ruidoso.

### 10. `skipLibCheck: true` en `tsconfig.json`

**Se elige:** activar.

**Gana:** no se pierde tiempo arreglando errores de tipos en `node_modules`, que
no son tuyos.

**Se pierde:** un error real de tipos en una dependencia queda oculto. El
`npm audit` y el chequeo de versiones cubren parte de eso.

### 11. Pinned versions vs rangos

**Se elige:** `next` y `eslint-config-next` con version exacta. Todo lo demas
con `^`.

**Gana:** Next es estricto con las personalizaciones y las deprecaciones entre
minors son reales. Un `^16.2.6` deja que un minor rompa el build un martes.

**Se pierde:** hay que mover la version a mano o esperar a Dependabot. Un
`package.json` con todo pineado es mas ruido; se eligio solo donde el costo del
problema es alto.

### 12. La deprecacion de PROMPT-SCAFFOLD.md

`PROMPT-SCAFFOLD.md` sigue en el repo, con una nota al principio que apunta acá.
Se conserva en vez de borrarlo porque:

- Alguien lo puede estar usando ahora mismo.
- Los repos publicos no se borran: quien lo.Find en un buscador sigue llegando.
- Comparar el prompt viejo con este es la forma mas rapida de entender que
  cambio y por que.

El prompt viejo era solo Flutter, sin Next.js, con auth asumido, DI por
codegen, y 17 defectos concretos. Este los corrige.

---

## Preguntas que este prompt no responde

Decidaselas antes de arrancar la PARTE A. No son bloqueantes: el prompt genera el
proyecto igual. Pero cada una cambia el codigo que genera.

1. **La app tiene usuarios o no.** Si no, no pegues `## PACK: auth`. Si si,
   pegalo desde el principio: agregar auth despues significa tocar el router, el
   `main.dart`, el DI y dos migraciones, y el cubit de auth tiene que conocer el
   router desde el dia uno.
2. **El backend es publico o privado.** Si publico, `## PACK: rpc-publicas` y la
   web seHFace anonima. Si privado, es `## PACK: auth` y nada mas.
3. **Where va la identidad.** `CurrentUserStub` esta bien si no hay usuarios. Con
   usuarios, pegá `CurrentUserSupabase`. Si tu app tiene identidad propia (un
   `deviceId`, una sesion corporativa), implementa `CurrentUser` a mano y borra las
   dos versiones.
4. **Si el l10n se va a usar de verdad.** El prompt deja el pipeline armado y las
   claves cargadas. `ErrorHandler` traduce los errores en espanol sin pasar por
   ARB, asi que es facil quedarse con la mitad del sistema. Si no vas a usar ARB,
   borralo: un pipeline a medio usar es peor que ninguno.
5. **Si el cache local es necesario.** Isar arranca aunque tu app sea online-only
   y no cachee nada. Si no vas a cachear, `current_user_stub.dart` sigue siendo la
   identidad correcta, pero `core/data/local/` no aporta y `core/services/
   cache_manager.dart` tampoco.
6. **Frecuencia de deploy.** Si hay varios deploys por dia, el slice de ejemplo
   es mas util todavia: verificar el pipeline con una feature descartable en vez
   de con la feature real.

---

## Versionado de este prompt

| Version | Que cambio |
|---|---|
| v2 (este) | Nucleo sin auth + packs. DI con `injectable` (registro por anotación, `@module` para lo externo, `service_locator.config.dart` commiteado). `*_data_source.dart`. `core/routing/`. `part of` en estados. `core/session/current_user.dart`. Slice descartable + `make drop-feature`. `ErrorHandler`. Tests pgTAP de seguridad como default. Migraciones con ordinal. Use cases con sufijo `usecase` en archivo y clase (`get_raffles_usecase.dart`, `GetRafflesUseCase`). |
| v1 | `PROMPT-SCAFFOLD.md`: Flutter unicamente, auth asumido, `*_datasource.dart`, `core/router/`. 17 defectos. |

**Cambios grandes respecto de la v1**, si venis de ahi:

1. **La auth paso deassumption a pack.** Es el cambio de fondo.
2. **`*_datasource.dart` -> `*_data_source.dart`.** Dos palabras.
3. **`core/router/` -> `core/routing/`.**
4. **Los estados pasaron a `part of` en vez de import.**
5. **`Failure` paso de `statusCode` a `code`, con `required message`.**
6. **Apareció `core/session/current_user.dart`** en lugar de acoplar el router a
   la sesion.
7. **Apareció `ErrorHandler`.**
8. **Se agrega un slice vertical verificable y su comando de borrado.**
9. **Los tests pgTAP de seguridad (RLS, `search_path`) son obligatorios**, no
   opcionales.
10. **Apareció la web Next.js completa**, con el patron de dos clientes de
    Supabase.
11. **Las migraciones usan ordinal de 5 digitos**, no timestamp.