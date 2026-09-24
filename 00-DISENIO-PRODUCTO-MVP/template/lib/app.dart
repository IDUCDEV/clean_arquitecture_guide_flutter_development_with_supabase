import 'package:flutter/material.dart';

import 'features/mvp/presentation/pages/home_page.dart';
import 'theme/app_theme.dart';

/// MaterialApp con theme M3 (light + dark). M3 es el default desde Flutter
/// 3.16: solo definimos colorScheme/textTheme, sin useMaterial3.
class MvpApp extends StatelessWidget {
  const MvpApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mi MVP',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: ThemeMode.system,
      home: const HomePage(),
    );
  }
}
