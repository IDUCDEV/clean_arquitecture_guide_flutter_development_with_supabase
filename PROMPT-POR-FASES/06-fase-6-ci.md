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

