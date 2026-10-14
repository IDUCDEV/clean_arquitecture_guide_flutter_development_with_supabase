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

