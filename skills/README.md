# Skills de scaffolding para Clean Architecture + Flutter + Supabase

Skills que generan **boilerplate / scaffolding** de código, dejando la implementación de la lógica al desarrollador.

## Documentación de ejemplo

- [GUIA-DE-USO.md](./GUIA-DE-USO.md) — **la guía completa**: qué inputs proveer a cada skill (obligatorios, opcionales, formatos y prompts de ejemplo), orquestación y troubleshooting.
- [EJEMPLO.md](./EJEMPLO.md) — **todo el ejemplo en un solo archivo**: el flujo paso a paso (feature Order de principio a fin) y el output íntegro de las 5 skills — `clean-arch-feature` (Parte II) y `di-getit-scaffold`, `go-route-scaffold`, `clean-arch-component` y `flutter-test-generator` (Parte III).

> Nota: estos archivos son **ejemplos de uso**, no skills.

## Índice

| Skill | Qué genera | Cuándo usarla |
|---|---|---|
| [flutter-test-generator](./flutter-test-generator/SKILL.md) | Tests unitarios boilerplate por capa | Cuando necesitas tests para un archivo existente |
| [clean-arch-feature](./clean-arch-feature/SKILL.md) | Feature completa (entity → page, con Supabase, páginas y wiring opcionales) | Cuando empiezas una feature nueva desde cero |
| [clean-arch-component](./clean-arch-component/SKILL.md) | Archivo individual (entity, model, usecase, cubit, page...) | Cuando añades una pieza a una feature existente |
| [di-getit-scaffold](./di-getit-scaffold/SKILL.md) | Módulo GetIt de inyección de dependencias | Cuando registras/anotas dependencias de una feature (el registro lo escribe `make gen`; se invoca desde `clean-arch-feature` con `wiring: di`) |
| [go-route-scaffold](./go-route-scaffold/SKILL.md) | Configuración de rutas GoRouter | Cuando añades rutas con/sin auth redirect y Sentry (se invoca desde `clean-arch-feature` con `wiring: router`) |

---

## Instalación

Las skills se cargan desde `.opencode/skills/` (per-proyecto) o `~/.opencode/skills/` (global). Este repo mantiene las fuentes en `skills/`; para usarlas en opencode:

1. Copia la skill que necesitas al destino elegido:
   ```bash
   cp -r skills/clean-arch-feature .opencode/skills/
   # o global: cp -r skills/clean-arch-feature ~/.opencode/skills/
   ```
2. Reinicia opencode para que detecte skills nuevas o modificadas.
3. Verifica con `/skills` que aparecen listadas.

> `EJEMPLO.md` y `GUIA-DE-USO.md` **no** se copian: son documentación de referencia, no skills.

---

## Prerrequisitos del proyecto

Las skills asumen un proyecto Flutter **ya inicializado** con la base Clean Architecture. Checklist:

- `lib/core/common/usecase.dart` — clase base `UseCase<Return, Params>`
- `lib/core/error/failures.dart` — `Failure`, `ServerFailure`, `CacheFailure`, `NetworkFailure`
- `lib/core/error/exceptions.dart` — `ServerException`, `CacheException`, `AuthException`
- `lib/core/services/snackbar_helper.dart` — `SnackbarHelper.show`
- `lib/core/widgets/app_button.dart` — `AppButton` + `AppButtonVariant`
- `lib/core/di/service_locator.dart` — `sl = GetIt.instance` + `configureDependencies()`. El registro lo escribe `make gen` en `service_locator.config.dart` (commiteado); `external_module.dart` declara las librerías de terceros (`@module`)
- `lib/core/router/app_router.dart` — `AppRouter` + `GoRouter`
- Dependencias en `pubspec.yaml`: `fpdart`, `equatable`, `flutter_bloc`, `supabase_flutter`, `get_it`, `go_router`, `injectable` (+ `injectable_generator` y `build_runner` para regenerar el `.config.dart` con `make gen`)

Si el proyecto no tiene la base de `core/`, créala primero (p. ej. con un prompt de bootstrap) antes de invocar las skills.

---

## Cómo usar las skills

Las skills están diseñadas para ser ejecutadas por el asistente AI. Solo tienes que pedir lo que necesitas en lenguaje natural:

### Ejemplos de prompts

**"Crea un feature 'product' con campos id, name, price, categoryId, createdAt"**
→ El asistente ejecuta `clean-arch-feature` y genera todos los archivos de las 4 capas.

**"Añade un usecase delete_product al feature product"**
→ El asistente ejecuta `clean-arch-component` con `component_type: usecase` y `operation: delete`.

**"Crea un feature 'product' (campos id, name, price, categoryId, createdAt) con páginas list y detail"**
→ El asistente ejecuta `clean-arch-feature` con `pages` y genera las páginas iniciales con su patrón (`list:listener_builder`, `detail:builder`).

**"Añade una página edit al feature product con patrón form"**
→ El asistente ejecuta `clean-arch-component` con `component_type: page`, `page_name: edit` y `pattern_type: form`.

**"Crea un feature product (campos id, name, price, categoryId, createdAt) y conéctalo a Supabase, tabla products, columnas: id uuid PK, name text, price float8"**
→ El asistente ejecuta `clean-arch-feature` con parámetros Supabase y genera entidad, modelo con snake_case, datasource con `_tableName` + `watchById`, y migración SQL.

**"Crea un feature product (campos id, name, price, categoryId, createdAt) con páginas list y detail, y regístralo en DI y en el router"**
→ El asistente ejecuta `clean-arch-feature` con `pages` y `wiring: [di, router]`. Tras generar los archivos, orquesta `di-getit-scaffold` (las clases salen anotadas; `make gen` escribe el registro en `service_locator.config.dart`) y `go-route-scaffold` (añade rutas a `app_router.dart`) en el mismo turno.

**"Registra el feature product en el service locator"**
→ El asistente ejecuta `di-getit-scaffold`: verifica las anotaciones de las clases del feature y te recuerda correr `make gen`.

**"Añade las rutas de products y login al router"**
→ El asistente ejecuta `go-route-scaffold` con las rutas especificadas.

**"Genera los tests para product_cubit"**
→ El asistente ejecuta `flutter-test-generator` sobre `product_cubit.dart`.

---

## Flujo de trabajo típico

```
1. Diseñas la feature (SDD: spec + design en OpenSpec)
        ↓
2. Pides scaffold + Supabase + páginas (+ wiring: DI/rutas) → clean-arch-feature
        ↓          (si pediste wiring, orquesta di-getit-scaffold + go-route-scaffold)
3. Implementas bodies de métodos (tú)
        ↓
4. Añades más usecases o páginas → clean-arch-component
        ↓
5. Implementas bodies (tú)
        ↓
6. Pides tests → flutter-test-generator
        ↓
7. Completas los tests (tú)
        ↓
8. Verificas con flutter test
```

---

## Referencia rápida de parámetros

| Skill | Parámetros | Formato |
|---|---|---|
| `clean-arch-feature` | `feature_name`, `fields`, `operations` | Campos: `nombre: Tipo` (ej `price: double`). Operaciones: `getAll, getById, create, update, delete` |
| | `table_name`, `columns` (Supabase) | Columnas: `nombre: tipo [constraints]` (ej `id: uuid PK`, `status: text DEFAULT 'pending'`) |
| | `pages` | `[page_name:pattern, ...]` — pattern: `listener_builder` / `builder` / `form` |
| | `wiring` | `[di]`, `[router]` o `[di, router]` |
| `clean-arch-component` | `component_type`, `feature_name` (+ extra según tipo) | `entity`, `model`, `usecase`, `cubit`, `datasource`, `repository`, `repository_impl`, `page` |
| `di-getit-scaffold` | `mode`, `app_name`, `features`, `external_libs` | `mode`: `injectable` (default) o `manual` |
| `go-route-scaffold` | `app_name`, `has_auth`, `routes`, `use_sentry` | Ruta: `path, page, feature, children, auth_required` |
| `flutter-test-generator` | archivo fuente | Ruta al `.dart` (o directorio) |

---

## Troubleshooting

- **El asistente no invocó la skill correcta** → pídele explícitamente: "Usa la skill `clean-arch-feature`...".
- **El código generado no compila** → verifica los [prerrequisitos](#prerrequisitos-del-proyecto) (imports de `core/`), que diste el `app_name` correcto, y que la feature no exista ya.
- **La skill no aparece en `/skills`** → reinicia opencode y revisa la ruta de instalación.
- **El output difiere de los ejemplos** → los templates de cada `SKILL.md` son la fuente de verdad; puede variar si editaste la skill o cambió el patrón del proyecto.

---

## Principios

- **Scaffolding only**: las skills generan estructura, nunca lógica de negocio
- `throw UnimplementedError()` en cada método — tú decides la implementación
- Siguen las convenciones exactas del proyecto: `fpdart`, `equatable`, `flutter_bloc`, `supabase_flutter`, `mocktail` + `bloc_test`, `go_router`, `get_it` + `injectable` (registro por anotación, `.config.dart` regenerado con `make gen`)
- Usan nombres snake_case para archivos, UpperCamelCase para clases
- Feature-first: cada feature es independiente dentro de `lib/features/`
