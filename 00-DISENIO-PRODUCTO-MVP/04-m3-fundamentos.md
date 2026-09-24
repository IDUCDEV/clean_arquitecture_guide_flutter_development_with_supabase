# 04 — Fundamentos de Material Design 3

**El sistema de diseño oficial de Google para apps móviles**

---

Material Design 3 (M3) es el sistema de diseño de Google, también conocido como **Material You**. Es la evolución de Material Design y **el que Flutter usa por defecto desde la versión 3.16** (antes de esa versión era opcional activarlo).

M3 se basa en 3 subsistemas principales:

```
M3 Theme
├── ColorScheme (color)
├── TextTheme (tipografía)
└── ShapeScheme (formas)
```

## 1. Color: esquemas tonales

M3 introduce el concepto de **paletas tonales**. En lugar de elegir colores individuales, eliges un **color semilla (seed)** y M3 genera una paleta completa de 12 tonos.

### Cómo funciona

```
seed: #6750A4 (púrpura)
  → genera 13 tonos (0, 5, 10, 20, 30, ..., 95, 100)
  → asigna roles: primary, secondary, tertiary, surface, error
```

| Rol | Uso | Ejemplo Flutter |
|---|---|---|
| `primary` | Botones principales, FAB, switches activos | `colorScheme.primary` |
| `onPrimary` | Texto/icono sobre primary | `colorScheme.onPrimary` |
| `secondary` | Botones secundarios, chips | `colorScheme.secondary` |
| `surface` | Fondos de pantalla, cards | `colorScheme.surface` |
| `surfaceContainer` | Cards, bottomsheets (nuevo en M3) | `colorScheme.surfaceContainer` |
| `tertiary` | Acentos alternativos | `colorScheme.tertiary` |
| `error` | Estados de error | `colorScheme.error` |

### Dynamic Color (Material You)

En Android 12+, el sistema puede generar el ColorScheme **desde el wallpaper del usuario**. Tu app se adapta automáticamente a los gustos del usuario.

```
En Android 12+  →  ColorScheme.fromSeed(source: userWallpaperColor)
En otros        →  ColorScheme.fromSeed(seedColor: brandColor)
```

### Contraste

M3 garantiza contraste mínimo:
- Texto normal: 4.5:1
- Texto grande: 3:1
- Iconos: 3:1

## 2. Tipografía: type scale

M3 define una **escala tipográfica** con 11 estilos. No son estilos aislados, sino un **sistema** que escala armónicamente.

| Style | Tamaño | Peso | Uso típico |
|---|---|---|---|
| `displayLarge` | 57 | Regular | Hero text |
| `displayMedium` | 45 | Regular | Pantallas de bienvenida |
| `displaySmall` | 36 | Regular | Encabezados grandes |
| `headlineLarge` | 32 | Regular | Títulos de sección |
| `headlineMedium` | 28 | Regular | Títulos de pantalla |
| `headlineSmall` | 24 | Regular | Subtítulos |
| `titleLarge` | 22 | Medium | App bar titles |
| `titleMedium` | 16 | Medium | Navigation, cards |
| `titleSmall` | 14 | Medium | Botones, tabs |
| `bodyLarge` | 16 | Regular | Cuerpo de texto |
| `bodyMedium` | 14 | Regular | Texto secundario |
| `bodySmall` | 12 | Regular | Captions, tags |
| `labelLarge` | 14 | Medium | Botones, chips |
| `labelMedium` | 12 | Medium | Texto en componentes |
| `labelSmall` | 11 | Medium | Textos pequeños |

### Regla de oro tipográfica M3

> Usa los **nombres semánticos**, no tamaños fijos.
>
> ✅ `Theme.of(context).textTheme.titleLarge`
>
> ❌ `TextStyle(fontSize: 22, fontWeight: FontWeight.w500)`

## 3. Forma (Shape)

M3 define formas por **categoría de componente**, no globalmente.

| Categoría | Esquinas típicas | Componentes |
|---|---|---|
| `small` | 8px | Botones, chips, text fields |
| `medium` | 12px | Cards, dialogos |
| `large` | 16px | Bottom sheets, navigation drawers |
| `extraLarge` | 20px | FAB grandes |

En Flutter, las formas se definen mediante `ShapeBorder`:

```dart
Card(
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.circular(12), // medium
  ),
)
```

## 4. Elevación

M3 cambió la forma de pensar la elevación. Ahora se usa **color en lugar de sombras** para indicar profundidad:

```
surfaceContainerLow    → nivel 1 (cerca del fondo)
surfaceContainer       → nivel 2
surfaceContainerHigh   → nivel 3 (cards levantadas)
surfaceContainerHighest→ nivel 4 (modales, dialogs)
```

Los contenedores de superficie (surface containers) permiten diferenciar capas sin añadir sombras artificiales.

## 5. Motion

M3 prioriza motion sutil y con propósito:

| Principio | Descripción |
|---|---|
| **Responsive** | La UI reacciona al toque inmediatamente (ripple) |
| **Expresivo** | Las transiciones cuentan una historia (shared element transitions) |
| **Familiar** | Usa curvas estándar (emphasized, standard) |

En Flutter, el ripple de M3 viene por defecto en todos los botones y componentes interactivos.

---

## Resumen: M3 en una página

```
M3 Theme
├── ColorScheme.fromSeed(seedColor: brandColor)
│   ├── light scheme
│   └── dark scheme
├── TextTheme (15 estilos, usa nombres semánticos)
└── Shape scheme (small=8, medium=12, large=16)
```

Lo más importante que debes recordar:

1. **Elige un seed color** y deja que M3 genere el resto
2. **Usa colorScheme.* siempre**, nunca colores hardcodeados
3. **Usa textTheme.* siempre**, nunca tamaños fijos
4. **Prefiere surfaceContainer** sobre sombras para profundidad
5. **Soporta dark mode** desde el día 1 (M3 lo hace fácil)

---

**Siguiente: [05 — Componentes M3 para Mobile](05-m3-componentes-mobile.md)**
