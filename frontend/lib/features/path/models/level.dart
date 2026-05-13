import 'package:freezed_annotation/freezed_annotation.dart';
import '../../lessons/models/task.dart';

part 'level.freezed.dart';
part 'level.g.dart';

@freezed
class Level with _$Level {
  const factory Level({
    required int id,
    required int orderIndex,
    required String title,
    String? description,
    @Default([]) List<Task> tasks,
  }) = _Level;

  factory Level.fromJson(Map<String, dynamic> json) => _$LevelFromJson(json);
}
