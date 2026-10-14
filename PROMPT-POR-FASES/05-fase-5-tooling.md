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

