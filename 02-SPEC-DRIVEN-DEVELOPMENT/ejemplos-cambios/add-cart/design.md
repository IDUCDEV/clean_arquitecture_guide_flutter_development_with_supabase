# Design: add-cart

## Context
Feature nueva siguiendo el patrón estándar del curso (Clean Architecture + Cubit + fpdart). Catálogo `products` ya existe con columna `stock`. El cálculo económico vive en la entity (puro, testeable); la validación de stock se delega a RPC para evitar carreras.

## Goals / Non-Goals
- Goals: carrito íntegro por cliente; reglas económicas centralizadas en domain; cupones con límite de uso
- Non-Goals: pagos, envíos, fidelización, realtime (el resumen se refresca al entrar)

## Decisions
### D1: Cálculos económicos en la entity (cliente)
- Decisión: subtotal/impuesto/total como métodos puros de `Cart`
- Alternativas: RPC `calculate_cart_totals` en cada lectura
- Por qué: testable sin red, cero latencia extra; los montos se revalidan al crear la orden (fuera de alcance)

### D2: Cupones NO combinables
- Decisión: un solo cupón activo por carrito
- Por qué: simplifica RN006 (tope 50%) y el modelo de datos; extensible después vía MODIFIED

### D3: Stock validado por RPC atómico
- Decisión: `rpc.add_cart_item(p_product_id, p_qty)` valida stock y descuenta dentro de una transacción security definer
- Alternativas: SELECT+UPDATE desde el datasource
- Por qué: evita oversell por concurrencia (riesgo detectado en Impact Report)

### D4: Precio congelado en cart_items
- Decisión: columna `unit_price` copiada al insertar
- Por qué: REQ-001 (RN007); el precio de catálogo puede cambiar después

## Ficheros afectados
| Elemento | Capa | Archivo | Req |
|----------|------|---------|-----|
| Cart, CartItem, Coupon | domain/entity | lib/features/cart/domain/entities/{cart,cart_item,coupon}.dart | REQ-003 |
| CartRepository | domain/repository | lib/features/cart/domain/repositories/cart_repository.dart | REQ-001..005 |
| CartModel, CouponModel | data/model | lib/features/cart/data/models/ | REQ-001..004 |
| CartRemoteDataSource | data/datasource | lib/features/cart/data/datasources/cart_remote_data_source.dart | REQ-001..005 |
| CartRepositoryImpl | data/repositories | lib/features/cart/data/repositories/cart_repository_impl.dart | REQ-001..005 |
| AddItemToCart, RemoveItem, GetCart, ApplyCoupon | domain/usecase | lib/features/cart/domain/usecases/ | REQ-001..004 |
| CartCubit / CartState | presentation/cubit | lib/features/cart/presentation/cubit/ | REQ-006 |
| CartPage + widgets | presentation/pages | lib/features/cart/presentation/pages/cart_page.dart | REQ-006 |
| Registro DI | core/di | lib/core/di/service_locator.dart | — |
| Ruta /cart | core/router | lib/core/router/app_router.dart | — |
| Migración 0007 | supabase/migrations | supabase/migrations/0007_carts_rls.sql | REQ-005 |

## Contratos Dart clave
```dart
abstract interface class CartRepository {
  Future<Either<Failure, Cart>> getCart();
  Future<Either<Failure, Unit>> addItem({required String productId});
  Future<Either<Failure, Unit>> removeItem({required String productId});
  Future<Either<Failure, Unit>> updateQuantity({required String productId, required int quantity});
  Future<Either<Failure, Cart>> applyCoupon({required String code});
}

sealed class CartState {}
class CartInitial extends CartState {}
class CartLoading extends CartState {}
class CartLoaded extends CartState { final Cart cart; const CartLoaded(this.cart); }
class CartError extends CartState { final String message; const CartError(this.message); }
```

## UI-UX · Pantallas (archivo .pen)

Wireframes con Pencil (módulo 08) en `openspec/changes/add-cart/design/add-cart-ui.pen` — archivo esperado, no incluido en el ejemplo. Los mensajes exactos viven en los escenarios de `spec.md`.

| Pantalla (.pen) | Escenario REQ | Estados visibles | Notas (interacciones) |
|-----------------|---------------|------------------|------------------------|
| CartPage (vacía) | REQ-003 | EmptyState sin totales | texto del estado vacío sin totales calculados |
| CartPage (con items) | REQ-001..003 | lista de items + subtotal/impuesto/total | recalcular tras add/remove/updateQuantity; descuento visible si hay cupón |
| CartPage (error) | REQ-001, REQ-004 | SnackBar: "Producto {nombre} sin stock disponible" · "Has alcanzado el límite de 50 productos" · "La cantidad debe ser mayor a 0" · "El cupón {codigo} ha expirado" · "El descuento supera el límite permitido" | mensajes exactos de los escenarios EARS |

## Flujo de datos
```
CartPage ──onTap──► CartCubit.addItem(productId)
                        │ emit CartLoading
                        ▼
                 AddItemToCart(repository)
                        ▼
                 CartRepositoryImpl ──► CartRemoteDataSource.addItem(...)
                        │ supabase.rpc('add_cart_item', params:{...})
                        ▼
                 Supabase: transacción (valida stock → inserta item)
                        ▼
        ◄── Either.right(cart) ──► CartLoaded(cart recalculado)
        │
        └── Either.left(Failure) ──► CartError(mensaje exacto del escenario)
```

## Backend Supabase
- Tablas:
  - `carts(id uuid pk, user_id uuid unique→auth.users, coupon_code fk nullable)`
  - `cart_items(id pk, cart_id fk, product_id fk, quantity int check >0, unit_price numeric, created_at)`
  - `coupons(code pk, type enum('percent','fixed'), value numeric, expires_at, max_uses, used_count)`
- RPC: `add_cart_item` security definer (valida stock + RN001 + RN003 atómicamente)
- RLS: enable en las 3 tablas; `USING (auth.uid() = user_id)` para carts y cart_items (via join); admin lectura con claim role
- Migración: `0007_carts_rls.sql`, idempotente (`create policy if not exists`)

## Boundaries aplicables a este cambio
- No tocar features existentes ni sus contratos
- No añadir paquetes a pubspec (todo existe)
- No desactivar RLS bajo ninguna circunstancia
