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

