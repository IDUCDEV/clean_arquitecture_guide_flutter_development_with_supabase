# 08 — Template de proyecto

**Starter Flutter con M3 + Clean Architecture para tu MVP**

---

El directorio `template/` contiene un proyecto Flutter listo para usar como base de tu MVP. Incluye:

- M3 theming completo (light + dark + dynamic color)
- Clean Architecture (data/domain/presentation)
- Componentes M3 reutilizables
- Estructura preparada para escalar

## Estructura

```
template/
├── lib/
│   ├── main.dart                    # Entry point
│   ├── app.dart                     # MaterialApp con M3
│   ├── theme/
│   │   ├── app_theme.dart           # ThemeData light + dark
│   │   ├── app_colors.dart          # ColorScheme.fromSeed
│   │   ├── app_typography.dart      # TextTheme M3
│   │   └── app_extensions.dart      # Spacing, Radii tokens
│   ├── features/
│   │   └── mvp/                     # Feature de ejemplo
│   │       ├── data/
│   │       │   ├── datasources/     # Fuentes de datos (API, local)
│   │       │   └── repositories/    # Implementación de repositorios
│   │       ├── domain/
│   │       │   ├── entities/        # Modelos de dominio
│   │       │   ├── repositories/    # Contratos (abstract)
│   │       │   └── usecases/        # Casos de uso
│   │       └── presentation/
│   │           ├── pages/           # Pantallas
│   │           └── widgets/         # Widgets reutilizables
│   └── core/
│       └── components/              # Componentes M3 compartidos
├── test/
│   └── ...                          # Tests unitarios + de widgets
└── pubspec.yaml
```

## Cómo usar el template

### Opción 1: Copiar sobre un proyecto existente

```bash
# Después de flutter create
cp -r template/lib/theme/ tu-proyecto/lib/theme/
cp -r template/lib/core/ tu-proyecto/lib/core/
# Adapta main.dart y app.dart
```

### Opción 2: Usar como base

```bash
cp -r template/ mi-mvp/
cd mi-mvp
# Edita pubspec.yaml con tu nombre, dependencias, etc.
flutter pub get
```

### Opción 3: Referencia de estudio

Lee cada archivo del template como ejemplo de implementación M3 + Clean Architecture.

## Personalización rápida

1. **Cambia el seed color** en `app_colors.dart`:

```dart
static ColorScheme light() => ColorScheme.fromSeed(
  seedColor: Color(0xFFTU_COLOR), // ← tu color de marca
);
```

2. **Agrega tu font** en `app_typography.dart` y `pubspec.yaml`:

```dart
// app_typography.dart
TextTheme(
  titleLarge: GoogleFonts.interTextTheme().titleLarge,
  bodyMedium: GoogleFonts.interTextTheme().bodyMedium,
)
```

3. **Agrega tus pantallas** en `features/mvp/presentation/pages/`:

```dart
class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Mi MVP')),
      body: Center(child: Text('¡A construir!')),
    );
  }
}
```

## Dependencias incluidas

En `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  google_fonts: ^8.2.1  # tipografía M3 fácil

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^6.0.0
```

## Integración con otros módulos

| Necesidad | Módulo relacionado |
|---|---|
| State management (BLoC/Cubit) | `16-BLOC-CUBIT` |
| Backend con Supabase | `03-SUPABASE` |
| Almacenamiento local | `04-ALMACENAMIENTO-LOCAL` |
| Testing | `05-TESTING` |
| Widgets avanzados | `15-WIDGETS-FLUTTER` |

---

**Siguiente: [09 — Caso completo MVP](09-caso-completo-mvp.md)**
