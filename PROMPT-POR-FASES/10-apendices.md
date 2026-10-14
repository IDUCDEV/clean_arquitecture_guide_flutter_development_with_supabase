# APENDICES

## Apéndice A -- Arbol completo generado

```
{{NOMBRE_PROYECTO}}/
│
├── apps/mobile/
│   ├── lib/
│   │   ├── main.dart
│   │   ├── core/
│   │   │   ├── common/usecase.dart
│   │   │   ├── config/app_config.dart
│   │   │   ├── constants/constants.dart
│   │   │   ├── data/local/
│   │   │   │   ├── isar_service.dart
│   │   │   │   └── isar_models/cached_entry.dart (+ .g.dart)
│   │   │   ├── di/{service_locator,external_module}.dart (+ .config.dart)
│   │   │   ├── error/{failures,exceptions}.dart
│   │   │   ├── network/network_info.dart
│   │   │   ├── routing/app_router.dart
│   │   │   ├── services/cache_manager.dart
│   │   │   ├── session/{current_user,current_user_stub}.dart
│   │   │   ├── theme/app_theme.dart
│   │   │   ├── utils/{app_info,error_handler,snackbar_helper,validators}.dart
│   │   │   └── widgets/
│   │   │       ├── app_button.dart
│   │   │       ├── app_card.dart
│   │   │       ├── app_text_field.dart
│   │   │       ├── empty_state.dart
│   │   │       ├── error_view.dart
│   │   │       ├── loading_indicator.dart
│   │   │       ├── pull_to_refresh_wrapper.dart
│   │   │       └── skeleton.dart
│   │   ├── features/{{FEATURE_EJEMPLO}}/
│   │   │   ├── data/
│   │   │   │   ├── datasources/{{FEATURE_EJEMPLO}}_local_data_source.dart
│   │   │   │   ├── models/{{FEATURE_EJEMPLO}}_model.dart
│   │   │   │   └── repositories/{{FEATURE_EJEMPLO}}_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entities/{{FEATURE_EJEMPLO}}_entity.dart
│   │   │   │   ├── repositories/{{FEATURE_EJEMPLO}}_repository.dart
│   │   │   │   └── usecases/
│   │   │   │       ├── create_{{FEATURE_EJEMPLO}}_usecase.dart
│   │   │   │       ├── delete_{{FEATURE_EJEMPLO}}_usecase.dart
│   │   │   │       └── get_{{FEATURE_EJEMPLO}}s_usecase.dart
│   │   │   └── presentation/
│   │   │       ├── cubit/
│   │   │       │   ├── {{FEATURE_EJEMPLO}}_cubit.dart
│   │   │       │   └── {{FEATURE_EJEMPLO}}_state.dart
│   │   │       ├── pages/
│   │   │       │   ├── {{FEATURE_EJEMPLO}}_detail_page.dart
│   │   │       │   └── {{FEATURE_EJEMPLO}}_page.dart
│   │   │       └── widgets/{{FEATURE_EJEMPLO}}_tile.dart
│   │   └── l10n/
│   │       ├── arb/{app_es.arb,app_en.arb}
│   │       ├── gen/                                   (gitignored)
│   │       └── l10n.dart
│   ├── test/
│   │   ├── core/
│   │   │   ├── common/usecase_test.dart
│   │   │   ├── error/{exceptions_test,failures_test}.dart
│   │   │   ├── session/current_user_stub_test.dart
│   │   │   ├── theme/app_theme_test.dart
│   │   │   ├── utils/{error_handler_test,validators_test}.dart
│   │   │   └── widgets/  (7 archivos, uno por widget)
│   │   ├── features/{{FEATURE_EJEMPLO}}/
│   │   │   ├── data/
│   │   │   │   ├── datasources/..._local_data_source_test.dart
│   │   │   │   ├── models/..._model_test.dart
│   │   │   │   └── repositories/..._repository_impl_test.dart
│   │   │   ├── domain/usecases/  (3 archivos)
│   │   │   └── presentation/
│   │   │       ├── cubit/..._cubit_test.dart
│   │   │       └── pages/..._page_test.dart
│   │   ├── fixtures/{{FEATURE_EJEMPLO}}.json
│   │   └── helpers/fixture_reader.dart
│   ├── assets/
│   ├── android/ ios/
│   ├── .env .env.example
│   ├── .fvmrc .fvm/fvm_config.json
│   ├── analysis_options.yaml
│   ├── l10n.yaml
│   ├── pubspec.yaml
│   ├── Makefile
│   └── README.md
│
├── apps/web/
│   ├── app/
│   │   ├── error.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── lib/
│   │   ├── supabase/{client,server}.ts
│   │   └── utils.ts
│   ├── components/ui/{card.tsx,card.test.tsx}
│   ├── public/
│   ├── .env.local .env.example
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── tsconfig.json
│   ├── vitest.config.ts vitest.setup.ts
│   ├── Makefile
│   └── README.md
│
├── supabase/
│   ├── config.toml
│   ├── migrations/
│   │   ├── README.md
│   │   ├── 00001_public_entries.sql
│   │   └── 00002_create_profiles.sql      (si pegaste PACK: auth)
│   ├── tests/
│   │   ├── 000_helpers.sql
│   │   ├── 001_schema_basico_test.sql
│   │   ├── 002_profiles_test.sql         (si pegaste PACK: auth)
│   │   └── 003_rpc_public_catalog_test.sql(si pegaste PACK: rpc-publicas)
│   ├── functions/.gitkeep
│   └── seed.sql
│
├── docs/
│   ├── adr/0001-estructura-del-monorepo.md
│   └── openspec/.gitkeep
│
├── tools/.gitkeep
├── .github/
│   ├── ISSUE_TEMPLATE/{bug_report,feature_request}.yml
│   └── workflows/{mobile,db,web,security}.yml
├── .vscode/
│   ├── extensions.json
│   ├── launch.json
│   └── settings.json.example
├── AGENTS.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── README.md
├── SECURITY.md
├── Makefile
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .nvmrc
├── commitlint.config.js
└── dependabot.yml
```

## Apéndice B -- Tabla de convenciones

Referencia rapida. Todo lo que hay aca estaavecitado en `AGENTS.md`; esta la
version completa con el por que.

### Flutter

| Concepto | Convencion | Por que |
|---|---|---|
| Organizacion | Feature-first: `features/<f>/{data,domain,presentation}` | Un cambio de negocio no hace saltar entre 5 carpetas |
| `lib/` | 3 entradas: `main.dart`, `core/`, `features/` | Si `lib/` tiene `models/` sueltas, se vuelve horizontal |
| Dependencia | `presentation -> domain <- data`; `core` no importa `features` | Un `core` que importa una feature es un ciclo |
| Imports | Siempre `package:` | Un import relativo se rompe al mover el archivo |
| Presentacion | `pages/`, `widgets/`, `utils/`, `cubit/` | Consistencia; `screens/` y `pages/` conviven mal |
| DataSource | `datasources/`, archivo `<algo>_data_source.dart` | **Dos palabras.** La forma de una palabra se ve en codigo viejo ajeno |
| Repositorio | `<algo>_repository.dart` + `_impl.dart` | El `Impl` separado del contrato, para poder mockear |
| Entidad | `<algo>_entity.dart` | Marca visual de "esto es dominio puro" |
| Modelo | `<algo>_model.dart`, `fromJson`/`toJson` explicitos | Sin `json_serializable`: el `.g.dart` esconde el mapeo |
| Use case | `<verbo>_<sustantivo>_usecase.dart`, con sufijo `usecase` | `sign_in_usecase.dart` y no `sign_in.dart` |
| Params | `<UseCase>Params`, `const`, `Equatable`, mismo archivo | Vive junto al use case que lo consume |
| Cubit | `Cubit`, nunca `Bloc` | Menos ceremonia para el 90% de las pantallas |
| Estado | `part of` del cubit, `sealed` + `final class` | El cubit tiene el estado sin importar el archivo |
| Variantes | `XCubit -> XState`, variantes `XLoaded` sin sufijo `State` | `RaffleListLoaded`, no `RaffleListStateLoaded` |
| Error | `XError(String message)` | La UI muestra texto, no tipos |
| `Either` | `package:fpdart/fpdart.dart` | `dartz` sin mantenimiento |
| Dependencias | GetIt + `injectable`, alias `sl` | El registro vive al lado de cada clase, no en un archivo compartido. Ver ADR 0002 |
| Registros | `@lazySingleton` en data/domain; `@injectable` (factory) en cubits de pantalla | Un cubit singleton fuga al rotar |
| Codegen de DI | `service_locator.config.dart` commiteado y regenerado con `make gen` | Si lo regeneras y hay diff, alguien anoto algo y no corro `make gen` |
| `SupabaseClient` | Se inyecta desde el `@module`, con `Supabase.instance.client` | GetIt guarda la referencia; la fuente unica sigue siendo la libreria |
| Env | `flutter_dotenv`, todo acceso via `AppConfig` | Un punto de lectura de credenciales, no veinte |
| Config | `AppConfig` (del `.env`) vs `AppConstants` (hechos) | Lo que varia por entorno se separa de lo que no |
| Cache | Isar community, arranque en `core/data/local/` | El cache es global; sus schemas tambien |
| TTL | `cachedAt` + `expiresAt` en toda coleccion | Un cache sin TTL es una fuente de datos obsoleta |
| Namespaces | Prefijo por feature en la clave del cache | Una coleccion compartida sin prefijo devuelve todo |
| Lint | `very_good_analysis` + `bloc_lint`, con la lista de `ignore` | Cada excepcion justificada al lado |
| Tests | `mocktail` + `bloc_test`, espejando `lib/` | Una ruta a un test te dice donde esta el codigo |
| Fixtures | JSON en `test/fixtures/` + `fixture_reader.dart` | El path del fixture va en el error |
| AAA | `// ARRANGE` / `// ACT` / `// ASSERT`, en mayusculas | Legible de un vistazo, sin depender del IDE |
| Prefijos de test | `mock*` para mocks, `t*` para datos | Se distingue el doble del dato real |
| Deprecaciones | El SDK exacto en `.fvmrc`, no `^3.11.0` | Dos personas con SDK distinto, bugs distintos |

### Backend

| Concepto | Convencion | Por que |
|---|---|---|
| Nombre de migration | `00001_nombre.sql`, ordinal de 5 digitos | Un timestamp no ordena; el ordinal deja ver los huecos |
| Nombre de policy | `<Actor> can <accion> <alcance>` | `Anyone can read public raffles` se lee solo |
| `TO` en la policy | Siempre explicito | `USING (true)` sin `to anon` es un invitation a equivocarse |
| RLS | Habilitada en **toda** tabla | RLS sin policy es denegar todo, y eso es una decision |
| `force row level security` | En tablas donde el owner no debe saltarse las policies | Sin esto, el owner ve todo |
| `security definer` | Siempre con `set search_path = ''` + esquemas calificados | Sin eso, la funcion es secuestrable |
| `grant execute` | `revoke from public` y `grant` a quien corresponda | El default de Postgres es permitir a todos |
| Columns nuevas | `NOT NULL DEFAULT`, siempre | Agregar una NOT NULL sin default rompe clientes viejos |
| Tests | pgTAP, en el mismo PR que la migration | Una migration sin test entra y no vuelve |
| Test de RLS | Feliz + `anon` + ajeno + dueno | Un test de RLS que solo prueba el camino feliz no prueba RLS |
| Secrets | La secret key nunca en el cliente | Salta RLS |

### Web

| Concepto | Convencion | Por que |
|---|---|---|
| Directorio | `app/`, `lib/`, `components/`, sin `src/` | El default de Next; `src/` es costumbre, no necesidad |
| Alias | `@/* -> ./*` | Sin `src/`, el alias apunta a la raiz |
| Versiones | `next` y `eslint-config-next` con version exacta | Un minor de Next rompe builds sin avisar |
| Supabase | `client.ts` (navegador) y `server.ts` (Node), dos archivos | El error aparece en el import, no en el primer click |
| Cliente de browser | `createBrowserClient()` a **nivel de modulo** | Adentro del componente se crea uno por render |
| Sesion en el servidor | `await cookies()`, `getAll`/`setAll` | Durante el render son read-only; por eso el `try/catch` |
| Verificacion de sesion | `auth.getUser()`, **nunca** `getSession()` | `getSession()` no valida el JWT. Es la diferencia entre verificar y confiar |
| Mutaciones | Server Actions (`'use server'`), no Route Handlers | Formularios sin logica de cliente ni exposure de claves |
| `next` en redirects | Validar que empieza con `/` y no con `//` | Sin eso, el login es un redirector abierto |
| Tailwind | v4 CSS-first con `@theme` | Un `tailwind.config.js` en v4 mezcla dos sistemas |
| Fontes | `next/font`, nunca `<link>` a una CDN | Sin request extra y sin CLS |
| Seguridad | Headers en `next.config.ts` | Centralizado, no disperso por componente |

## Apéndice C -- Decisiones de diseño, con sus contras

Cada seccion explica por que se eligio algo y que se pierde. Las partes "que se
pierde" son las que hay que leer antes de decidir que el tradeoff vale.

### 1. `injectable`, no registro manual

**Se elige:** anotaciones en cada clase + `service_locator.config.dart`
generado. `service_locator.dart` solo declara `sl` y `configureDependencies()`.

**Gana:** el registro vive al lado de la clase que se registra. Agregar una
feature es anotar cinco clases y correr `make gen`; nadie toca un archivo que
todas las features comparten, asi que dos features en paralelo no chocan en el
mismo diff. Cuando la abstracta cambia de implementacion, el cambio es de una
linea en la clase, no de un closure en un archivo de 400. Y el `@module` da un
lugar declarado para lo externo (`Isar`, `SupabaseClient`, `http.Client`) que la
cascada manual repartia entre comentarios.

**Se pierde:**

- Un archivo mas commiteado (`service_locator.config.dart`) que puede quedar
  viejo. Si alguien anota una clase y no corre `make gen`, el error no es de
  compilacion: aparece al primer resolve, con un `X is not registered`. Por eso
  CI regenera y hace `git diff --exit-code`.
- `grep sl<` deja de ser el mapa de dependencias. El mapa ahora es
  `grep '@lazySingleton\|@injectable\|@LazySingleton'` sobre `lib/`.
- Dos paquetes de codegen mas, con un rango de resolucion ajustado:
  `injectable_generator` y `isar_community_generator` se pelean por `analyzer`
  (ver ADR 0002, Versiones). Subir de Flutter obliga a revisar los dos juntos.
- Anotar cada clase. Es mecanico, pero es codigo que hay que escribir.

**Cuando cambiar:** a `inject.dart` si el codegen se vuelve lento o si queres
un grafo verificado en compile time. A registro manual si el proyecto se
congela y nadie va a agregar features: sin cambios, no hay nada que regenerar.

### 2. El nucleo no asume autenticacion

**Se elige:** identidad declarada y vacia (`CurrentUser` + `CurrentUserStub`),
auth en un pack aparte.

**Gana:** el nucleo sirve para una app con usuarios y para una sin ellos. La
pregunta "esta app tiene usuarios" la responde el dueno del proyecto, no el
bootstrap. Un `/login` generado compila, asi que el error aparecia meses despues,
cuando nadie recordaba por que estaba.

**Se pierde:** un proyecto con auth necesita dos pasos (pegar el pack) y un
archivo que borrar (`current_user_stub.dart`). Es un paso extra para el caso
comun.

**Por que no importa tanto:** el caso comun **es** con auth. La friccion esta en
la copia del prompt, una vez. El costo del error, en cambio, lo paga el que
herede el proyecto en un ano, y paga porque el codigo estaba bien.

### 3. Un slice vertical descartable

**Se elige:** `features/example/` con datasource en memoria y `make
drop-feature`.

**Gana:** al terminar la PARTE A, el proyecto esta verificado de punta a punta: DI,
router, l10n, Isar, cubit, Either, tests y el ciclo completo de una operacion. El
slice existe para poder borrar el acoplamiento: si no podes borrarlo sin tocar
nada mas, hay un problema, y lo encontraste en el momento de borrar y no tres
meses despues.

**Se pierde:** ~15 archivos que no van a ser codigo de producto. Y el `// TODO:`
del datasource de red queda como recordatorio de algo que quizas nunca
implementes.

**Alternativa descartada:** generar solo `core/` y dejar el slice en la
documentacion. El proyecto queda "limpio" y sin verificar hasta la primera
feature real, que es donde aparecen los errores de cableado.

### 4. `ErrorHandler` con strings, no l10n de errores

**Se elige:** un mapa de strings del proveedor a texto en español.

**Gana:** resuelve el problema mas comun de una app con l10n: el mensaje crudo de
Supabase ("Invalid login credentials") nunca llega a la UI. Y funciona sin
tener l10n implementado.

**Se pierde:** dos cosas.

1. **Los mensajes del proveedor son un contrato no documentado.** Cuando
   Supabase los cambia, el lookup falla, cae en `_fallback`, y el usuario ve
   "Algo salio mal" en vez de un mensaje util. Los tests del archivo son la unica
   defensa: cuando el string cambia, el test falla. Sin tests, el archivo
   degrada en silencio.

2. **Es la razon por la que el l10n puede quedarse sin implementar.** Con un
   traductor de errores funcionando, nadie siente la falta de ARB. Y con el
   tiempo aparecen strings en espanol en tres lugares (`ErrorHandler`,
   `AppConstants`, y literals en los cubits) que ya no se traducen.

**La migracion, si la hacia falta:** agregar un enum `FailureCode` al dominio,
mapear el string crudo al code **una vez** en el repositorio, y dejar el mensaje
para el usuario en el ARB. El string crudo deja de cruzar la frontera de `data`.
El pack de auth, paso P8, ya trae la forma de hacerlo.

### 5. `Failure` con `code` y `ServerException` con `statusCode`

**Se elige:** dos campos, en dos capas.

**Gana:** el codigo HTTP es un detalle del transporte; el `code` de negocio es
del dominio. El `Failure` que ve la UI lleva lo que la UI necesita.

**Se pierde:** hay que leer dos campos en vez de uno, y es facilollars. Cuando el
mensaje que se muestra necesita el status HTTP, hay que pasarlo a mano del
`ServerException` al `ServerFailure`.

**No confundir:** son cosas distintas. Un 404 de una RPC y un 404 de "este
elemento no existe en tu cuenta" son el mismo status con codigos distintos.

### 6. Comparar errores por `code`, no por mensaje

**Se elige:** comparar el tipo del `Failure` o un enum propio.

**Gana:** el mensaje de gotrue no esta tipado y cambia entre versiones. Un
`failure.message == 'email_not_confirmed'` compila, funciona hoy, y se rompe
cuando una dependencia actualiza.

**Se pierde:** hay que agregar el enum y el mapeo. Un `==` a un string es una
linea; el enum son quince.

### 7. RLS habilitado sin policies = denegar todo

**Se elige:** toda tabla nueva empieza con RLS habilitado y sin policies.

**Gana:** el default es seguro. Una tabla recien creada es privada hasta que
alguien decide abrirla, y esa decision queda escrita en el diff. Al reves —sin
RLS hasta que la agregues—, el default es expuesto.

**Se pierde:** un desarrollador nuevo ve "no puedo leer mi tabla" y no entiende
por que. El `001_schema_basico_test.sql` y el comentario en el README de
migrations existen por eso.

### 8. `SECURITY DEFINER` con `search_path` acotado

**Se elige:** `set search_path = ''` con todos los nombres calificados.

**Gana:** sin esto, la funcion resuelve nombres por el `search_path` de quien la
llama. Un atacante con `CREATE` en un schema pone un objeto con el nombre de
vuestra tabla interna y ejecuta su codigo dentro de la funcion, con los permisos
de la funcion. Es un takeover, no una fuga de datos.

**Se pierde:** verbosidad. `public.catalogo_items` en vez de `catalogo_items`, en
cada query de la funcion.

### 9. El `catch` especifico en el repositorio

**Se elige:** `on CacheException catch`, `on ServerException catch`, sin
`on Object catch` al final.

**Gana:** un `TypeError` de un bug de mapeo se rompe en los tests en vez de
aparecer al usuario como "Algo salio mal. Tipo 'Null' no es un subtipo de
'String'".

**Se pierde:** una excepcion no prevista sube hasta el borde de la app y la
mata. Es el comportamiento correcto: una excepcion no prevista es un bug, y un
bug deberia ser ruidoso.

### 10. `skipLibCheck: true` en `tsconfig.json`

**Se elige:** activar.

**Gana:** no se pierde tiempo arreglando errores de tipos en `node_modules`, que
no son tuyos.

**Se pierde:** un error real de tipos en una dependencia queda oculto. El
`npm audit` y el chequeo de versiones cubren parte de eso.

### 11. Pinned versions vs rangos

**Se elige:** `next` y `eslint-config-next` con version exacta. Todo lo demas
con `^`.

**Gana:** Next es estricto con las personalizaciones y las deprecaciones entre
minors son reales. Un `^16.2.6` deja que un minor rompa el build un martes.

**Se pierde:** hay que mover la version a mano o esperar a Dependabot. Un
`package.json` con todo pineado es mas ruido; se eligio solo donde el costo del
problema es alto.

### 12. La deprecacion de PROMPT-SCAFFOLD.md

`PROMPT-SCAFFOLD.md` sigue en el repo, con una nota al principio que apunta acá.
Se conserva en vez de borrarlo porque:

- Alguien lo puede estar usando ahora mismo.
- Los repos publicos no se borran: quien lo.Find en un buscador sigue llegando.
- Comparar el prompt viejo con este es la forma mas rapida de entender que
  cambio y por que.

El prompt viejo era solo Flutter, sin Next.js, con auth asumido, DI por
codegen, y 17 defectos concretos. Este los corrige.

---

