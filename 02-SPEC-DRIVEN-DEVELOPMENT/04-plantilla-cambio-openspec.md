# 04 - Plantilla de Cambio OpenSpec

> Copia esta estructura a `openspec/changes/<kebab-case-nombre>/` en tu proyecto Flutter y completa cada archivo. Cada sección indica qué fase del flujo produce ([ver 02-sdd-flutter-supabase.md](./02-sdd-flutter-supabase.md)).
>
> Antes de cada puerta, ejecuta `openspec validate` para comprobar el formato.

---

## Estructura de la carpeta

```
openspec/changes/add-<feature>/
├── proposal.md                  ← Fases 0 + 1 (Impact Report + alcance)
├── specs/
│   └── <capacidad>/             ← una carpeta por capacidad afectada
│       └── spec.md              ← Fase 1 (requisitos EARS, formato delta)
├── design.md                    ← Fase 2 (opcional: solo complejidad Intermedia+)
└── tasks.md                     ← Fase 3
```

Convención de nombre: `add-` para features nuevas, `update-` para modificar existentes, `remove-` para retirarlas.

---

## proposal.md

```markdown
# Proposal: add-<feature>

Impacto (Impact Report)
<!-- 5-15 líneas. Obligatorio en brownfield. -->
- Features afectadas: `lib/features/...` — [cuáles y cómo]
- Reutilizable: [contratos/widgets/tablas que ya existen]
- Supabase: tablas `[...]`, RLS existente `[...]`, migración nº `<n>`
- DI / rutas: `service_locator.dart` (+<n> registros), `app_router.dart` (+1 ruta)
- Riesgos: [los 2-3 principales]

Why (Problema)
[2-4 frases: qué necesidad real existe hoy sin resolver]

What Changes (Solución)
[Qué se construye/cambia, en lenguaje del dominio]

Capabilities
### New Capabilities
- `<capacidad>`: [una frase]

### Modified Capabilities
- `<capacidad>`: [qué cambia y por qué] <!-- si aplica -->

Scope (Alcance)
**Incluye:**
- [...]
**No incluye:**
- [...] <!-- explícito: pagos, envíos, realtime... lo que NO toca -->
**Dependencias:** [...]
**Suposiciones:** [...]
**Preguntas abiertas:** [→ cerrar antes de Puerta 1]

Actores y permisos
| Actor | Puede | No puede | Mapeo RLS |
|-------|-------|----------|-----------|
| Cliente | ... | ... | auth.uid() = user_id |

Impact
- Código: [ficheros nuevos/modificados estimados]
- Datos: [tablas nuevas/columnas/migraciones]
- Breaking changes: [ninguno / cuáles]
```

---

## specs/&lt;capacidad&gt;/spec.md

```markdown
WHY
<!-- Por qué existe esta capacidad, ligado al problema del proposal -->

Purpose
[1-2 frases: qué garantiza esta capacidad]

ADDED Requirements

### Requirement: <Nombre del requisito>
<Enunciado EARS resumen: qué hará el sistema y para quién>

#### Scenario: <Camino feliz>
- **WHEN** <disparador>
- **THEN** el sistema DEBERÁ <comportamiento observable>
- **AND** <efecto secundario si aplica>

#### Scenario: <Caso borde>
- **IF** <condición límite>
- **THEN** el sistema DEBERÁ <respuesta controlada>

#### Scenario: <Error>
- **IF** <fallo esperable>
- **THEN** el sistema DEBERÁ mostrar "<mensaje exacto>" y no alterar el estado

<!-- Repetir Requirement por cada operación atómica.
     Cubrir SIEMPRE: camino feliz + bordes + errores + seguridad (RLS). -->

MODIFIED Requirements
<!-- Solo si este cambio modifica requisitos ya archivados.
     Se reescribe el requisito COMPLETO; reemplaza al anterior. -->

REMOVED Requirements
<!-- Solo si algo deja de existir. Explicar el porqué. -->
```

Reglas EARS rápidas:
- **Ubicuo**: "El sistema DEBERÁ..." — invariable
- **Evento**: "CUANDO X EL sistema DEBERÁ..." — interacción
- **Estado**: "MIENTRAS X EL sistema DEBERÁ..."
- **No deseado**: "SI X ENTONCES el sistema DEBERÁ..."
- **Opcional**: "DONDE X EL sistema DEBERÁ..."

---

## design.md (opcional — Complejidad Simple lo omite)

```markdown
# Design: add-<feature>

Context
[Estado actual relevante: patrón existente que se sigue, restricciones descubiertas]

Goals / Non-Goals
- Goals: [...]
- Non-Goals: [...]

Decisions
<!-- Una por decisión no obvia -->
### D1: <título>
- Decisión: [...]
- Alternativas descartadas: [...]
- Por qué: [...]

Ficheros afectados
| Elemento | Capa | Archivo | Req |
|----------|------|---------|-----|
| <Entity> | domain/entity | lib/features/x/domain/entities/… | REQ-00x |
| <Repository> | domain/repository | lib/features/x/domain/repositories/… | … |
| <Model> | data/model | lib/features/x/data/models/… | … |
| <DataSource> | data/datasource | lib/features/x/data/datasources/… | … |
| <UseCase> | domain/usecase | lib/features/x/domain/usecases/… | … |
| <Cubit>/<State> | presentation/cubit | lib/features/x/presentation/cubit/… | … |
| <Page> | presentation/pages | lib/features/x/presentation/pages/… | … |
| Registro DI | core/di | lib/core/di/service_locator.dart | … |
| Ruta | core/router | lib/core/router/app_router.dart | … |

Contratos Dart clave
    abstract interface class <X>Repository {
      Future<Either<Failure, T>> operacion(...);
    }
    sealed class XState {}
    class XInitial extends XState {}
    class XLoading extends XState {}
    class XLoaded extends XState { final T data; XLoaded(this.data); }
    class XError extends XState { final String message; XError(this.message); }

Flujo de datos
    Page ──► Cubit ──► UseCase ──► RepositoryImpl ──► DataSource ──► Supabase
                                        │                        │
                              Either.left(Failure) ◄────────────┘
            ◄── CartError(message) ◄── mapeo de failures

UI-UX · Pantallas (archivo .pen)
<!-- Solo Intermedia/Compleja; Simple lo omite (igual que design.md).
     Wireframes hechos con Pencil (modulo 08): openspec/changes/<cambio>/design/<feature>-ui.pen
     Los mensajes/estados EXACTOS ya viven en la spec; aqui se mapea pantalla -> REQ. -->
| Pantalla (.pen) | Escenario REQ | Estados visibles | Notas (interacciones) |
|-----------------|---------------|------------------|------------------------|
| <Page> | REQ-00x | vacio · con datos · error | <snackbars / empty states con el mensaje exacto> |

Backend Supabase
- Tablas: [columnas, tipos, FKs, constraints]
- RLS: [política por escenario de seguridad]
- RPC/Triggers: [si hay cálculo atómico o concurrencia]
- Migración: supabase/migrations/NNNN_*.sql (idempotente, no editar previas)

Boundaries aplicables a este cambio
[Qué NO debe hacer el agente aquí: ej. no tocar feature Y, no añadir paquetes]
```

---

## tasks.md

```markdown
# Tasks: add-<feature>
> Modo de implementación: andamiaje
>   andamiaje = la IA genera el scaffold (throw UnimplementedError() + TODOs citando REQ) y TÚ implementas los métodos críticos
>   completo = la IA escribe todo (100%) y tú auditas cada diff contra la spec

1. Dominio
- [ ] 1.1 Crear <Entity> con invariantes
      Rol: experto Flutter/Dart + Clean Architecture
      Éxito: invariantes cubiertas por test unitario
      Req: REQ-001 · Commit: feat(x): add Entity

- [ ] 1.2 Definir interface <X>Repository (Either<Failure,T>)
      Éxito: firmas coinciden con design.md
      Req: REQ-002..007 · Commit: feat(x): add repository contract

- [ ] 1.3 UseCases (uno por operación)
      Éxito: mensajes exactos de los escenarios en failures de dominio
      Req: REQ spec · Commit: feat(x): add usecases

2. Capa de datos + Backend Supabase
- [ ] 2.1 Migración SQL + políticas RLS           ← si aplica; abre la capa para probar el flujo de datos
      (+ RPC si hay concurrencia · Edge Functions si aplica)
      Éxito: openspec validate + supabase db reset OK
      Req: escenarios RS · Commit: db(x): add tables and rls
- [ ] 2.2 <Model> fromJson/toJson (snake_case ↔ camelCase)
- [ ] 2.3 <RemoteDataSource> (llamadas exactas + errores de red)
- [ ] 2.4 <RepositoryImpl> (mapeo excepciones → Failure)

3. Estado y presentación
- [ ] 3.1 <State> sealed class
- [ ] 3.2 <Cubit> (transiciones + mensajes exactos de los escenarios)
- [ ] 3.3 <Page> + widgets (un render por estado)

4. Integración
- [ ] 4.1 Registros en service_locator.dart
- [ ] 4.2 Ruta en app_router.dart

5. Tests
- [ ] 5.1 Unit tests entidades/usecases (bordes de la spec)
- [ ] 5.2 Test repository impl (mock datasource) + integración contra la migración real
- [ ] 5.3 Widget test página clave

Trazabilidad
| Req | Tarea(s) | Test | Commits |
|-----|----------|------|---------|
| REQ-001 | 1.1 | entity_test | abc123 |
```

---

## Configuración — que `/opsx-apply-change` respete el modo

El modo se declara **por cambio** en la primera línea de `tasks.md` (véase arriba). Para que el agente de `/opsx-apply-change` —el único motor de implementación— lo cumpla de forma fiable, añade una vez al `openspec/config.yaml` de tu proyecto:

```yaml
# openspec/config.yaml — se añade una sola vez; el interruptor por cambio es la línea "Modo" de tasks.md
operations:
  apply:
    guidance:
      - "Si tasks.md declara 'Modo: andamiaje': NO escribas los bodies. Por cada tarea genera solo el scaffolding (throw UnimplementedError() + TODO citando REQ-xxx), NO marques la casilla - [x], y pausa para que el desarrollador complete e implemente."
      - "Si tasks.md declara 'Modo: completo': implementa la tarea al 100% contra la spec (caminos de éxito y error de los escenarios) y márcala - [x]."
```

> **Por qué funciona:** ese archivo vive en tu proyecto (`openspec/config.yaml`, junto a `lib/`), no es parte de la herramienta. El CLI lo lee en tiempo de ejecución (`openspec instructions apply`) y lo inyecta en el prompt del agente como `operationGuidance`, que el flujo built-in ordena leer y seguir. El interruptor por cambio sigue siendo la línea `Modo` de `tasks.md` — el `config.yaml` se configura una sola vez.

**Comportamiento según el modo** (vía `/opsx-apply-change`):

| Tarea | `andamiaje` | `completo` |
|-------|-------------|------------|
| Cuerpos | la IA deja `throw UnimplementedError()` + TODO citando REQ | la IA escribe el código completo |
| Casilla | se deja en `- [ ]` (la tarea NO está terminada) | se marca `- [x]` al cumplir la spec |
| Final | el agente pausa y pasas a implementar | el agente termina y tú auditas cada diff |

> La skill `clean-arch-feature` queda como **herramienta manual opcional (fuera del flujo)**: con `andamiaje` genera el scaffold del cambio completo y deja los bodies para ti; con `completo` puedes pedirle que implemente. En el flujo, el grano del andamiaje lo decide el modo dentro de `/opsx-apply-change`: `andamiaje` = scaffold por tarea y pausa en cada una; `completo` = escribe el cambio entero.

---

## Checklist de las 3 puertas

**Puerta 1 (tras Fase 1):** historias precisas · EARS con IDs · bordes cubiertos · alcance cerrado · delta correcto.

**Puerta 2 (tras Fase 2):** ficheros afectados completos · contratos coherentes · flujo con caminos de error · RLS especificada · decisiones registradas.

**Puerta 3 (tras Fase 3):** todo requisito tiene ≥1 tarea · trazabilidad bidireccional · tareas ≤3 ficheros · orden de oleadas correcto · tests presentes · `tasks.md` declara su modo (`andamiaje` | `completo`).

---

## Cierre

```bash
openspec validate            # formato OK
# ... implementar (Fase 4) ...
openspec archive add-<feature>
```

Ejemplos reales completados: [`ejemplos-cambios/`](./ejemplos-cambios/)
