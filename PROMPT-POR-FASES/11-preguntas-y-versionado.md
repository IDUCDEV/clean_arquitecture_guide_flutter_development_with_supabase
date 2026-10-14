## Preguntas que este prompt no responde

Decidaselas antes de arrancar la PARTE A. No son bloqueantes: el prompt genera el
proyecto igual. Pero cada una cambia el codigo que genera.

1. **La app tiene usuarios o no.** Si no, no pegues `## PACK: auth`. Si si,
   pegalo desde el principio: agregar auth despues significa tocar el router, el
   `main.dart`, el DI y dos migraciones, y el cubit de auth tiene que conocer el
   router desde el dia uno.
2. **El backend es publico o privado.** Si publico, `## PACK: rpc-publicas` y la
   web seHFace anonima. Si privado, es `## PACK: auth` y nada mas.
3. **Where va la identidad.** `CurrentUserStub` esta bien si no hay usuarios. Con
   usuarios, pegá `CurrentUserSupabase`. Si tu app tiene identidad propia (un
   `deviceId`, una sesion corporativa), implementa `CurrentUser` a mano y borra las
   dos versiones.
4. **Si el l10n se va a usar de verdad.** El prompt deja el pipeline armado y las
   claves cargadas. `ErrorHandler` traduce los errores en espanol sin pasar por
   ARB, asi que es facil quedarse con la mitad del sistema. Si no vas a usar ARB,
   borralo: un pipeline a medio usar es peor que ninguno.
5. **Si el cache local es necesario.** Isar arranca aunque tu app sea online-only
   y no cachee nada. Si no vas a cachear, `current_user_stub.dart` sigue siendo la
   identidad correcta, pero `core/data/local/` no aporta y `core/services/
   cache_manager.dart` tampoco.
6. **Frecuencia de deploy.** Si hay varios deploys por dia, el slice de ejemplo
   es mas util todavia: verificar el pipeline con una feature descartable en vez
   de con la feature real.

---

## Versionado de este prompt

| Version | Que cambio |
|---|---|
| v2 (este) | Nucleo sin auth + packs. DI con `injectable` (registro por anotación, `@module` para lo externo, `service_locator.config.dart` commiteado). `*_data_source.dart`. `core/routing/`. `part of` en estados. `core/session/current_user.dart`. Slice descartable + `make drop-feature`. `ErrorHandler`. Tests pgTAP de seguridad como default. Migraciones con ordinal. Use cases con sufijo `usecase` en archivo y clase (`get_raffles_usecase.dart`, `GetRafflesUseCase`). |
| v1 | `PROMPT-SCAFFOLD.md`: Flutter unicamente, auth asumido, `*_datasource.dart`, `core/router/`. 17 defectos. |

**Cambios grandes respecto de la v1**, si venis de ahi:

1. **La auth paso deassumption a pack.** Es el cambio de fondo.
2. **`*_datasource.dart` -> `*_data_source.dart`.** Dos palabras.
3. **`core/router/` -> `core/routing/`.**
4. **Los estados pasaron a `part of` en vez de import.**
5. **`Failure` paso de `statusCode` a `code`, con `required message`.**
6. **Apareció `core/session/current_user.dart`** en lugar de acoplar el router a
   la sesion.
7. **Apareció `ErrorHandler`.**
8. **Se agrega un slice vertical verificable y su comando de borrado.**
9. **Los tests pgTAP de seguridad (RLS, `search_path`) son obligatorios**, no
   opcionales.
10. **Apareció la web Next.js completa**, con el patron de dos clientes de
    Supabase.
11. **Las migraciones usan ordinal de 5 digitos**, no timestamp.