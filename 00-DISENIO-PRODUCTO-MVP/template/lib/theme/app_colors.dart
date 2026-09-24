import 'package:flutter/material.dart';

/// Paletas M3 generadas desde un color semilla. Cambia [seed] por el color
/// de marca de tu MVP y el resto de tonos se genera automáticamente.
abstract final class AppColors {
  static const Color seed = Color(0xFF6750A4);

  static ColorScheme get light => ColorScheme.fromSeed(seedColor: seed);

  static ColorScheme get dark =>
      ColorScheme.fromSeed(seedColor: seed, brightness: Brightness.dark);
}
