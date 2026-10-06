# Ejemplo completo — Feature "Orders" con las 5 skills

Documento consolidado que reúne en un solo archivo lo que antes vivía en `EJEMPLO-PRACTICO.md`, `EJEMPLO-RESULTADO-1.md` y `EJEMPLO-RESULTADO-2.md`:

- **[Parte I — Flujo paso a paso](#parte-i--flujo-paso-a-paso)** — los prompts y qué genera cada skill, con el escenario feature **Order** de principio a fin.
- **[Parte II — Output íntegro de `clean-arch-feature`](#parte-ii--output-íntegro-de-clean-arch-feature)** — cada archivo generado al 100% (entity → page + SQL + wiring), la fuente de verdad del output.
- **[Parte III — Output íntegro de las skills de infraestructura](#parte-iii--output-íntegro-de-las-skills-de-infraestructura)** — `di-getit-scaffold` (manual + injectable), `go-route-scaffold` (auth, Sentry, combinado), `clean-arch-component` y `flutter-test-generator`.

El flujo narra **qué genera cada skill y qué haces tú**; el código íntegro vive en las Partes II y III, que se referencian desde el flujo para no duplicar contenido.

---

## Escenario

Queremos un feature **Order** con:

- Listar pedidos, ver detalle, crear, actualizar, cancelar
- Persistencia en Supabase (tabla `orders`)
- Ruta `/orders` (lista) y `/orders/:id` (detalle)

---

# Parte I — Flujo paso a paso

> **División de roles:** esta parte narra el **flujo** (prompts, qué genera cada skill, qué haces tú). El **output íntegro de cada archivo** (código al 100%) vive en la [Parte II](#parte-ii--output-íntegro-de-clean-arch-feature) (feature completa) y la [Parte III](#parte-iii--output-íntegro-de-las-skills-de-infraestructura) (DI, rutas, componentes y tests). Aquí solo se muestran los bloques únicos; el resto se referencia para no duplicar.

---

## Paso 1: Scaffold completo del feature + Supabase + páginas

**Prompt para el asistente:**

> Crea un feature `order` con campos:
> - `id: String`
> - `userId: String`
> - `total: double`
> - `status: String`
> - `items: List<OrderItem>` (asumimos OrderItem como entidad separada)
> - `createdAt: DateTime`
>
> Operaciones CRUD: `getAll`, `getById`, `create`, `update`, `delete`
>
> Además, conéctalo a Supabase. Tabla `orders`:
> - `id: uuid PK`
> - `user_id: uuid NOT NULL`
> - `total: float8 NOT NULL`
> - `status: text NOT NULL DEFAULT 'pending'`
> - `items: jsonb NOT NULL DEFAULT '[]'`
> - `created_at: timestamptz NOT NULL DEFAULT now()`
>
> Páginas iniciales: `[list:listener_builder, detail:builder]`
>
> Y wiring: regístralo en DI y añade sus rutas al router (`/orders` → lista, `/orders/:id` → detalle)

**Qué genera `clean-arch-feature` (orquestando):** 18 archivos en `lib/features/order/` + la migración SQL, más el wiring sobre `lib/core/`. Ver el árbol de archivos completo en [Parte II — Árbol de archivos resultante](#árbol-de-archivos-resultante) — aquí no se duplica.

**Ejemplos de archivos generados:** `domain/entities/order.dart` y `data/models/order_model.dart` (con mapeo snake_case). Ver el contenido íntegro en [Parte II — sección 1](#1-domainentitiesorderdart) y [Parte II — sección 4](#4-datamodelsorder_modeldart-mapeo-snake_case-por-supabase) — aquí no se duplican.

**Tú haces después:**
- Revisar la migración SQL y ejecutarla en Supabase
- Ajustar RLS policies para filtrar por `user_id`
- Implementar los bodies de las páginas (`// TODO: render content`)

---

## Paso 2: Wiring automático — DI + rutas (orquestado)

Como pediste `wiring` en el **Paso 1**, `clean-arch-feature` no se detiene al generar los archivos: en el mismo turno invoca `di-getit-scaffold` y `go-route-scaffold`, pasándoles los componentes recién creados. Cada skill es dueña de su archivo central; aquí solo se delega.

### 2a. `di-getit-scaffold` deja el feature order anotado

En el modo por defecto (`injectable`), el registro **no se escribe a mano**: `di-getit-scaffold` verifica que las clases del feature salgan anotadas (los templates de `clean-arch-feature` ya las emiten) y que `external_module.dart` tenga lo externo que pide el feature:

```dart
// En las clases del feature order (ver íntegro en Parte II §12):
@LazySingleton(as: OrderRemoteDataSource)   // OrderRemoteDataSourceImpl
@LazySingleton(as: OrderRepository)         // OrderRepositoryImpl
@lazySingleton                              // GetOrders, GetOrder, CreateOrder, UpdateOrder, DeleteOrder
@injectable                                 // OrderCubit
```

Después corres `make gen` y `service_locator.config.dart` se regenera solo con los registros de Order.

El detalle completo está en **Parte II — sección 12** — aquí no se duplica.

**Tú haces después:** correr `make gen` y commitear `service_locator.config.dart` si cambió.

### 2b. `go-route-scaffold` actualiza el router

Actualiza `lib/core/router/app_router.dart` con las rutas de las páginas generadas en el Paso 1:

```dart
// routes: [
//   GoRoute(path: '/orders', builder: (_, __) => const OrdersListPage(),
//     routes: [ GoRoute(path: ':id', builder: ...) ]),
// ]
```

El código completo está en [Parte II — sección 13](#13-libcorerouterapp_routerdart--rutas-añadidas-por-go-route-scaffold) — aquí no se duplica.

**Tú haces después:**
- Envolver `MaterialApp.router(routerConfig: AppRouter().router)` con `MultiBlocProvider` que incluya los cubits necesarios
- Implementar `OrdersListPage` y `OrderDetailPage`

> **Sin `wiring`:** si hubieras omitido `wiring` en el prompt del Paso 1, estos dos sub-pasos no se ejecutarían; tendrías que pedirlos aparte ("Deja el feature order anotado para DI y corre `make gen`", "Añade rutas de orders al router").

---

## Paso 3: Implementar bodies (tú)

Hasta aquí todo ha sido scaffolding. Ahora implementas los bodies de:

1. **`order_remote_datasource.dart`** — llamadas a Supabase (`getAll`, `getById`, `create`, `update`, `delete`, `watchById`)
2. **`order_repository_impl.dart`** — lógica con Either + try/catch mapeando excepciones a failures
3. **`order_cubit.dart`** — llamar usecases y emitir estados

Ver el "después" (3 bodies ya implementados: datasource `getAll`, repository `getAll` y cubit `loadOrders`) en la sección **"Scaffolding vs implementado"** de la [Parte II](#scaffolding-vs-implementado) — aquí no se duplican.

---

## Paso 4: Añadir página extra a feature existente

Las páginas iniciales ya se generaron en el **Paso 1** (`orders_list_page.dart` con `listener_builder`, `order_detail_page.dart` con `builder`). Ahora imagina que semanas después quieres añadir una página de edición.

**Prompt:**

> Añade una página edit al feature order con patrón form

**Qué ejecuta `clean-arch-component`:**

Carga el template `form` de la sección **"Templates de página"** de `clean-arch-feature` (fuente única — no se duplica) y genera:

`lib/features/order/presentation/pages/order_edit_page.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:order_app/core/services/snackbar_helper.dart';
import 'package:order_app/core/widgets/app_button.dart';
import 'package:order_app/features/order/presentation/cubit/order_cubit.dart';

class OrderEditPage extends StatefulWidget {
  const OrderEditPage({super.key});

  @override
  State<OrderEditPage> createState() => _OrderEditPageState();
}

class _OrderEditPageState extends State<OrderEditPage> {
  final _formKey = GlobalKey<FormState>();

  // TODO: declare TextEditingController for each field
  // late final TextEditingController _statusController;

  @override
  void initState() {
    super.initState();
    // TODO: initialize controllers
    // _statusController = TextEditingController(text: initialValue);
  }

  @override
  void dispose() {
    // TODO: dispose controllers
    // _statusController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Edit Order')),
      body: BlocListener<OrderCubit, OrderState>(
        listener: (context, state) {
          // TODO: handle success / error side effects
          // if (state is OrderUpdated) {
          //   SnackbarHelper.show(context, 'Guardado exitoso', isSuccess: true);
          //   context.pop();
          // }
          // if (state is OrderError) {
          //   SnackbarHelper.show(context, state.message, isSuccess: false);
          // }
        },
        child: BlocBuilder<OrderCubit, OrderState>(
          builder: (context, state) {
            final isLoading = state is OrderLoading;

            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // TODO: TextFormField for each field
                    const SizedBox(height: 24),
                    AppButton(
                      label: 'Guardar',
                      onPressed: isLoading ? null : _submit,
                      variant: AppButtonVariant.primary,
                      isLoading: isLoading,
                    ),
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  void _submit() {
    // TODO: implement submit
    // if (_formKey.currentState!.validate()) {
    //   context.read<OrderCubit>().updateOrder(
    //     Order(...),
    //   );
    // }
  }
}
```

**Tú haces después:**
- Implementar controllers, validación y submit
- Conectar la página en el router (`go-route-scaffold`)

---

## Paso 5: Añadir usecase extra

**Prompt:**

> Añade un usecase `cancel_order` al feature order

**Qué genera `clean-arch-component`:**

`lib/features/order/domain/usecases/cancel_order.dart`:

```dart
import 'package:fpdart/fpdart.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/common/usecase.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';

/// `@lazySingleton`: el use case no tiene estado, una instancia para la app.
/// Converso: `CancelOrderParams` (abajo) NO se anota.
@lazySingleton
class CancelOrder extends UseCase<void, CancelOrderParams> {
  final OrderRepository repository;

  CancelOrder(this.repository);

  @override
  Future<Either<Failure, void>> call(CancelOrderParams params) async {
    throw UnimplementedError('CancelOrder.call');
  }
}

class CancelOrderParams extends Equatable {
  final String orderId;

  const CancelOrderParams({required this.orderId});

  @override
  List<Object?> get props => [orderId];
}
```

**Tú haces después:**
- Implementar `call()` llamando al repositorio
- El registro de `CancelOrder` aparece tras correr `make gen` (la clase ya lleva `@lazySingleton`)
- Añadir método `cancelOrder` en el cubit

---

## Paso 6: Generar tests

**Prompt:**

> Genera tests para order_cubit

**Qué ejecuta `flutter-test-generator`:**

```bash
python3 skills/flutter-test-generator/generate_test.py \
  lib/features/order/presentation/cubit/order_cubit.dart
```

**Output:**

`test/features/order/presentation/cubit/order_cubit_test.dart`:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:bloc_test/bloc_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/usecases/get_orders.dart';
import 'package:order_app/features/order/presentation/cubit/order_cubit.dart';

class MockGetOrders extends Mock implements GetOrders {}

void main() {
  late OrderCubit cubit;
  late MockGetOrders mockGetOrders;

  setUp(() {
    mockGetOrders = MockGetOrders();
    cubit = OrderCubit(
      getOrders: mockGetOrders,
      getOrder: GetOrder,       // TODO: mock
      createOrder: CreateOrder, // TODO: mock
      updateOrder: UpdateOrder, // TODO: mock
      deleteOrder: DeleteOrder, // TODO: mock
    );
  });

  tearDown(() {
    cubit.close();
  });

  group('OrderCubit', () {
    test('debería tener estado inicial correcto', () {
      // ASSERT: expect(cubit.state, isA<OrderInitial>())
    });

    test('debería emitir estados correctos en flujo exitoso', () {
      // usar blocTest(...)
    });

    test('debería emitir estados de error cuando falla', () {
      // ARRANGE: mockGetOrders(any()) retorna Left(ServerFailure(...))
      // ACT & ASSERT: blocTest con expect: [Loading, Error]
    });
  });
}
```

**Tú haces después:**
- Completar los bodies de cada test con datos reales
- Generar tests para datasource, repository, usecases, modelo
- Ejecutar `flutter test`

---

## Mini-escenarios

Variaciones rápidas para ver cómo cambia el resultado según los parámetros opcionales.

### Mini-A: Feature con Supabase **sin** páginas ni wiring

**Prompt:**

> Crea un feature `order` con campos id, userId, total, status, items, createdAt.
> Operaciones: getAll, getById, create, update, delete.
> Conéctalo a Supabase, tabla `orders` (id uuid PK, user_id uuid NOT NULL, total float8, status text, items jsonb, created_at timestamptz).

**Qué cambia vs el Paso 1:**

| Elemento | Paso 1 (con extras) | Mini-A (sin extras) |
|---|---|---|
| Páginas | `orders_list_page.dart` + `order_detail_page.dart` | placeholder genérico `order_page.dart` |
| `service_locator.config.dart` | Regenerado con `make gen` (wiring `di`) | No se toca — el resumen final lo recuerda |
| `app_router.dart` | Actualizado (wiring `router`) | No se toca |
| Entity, model, datasource, SQL + RLS | Generados | **Igual**, se generan |

Supabase funciona con o sin páginas/wiring; lo único que se omite son las extras.

### Mini-B: Añadir entity + model a feature existente

**Prompt:**

> Añade una entidad order_item con campos productId: String, quantity: int, price: double, y su model, al feature order

**Qué genera `clean-arch-component`** (dos archivos):

`lib/features/order/domain/entities/order_item.dart`:

```dart
import 'package:equatable/equatable.dart';

class OrderItem extends Equatable {
  const OrderItem({
    required this.productId,
    required this.quantity,
    required this.price,
  });

  final String productId;
  final int quantity;
  final double price;

  @override
  List<Object?> get props => [productId, quantity, price];

  OrderItem copyWith({
    String? productId,
    int? quantity,
    double? price,
  }) {
    return OrderItem(
      productId: productId ?? this.productId,
      quantity: quantity ?? this.quantity,
      price: price ?? this.price,
    );
  }

  @override
  String toString() => 'OrderItem(productId: $productId, quantity: $quantity, price: $price)';
}
```

`lib/features/order/data/models/order_item_model.dart`:

```dart
import 'package:order_app/features/order/domain/entities/order_item.dart';

class OrderItemModel extends OrderItem {
  const OrderItemModel({
    required super.productId,
    required super.quantity,
    required super.price,
  });

  factory OrderItemModel.fromJson(Map<String, dynamic> json) {
    return OrderItemModel(
      productId: json['product_id'] as String,
      quantity: (json['quantity'] as num).toInt(),
      price: (json['price'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'product_id': productId,
        'quantity': quantity,
        'price': price,
      };

  factory OrderItemModel.fromEntity(OrderItem entity) => OrderItemModel(
        productId: entity.productId,
        quantity: entity.quantity,
        price: entity.price,
      );

  OrderItem toEntity() => OrderItem(
        productId: productId,
        quantity: quantity,
        price: price,
      );
}
```

**Tú haces después:** implementar los bodies y, si la entidad se usa desde otra clase, ajustar los imports/campos correspondientes.

---

## Resumen del flujo completo

| Paso | Skill | Archivos generados | Lo que haces tú |
|---|---|---|---|
| 1 | `clean-arch-feature` | 18 archivos + SQL migration + 2 páginas | Ejecutar migración, ajustar RLS, bodies de páginas |
| 2 | `clean-arch-feature` → orquesta `di-getit-scaffold` + `go-route-scaffold` | Feature anotado + `make gen` → `service_locator.config.dart`; `app_router.dart` actualizado | Correr `make gen`, conectar en main.dart |
| 3 | *(tú implementas)* | — | Bodies de datasource, repository, cubit |
| 4 | `clean-arch-component` | order_edit_page.dart | Implementar + conectar router |
| 5 | `clean-arch-component` | cancel_order.dart (`@lazySingleton`) | Implementar + `make gen` + método en cubit |
| 6 | `flutter-test-generator` | order_cubit_test.dart | Completar datos de prueba |
| 7 | *(tú completas)* | — | Tests restantes + `flutter test` |

---

# Parte II — Output íntegro de `clean-arch-feature`

Esta parte muestra el **resultado final completo** que produce `clean-arch-feature` para el escenario de la [Parte I](#parte-i--flujo-paso-a-paso). Mientras que la Parte I narra el *flujo paso a paso* con fragmentos, aquí se muestra **cada archivo generado al 100%** — listo para comparar contra tu propio resultado.

## Cómo usar la Parte II

1. Ejecuta el prompt del [Paso 1](#paso-1-scaffold-completo-del-feature--supabase--páginas) en un proyecto con los [prerrequisitos de la arquitectura base](./README.md#prerrequisitos-del-proyecto).
2. Compara archivo por archivo tu resultado contra el de aquí.
3. Diferencias aceptables:
   - `order_app` → el nombre de tu paquete (aparece en imports).
   - `{timestamp}` en el nombre de la migración → la fecha real de generación.
   - Orden de métodos/imports si editaste la skill o tu convención difiere.
4. Si algo difiere de forma estructural (clases, estados, patrones de página), revisa el SKILL.md de la skill correspondiente — el template es la fuente de verdad.

> **Nota:** este es scaffolding puro. Todos los bodies son `throw UnimplementedError()` / `// TODO`. La sección [Scaffolding vs implementado](#scaffolding-vs-implementado) muestra cómo se ven 3 de ellos ya implementados.

---

## Árbol de archivos resultante

```
lib/features/order/
├── data/
│   ├── datasources/
│   │   └── order_remote_datasource.dart
│   ├── models/
│   │   └── order_model.dart
│   └── repositories/
│       └── order_repository_impl.dart
├── domain/
│   ├── entities/
│   │   └── order.dart
│   ├── repositories/
│   │   └── order_repository.dart
│   └── usecases/
│       ├── get_orders.dart
│       ├── get_order.dart
│       ├── create_order.dart
│       ├── update_order.dart
│       └── delete_order.dart
└── presentation/
    ├── cubit/
    │   ├── order_cubit.dart
    │   └── order_state.dart
    └── pages/
        ├── orders_list_page.dart        # pattern listener_builder
        └── order_detail_page.dart       # pattern builder
supabase/
└── migrations/
    └── {timestamp}_create_orders.sql
```

Además, `clean-arch-feature` orquesta el wiring (`[di, router]`): deja las clases del feature **anotadas** para DI y **actualiza** el router:

```
lib/core/di/service_locator.config.dart  # regenerado por `make gen` con los registros de Order (clases anotadas en los templates)
lib/core/router/app_router.dart          # + rutas /orders y /orders/:id (go-route-scaffold)
```

---

## 1. `domain/entities/order.dart`

```dart
import 'package:equatable/equatable.dart';

class Order extends Equatable {
  const Order({
    required this.id,
    required this.userId,
    required this.total,
    required this.status,
    required this.items,
    required this.createdAt,
  });

  final String id;
  final String userId;
  final double total;
  final String status;
  final List<OrderItem> items;
  final DateTime createdAt;

  @override
  List<Object?> get props => [id, userId, total, status, items, createdAt];

  Order copyWith({
    String? id,
    String? userId,
    double? total,
    String? status,
    List<OrderItem>? items,
    DateTime? createdAt,
  }) {
    return Order(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      total: total ?? this.total,
      status: status ?? this.status,
      items: items ?? this.items,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  @override
  String toString() => 'Order(id: $id, status: $status, total: $total)';
}
```

---

## 2. `domain/repositories/order_repository.dart`

```dart
import 'package:fpdart/fpdart.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/entities/order.dart';

abstract class OrderRepository {
  Future<Either<Failure, List<Order>>> getAll();

  Future<Either<Failure, Order>> getById(String id);

  Future<Either<Failure, void>> create(Order order);

  Future<Either<Failure, void>> update(Order order);

  Future<Either<Failure, void>> delete(String id);
}
```

---

## 3. UseCases (`domain/usecases/`)

### `get_orders.dart`

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/common/usecase.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';

/// `@lazySingleton`: el use case no tiene estado, una instancia para la app.
@lazySingleton
class GetOrders extends UseCase<List<Order>, NoParams> {
  final OrderRepository repository;

  GetOrders(this.repository);

  @override
  Future<Either<Failure, List<Order>>> call(NoParams params) async {
    throw UnimplementedError('GetOrders.call');
  }
}
```

### `get_order.dart`

```dart
import 'package:equatable/equatable.dart';
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/common/usecase.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';

/// `@lazySingleton`: el use case no tiene estado, una instancia para la app.
/// Converso: `GetOrderParams` (abajo) NO se anota.
@lazySingleton
class GetOrder extends UseCase<Order, GetOrderParams> {
  final OrderRepository repository;

  GetOrder(this.repository);

  @override
  Future<Either<Failure, Order>> call(GetOrderParams params) async {
    throw UnimplementedError('GetOrder.call');
  }
}

class GetOrderParams extends Equatable {
  final String id;

  const GetOrderParams({required this.id});

  @override
  List<Object?> get props => [id];
}
```

### `create_order.dart`

```dart
import 'package:equatable/equatable.dart';
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/common/usecase.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';

/// `@lazySingleton`: el use case no tiene estado, una instancia para la app.
/// Converso: `CreateOrderParams` (abajo) NO se anota.
@lazySingleton
class CreateOrder extends UseCase<void, CreateOrderParams> {
  final OrderRepository repository;

  CreateOrder(this.repository);

  @override
  Future<Either<Failure, void>> call(CreateOrderParams params) async {
    throw UnimplementedError('CreateOrder.call');
  }
}

class CreateOrderParams extends Equatable {
  final String userId;
  final double total;
  final String status;
  final List<OrderItem> items;

  const CreateOrderParams({
    required this.userId,
    required this.total,
    required this.status,
    required this.items,
  });

  @override
  List<Object?> get props => [userId, total, status, items];
}
```

### `update_order.dart`

```dart
import 'package:equatable/equatable.dart';
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/common/usecase.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';

/// `@lazySingleton`: el use case no tiene estado, una instancia para la app.
/// Converso: `UpdateOrderParams` (abajo) NO se anota.
@lazySingleton
class UpdateOrder extends UseCase<void, UpdateOrderParams> {
  final OrderRepository repository;

  UpdateOrder(this.repository);

  @override
  Future<Either<Failure, void>> call(UpdateOrderParams params) async {
    throw UnimplementedError('UpdateOrder.call');
  }
}

class UpdateOrderParams extends Equatable {
  final String id;
  final String userId;
  final double total;
  final String status;
  final List<OrderItem> items;

  const UpdateOrderParams({
    required this.id,
    required this.userId,
    required this.total,
    required this.status,
    required this.items,
  });

  @override
  List<Object?> get props => [id, userId, total, status, items];
}
```

### `delete_order.dart`

```dart
import 'package:equatable/equatable.dart';
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/common/usecase.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';

/// `@lazySingleton`: el use case no tiene estado, una instancia para la app.
/// Converso: `DeleteOrderParams` (abajo) NO se anota.
@lazySingleton
class DeleteOrder extends UseCase<void, DeleteOrderParams> {
  final OrderRepository repository;

  DeleteOrder(this.repository);

  @override
  Future<Either<Failure, void>> call(DeleteOrderParams params) async {
    throw UnimplementedError('DeleteOrder.call');
  }
}

class DeleteOrderParams extends Equatable {
  final String id;

  const DeleteOrderParams({required this.id});

  @override
  List<Object?> get props => [id];
}
```

---

## 4. `data/models/order_model.dart` (mapeo snake_case por Supabase)

```dart
import 'package:order_app/features/order/domain/entities/order.dart';

class OrderModel extends Order {
  const OrderModel({
    required super.id,
    required super.userId,
    required super.total,
    required super.status,
    required super.items,
    required super.createdAt,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    return OrderModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      total: (json['total'] as num).toDouble(),
      status: json['status'] as String,
      items: (json['items'] as List)
          .map((e) => OrderItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'user_id': userId,
        'total': total,
        'status': status,
        'items': items.map((e) => e.toJson()).toList(),
        'created_at': createdAt.toIso8601String(),
      };

  factory OrderModel.fromEntity(Order entity) => OrderModel(
        id: entity.id,
        userId: entity.userId,
        total: entity.total,
        status: entity.status,
        items: entity.items,
        createdAt: entity.createdAt,
      );

  Order toEntity() => Order(
        id: id,
        userId: userId,
        total: total,
        status: status,
        items: items,
        createdAt: createdAt,
      );
}
```

---

## 5. `data/datasources/order_remote_datasource.dart` (con `_tableName` + `watchById`)

```dart
import 'dart:async';
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:order_app/core/error/exceptions.dart';
import 'package:order_app/features/order/data/models/order_model.dart';

abstract class OrderRemoteDataSource {
  Future<List<OrderModel>> getAll();

  Future<OrderModel> getById(String id);

  Future<void> create(OrderModel order);

  Future<void> update(OrderModel order);

  Future<void> delete(String id);

  Stream<OrderModel> watchById(String id);
}

/// `@LazySingleton(as:)`: cuando algo pida `OrderRemoteDataSource`, se
/// resuelve a esta concreta. `make gen` escribe el registro.
@LazySingleton(as: OrderRemoteDataSource)
class OrderRemoteDataSourceImpl implements OrderRemoteDataSource {
  final SupabaseClient _supabase;
  final String _tableName = 'orders';

  OrderRemoteDataSourceImpl({required SupabaseClient supabase})
      : _supabase = supabase;

  @override
  Future<List<OrderModel>> getAll() {
    throw UnimplementedError('OrderRemoteDataSource.getAll');
  }

  @override
  Future<OrderModel> getById(String id) {
    throw UnimplementedError('OrderRemoteDataSource.getById');
  }

  @override
  Future<void> create(OrderModel order) {
    throw UnimplementedError('OrderRemoteDataSource.create');
  }

  @override
  Future<void> update(OrderModel order) {
    throw UnimplementedError('OrderRemoteDataSource.update');
  }

  @override
  Future<void> delete(String id) {
    throw UnimplementedError('OrderRemoteDataSource.delete');
  }

  @override
  Stream<OrderModel> watchById(String id) {
    throw UnimplementedError('OrderRemoteDataSource.watchById');
  }
}
```

---

## 6. `data/repositories/order_repository_impl.dart`

```dart
import 'package:fpdart/fpdart.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/error/exceptions.dart';
import 'package:order_app/core/error/failures.dart';
import 'package:order_app/features/order/data/datasources/order_remote_datasource.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';

/// `@LazySingleton(as:)`: cuando algo pida `OrderRepository`, se resuelve a
/// esta concreta. `make gen` escribe el registro.
@LazySingleton(as: OrderRepository)
class OrderRepositoryImpl implements OrderRepository {
  final OrderRemoteDataSource remoteDataSource;

  OrderRepositoryImpl({required this.remoteDataSource});

  @override
  Future<Either<Failure, List<Order>>> getAll() {
    throw UnimplementedError('OrderRepositoryImpl.getAll');
  }

  @override
  Future<Either<Failure, Order>> getById(String id) {
    throw UnimplementedError('OrderRepositoryImpl.getById');
  }

  @override
  Future<Either<Failure, void>> create(Order order) {
    throw UnimplementedError('OrderRepositoryImpl.create');
  }

  @override
  Future<Either<Failure, void>> update(Order order) {
    throw UnimplementedError('OrderRepositoryImpl.update');
  }

  @override
  Future<Either<Failure, void>> delete(String id) {
    throw UnimplementedError('OrderRepositoryImpl.delete');
  }
}
```

---

## 7. `presentation/cubit/order_cubit.dart`

```dart
import 'package:bloc/bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/common/usecase.dart';
import 'package:order_app/features/order/domain/entities/order.dart';
import 'package:order_app/features/order/domain/usecases/create_order.dart';
import 'package:order_app/features/order/domain/usecases/delete_order.dart';
import 'package:order_app/features/order/domain/usecases/get_order.dart';
import 'package:order_app/features/order/domain/usecases/get_orders.dart';
import 'package:order_app/features/order/domain/usecases/update_order.dart';

part 'order_state.dart';

/// `@injectable` genera un `factory`: cada pantalla que pida el cubit recibe
/// una instancia nueva. **Nunca `@lazySingleton` en un cubit de pantalla.**
@injectable
class OrderCubit extends Cubit<OrderState> {
  final GetOrders _getOrders;
  final GetOrder _getOrder;
  final CreateOrder _createOrder;
  final UpdateOrder _updateOrder;
  final DeleteOrder _deleteOrder;

  OrderCubit({
    required GetOrders getOrders,
    required GetOrder getOrder,
    required CreateOrder createOrder,
    required UpdateOrder updateOrder,
    required DeleteOrder deleteOrder,
  })  : _getOrders = getOrders,
        _getOrder = getOrder,
        _createOrder = createOrder,
        _updateOrder = updateOrder,
        _deleteOrder = deleteOrder,
        super(OrderInitial());

  void loadOrders() {
    throw UnimplementedError('OrderCubit.loadOrders');
  }

  void loadOrder(String id) {
    throw UnimplementedError('OrderCubit.loadOrder');
  }

  void createOrder(Order order) {
    throw UnimplementedError('OrderCubit.createOrder');
  }

  void updateOrder(Order order) {
    throw UnimplementedError('OrderCubit.updateOrder');
  }

  void deleteOrder(String id) {
    throw UnimplementedError('OrderCubit.deleteOrder');
  }

  void clearError() {
    // TODO: optional — emit copy of previous state without error
  }
}
```

---

## 8. `presentation/cubit/order_state.dart`

```dart
part of 'order_cubit.dart';

sealed class OrderState extends Equatable {
  const OrderState();

  @override
  List<Object?> get props => [];
}

final class OrderInitial extends OrderState {}

final class OrderLoading extends OrderState {}

final class OrdersLoaded extends OrderState {
  final List<Order> orders;
  const OrdersLoaded(this.orders);

  @override
  List<Object?> get props => [orders];
}

final class OrderLoaded extends OrderState {
  final Order order;
  const OrderLoaded(this.order);

  @override
  List<Object?> get props => [order];
}

final class OrderError extends OrderState {
  final String message;
  const OrderError(this.message);

  @override
  List<Object?> get props => [message];
}
```

---

## 9. `presentation/pages/orders_list_page.dart` (pattern `listener_builder`)

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:order_app/core/services/snackbar_helper.dart';
import 'package:order_app/core/widgets/app_button.dart';
import 'package:order_app/features/order/presentation/cubit/order_cubit.dart';

class OrdersListPage extends StatefulWidget {
  const OrdersListPage({super.key});

  @override
  State<OrdersListPage> createState() => _OrdersListPageState();
}

class _OrdersListPageState extends State<OrdersListPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<OrderCubit>().loadOrders();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Orders')),
      body: BlocListener<OrderCubit, OrderState>(
        listener: (context, state) {
          // TODO: handle side effects
          // if (state is OrderLoaded && state.xxxError != null) {
          //   SnackbarHelper.show(context, state.xxxError!, isSuccess: false);
          //   context.read<OrderCubit>().clearXxxError();
          // }
          // if (state is OrderActionSuccess) {
          //   SnackbarHelper.show(context, 'Operación exitosa', isSuccess: true);
          //   context.pop();
          // }
        },
        child: BlocBuilder<OrderCubit, OrderState>(
          builder: (context, state) {
            if (state is OrderLoading) {
              return const Center(child: CircularProgressIndicator());
            }
            if (state is OrderError) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(state.message, overflow: TextOverflow.ellipsis),
                    const SizedBox(height: 16),
                    AppButton(
                      label: 'Reintentar',
                      onPressed: () => context.read<OrderCubit>().loadOrders(),
                      variant: AppButtonVariant.primary,
                    ),
                  ],
                ),
              );
            }
            if (state is OrdersLoaded) {
              // TODO: render content
              return const Center(child: Text('Implement OrdersListPage content'));
            }
            return const Center(child: CircularProgressIndicator());
          },
        ),
      ),
    );
  }

  void _refresh() {
    context.read<OrderCubit>().loadOrders();
  }
}
```

---

## 10. `presentation/pages/order_detail_page.dart` (pattern `builder`)

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:order_app/core/widgets/app_button.dart';
import 'package:order_app/features/order/presentation/cubit/order_cubit.dart';

class OrderDetailPage extends StatelessWidget {
  const OrderDetailPage({super.key, required this.id});

  final String id;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Order Detail')),
      body: BlocBuilder<OrderCubit, OrderState>(
        builder: (context, state) {
          if (state is OrderLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state is OrderLoaded) {
            // TODO: render content
            return const Center(child: Text('Implement OrderDetailPage content'));
          }
          if (state is OrderError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(state.message, overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 16),
                  AppButton(
                    label: 'Reintentar',
                    onPressed: () => context.read<OrderCubit>().loadOrder(id),
                    variant: AppButtonVariant.primary,
                  ),
                ],
              ),
            );
          }
          return const Center(child: CircularProgressIndicator());
        },
      ),
    );
  }
}
```

---

## 11. `supabase/migrations/{timestamp}_create_orders.sql`

```sql
-- Create orders table
-- Review and customize before applying

CREATE TABLE orders (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  total float8 NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  items jsonb NOT NULL DEFAULT '[]',
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX orders_user_id_idx ON orders (user_id);
CREATE INDEX orders_created_at_idx ON orders (created_at);

-- Enable Row Level Security
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- RLS Policies (customize per business rules)

-- Allow read access to authenticated users
CREATE POLICY "Users can read orders"
  ON orders
  FOR SELECT
  TO authenticated
  USING (true);

-- Allow insert for authenticated users
CREATE POLICY "Users can insert orders"
  ON orders
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

-- Allow update for own records
CREATE POLICY "Users can update own orders"
  ON orders
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

-- Triggers
-- (add triggers if needed)
```

---

## Wiring: orquestación de DI y rutas

### 12. `lib/core/di/` — anotaciones del feature order (por `di-getit-scaffold`)

En modo `injectable` el registro **no se escribe a mano**: cada clase del feature se anota donde vive y `make gen` produce `service_locator.config.dart`.

**`service_locator.dart` no cambia** — solo declara `sl` + `configureDependencies()` (lo genera el bootstrap):

```dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';
import 'package:order_app/core/di/service_locator.config.dart';

final GetIt sl = GetIt.instance;

@InjectableInit(
  initializerName: 'init',
  preferRelativeImports: false,
)
Future<void> configureDependencies() async {
  await sl.init();
}
```

**Anotaciones de las clases del feature** (los templates de `clean-arch-feature` ya las emiten; aquí están consolidadas):

```dart
// data/datasources/order_remote_datasource.dart
@LazySingleton(as: OrderRemoteDataSource)
class OrderRemoteDataSourceImpl implements OrderRemoteDataSource { ... }

// data/repositories/order_repository_impl.dart
@LazySingleton(as: OrderRepository)
class OrderRepositoryImpl implements OrderRepository { ... }

// domain/usecases/get_orders.dart (get_order, create_order, update_order, delete_order: igual)
@lazySingleton
class GetOrders extends UseCase<List<Order>, NoParams> { ... }

// presentation/cubit/order_cubit.dart
@injectable
class OrderCubit extends Cubit<OrderState> { ... }
```

**`external_module.dart`** (si el proyecto no lo traía del bootstrap, se crea con lo que el feature pide de terceros): `SupabaseClient` vía `Supabase.instance.client`, `Isar` (`@preResolve`), `InternetConnection.createInstance()` y `http.Client()`.

Entity, Model, la interface `OrderRepository` y los `*Params` **no** llevan anotación: son tipos de datos o contratos, no registros.

**Tú haces después:** `make gen` (regenera `service_locator.config.dart`) y verifica que el diff sea solo ese `.config.dart`.

### 13. `lib/core/router/app_router.dart` — rutas añadidas por `go-route-scaffold`

`go-route-scaffold` (básico, sin auth ni Sentry) añade las rutas dentro de la lista `routes`:

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:order_app/features/order/presentation/pages/orders_list_page.dart';
import 'package:order_app/features/order/presentation/pages/order_detail_page.dart';

class AppRouter {
  late final GoRouter router;

  AppRouter() {
    router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/orders',
          builder: (_, __) => const OrdersListPage(),
          routes: [
            GoRoute(
              path: ':id',
              builder: (_, state) => OrderDetailPage(
                id: state.pathParameters['id']!,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
```

---

## Scaffolding vs implementado

Todo lo anterior es estructura con `throw UnimplementedError()`. Así se ven 3 bodies ya implementados (tu trabajo — el "después"):

**Datasource — `getAll()`:**

```dart
@override
Future<List<OrderModel>> getAll() async {
  final response = await _supabase
      .from(_tableName)
      .select()
      .order('created_at', ascending: false);
  return (response as List).map((e) => OrderModel.fromJson(e)).toList();
}
```

**Repository — `getAll()`:**

```dart
@override
Future<Either<Failure, List<Order>>> getAll() async {
  try {
    final models = await remoteDataSource.getAll();
    return Right(models.map((m) => m.toEntity()).toList());
  } on ServerException catch (e) {
    return Left(ServerFailure(e.message));
  } on CacheException catch (e) {
    return Left(CacheFailure(e.message));
  }
}
```

**Cubit — `loadOrders()`:**

```dart
Future<void> loadOrders() async {
  emit(OrderLoading());
  final result = await _getOrders(NoParams());
  result.fold(
    (failure) => emit(OrderError(failure.message)),
    (orders) => emit(OrdersLoaded(orders)),
  );
}
```

---

# Parte III — Output íntegro de las skills de infraestructura

Esta parte muestra el **resultado final completo** que producen `di-getit-scaffold`, `go-route-scaffold`, `clean-arch-component` y `flutter-test-generator`, siguiendo el mismo formato "espejo" de la [Parte II](#parte-ii--output-íntegro-de-clean-arch-feature) (que cubre `clean-arch-feature`).

Escenario base: el feature **Order** con Supabase del [Escenario](#escenario) (app `order_app`).

## Cómo usar la Parte III

- Compara archivo por archivo contra tu resultado real.
- Diferencias aceptables: `order_app` (nombre del paquete), nombres de rutas, imports comentados si la página aún no existe.
- Los templates de cada `SKILL.md` son la fuente de verdad.

---

## A. `di-getit-scaffold` — registro de dependencias

### A.1 Prompts

> Registra el feature order en service_locator (modo `injectable` — default)

> ¿Proyecto brownfield con cascada manual (v1)? Pide el modo `manual` → ver [A.3](#a3-output-modo-manual--legacy--brownfield).

### A.2 Output (modo injectable — default)

Con `injectable` no hay bloque nuevo que añadir a `service_locator.dart`: las clases del feature se anotan donde viven y `make gen` regenera `service_locator.config.dart`.

**`lib/core/di/service_locator.dart`** (estático — igual al del bootstrap):

```dart
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';

import 'package:order_app/core/di/service_locator.config.dart';

final GetIt sl = GetIt.instance;

@InjectableInit(
  initializerName: 'init',
  preferRelativeImports: false,
)
Future<void> configureDependencies() async {
  await sl.init();
}
```

**`lib/core/di/external_module.dart`** (terceros que el feature necesita):

```dart
import 'package:http/http.dart' as http;
import 'package:injectable/injectable.dart';
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart';
import 'package:isar_community/isar.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:order_app/core/data/local/isar_service.dart';

@module
abstract class ExternalModule {
  @preResolve
  Future<Isar> get isar async {
    await IsarService.initialize();
    return IsarService.instance;
  }

  @lazySingleton
  InternetConnection get internetConnection =>
      InternetConnection.createInstance();

  @lazySingleton
  http.Client get httpClient => http.Client();

  @lazySingleton
  SupabaseClient get supabaseClient => Supabase.instance.client;
}
```

**Anotaciones en las clases del feature** (las emiten los templates de `clean-arch-feature` / `clean-arch-component`; aquí están consolidadas):

| Clase | Anotación | Registro que genera |
|---|---|---|
| `OrderRemoteDataSourceImpl` | `@LazySingleton(as: OrderRemoteDataSource)` | lazySingleton de la abstracta |
| `OrderRepositoryImpl` | `@LazySingleton(as: OrderRepository)` | lazySingleton de la abstracta |
| `GetOrders`, `GetOrder`, `CreateOrder`, `UpdateOrder`, `DeleteOrder` | `@lazySingleton` | una instancia para la app |
| `OrderCubit` | `@injectable` | `factory`, una por pantalla |
| Entity, Model, `OrderRepository`, `*Params` | — | **nunca** se anotan |

> El registro real lo escribe `make gen` en `service_locator.config.dart`, que **se commitea** y nunca se edita a mano. Si al regenerar queda un diff, alguien anotó algo sin correr `make gen` (CI lo detecta con `git diff --exit-code`).

### A.3 Output (modo manual — legacy / brownfield)

> ⚠️ **Modo legacy:** solo para proyectos con la cascada manual ya existente (v1) que aún no migran a `injectable`. Para proyectos nuevos usa el modo `injectable` ([A.2](#a2-output-modo-injectable--default)).

**Prompt:** "Registra el feature order en service_locator en modo manual"

`lib/core/di/service_locator.dart` completo:

```dart
import 'package:get_it/get_it.dart';
import 'package:http/http.dart' as http;
import 'package:internet_connection_checker_plus/internet_connection_checker_plus.dart';
import 'package:isar_community/isar.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
// ... imports de datasources, repositories, usecases, cubits
import 'package:order_app/features/order/data/datasources/order_remote_datasource.dart';
import 'package:order_app/features/order/data/repositories/order_repository_impl.dart';
import 'package:order_app/features/order/domain/repositories/order_repository.dart';
import 'package:order_app/features/order/domain/usecases/create_order.dart';
import 'package:order_app/features/order/domain/usecases/delete_order.dart';
import 'package:order_app/features/order/domain/usecases/get_order.dart';
import 'package:order_app/features/order/domain/usecases/get_orders.dart';
import 'package:order_app/features/order/domain/usecases/update_order.dart';
import 'package:order_app/features/order/presentation/cubit/order_cubit.dart';
// import 'package:order_app/core/services/user_session.dart';
// import 'package:order_app/core/network/network_info.dart';

final GetIt sl = GetIt.instance;

Future<void> initDependencies() async {
  await IsarService.initialize();

  // ──────────────────────────────────────────────
  // External libraries
  // ──────────────────────────────────────────────
  sl
    ..registerLazySingleton<Isar>(() => IsarService.instance)
    ..registerLazySingleton<InternetConnection>(InternetConnection.createInstance)
    ..registerLazySingleton<http.Client>(http.Client.new);
  // `SupabaseClient` NO se registra: los datasources reciben
  // `Supabase.instance.client` directo en su constructor.

  // ──────────────────────────────────────────────
  // Core services
  // ──────────────────────────────────────────────
  sl
    ..registerLazySingleton<NetworkInfo>(() => NetworkInfoImpl(sl<InternetConnection>()))
    ..registerLazySingleton<UserSession>(() => UserSessionImpl(sl<Isar>(), supabase: Supabase.instance.client))
    ..registerLazySingleton<CacheManager>(CacheManager.new);

  // ──────────────────────────────────────────────
  // DataSources
  // ──────────────────────────────────────────────
  sl
    ..registerLazySingleton<OrderRemoteDataSource>(
      () => OrderRemoteDataSourceImpl(supabase: Supabase.instance.client),
    );

  // ──────────────────────────────────────────────
  // Repositories
  // ──────────────────────────────────────────────
  sl
    ..registerLazySingleton<OrderRepository>(
      () => OrderRepositoryImpl(
        remoteDataSource: sl<OrderRemoteDataSource>(),
      ),
    );

  // ──────────────────────────────────────────────
  // UseCases
  // ──────────────────────────────────────────────
  sl
    ..registerLazySingleton(() => GetOrders(sl()))
    ..registerLazySingleton(() => GetOrder(sl()))
    ..registerLazySingleton(() => CreateOrder(sl()))
    ..registerLazySingleton(() => UpdateOrder(sl()))
    ..registerLazySingleton(() => DeleteOrder(sl()));

  // ──────────────────────────────────────────────
  // Cubits
  // ──────────────────────────────────────────────
  sl
    ..registerFactory(() => OrderCubit(
          getOrders: sl(),
          getOrder: sl(),
          createOrder: sl(),
          updateOrder: sl(),
          deleteOrder: sl(),
        ));
}
```

> Si `service_locator.dart` ya existía con otros features, `di-getit-scaffold` **añade** los nuevos registros en su sección correspondiente, respetando el orden de capas. `SupabaseClient` no se registra (los datasources reciben `Supabase.instance.client` directo) y los imports de `core/` van comentados hasta que existan esos servicios.

---

## B. `go-route-scaffold` — configuración de rutas

### B.1 Básico (sin auth, sin Sentry)

Ver [Parte II — sección 13](#13-libcorerouterapp_routerdart--rutas-añadidas-por-go-route-scaffold) — el output completo ya está mostrado ahí, no se duplica.

### B.2 Con auth redirect

**Prompt:**

> Añade rutas al router con auth redirect. Estado autenticado: AuthAuthenticated. Rutas: `/login` → LoginPage, `/` → HomePage, `/orders` → OrdersListPage, `/orders/:id` → OrderDetailPage

Output — `lib/core/router/app_router.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
// TODO: import pages de auth y home (no generadas en este escenario)
// import 'package:order_app/features/auth/presentation/cubit/auth_cubit.dart';
// import 'package:order_app/features/auth/presentation/pages/login_page.dart';
// import 'package:order_app/features/home/presentation/pages/home_page.dart';
import 'package:order_app/features/order/presentation/pages/orders_list_page.dart';
import 'package:order_app/features/order/presentation/pages/order_detail_page.dart';

class AppRouter {
  late final GoRouter router;

  AppRouter() {
    router = GoRouter(
      initialLocation: '/login',
      redirect: (context, state) {
        final auth = context.read<AuthCubit>().state;
        final estaAutenticado = auth is AuthAuthenticated;
        final estaEnLogin = state.matchedLocation == '/login';

        // TODO: implement auth redirect
        // if (!estaAutenticado && !estaEnLogin) return '/login';
        // if (estaAutenticado && estaEnLogin) return '/';
        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (_, __) {
            // TODO: replace with LoginPage
            throw UnimplementedError('LoginPage not implemented');
          },
        ),
        GoRoute(
          path: '/',
          builder: (_, __) {
            // TODO: replace with HomePage
            throw UnimplementedError('HomePage not implemented');
          },
        ),
        GoRoute(
          path: '/orders',
          builder: (_, __) => const OrdersListPage(),
          routes: [
            GoRoute(
              path: ':id',
              builder: (_, state) => OrderDetailPage(
                id: state.pathParameters['id']!,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
```

> Las páginas de auth/home existen en tu proyecto real: se descomentan los imports y se reemplaza el `throw UnimplementedError` por `const LoginPage()` / `const HomePage()`.

### B.3 Con Sentry

**Prompt:** "Añade rutas al router con Sentry. Rutas: `/orders` y `/orders/:id`"

Output — `lib/core/router/app_router.dart`:

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'package:order_app/features/order/presentation/pages/orders_list_page.dart';
import 'package:order_app/features/order/presentation/pages/order_detail_page.dart';

class AppRouter {
  late final GoRouter router;

  AppRouter() {
    router = GoRouter(
      initialLocation: '/',
      routes: [
        GoRoute(
          path: '/orders',
          builder: (_, __) => const OrdersListPage(),
          routes: [
            GoRoute(
              path: ':id',
              builder: (_, state) => OrderDetailPage(
                id: state.pathParameters['id']!,
              ),
            ),
          ],
        ),
      ],
      observers: [
        SentryNavigatorObserver(),
      ],
    );
  }
}
```

Configuración adicional en `main.dart`:

```dart
await SentryFlutter.init(
  (options) {
    options.dsn = 'your-dsn';
    options.tracesSampleRate = 1.0;
  },
  appRunner: () => runApp(const MyApp()),
);
```

### B.4 Combinado (auth + Sentry)

`go-route-scaffold` soporta `has_auth: true` y `use_sentry: true` a la vez: el resultado es el template **B.2** con la lista `observers: [SentryNavigatorObserver()]` añadida al final de `GoRouter(...)`.

---

## C. `clean-arch-component` — piezas individuales (compacto)

Sus templates son los **mismos archivos** que `clean-arch-feature` genera (fuente única). Por eso aquí solo se mapea qué genera cada tipo y **dónde ver su ejemplo completo**:

| `component_type` | Archivo generado | Ejemplo completo en |
|---|---|---|
| `entity` | `domain/entities/{feature}.dart` | [Parte II — sección 1](#1-domainentitiesorderdart), Parte I Mini-B |
| `model` | `data/models/{feature}_model.dart` | [Parte II — sección 4](#4-datamodelsorder_modeldart-mapeo-snake_case-por-supabase), Parte I Mini-B |
| `usecase` | `domain/usecases/{action}_{feature}.dart` | Parte I Paso 5 (`cancel_order`) |
| `cubit` | `presentation/cubit/{feature}_cubit.dart` | [Parte II — sección 7](#7-presentationcubitorder_cubitdart) |
| `datasource` | `data/datasources/{feature}_remote_datasource.dart` | [Parte II — sección 5](#5-datadatasourcesorder_remote_datasourcedart-con-_tablename--watchbyid) |
| `repository` | `domain/repositories/{feature}_repository.dart` | [Parte II — sección 2](#2-domainrepositoriesorder_repositorydart) |
| `repository_impl` | `data/repositories/{feature}_repository_impl.dart` | [Parte II — sección 6](#6-datarepositoriesorder_repository_impldart) |
| `page` | `presentation/pages/{feature}_{page}_page.dart` | Parte I Paso 4 (pattern `form`) |

**Prompt típico → resultado:**

> "Añade un usecase cancel_order al feature order"

→ 1 archivo: `lib/features/order/domain/usecases/cancel_order.dart` (con `CancelOrder` + `CancelOrderParams extends Equatable`, body `throw UnimplementedError`). Ver output completo en [Parte I Paso 5](#paso-5-añadir-usecase-extra).

---

## D. `flutter-test-generator` — tests boilerplate (compacto)

### D.1 Uso

```bash
python3 skills/flutter-test-generator/generate_test.py lib/features/order/data/models/order_model.dart
```

Genera `test/features/order/data/models/order_model_test.dart` (mismo path bajo `test/`).

### D.2 Capas detectadas

| Path en `lib/` | Test generado |
|---|---|
| `domain/entities/` | Equatable, copyWith, props |
| `domain/usecases/` | Mock repository + `Either<Failure, T>` |
| `data/models/` | fromJson, toJson, roundtrip, conversión entidad |
| `data/datasources/` | Mock client + `ServerException` |
| `data/repositories/` | Mock datasources + network (online/offline) |
| `presentation/cubit/` (no state) | `blocTest` + mock usecases |
| `presentation/cubit/` (state) | Igualdad y props de cada estado |
| `presentation/pages/` o `widgets/` | `testWidgets` + mock `BlocProvider` |

### D.3 Output de ejemplo — test de **model** (capa aún no mostrada)

**Prompt:** "Genera tests para order_model"

Output — `test/features/order/data/models/order_model_test.dart`:

```dart
import 'package:flutter_test/flutter_test.dart';
import 'dart:convert';
import 'dart:io';
import 'package:order_app/features/order/data/models/order_model.dart';
import '../../../helpers/fixture_reader.dart';

void main() {
  group('OrderModel', () {
    group('fromJson', () {
      test('debería retornar un modelo válido desde JSON', () {
        // ARRANGE: cargar fixture con fixtureAsMap('order')
        // ACT: llamar OrderModel.fromJson(jsonMap)
        // ASSERT: verificar cada campo del modelo resultante
      });

      test('debería lanzar error cuando falta un campo requerido', () {
        // ARRANGE: crear JSON parcial sin campos required
        // ACT & ASSERT: expect(() => OrderModel.fromJson(incomplete), throwsA(isA<TypeError>()))
      });

      test('debería ignorar campos extra en el JSON', () {
        // ARRANGE: crear JSON con campos adicionales
        // ACT: llamar OrderModel.fromJson(jsonMap)
        // ASSERT: verificar que se crea el modelo correctamente
      });
    });

    group('toJson', () {
      test('debería retornar un mapa JSON válido', () {
        // ARRANGE: crear instancia del modelo
        // ACT: llamar model.toJson()
        // ASSERT: verificar keys y valores (incluyendo snake_case si aplica)
      });
    });

    group('roundtrip', () {
      test('toJson + fromJson debería ser inverso', () {
        // ARRANGE: crear instancia del modelo
        // ACT: json = model.toJson(); recreated = Model.fromJson(json)
        // ASSERT: expect(recreated, equals(original))
      });
    });

    group('entity conversion', () {
      test('toEntity debería retornar Entity correcta', () {
        // ARRANGE: crear instancia del modelo
        // ACT: llamar model.toEntity()
        // ASSERT: verificar que retorna isA<Entity>() con campos mapeados
      });

      test('fromEntity debería crear Model desde Entity', () {
        // ARRANGE: crear instancia de Entity
        // ACT: llamar Model.fromEntity(entity)
        // ASSERT: verificar que retorna isA<Model>() con campos copiados
      });
    });
  });
}
```

> Los bodies van vacíos con comentarios AAA en español — el desarrollador completa la lógica. El cubit test se muestra en [Parte I Paso 6](#paso-6-generar-tests).

---

## Cierre / Siguiente paso

- Revisar y ejecutar la migración en Supabase (`supabase db push` o el SQL editor).
- Ajustar las RLS policies si tu regla de negocio no es `auth.uid() = user_id`.
- Completar los bodies de cada archivo.
- Completar los tests con datos reales y ejecutar `flutter test`.
