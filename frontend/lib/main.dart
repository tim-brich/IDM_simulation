import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/theme.dart';
import 'core/routing/router.dart';

void main() {
  runApp(const ProviderScope(child: BashkiriaApp()));
}

class BashkiriaApp extends StatelessWidget {
  const BashkiriaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Bashkiria Discovery',
      theme: AppTheme.darkTheme,
      routerConfig: router,
    );
  }
}
