import 'dart:ui' show lerpDouble;

import 'package:flutter/material.dart';

/// Tokens de espaciado que M3 no cubre. Acceso vía
/// `Theme.of(context).extension<AppSpacing>()!.md`.
class AppSpacing extends ThemeExtension<AppSpacing> {
  final double xs;
  final double sm;
  final double md;
  final double lg;
  final double xl;

  const AppSpacing({
    required this.xs,
    required this.sm,
    required this.md,
    required this.lg,
    required this.xl,
  });

  static const AppSpacing standard = AppSpacing(
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  );

  @override
  AppSpacing copyWith({
    double? xs,
    double? sm,
    double? md,
    double? lg,
    double? xl,
  }) {
    return AppSpacing(
      xs: xs ?? this.xs,
      sm: sm ?? this.sm,
      md: md ?? this.md,
      lg: lg ?? this.lg,
      xl: xl ?? this.xl,
    );
  }

  @override
  AppSpacing lerp(AppSpacing? other, double t) {
    if (other == null) return this;
    return AppSpacing(
      xs: lerpDouble(xs, other.xs, t)!,
      sm: lerpDouble(sm, other.sm, t)!,
      md: lerpDouble(md, other.md, t)!,
      lg: lerpDouble(lg, other.lg, t)!,
      xl: lerpDouble(xl, other.xl, t)!,
    );
  }
}

/// Tokens de radio de esquina según las categorías M3 (small/medium/large).
class AppRadii extends ThemeExtension<AppRadii> {
  final double small;
  final double medium;
  final double large;

  const AppRadii({
    required this.small,
    required this.medium,
    required this.large,
  });

  static const AppRadii standard = AppRadii(small: 8, medium: 12, large: 16);

  @override
  AppRadii copyWith({double? small, double? medium, double? large}) {
    return AppRadii(
      small: small ?? this.small,
      medium: medium ?? this.medium,
      large: large ?? this.large,
    );
  }

  @override
  AppRadii lerp(AppRadii? other, double t) {
    if (other == null) return this;
    return AppRadii(
      small: lerpDouble(small, other.small, t)!,
      medium: lerpDouble(medium, other.medium, t)!,
      large: lerpDouble(large, other.large, t)!,
    );
  }
}
