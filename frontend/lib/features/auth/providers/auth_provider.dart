import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/api_client.dart';

part 'auth_provider.g.dart';

@riverpod
class AuthToken extends _$AuthToken {
  @override
  String? build() => null;

  void setToken(String token) {
    state = token;
    dio.options.headers['Authorization'] = 'Bearer \$token';
  }

  void logout() {
    state = null;
    dio.options.headers.remove('Authorization');
  }
}
