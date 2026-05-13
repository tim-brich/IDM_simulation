import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:dio/dio.dart';
import '../../../core/api_client.dart';

part 'auth_provider.g.dart';

@riverpod
class AuthToken extends _$AuthToken {
  @override
  String? build() => null;

  void setToken(String token) {
    state = token;
    dio.options.headers['Authorization'] = 'Bearer $token';
  }

  void logout() {
    state = null;
    dio.options.headers.remove('Authorization');
  }
}

@riverpod
class Login extends _$Login {
  @override
  FutureOr<void> build() {}

  Future<void> login(String email, String password) async {
    state = const AsyncValue.loading();
    try {
      // First try to register if user doesn't exist
      try {
        await dio.post('/auth/register', data: {
          'email': email,
          'password': password,
        });
      } catch (e) {
        // Ignore error if user already exists
      }

      // Then login
      final response = await dio.post(
        '/auth/login',
        data: FormData.fromMap({
          'username': email,
          'password': password,
        }),
      );

      final token = response.data['access_token'];
      ref.read(authTokenProvider.notifier).setToken(token);

      state = const AsyncValue.data(null);
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
      rethrow;
    }
  }
}
