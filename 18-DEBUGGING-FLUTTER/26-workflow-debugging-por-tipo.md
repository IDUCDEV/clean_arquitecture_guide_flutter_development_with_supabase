# 26 — Workflow de Debugging por Tipo de Bug

> Diferentes tipos de bugs requieren diferentes estrategias. Este archivo te da el workflow exacto para cada tipo: UI, estado, performance, red, memoria, compilación y hot reload.

---

## 1. Framework general de debugging

```
1. REPRODUCIR    → ¿Cómo hago que pase otra vez?
2. AISLAR        → ¿Dónde exactamente falla?
3. DIAGNOSTICAR  → ¿Por qué falla?
4. CORREGIR      → ¿Cómo lo arreglo sin romper algo?
5. VERIFICAR     → ¿Sigue funcionando todo?
```

---

## 2. Tipo 1: UI Bug (algo se ve mal)

**Flujo:**

```
1. Widget Inspector (DevTools)
2. Select Widget Mode (VSCode: Ctrl+Shift+P / Cmd+Shift+P → Flutter: Select Widget)
3. Inspeccionar propiedades
4. Verificar constraints (SizedBox, Expanded, Flexible)
5. Revisar MediaQuery si es responsive
```

**Herramienta:** DevTools → Flutter Inspector → Select Widget

**Desde código (sin DevTools):**
```dart
// Ver bounds y constraints de cada widget
debugPaintSizeEnabled = true;

// Ver árbol de widgets completo
debugDumpWidgetTree();

// Ver qué se repinta
debugProfilePaintsEnabled = true;
```
> Ver [28-debugging-programatico-flutter.md](./28-debugging-programatico-flutter.md) para todas las herramientas programáticas.

**Ejemplo:**

```dart
// ❌ Widget se desborda
Container(
  width: double.infinity,
  height: 300,
  child: Text('Muy largo texto que no cabe y se desborda del contenedor'),
)

// ✅ Con overflow controlado
Container(
  width: double.infinity,
  child: Text(
    'Texto largo',
    maxLines: 2,
    overflow: TextOverflow.ellipsis,
  ),
)
```

---

## 3. Tipo 2: State Bug (estado inconsistente)

**Flujo:**

```
1. Agregar prints en cada cambio de estado
2. Verificar si mounted antes de setState
3. Revisar si hay múltiples setState en secuencia
4. Usar DevTools → extensión Bloc Inspector (si usa BLoC)
5. Verificar inicialización del state
```

**Herramienta:** Print debugging + Bloc Inspector

**Ejemplo:**

```dart
// ❌ Estado se resetea
class MyCubit extends Cubit<MyState> {
  MyCubit() : super(MyInitial());

  void load() async {
    emit(Loading()); // Emit loading
    final data = await fetch();
    // Si fetch lanza error, nunca llega aquí
    emit(Loaded(data));
  }
}

// ✅ Manejo correcto
void load() async {
  emit(Loading());
  try {
    final data = await fetch();
    emit(Loaded(data));
  } catch (e) {
    emit(Error(e.toString()));
  }
}
```

---

## 4. Tipo 3: Performance Bug (app lenta)

**Flujo:**

```
1. DevTools → Performance Overlay (Enable)
2. DevTools → Performance → Record
3. Buscar "jank" (frames > 16ms)
4. Identificar widget que causa rebuilds
5. Aplicar const, RepaintBoundary, o lazy loading
```

**Herramienta:** DevTools → Performance

**Checklist:**

```
□ ¿Usas const en widgets que no cambian?
□ ¿ListView.builder en vez de ListView?
□ ¿Imágenes con BoxFit adecuado y cacheWidth/cacheHeight?
□ ¿Evitas rebuilds innecesarios?
□ ¿Usas RepaintBoundary en animations?
```

---

## 5. Tipo 4: Network Bug (API falla)

**Flujo:**

```
1. DevTools → Network → Ver request/response
2. Copiar como cURL para probar externamente
3. Verificar headers (Authorization, Content-Type)
4. Verificar status code (200, 400, 401, 403, 500)
5. Verificar body del request
```

**Herramienta:** DevTools → Network

**Debugging de Supabase:**

```dart
// Agregar logging
final supabase = SupabaseClient(url, key);

// Ver queries en consola
final data = await supabase
    .from('users')
    .select()
    .order('created_at', ascending: false);

// Imprimir query result
print('Query result: $data');
print('Rows: ${data.length}');
```

---

## 6. Tipo 5: Memory Leak

**Flujo:**

```
1. DevTools → Memory → Take Heap Snapshot
2. Hacer acción que debería liberar memoria
3. Take another snapshot
4. Comparar snapshots
5. Si objetos crecen → buscar suscripciones no canceladas
```

**Herramienta:** DevTools → Memory

**Comunes:**

```dart
// ❌ Suscripción no cancelada
void initState() {
  _stream.listen((_) {}); // Nunca se cancela
}

// ❌ Controller no disposed
final _controller = StreamController(); // Nunca se cierra

// ❌ Timer no cancelado
Timer.periodic(Duration(seconds: 1), (_) {}); // Nunca se cancela
```

---

## 7. Tipo 6: Build Error (compilación)

**Flujo:**

```
1. Leer el error completo (no solo la primera línea)
2. Buscar "error:" en el output
3. Identificar archivo y línea
4. Verificar tipos de datos
5. Verificar imports
6. Verificar null safety
```

**Errores comunes en Flutter:**

```
// "RenderFlex overflowed" → Widget se desborda
// "Incorrect use of ParentDataWidget" → Expanded/Flexible sin ListView/Row/Column
// "A RenderFlex overflowed" → Text muy largo sin wrap
```

---

## 8. Tipo 7: Hot Reload no funciona

**Flujo:**

```
1. Verificar si el cambio es "hot reloadable"
2. Cambios en initState NO se recargan con hot reload
3. Cambios en main() NO se recargan
4. Cambios en imports NO se recargan
5. Usar Hot Restart (no Hot Reload)
```

**No recarga con Hot Reload:**

- `initState()`
- `main()`
- `const` values
- Imports
- Static fields

---

## 9. Cheat Sheet: ¿Qué herramienta para qué?

| Bug | Herramienta | Atajo |
|---|---|---|
| UI se ve mal | Widget Inspector | DevTools → Flutter Inspector |
| Estado inconsistente | Bloc Inspector / Prints | — |
| App lenta | Performance View | DevTools → Performance |
| API falla | Network View | DevTools → Network |
| Memory leak | Memory View | DevTools → Memory |
| Build error | Terminal output | Leer error completo |
| Hot Reload no funciona | Hot Restart | R (consola) / Shift+F5 (VS Code) |

---

## Resumen

| Tipo de bug | Primer paso | Herramienta principal |
|---|---|---|
| **UI** | Select Widget Mode | Flutter Inspector |
| **Estado** | Prints en cada cambio | Bloc Inspector |
| **Performance** | Performance Overlay | Performance View |
| **Network** | Ver request en Network | Network View |
| **Memoria** | Heap snapshot base | Memory View |
| **Compilación** | Leer el error completo | Terminal |
| **Hot Reload** | Cambiar a Hot Restart | Consola / VS Code |

Este workflow cierra la guía: combina todo lo aprendido en los capítulos anteriores — DevTools, rendering, rendimiento, debugging de UI y código asíncrono — para diagnosticar y resolver cualquier problema que aparezca en tu app Flutter.

> Para un enfoque paso-a-paso más sistemático, ver [29-playbook-debugging-sistematico.md](./29-playbook-debugging-sistematico.md).

---

## 📚 Referencias

- [Flutter | Debugging tools](https://docs.flutter.dev/tools) — Panorama de herramientas de debugging
- [Flutter | DevTools](https://docs.flutter.dev/tools/devtools) — Documentación de DevTools
- [Flutter | Hot reload](https://docs.flutter.dev/tools/hot-reload) — Qué se recarga y qué no

---

> 📖 **Volver al índice:** [README.md](./README.md)
