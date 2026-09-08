# 05 - Referencia Rápida

> Cheat sheet de SDD: fases, puertas, EARS, boundaries, proporcionalidad y OpenSpec.

---

## Las 4 fases de SDD

```
REQUISITOS → DISEÑO → TAREAS → IMPLEMENTACIÓN
   ¿QUÉ?      ¿CÓMO?    ¿EN QUÉ        ¿EJECUTAR
                         ORDEN?          (agente/humano)
```

| Fase | Entregable | Quién participa |
|------|-----------|-----------------|
| Requisitos | Historias, criterios, reglas | PO + equipo |
| Diseño | Arquitectura, contratos, tablas | Developer + agente |
| Tareas | Unidades atómicas con prompts | Developer |
| Implementación | Código, tests, commits | Agente + developer |

---

## Las 3 puertas de aprobación

```
PUERTA 1              PUERTA 2              PUERTA 3
Requisitos → Diseño   Diseño → Tareas       Tareas → Implementación
```

| Puerta | Pregunta clave | Qué verificar |
|--------|---------------|---------------|
| **1** | ¿Resolvemos el problema correcto? | Requisitos completos, criterios verificables, reglas explícitas |
| **2** | ¿Es viable y coherente? | Patrones del codebase, dependencias, orden lógico |
| **3** | ¿Estas tareas producen el diseño? | Cobertura, sin huecos, prompts precisos |

**Regla de oro:** El coste de corregir un error crece exponencialmente por fase. Corregir en requisitos es trivial; corregir en implementación es caro.

---

## Notación EARS (5 patrones)

| Patrón | Palabra clave | Template | Ejemplo Flutter |
|--------|--------------|----------|-----------------|
| **Ubicuo** | (sin condición) | "El sistema SHALL [comportamiento]" | "La app SHALL mostrar el nombre del usuario en todas las páginas" |
| **Evento** | **CUANDO** | "CUANDO [evento], el sistema SHALL [respuesta]" | "CUANDO el usuario pulsa logout, el sistema SHALL cerrar sesión" |
| **Estado** | **MIENTRAS** | "MIENTRAS [condición], el sistema SHALL [comportamiento]" | "MIENTRAS el formulario sea inválido, el botón SHALL estar deshabilitado" |
| **No deseado** | **SI** | "SI [error], el sistema SHALL [recuperación]" | "SI la sesión expira, el sistema SHALL redirigir al login" |
| **Opcional** | **DONDE** | "DONDE [configuración], el sistema SHALL [comportamiento]" | "DONDE el usuario habilitó biometría, el sistema SHALL ofrecer login por huella" |

**Template universal:**
```
MIENTRAS [precondición], CUANDO [evento], el sistema debe [respuesta]
```

---

## Sistema de boundaries (Always / Ask First / Never)

| Nivel | Significado | Ejemplo Flutter |
|-------|-------------|-----------------|
| **Always** | El agente ejecuta sin preguntar | `flutter analyze`, naming conventions, const constructors |
| **Ask First** | Requiere aprobación antes de ejecutar | Añadir dependencias, modificar migrations, cambiar routing |
| **Never** | Líneas rojas absolutas | Commitear .env, editar build.gradle, modificar RLS de producción |

**Regla de evolución:** A medida que el equipo gana confianza, algo que hoy es Ask First puede pasar a Always.

---

## Principio de proporcionalidad

### Pregunta de calibración

> ¿Qué pasa si el agente toma la decisión equivocada en este punto?

| Respuesta | Acción |
|-----------|--------|
| "Lo corrijo en 2 minutos" | No necesita especificarse |
| "Pierdo horas o introduzco un bug sutil" | Sí necesita especificarse |

### Cuándo usar SDD vs vibe coding

| Situación | Herramienta |
|-----------|-------------|
| Bug trivial, script, prototipo | Vibe coding |
| Feature compleja, cambio con riesgo, trabajo en equipo | SDD |
| Feature nueva en codebase existente | SDD + Impact Report |
| Refactor grande | SDD (flujo completo) |

---

## Equivalencias de terminología (glosario de dilución)

Equivalencia de términos entre el método de diseño anterior y SDD:

| Equivalencia | Ahora (SDD estándar) | Dónde vive |
|------------------------|----------------------|------------|
| Paso Alcance | Sección Scope del `proposal.md` | Fase 1 |
| Formular + Actorizar | Historias precisas + tabla de actores/permisos | Fase 1 |
| Descomponer | Operaciones atómicas → requisitos dirigidos por evento EARS | Fase 1 |
| Entidades | Specs por componente Clean Arch | Fase 1 |
| Reglas RN (negocio) | Requisitos EARS (ubicuo/evento/no deseado) + escenarios | `specs/*/spec.md` |
| Reglas RT (técnicas) | Decisiones explícitas en `design.md` | Fase 2 |
| Reglas RS (seguridad) | Escenarios EARS + políticas RLS | spec + design §Backend |
| Mapeo a capas | Tabla "Ficheros afectados" | `design.md` |
| Contratos + ADRs | Sección Contratos Dart + Decisions | `design.md` |
| Flujo de datos | Diagrama Page→Cubit→UseCase→Repo→DataSource→Supabase | `design.md` |
| Diseño de pantallas (wireframes UI) | Sección `design.md §UI-UX` + archivo `.pen` (Pencil, módulo 08) | Fase 2 |
| Estados de pantalla (mensajes exactos) | Escenarios EARS dentro de cada Requirement | Fase 1 |
| Criterios BDD | Escenarios GIVEN-WHEN-THEN dentro de cada Requirement | deltas |

> **Nota:** Los "Criterios BDD" y los "escenarios EARS" son la misma cosa: cada `#### Scenario:` con `GIVEN/WHEN/THEN` en `spec.md` **es** el criterio de aceptación. Ver también sección 1.5 de `02-sdd-flutter-supabase.md`.
| Trazabilidad | Matriz Req ↔ tarea ↔ test ↔ commit | `tasks.md` |
| Estimación de complejidad | Proporcionalidad Simple/Intermedia/Compleja | todo el flujo |
| Sprint Planning (Scrum) | Puerta 3: aprobar tasks.md antes de ejecutar | ceremonias |
| Sprint Review | Revisión final contra la spec al cierre de la implementación | ceremonias |

---

## Maldición de las instrucciones

> A más instrucciones en un prompt, menor probabilidad de que el modelo cumpla cada una.

**Señales de spec sobrecargada:**
- El agente ignora restricciones escritas
- Cumple lo del principio pero no lo del final
- Mejora cuando se reduce la spec
- Acierta con tareas aisladas y falla con varias juntas

**Solución:** Dividir, no acumular. Cinco specs de 10 instrucciones > una de 50.

---

## Specs vivas: 3 niveles de vida

| Nivel | Descripción | Deriva |
|-------|-------------|--------|
| **Spec-first** | Se escribe antes, guía la tarea, se descarta | No aplica |
| **Spec-anchored** | Se mantiene como documentación viva | Riesgo real → actualizar en mismo commit |
| **Spec-as-source** | La spec es el artefacto principal; código se regenera | Desaparece por diseño (experimental) |

### Clarity Gate (prueba de calidad)

> ¿Puede un agente diferente generar código equivalente solo con la spec?

- **Sí** → spec clara y completa
- **No** → faltan supuestos implícitos → actualizar spec

---

## OpenSpec: comandos rápidos (CLI v1.11.0, OpenCode)

| Comando | Acción |
|---------|--------|
| `npm install -g @fission-ai/openspec@latest` | Instalar |
| `openspec init` | Inicializar en el proyecto |
| `openspec update` | Refrescar skills y commands instalados |
| `openspec list` | Listar cambios activos |
| `openspec show <item>` | Ver un cambio o spec (reemplaza `change` y `spec` deprecated) |
| `openspec show <item> --diff` | Ver diffs de requisitos contra specs principales |
| `openspec status --change <id>` | Checklist de progreso de artifacts |
| `openspec validate` | Validar formato de changes/specs |
| `openspec schemas` | Listar schemas de workflow disponibles |
| `/opsx-explore` | Explorar opciones (no crea archivos) |
| `/opsx-propose <nombre>` | Crear cambio completo |
| `/opsx-apply-change` | Ejecutar tareas |
| `/opsx-verify-change` | Verificar cumplimiento de specs (solo reporte) |
| `/opsx-archive-change` | Archivar cambio y consolidar specs |

> **Deprecated:** `openspec change <id>` y `openspec spec <cap>` → usa `openspec show` en su lugar.

Detalle completo: [03-openspec-guia-practica.md](./03-openspec-guia-practica.md)

**Glosario oficial:** [openspec.dev/docs/glossary](https://openspec.dev/docs/glossary)

---

## Plantilla de spec (copia y pega)

```markdown
### Requirement: [Nombre] [Componente]
The [Sistema/Capa] SHALL [comportamiento].

#### Scenario: [Éxito]
- GIVEN [precondición]
- WHEN [acción]
- THEN [resultado esperado]

#### Scenario: [Error]
- GIVEN [condición de error]
- WHEN [acción]
- THEN [resultado de error]
```

---

## Antipatrones de SDD

| Antipatrones | Descripción | Solución |
|-------------|-------------|----------|
| **Sobreespecificación** | Más tiempo en specs que en código | Principio de proporcionalidad |
| **Teatro de especificación** | Specs que nadie revisa de verdad | Puertas de aprobación reales |
| **Documentación zombi** | Specs que nadie consulta | decidir qué mantener, qué dejar morir |
| **Rigidez excesiva** | Mismo proceso para bug trivial y feature compleja | Calibrar intensidad |
| **Puertas como cuellos de botella** | Aprobación bloqueada por ausencia | Delegación asíncrona |

---

## Métricas (cap. 22 del libro)

| Tipo | Ejemplos |
|------|----------|
| De flujo | Tiempo de ciclo por fase, % de cambios que pasan la puerta a la primera, retrabajos por fase |
| De resultado | Bugs en producción, deriva spec-código, velocidad de onboarding |

**Qué NO medir:** líneas de spec producidas, número de requisitos — fomenta teatro de especificación.

---

## Referencia completa

| Documento | Ubicación |
|-----------|-----------|
| Teoría: mapa del libro oficial | [01-teoria-sdd.md](./01-teoria-sdd.md) · `pdf/SDDEquiposAgiles_v.1.pdf` |
| Resumen state-of-the-art | `pdf/Guia-SDD-equipos-agiles.pdf` |
| Metodología aplicada a Flutter+Supabase | [02-sdd-flutter-supabase.md](./02-sdd-flutter-supabase.md) |
| OpenSpec guía práctica | [03-openspec-guia-practica.md](./03-openspec-guia-practica.md) |
| Plantilla de cambio | [04-plantilla-cambio-openspec.md](./04-plantilla-cambio-openspec.md) |
| Ejemplos completos | [`ejemplos-cambios/`](./ejemplos-cambios/) |
