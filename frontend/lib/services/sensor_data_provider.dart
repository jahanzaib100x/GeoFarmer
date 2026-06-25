import 'package:flutter/foundation.dart';

class SensorDataProvider extends ChangeNotifier {
  static final SensorDataProvider _instance = SensorDataProvider._internal();
  factory SensorDataProvider() => _instance;
  SensorDataProvider._internal();

  double? _soilMoisture;
  double? _temperature;
  double? _humidity;

  double? get soilMoisture => _soilMoisture;
  double? get temperature => _temperature;
  double? get humidity => _humidity;

  bool get isConnected => _soilMoisture != null && _temperature != null && _humidity != null;

  void updateReadings(double moisture, double temp, double hum) {
    _soilMoisture = moisture;
    _temperature = temp;
    _humidity = hum;
    notifyListeners();
  }
}
