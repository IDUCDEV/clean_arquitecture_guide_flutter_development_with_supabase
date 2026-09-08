# 31 — Debugging por Capa: Ejecución Aislada de cada Capa con el Debugger

> Cuando desarrollas en **modo andamiaje SDD** ([02-SPEC-DRIVEN-DEVELOPMENT](../02-SPEC-DRIVEN-DEVELOPMENT/)), la IA genera el esqueleto de cada fichero con `throw UnimplementedError()` y **tú implementas los cuerpos**. El problema: una feature recién andamiada **no está cableada** — no ves su resultado desde la app completa porque las capas superiores todavía no existen. Este capítulo te da la técnica para **correr cada capa de forma aislada con el debugger** y verificar, en tiempo real, que hace lo que debe — sin tests obligatorios y sin depender de la IA para debugear.

---

## 1. El problema que resuelve

En el flujo SDD, para llegar a la feature `add-cart` tienes 6+ ficheros por capa:

```
domain/entities/cart.dart          → throw UnimplementedError()
domain/usecases/get_cart.dart      → throw UnimplementedError()
data/models/cart_model.dart        → throw UnimplementedError()
data/datasources/cart_remote_datasource.dart  → throw UnimplementedError()
data/repositories/cart_repository_impl.dart   → throw UnimplementedError()
presentation/cubit/cart_cubit.dart → throw UnimplementedError()
presentation/pages/cart_page.dart  → throw UnimplementedError()
```

**No puedes** arrancar la app y ver el resultado porque:
- La ruta `/cart` aún no existe o no está guardada por sesión.
- `CartPage` depende de `CartCubit`, que depende de usecases, que dependen del repository, que depende del datasource... y nada está implementado aún.
- GetIt (`service_locator.dart`) registra dependencias que aún lanzan `UnimplementedError`.

**La solución:** crear un **entrypoint aislado (scratchpad)** por capa que instancie SOLO esa capa, le inyecte a mano lo que necesita, la invoque y deje el **debugger** para pisar línea a línea. Así verificas cada capa **en el momento exacto en que la implementas**, sin esperar a cablear toda la feature ni depender de la app.

> Esta es la diferencia entre **testing** (que automatiza verificación y vive en [05-TESTING](../05-TESTING/)) y **este capítulo**: ejecución *manual e interactiva* con el debugger para **entender y verificar el comportamiento real** mientras escribes. No son excluyentes — se complementan. Cuando una capa te cuesta "verla bien" con el debugger, ese es el mejor momento para escribirle un test (usa la skill `flutter-test-generator`).

---

## 2. Los dos modos de verificación (clave)

Antes de escribir código, decide **qué le inyectas** a la capa para correrla aislada. Hay dos modos:

### Modo A: REAL (integración) — para capas de datos
Las capas que hablan hacia afuera (datasource → Supabase; repository → datasource) se verifican mejor contra sus **dependencias reales**. El objetivo es **ver la respuesta real** de la API, la excepción real, el request HTTP real.

```dart
// SCRATCH — datasource REAL contra Supabase
// No hay fake. Construyes el client real y ves el JSON que devuelve.
final client = SupabaseClient(
  const String.fromEnvironment('SUPABASE_URL'),
  const String.fromEnvironment('SUPABASE_ANON_KEY'),
);
final ds = CartRemoteDataSource(client: client);

// Pones AQUÍ un breakpoint → ves la respuesta realmente devuelta
final items = await ds.getCart(userId: 'test-123');
print(items); // ElevatedButton? No — el JSON real mapeado
```

### Modo B: AISLADO CON STUB — para capas superiores
Las capas que dependen de capas **internas aún no implementadas** (usecase → repository; cubit → usecases) se verifican con un **stub manual** — objeto que imita a la dependencia para ejercitar la lógica de la capa sin esperar a tenerla.

```dart
// SCRATCH — usecase con repository STUB (aún no implementado)
class _CartRepositoryStub implements CartRepository {
  @override
  Future<Either<Failure, List<Cart>>> getCart({required String userId}) async {
    return Right([Cart(id: '1', items: [...])]); // dato de prueba fijo
  }
}

void main() async {
  final usecase = GetCart(repository: _CartRepositoryStub());
  final result = await usecase(GetCartParams(userId: 'test-123'));
  // Breakpoint aquí → ves el Either<Failure, List<Cart>> resultante
  result.fold(
    (l) => print('Failure: $l'),
    (r) => print('Éxito: ${r.length} items'),
  );
}
```

> **Regla práctica:** usa **Modo A (real)** siempre que la dependencia externa ya exista y quieras ver el comportamiento real. Usa **Modo B (stub)** SOLO cuando la dependencia inferior todavía no está lista y quieres verificar la lógica de la capa sin bloquearte. La matriz de la sección 5 te dice cuál elegir por capa.

---

## 3. El patrón scratchpad: dónde y cómo

### 3.1 Dónde vivir
Crea una carpeta `tool/scratch/` (recomendado — no se compila a producción) o `lib/scratch/`. Un `main` por capa:

```
tool/scratch/
├── main_entity.dart       → dart run
├── main_model.dart        → dart run
├── main_state.dart        → dart run
├── main_usecase.dart      → dart run
├── main_datasource.dart   → flutter run -t tool/scratch/main_datasource.dart
├── main_repository.dart   → flutter run -t
├── main_cubit.dart        → flutter run -t
└── main_page.dart         → flutter run -t
```

> **¿`dart run` o `flutter run -t`?** Si la capa NO toca Flutter (no importa `flutter/*`, no usa widgets, no usa paquetes que requieran motor Flutter) → `dart run`. Si toca Flutter (datasource con `supabase_flutter`, cubit con `flutter_bloc`, page) → `flutter run -t <archivo>`.

### 3.2 Cómo lanzarlo con el debugger
Añade entradas al `launch.json` (ver [02-configuracion-launch-json.md](./02-configuracion-launch-json.md)) para cada scratchpad. Así lo lanzas con `F5` y pisas breakpoints como en la app:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Scratch: UseCase (dart)",
      "type": "dart",
      "request": "launch",
      "program": "tool/scratch/main_usecase.dart"
    },
    {
      "name": "Scratch: DataSource (flutter)",
      "type": "dart",
      "request": "launch",
      "program": "tool/scratch/main_datasource.dart",
      "dartDefine": [
        "SUPABASE_URL=http://localhost:54321",
        "SUPABASE_ANON_KEY=eyJ..."
      ]
    },
    {
      "name": "Scratch: Cubit (flutter)",
      "type": "dart",
      "request": "launch",
      "program": "tool/scratch/main_cubit.dart"
    }
  ]
}
```

> Usa el `presentation` de [02 §13](./02-configuracion-launch-json.md#13-presentation--ordenar-y-agrupar-configuraciones) para agrupar todos los `Scratch: *` en un submenú y ocultar el ruido.

---

## 4. Inyección manual (sin GetIt)

El andamiaje registra dependencias en GetIt, pero en el scratchpad **no quieres depender del DI global** (esas dependencias aún lanzan `UnimplementedError`). Inyectas **a mano** en el `main`:

```dart
// ❌ No hagas esto en el scratch (depende de capas aún rotas)
final ds = GetIt.I<CartRemoteDataSource>();

// ✅ Haz esto: construyes SOLO lo que tu capa necesita
final ds = CartRemoteDataSource(client: realClient);      // Modo A
final repo = CartRepositoryImpl(datasource: ds);          // Modo A (ds ya real)
final usecase = GetCart(repository: stubRepo);            // Modo B
final cubit = CartCubit(usecases: [stubUsecase]);        // Modo B
```

Esto te da **control total del harness**: decides exactamente qué se ejecuta y qué se simula, y el debugger se centra en tu capa, no en el cableado.

---

## 5. Matriz: cómo ejecutar y verificar cada capa

| Capa | Runtime | Qué inyecto | Modo | Qué verifico (breakpoint/debugPrint) |
|---|---|---|---|---|
| **Entity** | `dart run` | nada | — | Cálculos puros, invariantes, `Equatable`/`copyWith`, bordes (total, descuento) |
| **Model** | `dart run` | nada | — | `fromJson`/`toJson`, roundtrip, mapeo snake↔camel, conversión a entity |
| **State** | `dart run` | nada | — | Igualdad/`props`, que cada estado sea distinto del anterior |
| **UseCase** | `dart run` | repository | **B (stub)** si repo aún no está, o A si ya existe | `Either<Failure,T>`, mensajes EXACTOS de validación (RN001-RN006) |
| **DataSource** | `flutter run -t` | client real | **A (real)** | Respuesta JSON real, excepciones reales (`AuthException`, `SocketException`), RPC |
| **RepositoryImpl** | `flutter run -t` | datasource | A (si ya) o B (stub) | Mapeo excepción→`Failure`, delega al datasource |
| **Cubit** | `flutter run -t` | usecases | A (si ya) o B (stub) | Transiciones de estado una a una, `BlocObserver` |
| **Page/Widget** | `flutter run` | cubit | A o B + Widget Inspector | Render por cada estado (Loading/Loaded/Error) |

> **Entity / Model / State** no inyectan nada y no tocan I/O → se corren con `dart run` puro, lo más rápido y simple para verificar lógica pura. Los **debugPrint** aquí son muy útiles para ver el resultado de cálculos sin abrir la app.

---

## 6. Capa a capa: qué hace cada scratchpad

### 6.1 Entity — lógica pura
Verificas cálculos e invariantes con `dart run`, sin dependencias.

```dart
// tool/scratch/main_entity.dart
import '../...' ; // ruta a tu entidad

void main() {
  final cart = Cart(
    items: [
      CartItem(name: 'Camiseta', price: 100, quantity: 2),
      CartItem(name: 'Gorra', price: 50, quantity: 1),
    ],
  );
  // Breakpoint aquí → inspecciona subtotal, impuesto, total
  print('Subtotal: ${cart.subtotal}');   // 250
  print('Impuesto: ${cart.tax}');        // 40 (16%)
  print('Total: ${cart.total}');         // 290
  // if (cart.cartItems.isEmpty) { } // prueba bordes
}
```
> Verifica también `copyWith` y `==`/`hashCode` (Equatable): crea dos carts iguales y comprueba `a == b`.

### 6.2 Model — roundtrip JSON
```dart
// tool/scratch/main_model.dart
void main() {
  const json = {'id': '1', 'name': 'Camiseta', 'price': 100.0, 'createdAt': '2024-01-01T00:00:00Z'};
  // Breakpoint en fromJson → pisa el mapeo snake→camel
  final model = CartModel.fromJson(json);
  print(model.toJson()); // roundtrip: sale igual que entró
  print(model.toEntity()); // conversión a entidad de dominio
}
```

### 6.3 UseCase — lógica + stub de repository
```dart
// tool/scratch/main_usecase.dart
class _CartRepositoryStub implements CartRepository { /* ... */ }

void main() async {
  final usecase = GetCart(repository: _CartRepositoryStub());
  final result = await usecase(GetCartParams(userId: 'u1'));
  // Breakpoint aquí → ver el Either. Escribe el mensaje EXACTO del escenario.
  result.fold((l) => print('Failure: ${l.message}'), (r) => print('OK: ${r.length}'));
}
```
> Los mensajes de failure deben coincidir **exactamente** con los escenarios del spec (RN001-RN006 del `tasks.md`). El debugger te deja verlos antes de commitear.

### 6.4 DataSource — REAL contra Supabase (Modo A)
```dart
// tool/scratch/main_datasource.dart
import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Supabase.initialize(
    url: const String.fromEnvironment('SUPABASE_URL'),
    anonKey: const String.fromEnvironment('SUPABASE_ANON_KEY'),
  );
  final ds = CartRemoteDataSource(client: Supabase.instance.client);
  try {
    final items = await ds.getCart(userId: 'test-123');
    // Breakpoint aquí → ves la respuesta REAL devuelta por la API
    print('Items: $items');
  } on AuthException catch (e) {
    print('Auth real: ${e.message}');
  } on SocketException catch (e) {
    print('Red real: $e'); // sin conexión
  }
}
```
> **No necesitas fake** aquí: quieres ver la respuesta real. Abre **DevTools → Network View** mientras corres este scratchpad para ver el request HTTP real, su status y su payload (ver [13-network-view.md](./13-network-view.md)).

### 6.5 RepositoryImpl — mapeo excepción → Failure
```dart
// tool/scratch/main_repository.dart
// Si el datasource ya está listo → usa el REAL (Modo A).
// Si no → stub del datasource que lanza una excepción, y verificas que
// el repository la convierte en el Failure correcto.
```

### 6.6 Cubit — transiciones de estado
```dart
// tool/scratch/main_cubit.dart
void main() {
  final cubit = CartCubit(usecases: [GetCart(repository: stubRepo)]);
  // Registra un observer para ver cada estado emitido
  final sub = cubit.stream.listen((state) => print('→ $state'));
  cubit.loadCart(); // Breakpoint en el cubit → pisa la transición
  // Verifica: Initial → Loading → Loaded (o Error)
}
```
> Con `flutter run -t` + DevTools puedes conectar el **Bloc Inspector** y ver las transiciones visualmente (ver [16-BLOC-CUBIT](../16-BLOC-CUBIT/)).

### 6.7 Page/Widget — render por estado
```dart
// tool/scratch/main_page.dart
void main() {
  runApp(MaterialApp(
    home: BlocProvider(
      create: (_) => CartCubit(usecases: [stubUsecase]),
      child: const CartPage(),
    ),
  ));
}
```
> Usa **Flutter Inspector → Select Widget Mode** para ver cómo renderiza cada estado (Loading/Loaded/Error). Puedes inyectar el cubit con un estado `Error` fijo para ver ese render sin esperar un fallo real.

---

## 7. Secuencia de build order SDD: verificar capa a capa

Este es el flujo completo conforme implementas el andamiaje. El bucle por capa es:

```
1. Escribes el cuerpo de la capa (reemplazas throw UnimplementedError)
2. Creas el scratchpad para esa capa (o reutilizas uno)
3. Lo corres con el debugger (F5) y pisas los breakpoints
4. Verificas que hace lo que dice el criterio "Éxito" del tasks.md
5. ¿OK? → pasas a la siguiente capa. ¿Mal? → corriges e iteras
```

### Orden sugerido (dependencia de abajo hacia arriba)

| Paso | Capa | Verificas | Modo |
|---|---|---|---|
| 1 | **Entity** | cálculos puros, invariantes | — |
| 2 | **Model** | roundtrip JSON ↔ entity | — |
| 3 | **DataSource** | respuesta REAL de la API | **A real** |
| 4 | **State** | igualdad de estados | — |
| 5 | **RepositoryImpl** | mapeo excepción → Failure | A (ds real) |
| 6 | **UseCase** | Either + mensajes exactos | B stub (repo ya real) |
| 7 | **Cubit** | transiciones de estado | B stub (useCases reales) |
| 8 | **Page/Widget** | render por estado | B + Widget Inspector |
| 9 | **Wiring** (DI + ruta) | app completa ya funciona | — |

> El orden real lo decide la estructura del `tasks.md` de tu feature, pero el principio es el mismo: **verifica cada capa en cuanto la terminas, antes de construir la siguiente**. Así los bugs se aíslan a la capa recién escrita — nunca arrastras un error de la capa 2 mientras depuras la 6.

---

## 8. Checklist: "¿esta capa está verificada?"

Antes de pasar a la siguiente capa, confirma:

```
□ Corrí la capa aislada con el debugger (F5) y pisé los breakpoints clave
□ Vi el resultado real esperado (respuesta API, cálculo, estado, render)
□ Probé al menos el camino feliz Y el camino de error/borde
□ Si el spec define mensajes/valores exactos, los verifiqué literalmente
□ No necesité la app completa ni la IA para saber que funciona
□ (Si la capa fue difícil de "ver") escribí un test con flutter-test-generator
```

---

## Resumen

| Concepto | Valor |
|---|---|
| **Problema** | Feature andamiada no está cableada → no se ve desde la app |
| **Solución** | Scratchpad (`tool/scratch/main_*.dart`) por capa, corrido con el debugger |
| **Modo A (real)** | datos: datasource/repository contra Supabase real, ver respuesta real |
| **Modo B (stub)** | superiores: usecase/cubit con stub manual mientras la dependencia no está |
| **`dart run`** | capas puras sin Flutter (entity, model, state, usecase) |
| **`flutter run -t`** | capas que tocan Flutter (datasource, repository, cubit, page) |
| **Puente a tests** | si una capa cuesta verla bien, ese es el momento de escribir su test (05) |

> Para lanzar cada scratchpad configura entradas en el `launch.json` — ver [02-configuracion-launch-json.md](./02-configuracion-launch-json.md). Para las capas de datos, combínalo con [Network View](./13-network-view.md). Para estados, con el guard de [07-practicas-vscode](./07-practicas-vscode.md). Este capítulo es la pieza que une "escribo una capa" con "la verifico aislada, sin depender de la IA".

---

## 📚 Módulos relacionados

- [05-TESTING](../05-TESTING/) — Verificación automatizada (complemento: tests por capa)
- [02-SPEC-DRIVEN-DEVELOPMENT](../02-SPEC-DRIVEN-DEVELOPMENT/) — Origen del andamiaje y criterios "Éxito" por capa
- [01-CLEAN-ARCHITECTURE](../01-CLEAN-ARCHITECTURE/) — Las capas que recorres aquí
- [16-BLOC-CUBIT](../16-BLOC-CUBIT/) — Debugging de estados (BlocObserver)

---

> 📖 **Volver al índice:** [README.md](./README.md)
