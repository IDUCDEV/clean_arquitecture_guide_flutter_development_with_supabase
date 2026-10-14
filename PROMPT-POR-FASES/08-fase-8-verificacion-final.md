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
`PROMPT-POR-FASES/09-parte-b-packs.md`.

## Pendientes manuales

Los que requieren una herramienta que no esta en este entorno: firma de
release, flavors de iOS, deploy de la web, configuracion de Sentry.
```

