import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Escala tipográfica M3. Usa los nombres semánticos (titleLarge, bodyMedium…)
/// siempre, y personaliza la fuente de marca aquí.
abstract final class AppTypography {
  static TextTheme build(ColorScheme colorScheme) {
    final base = GoogleFonts.interTextTheme();
    return base
        .apply(
          bodyColor: colorScheme.onSurface,
          displayColor: colorScheme.onSurface,
        )
        .copyWith(
          titleLarge: base.titleLarge?.copyWith(
            fontSize: 22,
            fontWeight: FontWeight.w500,
          ),
        );
  }
}
