import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/api_client.dart';
import '../models/level.dart';
import '../../auth/models/user.dart';

part 'path_provider.g.dart';

@riverpod
Future<List<Level>> levels(Ref ref) async {
  final response = await dio.get('/levels');
  return (response.data as List).map((l) => Level.fromJson(l)).toList();
}

@riverpod
Future<User> currentUser(Ref ref) async {
  final response = await dio.get('/me');
  return User.fromJson(response.data);
}
