import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import '../../features/auth/screens/auth_screen.dart';
import '../../features/path/screens/path_screen.dart';
import '../../features/lessons/screens/lesson_screen.dart';

final GoRouter router = GoRouter(
  initialLocation: '/auth',
  routes: [
    GoRoute(
      path: '/auth',
      builder: (context, state) => const AuthScreen(),
    ),
    GoRoute(
      path: '/path',
      builder: (context, state) => const PathScreen(),
    ),
    GoRoute(
      path: '/lesson/:levelId',
      builder: (context, state) {
        final levelId = int.parse(state.pathParameters['levelId']!);
        return LessonScreen(levelId: levelId);
      },
    ),
  ],
);
