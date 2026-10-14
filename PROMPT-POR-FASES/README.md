# PROMPT — Bootstrap de monorepo por fases

Prompt de bootstrap del monorepo (Flutter + Supabase + Next.js), dividido por
fases para leerlo y editarlo de a una fase a la vez.

**Estos archivos son el prompt canónico.** No existe un archivo monolítico: si
necesitás el prompt completo, concatená los 12 archivos en orden (ver abajo).

---

## Orden de lectura

| # | Archivo | Contenido |
|---|---|---|
| 00 | [00-intro-y-contrato.md](./00-intro-y-contrato.md) | Qué es el documento, Variables, Contrato de ejecución, Orden de ejecución, Instrucciones generales para el agente |
| 01 | [01-fase-1-raiz-del-monorepo.md](./01-fase-1-raiz-del-monorepo.md) | **FASE 1** — Raíz del monorepo (estructura, `.editorconfig`, `.gitignore`, `.env.example`, `Makefile`, `README`, `AGENTS.md`, `CLAUDE.md`, `SECURITY.md`, `CONTRIBUTING.md`, ADRs, soporte de commits) |
| 02 | [02-fase-2-backend-supabase.md](./02-fase-2-backend-supabase.md) | **FASE 2** — Backend `supabase/` (estructura, `config.toml`, migraciones, tests pgTAP, `seed.sql`) |
| 03 | [03-fase-3-core-flutter.md](./03-fase-3-core-flutter.md) | **FASE 3** — Core de Flutter `apps/mobile/` (`pubspec`, `analysis_options`, i18n, `main.dart`, `core/error`, usecase, config, network, utils, cache local, session, DI, routing, theme, widgets, tests de core) |
| 04 | [04-fase-4-slice-vertical.md](./04-fase-4-slice-vertical.md) | **FASE 4** — El slice vertical descartable (dominio, datos, presentación, registro en DI, fixture, tests de la feature) |
| 05 | [05-fase-5-tooling.md](./05-fase-5-tooling.md) | **FASE 5** — Tooling (`apps/mobile/Makefile`, flavor de build, `.fvmrc`) |
| 06 | [06-fase-6-ci.md](./06-fase-6-ci.md) | **FASE 6** — CI (decisión de pinning por SHA, workflows `mobile`, `db`, `web`, `security`) |
| 07 | [07-fase-7-web-nextjs.md](./07-fase-7-web-nextjs.md) | **FASE 7** — Web Next.js anónima (estructura, `package.json`, `tsconfig`, `next.config`, patrón de dos clientes Supabase, layout/page, UI, env, lint/test, Makefile) |
| 08 | [08-fase-8-verificacion-final.md](./08-fase-8-verificacion-final.md) | **FASE 8** — Verificación final (checklist, los cinco tests, el grep sin auth, reporte final) |
| 09 | [09-parte-b-packs.md](./09-parte-b-packs.md) | **PARTE B** — PACKS opcionales: `auth`, `rpc-publicas`, `storage`, `observability` |
| 10 | [10-apendices.md](./10-apendices.md) | **APÉNDICES** — A (árbol completo generado), B (tabla de convenciones), C (decisiones de diseño y sus contras) |
| 11 | [11-preguntas-y-versionado.md](./11-preguntas-y-versionado.md) | Preguntas que el prompt no responde y Versionado del prompt |

---

## Cómo pegar el prompt completo

Para el bootstrap de una sola pasada, concatená los 12 archivos en orden
(excluí este `README.md`):

```bash
cat PROMPT-POR-FASES/00-intro-y-contrato.md \
    PROMPT-POR-FASES/01-fase-1-raiz-del-monorepo.md \
    PROMPT-POR-FASES/02-fase-2-backend-supabase.md \
    PROMPT-POR-FASES/03-fase-3-core-flutter.md \
    PROMPT-POR-FASES/04-fase-4-slice-vertical.md \
    PROMPT-POR-FASES/05-fase-5-tooling.md \
    PROMPT-POR-FASES/06-fase-6-ci.md \
    PROMPT-POR-FASES/07-fase-7-web-nextjs.md \
    PROMPT-POR-FASES/08-fase-8-verificacion-final.md \
    PROMPT-POR-FASES/09-parte-b-packs.md \
    PROMPT-POR-FASES/10-apendices.md \
    PROMPT-POR-FASES/11-preguntas-y-versionado.md
```

O, por fase, abrí solo el archivo que estás desarrollando.

---

## Puntos `> VERIFICAR`

El prompt marca los comandos de verificación con `> **VERIFICAR ...**`.
Están en:

- **FASE 1** — `01-fase-1-raiz-del-monorepo.md`
- **FASE 2** — `02-fase-2-backend-supabase.md`
- **FASE 3** — `03-fase-3-core-flutter.md` (por sub-sección: 3.1, 3.2, 3.3, 3.4, 3.6, 3.18, 3.19)
- **FASE 4** — `04-fase-4-slice-vertical.md` (al final y al cierre de tests)
- **FASE 7** — `07-fase-7-web-nextjs.md`
