import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme.dart';

class PathScreen extends StatelessWidget {
  const PathScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Путь обучения'),
        backgroundColor: AppTheme.backgroundDark,
        elevation: 0,
        actions: [
          Row(
            children: const [
              Icon(Icons.local_fire_department, color: AppTheme.gold),
              SizedBox(width: 4),
              Text('2', style: TextStyle(color: AppTheme.gold, fontWeight: FontWeight.bold, fontSize: 18)),
              SizedBox(width: 16),
            ],
          )
        ],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: 3,
        itemBuilder: (context, index) {
          final isLocked = index > 0;
          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            child: InkWell(
              onTap: isLocked ? null : () => context.push('/lesson/${index + 1}'),
              borderRadius: BorderRadius.circular(16),
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundColor: isLocked ? Colors.grey[800] : AppTheme.emerald,
                      child: Icon(
                        isLocked ? Icons.lock : Icons.play_arrow,
                        color: Colors.white,
                        size: 30,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Уровень ${index + 1}',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: isLocked ? Colors.grey : Colors.white,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            isLocked ? 'Завершите предыдущие уроки' : 'Основы знакомства',
                            style: TextStyle(color: isLocked ? Colors.grey : Colors.grey[400]),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
