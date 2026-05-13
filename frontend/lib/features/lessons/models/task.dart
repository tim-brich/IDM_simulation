import 'package:freezed_annotation/freezed_annotation.dart';

part 'task.freezed.dart';
part 'task.g.dart';

@freezed
class Task with _$Task {
  const factory Task({
    required int id,
    required int levelId,
    required String type,
    required String question,
    String? imageUrl,
    Map<String, dynamic>? metadataJson,
  }) = _Task;

  factory Task.fromJson(Map<String, dynamic> json) => _$TaskFromJson(json);
}

@freezed
class AnswerResult with _$AnswerResult {
  const factory AnswerResult({
    required bool isCorrect,
    String? feedback,
    int? stars,
    required int xpEarned,
  }) = _AnswerResult;

  factory AnswerResult.fromJson(Map<String, dynamic> json) => _$AnswerResultFromJson(json);
}
