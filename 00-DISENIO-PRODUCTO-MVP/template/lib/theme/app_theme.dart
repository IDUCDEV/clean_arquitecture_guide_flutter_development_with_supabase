import 'package:flutter/material.dart';

import 'app_colors.dart';
import 'app_extensions.dart';
import 'app_typography.dart';

/// Tema central del MVP. M3 es el default desde Flutter 3.16,
/// así que basta definir el ColorScheme con [ColorScheme.fromSeed].
abstract final class AppTheme {
  static ThemeData get light => _build(Brightness.light);

  static ThemeData get dark => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final scheme = switch (brightness) {
      Brightness.light => AppColors.light,
      Brightness.dark => AppColors.dark,
    };
    return ThemeData(
      brightness: brightness,
      colorScheme: scheme,
      textTheme: AppTypography.build(scheme),
      extensions: [AppSpacing.standard, AppRadii.standard],
    );
  }
}
