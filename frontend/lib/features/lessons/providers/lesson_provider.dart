import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../../../core/api_client.dart';
import '../models/task.dart';

part 'lesson_provider.g.dart';

@riverpod
Future<List<Task>> levelTasks(Ref ref, int levelId) async {
  final response = await dio.get('/levels/$levelId/tasks');
  return (response.data as List).map((t) => Task.fromJson(t)).toList();
}

@riverpod
class SubmitAnswer extends _$SubmitAnswer {
  @override
  FutureOr<AnswerResult?> build() => null;

  Future<void> submit(int taskId, String answer) async {
    state = const AsyncValue.loading();
    try {
      final response = await dio.post('/tasks/$taskId/submit', data: {'answer': answer});
      state = AsyncValue.data(AnswerResult.fromJson(response.data));
    } catch (e) {
      state = AsyncValue.error(e, StackTrace.current);
    }
  }
}
