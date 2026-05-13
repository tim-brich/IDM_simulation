import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../core/theme.dart';
import '../providers/lesson_provider.dart';

class LessonScreen extends ConsumerStatefulWidget {
  final int levelId;
  const LessonScreen({super.key, required this.levelId});

  @override
  ConsumerState<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends ConsumerState<LessonScreen> {
  final TextEditingController _controller = TextEditingController();

  void _submitAnswer(int taskId) async {
    final answer = _controller.text;
    if (answer.isEmpty) return;

    await ref.read(submitAnswerProvider.notifier).submit(taskId, answer);
    final resultState = ref.read(submitAnswerProvider);

    if (resultState.hasValue && resultState.value != null) {
      final result = resultState.value!;
      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        backgroundColor: Colors.transparent,
        builder: (context) => _FeedbackSheet(
          isCorrect: result.isCorrect,
          feedback: result.feedback,
          stars: result.stars,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final tasksAsyncValue = ref.watch(levelTasksProvider(widget.levelId));

    return Scaffold(
      appBar: AppBar(
        title: Text('Урок ${widget.levelId}'),
        backgroundColor: AppTheme.backgroundDark,
        elevation: 0,
      ),
      body: tasksAsyncValue.when(
        data: (tasks) {
          if (tasks.isEmpty) {
            return const Center(child: Text("Нет заданий для этого уровня"));
          }
          final currentTask = tasks.first; // Simplification: just show first task for MVP UI

          return SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  LinearProgressIndicator(
                    value: 0.3,
                    backgroundColor: AppTheme.graphite,
                    color: AppTheme.emerald,
                    minHeight: 8,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  const SizedBox(height: 32),

                  if (currentTask.imageUrl != null) ...[
                    ClipRRect(
                      borderRadius: BorderRadius.circular(16),
                      child: CachedNetworkImage(
                        imageUrl: currentTask.imageUrl!,
                        height: 200,
                        fit: BoxFit.cover,
                        placeholder: (context, url) => const Center(child: CircularProgressIndicator()),
                        errorWidget: (context, url, error) => const Icon(Icons.error),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],

                  Text(
                    'Задание (${currentTask.type}):',
                    style: const TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    currentTask.question,
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 32),

                  TextField(
                    controller: _controller,
                    decoration: InputDecoration(
                      hintText: 'Ваш ответ...',
                      filled: true,
                      fillColor: AppTheme.graphite,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(16),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    maxLines: 3,
                    minLines: 1,
                  ),
                  const Spacer(),

                  SizedBox(
                    height: 56,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.emerald,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(16),
                        ),
                      ),
                      onPressed: () => _submitAnswer(currentTask.id),
                      child: const Text('Проверить', style: TextStyle(fontSize: 18, color: Colors.white)),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
      ),
    );
  }
}

class _FeedbackSheet extends StatelessWidget {
  final bool isCorrect;
  final String? feedback;
  final int? stars;

  const _FeedbackSheet({
    required this.isCorrect,
    this.feedback,
    this.stars,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        color: AppTheme.graphite,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(
                isCorrect ? Icons.check_circle_outline : Icons.error_outline,
                color: isCorrect ? AppTheme.emerald : Colors.redAccent,
                size: 32,
              ),
              const SizedBox(width: 16),
              Text(
                isCorrect ? 'Ответ верный!' : 'Ответ неверный',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: isCorrect ? AppTheme.emerald : Colors.redAccent,
                ),
              ),
              if (stars != null) ...[
                const Spacer(),
                Row(
                  children: List.generate(3, (index) => Icon(
                    index < stars! ? Icons.star : Icons.star_border,
                    color: AppTheme.gold,
                  )),
                )
              ]
            ],
          ),
          if (feedback != null && feedback!.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              '💡 $feedback',
              style: const TextStyle(fontSize: 16, color: Colors.white70),
            ),
          ],
          const SizedBox(height: 32),
          SizedBox(
            height: 50,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: isCorrect ? AppTheme.emerald : Colors.redAccent,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              onPressed: () {
                context.pop();
              },
              child: const Text('Понятно', style: TextStyle(color: Colors.white, fontSize: 16)),
            ),
          )
        ],
      ),
    );
  }
}
