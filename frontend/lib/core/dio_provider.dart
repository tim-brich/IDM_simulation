import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'api_client.dart';
import '../features/auth/providers/auth_provider.dart';

part 'dio_provider.g.dart';

@riverpod
Dio dioClient(Ref ref) {
  final token = ref.watch(authTokenProvider);

  // Clear existing interceptors to prevent duplicates
  dio.interceptors.clear();

  dio.interceptors.add(
    InterceptorsWrapper(
      onRequest: (options, handler) {
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ),
  );

  return dio;
}
