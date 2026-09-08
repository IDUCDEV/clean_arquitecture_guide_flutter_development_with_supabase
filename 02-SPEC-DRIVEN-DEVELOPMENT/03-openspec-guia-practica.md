# 03 - OpenSpec: Guía Práctica

> La herramienta líder de SDD. Specs como markdown vivo en tu repositorio, ejecutables por 40+ agentes de IA.

---

## Qué es OpenSpec

OpenSpec es un framework ligero de Spec Driven Development, open source (MIT), creado por Fission-AI. Tiene 66.9k estrellas en GitHub, más de 265k desarrolladores al mes, y crea una nueva spec cada dos segundos. Es la herramienta más adoptada para implementar SDD en proyectos reales.

**Filosofía:**
- Fluid, no rígido
- Iterativo, no waterfall
- Fácil, no complejo
- Diseñado para brownfield (código existente), no solo greenfield
- Escalable de proyectos personales a empresas

**No necesita:** API keys, MCP servers, ni configuración compleja.

---

## Instalación

```bash
# Requiere Node.js 20.19.0 o superior
npm install -g @fission-ai/openspec@latest
```

También soporta pnpm, yarn (solo Classic 1.x), bun, deno y nix. Detalles en [openspec.dev/docs/installation](https://openspec.dev/docs/installation).

**Verificar instalación:**
```bash
openspec --version
```

---

## Inicialización en un proyecto Flutter

```bash
# Navega a la raíz de tu proyecto Flutter
cd mi-proyecto-flutter

# Inicializa OpenSpec (interactive: pregunta qué agentes usas)
openspec init

# O saltar el picker:
openspec init --tools opencode
```

**Qué crea:**
```
mi-proyecto-flutter/
├── openspec/
│   ├── config.yaml           ← Configuración del proyecto (contexto, reglas, operaciones)
│   ├── specs/                ← Specs vivas del proyecto
│   │   └── .gitkeep
│   └── changes/              ← Cambios en progreso
│       └── archive/          ← Cambios completados se mueven aquí
│           └── .gitkeep
├── AGENTS.md                 ← Constitución del proyecto (instrucciones para agentes IA)
└── .opencode/                ← Archivos de configuración para OpenCode
    ├── skills/               ← Skills (instrucciones workflows)
    │   ├── openspec-explore/
    │   ├── openspec-propose/
    │   ├── openspec-apply-change/
    │   └── ...
    └── commands/             ← Comandos slash (entry points alternativos)
        ├── opsx-explore.md   → /opsx-explore
        ├── opsx-propose.md   → /opsx-propose
        └── ...
```

**`openspec init` pregunta qué agentes usas y genera sus archivos de configuración.** Cada agente recibe skills + commands en su formato nativo (`.claude/skills/` + `.claude/commands/opsx/`, `.cursor/skills/` + `.cursor/commands/`, etc.). Ver [supported tools](https://openspec.dev/docs/supported-tools) para la matriz completa (40+ herramientas).

> **Verificado contra CLI v1.11.0** (`@fission-ai/openspec`). Si tu versión difiere, ejecuta `openspec --version` y `openspec update` tras instalar.

---

## Skills vs Commands (Delivery modes)

OpenSpec instala cada workflow en **dos formas**:

| Forma | Ejemplo (OpenCode) | Qué es |
|-------|-------------------|--------|
| **Skill** | `openspec-apply-change` | Instrucciones que el agente carga automáticamente |
| **Command** | `/opsx-apply` | Entry point slash que escribes tú |

Las dos son funcionalmente idénticas. Skills son el estándar más nuevo y compartido entre herramientas; commands son el entry point para herramientas que no pueden invocar skills directamente.

**Delivery modes** (configurados con `openspec config profile`):

| Mode | Qué instala |
|------|-------------|
| `both` (default) | Skills + commands |
| `skills` | Solo skills |
| `commands` | Solo commands |

```bash
# Cambiar delivery mode
openspec config set delivery skills

# Picker interactivo de profiles y delivery
openspec config profile
```

---

## Workflow completo (5 pasos)

```
1. Explore  →  2. Propose  →  3. Review  →  4. Apply  →  5. Archive
   pensar        planificar     corregir      construir     consolidar
```

### Paso 1: Explorar antes de decidir

```bash
# En tu agente IA (OpenCode, Claude Code, Cursor, etc.)
/opsx-explore
```

El agente lee tu codebase y te ayuda a pensar antes de escribir nada. **No crea archivos ni escribe código.** Útil cuando no estás seguro de cómo implementar algo.

**Ejemplo:**
```
Tú: /opsx-explore
IA: ¿Qué quieres explorar?
Tú: Quiero agregar modo oscuro pero no estoy seguro de cómo hacerlo limpiamente
IA: [lee tu setup de temas] La ruta más limpia: ThemeMode en el Cubit raíz +
    ThemeData claro/oscuro en app_theme.dart, persistido en SharedPreferences.
    Sin dependencias nuevas. ¿Lo acotamos?
Tú: Sí, hagámoslo
```

### Paso 2: Proponer un cambio

```bash
/opsx-propose add-dark-mode
```

OpenSpec genera una carpeta completa de cambio:

```
openspec/changes/add-dark-mode/
├── proposal.md       ← Por qué y qué cambia
├── specs/            ← Requirements y escenarios
│   └── theme/
│       └── spec.md
├── design.md         ← Decisiones técnicas (solo si aplica)
└── tasks.md          ← Checklist de implementación
```

**El agente genera esto automáticamente.** Tú solo revisas y ajustas.

### Paso 3: Revisar el plan

Antes de que el agente escriba código, revisas:
- `proposal.md` — ¿Estamos resolviendo el problema correcto?
- `specs/` — ¿Los requisitos son claros y verificables?
- `design.md` — ¿Las decisiones técnicas son coherentes con el codebase?
- `tasks.md` — ¿Las tareas están en el orden correcto?

**Tip:** usa `openspec show add-dark-mode --diff` para ver los diffs de requisitos contra las specs principales antes de archivar.

### Paso 4: Ejecutar

```bash
/opsx-apply-change
```

El agente implementa las tareas una por una:

```
✓ 1.1 ThemeCubit + estados sealed
✓ 1.2 Persistencia de preferencia
✓ 2.1 ThemeData claro/oscuro en app_theme.dart
✓ 2.2 Ruta y wiring en app_router.dart
```

**Si se interrumpe o agota contexto:** abre nueva sesión y vuelve a pedir apply. Reanuda en la primera tarea sin marcar.

### Paso 5: Archivar

```bash
/opsx-archive-change
```

El cambio se archiva en `openspec/changes/archive/YYYY-MM-DD-nombre/` y las deltas se fusionan con las specs principales. Listo para el siguiente feature.

---

## Qué son las specs en OpenSpec

Las specs son **markdown simple** con requisitos concretos y escenarios. No hay sintaxis especial que aprender.

**Ejemplo de spec:**
```markdown
ADDED Requirements

### Requirement: Theme selection
The app SHALL let users switch between light and dark themes,
defaulting to the system preference.

#### Scenario: User toggles dark mode
- **WHEN** the user clicks the theme toggle
- **THEN** the app switches to dark mode and persists the choice

#### Scenario: System preference detection
- **GIVEN** the user has not set a theme preference
- **WHEN** the app loads
- **THEN** the theme matches the system setting
```

**Cómo se organizan:**
```
openspec/specs/
├── auth-login/
│   └── spec.md
├── auth-session/
│   └── spec.md
├── checkout-cart/
│   └── spec.md
└── checkout-payment/
    └── spec.md
```

Cada spec vive en su carpeta, al lado del código que implementa. Cuando un agente necesita contexto, lee la spec. Cuando alguien nuevo se une al equipo, browsa la biblioteca.

**Delta specs** (en los cambios): solo describen lo que cambia, bajo headers `ADDED` / `MODIFIED` / `REMOVED` / `RENAMED`. Al archivar, se fusionan con las specs principales.

---

## Skills disponibles (12 workflows)

### Core (6 — instalados por defecto)

| Skill | Función |
|-------|---------|
| `openspec-explore` | Explorar opciones antes de decidir (no crea archivos) |
| `openspec-propose <nombre>` | Crear proposal + specs + design + tasks en un paso |
| `openspec-apply-change` | Ejecutar las tareas del cambio actual |
| `openspec-update-change` | Revisar coherencia y actualizar artefactos existentes |
| `openspec-sync-specs` | Fusionar deltas de specs con las specs principales (sin archivar) |
| `openspec-archive-change` | Archivar cambio completado y consolidar specs |

### Optional (6 — se agregan con `openspec config profile`)

| Skill | Función |
|-------|---------|
| `openspec-new-change` | Crear esqueleto vacío de cambio (modo artesano) |
| `openspec-continue-change` | Crear el siguiente artifact uno a uno |
| `openspec-ff-change` | Fast-forward: crear proposal + todos los artifacts en un solo paso |
| `openspec-verify-change` | Verificar que la implementación cumple las specs (solo reporte) |
| `openspec-bulk-archive-change` | Archivar varios cambios completados a la vez |
| `openspec-onboard` | Onboarding: aprender el workflow haciendo un cambio real (~15 min) |

> **Nota:** el nombre del skill puede variar como slash command según el agente. OpenCode usa `/opsx-explore`, Claude Code usa `/opsx:explore`, Cursor usa `/opsx-explore`. Los skill IDs (`openspec-explore`) son los mismos en todas las herramientas.

> **Dos estilos de arranque:** `openspec-propose` es el **modo copiloto** (la IA redacta la primera versión de proposal/spec/design/tasks y tú apruebas). `openspec-new-change` es el **modo artesano** (crea solo el esqueleto y lo llenas tú; la IA refina después con `openspec-update-change`). Ambos convergen en la misma Puerta 1 — detalles en [02-sdd-flutter-supabase.md §Dos modos de crear el cambio](./02-sdd-flutter-supabase.md#dos-modos-de-crear-el-cambio).

---

## Comandos de la CLI

### Set up

| Comando | Qué hace |
|---------|----------|
| `openspec init` | Inicializa OpenSpec en el proyecto (interactivo) |
| `openspec update` | Actualiza archivos de agentes instalados |
| `openspec config` | Ver y cambiar configuración global |

### Changes y specs

| Comando | Qué hace |
|---------|----------|
| `openspec list` | Lista cambios activos |
| `openspec list --specs` | Lista specs archivadas |
| `openspec show <item>` | Muestra un cambio o spec (reemplaza a `openspec change` y `openspec spec`) |
| `openspec show <item> --diff` | Muestra el cambio con diffs de requisitos contra specs principales |
| `openspec view` | Dashboard de un pantalla de cambios y specs |
| `openspec validate` | Valida formato de changes/specs contra los schemas |
| `openspec validate --all` | Valida todos los changes y specs |
| `openspec archive <id>` | Archiva un cambio (equivale al slash command) |

### Workflows y schemas

| Comando | Qué hace |
|---------|----------|
| `openspec new change <name>` | Crea un nuevo cambio con metadata YAML |
| `openspec status --change <id>` | Checklist de progreso de artifacts de un cambio |
| `openspec instructions <artifact>` | Instrucciones detalladas para crear un artifact |
| `openspec templates` | Rutas de templates de un schema |
| `openspec schemas` | Lista schemas de workflow disponibles |
| `openspec schema fork <src> <name>` | Forkiar un schema existente al proyecto (experimental) |
| `openspec schema init <name>` | Crear un schema desde cero (experimental) |

### Utilidades

| Comando | Qué hace |
|---------|----------|
| `openspec doctor` | Diagnóstico de la instalación local |
| `openspec feedback` | Enviar feedback sobre OpenSpec |
| `openspec completion` | Instalar/generar completions de shell |

> **Comandos deprecated:** `openspec change <id>` y `openspec spec <cap>` funcionan pero muestran un warning. Usa `openspec show` en su lugar.

La validación (`openspec validate`) comprueba que cada spec tenga secciones `WHY`/`Purpose` y requisitos en formato delta correcto — úsala antes de cada puerta. Nuevos flags: `--archived` (verificar archivados), `--strict` (warnings como errores), `--report findings` (solo items con issues).

---

## Project Configuration (config.yaml)

`openspec/config.yaml` le dice a los workflows cómo planificar cambios. Tres campos principales:

```yaml
# openspec/config.yaml
schema: spec-driven              # Schema a usar (default: spec-driven)

context: |
  Tech stack: Flutter 3.x + Dart, Clean Architecture, Supabase
  Usamos BLoC/Cubit para estado, GetIt para DI, GoRouter para routing
  Commits convencionales: feat(x):, fix(x):, refactor(x):

rules:
  proposal:
    - Mantener proposals bajo 500 palabras
  tasks:
    - Cada tarea UI incluye widget test
    - Cada tarea de datos incluye integration test contra migración real

operations:
  apply:
    guidance:
      - "Si tasks.md declara 'Modo: andamiaje': NO escribas los bodies. Genera solo scaffold (throw UnimplementedError() + TODO citando REQ-xxx), NO marques la casilla - [x], y pausa para que el desarrollador complete."
      - "Si tasks.md declara 'Modo: completo': implementa la tarea al 100% contra la spec y márcala - [x]."
  archive:
    guidance:
      - Resumir qué se entregó antes de archivar
```

| Campo | Qué hace | Injectado en |
|-------|----------|-------------|
| `context` | Contexto que el agente recibe siempre | Todo: cada artifact, apply, archive |
| `rules` | Reglas extra para un artifact específico | Solo la creación de ese artifact |
| `operations` | Guía para apply y archive | Solo apply y archive |

**El idioma de output** se cambia con una línea en context: `Write all artifacts in Spanish.`

> **Por qué funciona:** config.yaml vive en tu proyecto (`openspec/config.yaml`, junto a `lib/`), no es parte de la herramienta. El CLI lo lee en tiempo de ejecución (`openspec instructions`) y lo inyecta en el prompt del agente.

---

## Schemas personalizados

Un schema define qué artifacts produce un cambio, en qué orden, desde qué templates. El default es `spec-driven`:

```
proposal → specs → design → tasks
```

### Forkiar un schema existente

```bash
# Copiar spec-driven al proyecto
openspec schema fork spec-driven mi-flow

# Editar openspec/schemas/mi-flow/schema.yaml y templates/
# Apuntar el proyecto al schema forked:
# openspec/config.yaml → schema: mi-flow
```

### Crear desde cero

```bash
openspec schema init lite --description "Flujo ligero" --artifacts proposal,tasks
```

### Validar un schema

```bash
openspec schema validate mi-flow
```

Los schemas viven en `openspec/schemas/` (committeados con el repo) o en `~/.local/share/openspec/schemas/` (globales por máquina). Los schemas del proyecto ganan sobre los built-in.

---

## Multi-repo (beta)

Para proyectos que planifican features que span múltiples repos:

### Stores

Un store es un repo OpenSpec standalone que comparten varios repos de código:

```
team-plans/          (store: OpenSpec en su propio repo)
├── openspec/
│   ├── specs/
│   └── changes/
web-app/             (code repo → connecta al store)
api-server/          (code repo → connecta al store)
```

```bash
# Crear un store (una persona, una vez)
openspec store setup

# Unirse al store (cada teammate)
git clone git@github.com:acme/team-plans.git ~/openspec/team-plans
openspec store register ~/openspec/team-plans

# Trabajar contra el store
openspec status --store team-plans
openspec new change add-login --store team-plans
```

### Worksets

Abrir el store y los repos en una sola ventana del editor:

```bash
openspec workset create platform \
  --member ~/src/web-app \
  --member ~/openspec/team-plans \
  --tool code

openspec workset open platform
```

---

## Cloud Agent (early access)

Capa always-on para equipos que usan OpenSpec en uno o más repos. Detecta **spec drift**: cuando un PR cambia el comportamiento del producto sin actualizar la spec.

**Qué hace:**
- Compara PRs con las requirements y cita las líneas exactas cuando discrepan
- Abre PRs correctivos automáticamente
- Escanea repos conectados diariamente

**Ejemplo de drift detectado:**
```
spec drift found — PR check

Customers lose access when they cancel
  Requirement: openspec/specs/billing/spec.md:64
    "Canceled subscriptions remain active through current_period_end"
  Code: src/billing/cancel-subscription.ts:37
    "cancellation sets status to canceled immediately"

Next: Keep access active through current_period_end, or revise requirement
```

> Early access gratuito para equipos. Configuración <15 min. Más info en [openspec.dev/blog/openspec-cloud-agents](https://openspec.dev/blog/openspec-cloud-agents).

---

## Ejemplo completo: Login con Supabase Auth

### Contexto
Proyecto Flutter con Clean Architecture, Supabase como backend.

### Paso 1: Explorar
```
/opsx-explore
→ Quiero agregar login con Supabase Auth
→ El agente lee tu codebase y sugiere la mejor integración
```

### Paso 2: Proponer
```
/opsx-propose add-supabase-auth
```

**Lo que genera:**

`openspec/changes/add-supabase-auth/proposal.md`:
```markdown
# Proposal: Add Supabase Authentication

Problem
Users need to authenticate to access protected features.

Solution
Integrate Supabase Auth with email/password login, following Clean Architecture.

Impact
- New feature: `auth` under `lib/features/`
- Dependencies: supabase_flutter (already in pubspec)
- No breaking changes to existing features
```

`openspec/changes/add-supabase-auth/specs/auth-login/spec.md`:
```markdown
ADDED Requirements

### Requirement: Email/password login
The system SHALL authenticate users via email and password using Supabase Auth.

#### Scenario: Successful login
- GIVEN a registered user with valid credentials
- WHEN the user submits the login form
- THEN the system returns a User entity and navigates to the home screen

#### Scenario: Invalid credentials
- GIVEN a user with wrong password
- WHEN the user submits the login form
- THEN the system displays "Credenciales inválidas" and stays on the login screen

#### Scenario: Network error
- GIVEN no internet connection
- WHEN the user submits the login form
- THEN the system displays "Error de conexión" with a retry option

### Requirement: Session persistence
The system SHALL persist the user session across app restarts.

#### Scenario: App restart with valid session
- GIVEN a user previously logged in
- WHEN the app restarts
- THEN the user is redirected to the home screen without re-authenticating
```

`openspec/changes/add-supabase-auth/design.md`:
```markdown
# Design: Supabase Auth

Architecture
Follow Clean Architecture layers:
- Domain: User entity, AuthRepository interface, LoginUseCase
- Data: AuthDataSource (Supabase), AuthRepositoryImpl, UserModel
- Presentation: AuthCubit, AuthState, LoginPage

Decisions
- Use Supabase GoTrue client for auth operations
- Store session via Supabase's built-in persistence
- Emit auth state changes via Stream in Cubit
```

`openspec/changes/add-supabase-auth/tasks.md`:
```markdown
# Tasks

- [ ] 1. Create User entity (domain/entities/user.dart)
- [ ] 2. Create AuthRepository interface (domain/repositories/auth_repository.dart)
- [ ] 3. Create LoginUseCase (domain/usecases/login.dart)
- [ ] 4. Create UserModel with snake_case mapping (data/models/user_model.dart)
- [ ] 5. Create AuthRemoteDataSource (data/datasources/auth_remote_datasource.dart)
- [ ] 6. Create AuthRepositoryImpl (data/repositories/auth_repository_impl.dart)
- [ ] 7. Create AuthCubit + AuthState (presentation/cubit/)
- [ ] 8. Create LoginPage with form pattern (presentation/pages/)
- [ ] 9. Register in DI (service_locator.dart)
- [ ] 10. Add route (app_router.dart)
- [ ] 11. Write unit tests for LoginUseCase
- [ ] 12. Write widget test for LoginPage
```

### Paso 3: Revisar
Revisas cada artefacto. Ajustas si algo no está bien (ej: agregar "recordar sesión" al spec).

### Paso 4: Ejecutar
```
/opsx-apply-change
→ El agente ejecuta las 12 tareas una por una
→ Cada tarea genera código que cumple la spec
```

### Paso 5: Archivar
```
/opsx-archive-change
→ Las specs de auth-login se actualizan
→ El cambio queda documentado en el historial
```

---

## Comparativa con otras herramientas

| Característica | OpenSpec | Spec Kit (GitHub) | Kiro (AWS) |
|----------------|---------|-------------------|------------|
| Tipo | CLI open source | CLI open source | IDE dedicado |
| Facilidad | Ligero, 1 comando | Más pesado, Python setup | Integrado, sin CLI |
| Flexibilidad | Fluido, sin fases rígidas | Fases rígidas | Flujo impuesto |
| Agentes | 40+ soportados | ~30 soportados | Solo Claude |
| Brownfield | Sí (diseñado para ello) | Sí | Sí |
| Specs en repo | Sí (openspec/) | Sí (.spec/) | No (en el IDE) |
| Schemas custom | Sí (fork/init) | No | No |
| Multi-repo | Sí (stores, beta) | No | No |
| Cloud/Drift | Sí (Cloud Agent, early access) | No | No |
| Coste | Gratis | Gratis | Requiere suscripción |

**Conclusión:** OpenSpec es la opción más flexible, con más features (schemas, multi-repo, cloud) y la mayor comunidad. Spec Kit es más estructurado pero más pesado. Kiro es potente pero te encierra en su IDE.

---

## Actualización

```bash
# Actualizar OpenSpec (ofrece upgrade de CLI si hay nueva versión)
openspec update

# O forzar reinstall
npm install -g @fission-ai/openspec@latest
```

`openspec update` detecta la versión del CLI y ofrece actualizar. Después refresca los archivos de skills y commands instalados en el proyecto. Nunca toca `openspec/schemas/` (tus forks se preservan).

---

## Configuración de telemetría

OpenSpec recopila stats anónimas (solo comandos, no contenido). Para desactivar:

```bash
# Opción 1: config global
openspec config set telemetry.enabled false

# Opción 2: variable de entorno
export OPENSPEC_TELEMETRY=0
```

---

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `command not found: openspec` | No está instalado globalmente | `npm install -g @fission-ai/openspec@latest` |
| `Node.js version too old` | Versión de Node menor a 20.19.0 | Actualizar Node.js |
| Slash commands no aparecen | Agentes no configurados | Ejecutar `openspec update` en el proyecto |
| Specs no se generan | No se ejecutó `/opsx-propose` primero | Ejecutar propose antes de apply |
| `No OpenSpec root found` | Fuera de un proyecto o sin `--store` | Navegar al directorio del proyecto o pasar `--store <id>` |
| `Schema not found` | Schema configurado no existe | `openspec schemas` para ver disponibles, o `openspec schema fork spec-driven <name>` |
| `Store not registered` | Store no registrado en la máquina | `openspec store register <path>` |

---

## Glosario rápido

| Término | Definición |
|---------|-----------|
| **Artifact** | Documento de planificación: proposal.md, delta specs, design.md, tasks.md |
| **Capability** | Área de comportamiento del sistema. Cada una tiene un spec en `openspec/specs/<cap>/spec.md` |
| **Change proposal** | Unidad de trabajo: carpeta bajo `openspec/changes/<nombre>/` |
| **Delta spec** | Spec dentro de un cambio que describe solo lo que cambia (ADDED/MODIFIED/REMOVED/RENAMED) |
| **Main specs** | El árbol `openspec/specs/`: comportamiento actual acordado del sistema |
| **Schema** | Definición de qué artifacts produce un cambio y en qué orden |
| **Store** | Repo OpenSpec standalone para planificación multi-repo |
| **Workset** | Lista guardada de carpetas para abrir juntas en un editor |

Glosario completo: [openspec.dev/docs/glossary](https://openspec.dev/docs/glossary)

---

## Referencias

- **Sitio web:** [openspec.dev](https://openspec.dev)
- **Docs:** [openspec.dev/docs](https://openspec.dev/docs)
- **GitHub:** [github.com/Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) (66.9k stars)
- **Discord:** [discord.gg/YctCnvvshC](https://discord.gg/YctCnvvshC)
- **Metodología aplicada a tu stack:** [02-sdd-flutter-supabase.md](./02-sdd-flutter-supabase.md)
- **Plantilla de cambio:** [04-plantilla-cambio-openspec.md](./04-plantilla-cambio-openspec.md)
- **Ejemplos listos para copiar:** [`ejemplos-cambios/`](./ejemplos-cambios/)
