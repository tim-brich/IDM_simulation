import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

final dio = Dio(
  BaseOptions(
    // Localhost on Android emulator is 10.0.2.2.
    // Use localhost or 127.0.0.1 for web/iOS emulator.
    baseUrl: kIsWeb ? 'http://localhost:80' : 'http://10.0.2.2:80',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ),
);
