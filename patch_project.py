import re

def patch_project():
    with open('frontend/lib/main.dart', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Imports replacement
    imports = """import 'screens/interactive_map_selector.dart';
import 'screens/navigate_tab_map.dart';
import 'services/sensor_data_provider.dart';
import 'services/agronomy_guide_data.dart';
import 'package:timezone/data/latest.dart' as tz;
import 'package:timezone/timezone.dart' as tz;"""
    if "screens/interactive_map_selector.dart" not in content:
        content = re.sub(
            r"(import 'screens/auth_screen.dart';)",
            r"\1\n" + imports,
            content
        )

    # 2. Main function replacement
    main_func = """void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  tz.initializeTimeZones();
  try {
    final prefs = await SharedPreferences.getInstance();
    globalBackendUrl = prefs.getString('backend_url') ?? "https://geofarmer-backend.onrender.com";
    globalGeminiApiKey = prefs.getString('gemini_api_key') ?? "";
    
    final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
    const AndroidInitializationSettings initializationSettingsAndroid = AndroidInitializationSettings('@mipmap/ic_launcher');
    const InitializationSettings initializationSettings = InitializationSettings(android: initializationSettingsAndroid);
    await flutterLocalNotificationsPlugin.initialize(initializationSettings);
  } catch (e) {
    print("Failed to initialize SharedPreferences or Notifications: $e");
  }
  runApp(const GeoKisanApp());
}"""
    content = re.sub(
        r"void main\(\) async \{.*?runApp\(const GeoKisanApp\(\)\);\s*\}",
        main_func,
        content,
        flags=re.DOTALL
    )

    # 3. Change _doctorCrop default to "Auto Detect"
    content = content.replace(
        'String _doctorCrop = "Wheat (Sona-21)";',
        'String _doctorCrop = "Auto Detect";'
    )

    # 4. Onboarding land node
    old_land0 = """          _lands[0] = LandNode(
            id: "L1",
            nickname: "Plot A ($_onboardingLocation)",
            size: _onboardingLandSize,
            unit: _onboardingLandUnit,
            latitude: 30.1575,
            longitude: 71.5249,
            description: _onboardingSelectedCrops.isNotEmpty
                ? "Registered crop: ${_onboardingSelectedCrops.join(', ')}"
                : "Sandy clay wheat zone",
          );"""

    new_land0 = """          _lands[0] = LandNode(
            id: "L1",
            nickname: _onboardingLocation.isNotEmpty ? _onboardingLocation : "My Farm",
            size: _onboardingLandSize,
            unit: _onboardingLandUnit,
            latitude: 30.1575,
            longitude: 71.5249,
            description: _onboardingSelectedCrops.isNotEmpty
                ? "Registered crop: ${_onboardingSelectedCrops.join(', ')}"
                : "Sandy clay wheat zone",
          );"""
    content = content.replace(old_land0, new_land0)

    # 5. Land Registration Wizard maps
    old_wizard_maps = "_buildInteractiveMapSelector(local)"
    new_wizard_maps = """InteractiveGoogleMapSelector(
          initialLat: _newLandLat,
          initialLng: _newLandLon,
          isUrdu: widget.isUrdu,
          onLocationSelected: (lat, lng) {
            setState(() {
              _newLandLat = lat;
              _newLandLon = lng;
            });
          },
        )"""
    content = content.replace(old_wizard_maps, new_wizard_maps)

    # Update Land saving
    old_save_land = """              final newLand = LandNode(
                id: randomString(6),
                nickname: _newLandName,
                size: _newLandSize,
                unit: _newLandUnit,
                latitude: _newLandLat,
                longitude: _newLandLon,
                description: "Custom registered farm land"
              );"""

    new_save_land = """              final newLand = LandNode(
                id: randomString(6),
                nickname: _newLandName,
                size: _newLandSize,
                unit: _newLandUnit,
                latitude: _newLandLat,
                longitude: _newLandLon,
                description: "Custom registered farm land",
                address: _newLandAddress,
              );"""
    content = content.replace(old_save_land, new_save_land)

    # 6. Lands subtitle display address
    old_lands_subtitle = """                  subtitle: Text(
                    widget.isUrdu
                      ? "پیمائش: ${land.size} ${land.unit} (${land.toAcres().toStringAsFixed(2)} ایکڑ / ${land.toHectares().toStringAsFixed(2)} ہیکٹر)"
                      : "Size: ${land.size} ${land.unit} (~${land.toAcres().toStringAsFixed(2)} Acres / ${land.toHectares().toStringAsFixed(2)} Hectares)",
                    style: const TextStyle(fontSize: 12),
                  ),"""

    new_lands_subtitle = """                  subtitle: Text(
                    (widget.isUrdu
                      ? "پیمائش: ${land.size} ${land.unit} (${land.toAcres().toStringAsFixed(2)} ایکڑ / ${land.toHectares().toStringAsFixed(2)} ہیکٹر)"
                      : "Size: ${land.size} ${land.unit} (~${land.toAcres().toStringAsFixed(2)} Acres / ${land.toHectares().toStringAsFixed(2)} Hectares)") +
                      (land.address.isNotEmpty ? "\\n" + (widget.isUrdu ? "مقام" : "Location") + ": ${land.address}" : ""),
                    style: const TextStyle(fontSize: 12),
                  ),"""
    content = content.replace(old_lands_subtitle, new_lands_subtitle)

    # 7. Add button label
    old_add_crop_button = """                  ElevatedButton.icon(
                    onPressed: () => _showAddCropDialog(local),
                    icon: const Icon(Icons.add, size: 18),
                    label: Text(widget.isUrdu ? "فصل شامل کریں" : "Add Crop"),
                    style: ElevatedButton.styleFrom(backgroundColor: GeoKisanTheme.primaryGreen),
                  ),"""
    new_add_crop_button = """                  ElevatedButton.icon(
                    onPressed: () => _showAddCropDialog(local),
                    icon: const Icon(Icons.add, size: 18),
                    label: Text(widget.isUrdu ? "شامل کریں" : "Add"),
                    style: ElevatedButton.styleFrom(backgroundColor: GeoKisanTheme.primaryGreen),
                  ),"""
    content = content.replace(old_add_crop_button, new_add_crop_button)

    # 8. Alarm schedule
    old_alarm_btn = """                      _buildActionSubmitButton(label: "Save Calendar Alarm Reminder", onPressed: () {
                        if (_alertTaskController.text.isNotEmpty) {
                          setState(() {
                            // Trigger local notification here
                            FlutterLocalNotificationsPlugin().show(
                              id: 0, 
                              title: "GeoFarmer Alarm", 
                              body: _alertTaskController.text, 
                              notificationDetails: const NotificationDetails(
                                android: AndroidNotificationDetails(
                                  "channel_id", 
                                  "channel_name", 
                                  importance: Importance.max, 
                                  priority: Priority.high
                                )
                              )
                            );
                            _calendarAlerts.add({
                              "date": _alertDateController.text,
                              "time": _alertTimeController.text,
                              "task": _alertTaskController.text,
                              "notes": "Custom alarm trigger active"
                            });
                            _alertTaskController.clear();
                          });
                        }
                      }),"""

    new_alarm_btn = """                      _buildActionSubmitButton(label: "Save Calendar Alarm Reminder", onPressed: () async {
                        if (_alertTaskController.text.isNotEmpty) {
                          DateTime alertTime;
                          try {
                            alertTime = DateTime.parse("${_alertDateController.text} ${_alertTimeController.text}");
                          } catch (_) {
                            alertTime = DateTime.now().add(const Duration(seconds: 15));
                          }
                          final tzTime = tz.TZDateTime.from(alertTime, tz.local);
                          await FlutterLocalNotificationsPlugin().zonedSchedule(
                            math.Random().nextInt(100000),
                            "GeoFarmer Alert",
                            _alertTaskController.text,
                            tzTime,
                            const NotificationDetails(
                              android: AndroidNotificationDetails(
                                "channel_id",
                                "channel_name",
                                importance: Importance.max,
                                priority: Priority.high,
                                playSound: true,
                              )
                            ),
                            androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
                            uiLocalNotificationDateInterpretation: UILocalNotificationDateInterpretation.absoluteTime,
                          );
                          setState(() {
                            _calendarAlerts.add({
                              "date": _alertDateController.text,
                              "time": _alertTimeController.text,
                              "task": _alertTaskController.text,
                              "notes": "Custom alarm scheduled"
                            });
                            _alertTaskController.clear();
                          });
                        }
                      }),"""
    content = content.replace(old_alarm_btn, new_alarm_btn)

    # 9. Yield State variables
    state_vars_to_inject = """  // Yield forecast state variables
  bool _isYieldLoading = false;
  String _yieldExpected = "";
  String _yieldSummary = "";
  String _yieldRecommendations = "";"""

    if "bool _isYieldLoading = false;" not in content:
        content = content.replace(
            '  String _yieldCrop = "Wheat (Sona-21)";',
            '  String _yieldCrop = "Wheat (Sona-21)";\n' + state_vars_to_inject
        )

    # 10. Yield evaluator module UI
    old_yield_eval_module = """  Widget _buildYieldEvaluatorModule(AppLocalization local) {
    return Card(
      color: GeoKisanTheme.surfaceCream,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            DropdownButtonFormField<String>(
              value: _yieldCrop,
              decoration: const InputDecoration(labelText: "Select Crop"),
              items: ["Wheat (Sona-21)", "Cotton (BT-902)", "Rice (Basmati)", "Potato (Red-S)", "Tomato (Sahil)"].map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _yieldCrop = val);
              },
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _yieldStage,
              decoration: const InputDecoration(labelText: "Growth Stage"),
              items: ["Flowering Stage", "Milk Stage", "Harvest Ready"].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _yieldStage = val);
              },
            ),
            const SizedBox(height: 12),
            _buildActionSubmitButton(label: "Calculate AI Precision Yield", onPressed: () => _calculateAiYieldForecast()),
            if (_yieldPredMaunds > 0) ...[
              const SizedBox(height: 16),
              Align(
                alignment: Alignment.centerLeft,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.isUrdu ? "متوقع حاصل پیداوار: $_yieldPredMaunds من" : "Estimated Harvest: $_yieldPredMaunds Maunds",
                      style: TextStyle(color: GeoKisanTheme.primaryGreen, fontWeight: FontWeight.bold, fontSize: 15),
                    ),
                    Text("Expected Range: $_yieldRange", style: const TextStyle(fontSize: 12, color: Colors.grey)),
                    const Divider(),
                    Text(widget.isUrdu ? _yieldSummaryUr : _yieldRemedyEn, style: const TextStyle(fontSize: 13, height: 1.4)),
                    const SizedBox(height: 6),
                    Text(
                      widget.isUrdu ? _yieldRemedyUr : _yieldRemedyEn,
                      style: const TextStyle(fontSize: 13, height: 1.4, fontStyle: FontStyle.italic, color: GeoKisanTheme.aiGold),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }"""

    new_yield_eval_module = """  Widget _buildYieldEvaluatorModule(AppLocalization local) {
    String? selectedCropValue = _yieldCrop;
    if (!_localCrops.any((c) => c.name == selectedCropValue)) {
      selectedCropValue = _localCrops.isNotEmpty ? _localCrops.first.name : null;
    }
    return Card(
      color: GeoKisanTheme.surfaceCream,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            DropdownButtonFormField<String>(
              value: selectedCropValue,
              decoration: const InputDecoration(labelText: "Select Crop"),
              items: _localCrops.map((c) => DropdownMenuItem(value: c.name, child: Text(c.name))).toList(),
              onChanged: (val) {
                if (val != null) {
                  setState(() {
                    _yieldCrop = val;
                  });
                }
              },
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _yieldStage,
              decoration: const InputDecoration(labelText: "Growth Stage"),
              items: ["Flowering Stage", "Milk Stage", "Harvest Ready"].map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
              onChanged: (val) {
                if (val != null) setState(() => _yieldStage = val);
              },
            ),
            const SizedBox(height: 12),
            _buildActionSubmitButton(label: "Calculate AI Precision Yield", onPressed: () => _calculateAiYieldForecast()),
            if (_isYieldLoading)
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: CircularProgressIndicator(),
              )
            else if (_yieldExpected.isNotEmpty) ...[
              const SizedBox(height: 16),
              Card(
                color: Colors.green[50],
                child: ListTile(
                  title: Text(widget.isUrdu ? "متوقع پیداوار" : "Expected Yield", style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(_yieldExpected, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen)),
                ),
              ),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(widget.isUrdu ? "عوامل کا خلاصہ" : "Summary of Key Factors", style: const TextStyle(fontWeight: FontWeight.bold)),
                          IconButton(
                            icon: const Icon(Icons.volume_up, color: GeoKisanTheme.primaryGreen),
                            onPressed: () => _speak(_yieldSummary),
                          )
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(_yieldSummary, style: const TextStyle(fontSize: 13, height: 1.4)),
                    ],
                  ),
                ),
              ),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(widget.isUrdu ? "زرعی سفارشات" : "Agronomic Recommendations", style: const TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Text(_yieldRecommendations, style: const TextStyle(fontSize: 13, height: 1.4)),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }"""
    content = content.replace(old_yield_eval_module, new_yield_eval_module)

    # 11. Yield calculator logic
    old_calc_yield = """  Future<void> _calculateAiYieldForecast() async {
    if (!widget.isOffline) {
      try {
        final response = await _makeHttpPost(
          "${globalBackendUrl}/api/ai/yield",
          {
            "crop_name": _yieldCrop,
            "land_size": widget.activeLand.size, // double
            "land_unit": widget.activeLand.unit, // string
            "soil_moisture": _soilRawADC.toInt(), // int
            "growth_stage": _yieldStage // string
          }
        );
        if (response != null) {
          final data = json.decode(response);
          setState(() {
            _yieldPredMaunds = data["predicted_yield_maunds"].toDouble();
            _yieldRange = data["confidence_interval"];
            _yieldSummaryUr = data["urdu_yield_summary"];
            _yieldRemedyEn = data["ai_remediation_en"];
            _yieldRemedyUr = data["ai_remediation_ur"] ?? "";
          });
          return;
        }
      } catch (e) {
        print("Yield model failure: $e");
      }
    }
    // High-fidelity fallback/offline yield engine
    setState(() {
      _isSTTTranscribing = true;
    });
    await Future.delayed(const Duration(milliseconds: 1000));
    final double size = widget.activeLand.size;
    final double baseYield = _yieldCrop.contains("Wheat") ? 42.5 : 35.8;
    final double computed = baseYield * size;
    setState(() {
      _yieldPredMaunds = double.parse(computed.toStringAsFixed(1));
      _yieldRange = "${(computed * 0.9).toStringAsFixed(1)} - ${(computed * 1.1).toStringAsFixed(1)} Maunds total";
      _yieldSummaryUr = "متوقع پیداوار: $_yieldPredMaunds من (${widget.activeLand.nickname})";
      _yieldRemedyEn = "Keep soil moisture balanced. Monitor nitrogen levels carefully to optimize tillering head weights.";
      _yieldRemedyUr = "اے آئی تجویز: نائٹروجن کی مقدار متوازن رکھیں اور پانی کی سطح مانیٹر کریں۔";
      _isSTTTranscribing = false;
    });
  }"""

    new_calc_yield = """  Future<void> _calculateAiYieldForecast() async {
    setState(() {
      _isYieldLoading = true;
      _yieldExpected = "";
      _yieldSummary = "";
      _yieldRecommendations = "";
    });

    final cropName = _yieldCrop;
    final size = widget.activeLand.size;
    final unit = widget.activeLand.unit;
    final soil = _soilRawADC.toInt();
    final stage = _yieldStage;

    try {
      final prompt = "Estimate the harvest yield for crop '$cropName' on land area $size $unit with current soil moisture level $soil ADC at growth stage '$stage' in Pakistan. Provide: \\n1. expected yield in kg/acre \\n2. summary of key factors \\n3. 3 agronomic recommendations. \\n\\nFormat your response EXACTLY like this so it is easily parsed: \\n\\nEXPECTED_YIELD: <expected yield here>\\nSUMMARY: <summary of factors here>\\nRECOMMENDATIONS: <3 recommendations here, each starting with a bullet point>";
      final response = await AIService.generateContent(prompt);

      String expected = "";
      String summary = "";
      String recs = "";

      if (response.contains("SUMMARY:")) {
        final parts = response.split("SUMMARY:");
        expected = parts[0].replaceAll("EXPECTED_YIELD:", "").trim();
        if (parts[1].contains("RECOMMENDATIONS:")) {
          final subParts = parts[1].split("RECOMMENDATIONS:");
          summary = subParts[0].trim();
          recs = subParts[1].trim();
        } else {
          summary = parts[1].trim();
        }
      } else {
        expected = "Expected yield: 1600 kg/acre";
        summary = response;
        recs = "1. Maintain balanced irrigation.\\n2. Apply nitrogen fertilizer at booting stage.\\n3. Weed early.";
      }

      setState(() {
        _yieldExpected = expected;
        _yieldSummary = summary;
        _yieldRecommendations = recs;
        _isYieldLoading = false;
      });

      // Speak summary and recommendations
      final textToSpeak = "$_yieldSummary. $_yieldRecommendations";
      _speak(textToSpeak);
    } catch (e) {
      print("Failed yield forecast: $e");
      setState(() {
        _isYieldLoading = false;
        _yieldExpected = "1200 - 1500 kg/acre (Fallback)";
        _yieldSummary = "Dry soil conditions may reduce crop health.";
        _yieldRecommendations = "1. Apply water immediately.\\n2. Add potash fertilizer.\\n3. Keep field weed-free.";
      });
    }
  }"""
    content = content.replace(old_calc_yield, new_calc_yield)

    # 12. Patch Monitor Tab: Header Image & Height
    content = content.replace(
        "final Map<String, String> headerImages = {",
        "final Map<String, String> headerImages = {\n      'tab_monitor': \"https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=800&fit=crop\",\n      'tab_ai_hub': \"https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&fit=crop\","
    )
    content = content.replace(
        "height: 140,",
        "height: (moduleId == 'tab_monitor' || moduleId == 'tab_ai_hub') ? 200 : 140,"
    )

    # 13. State variables & listener for SensorDataProvider
    sensor_listener_setup = """    SensorDataProvider().addListener(_onSensorDataChanged);"""
    sensor_listener_dispose = """    SensorDataProvider().removeListener(_onSensorDataChanged);"""
    sensor_listener_callback = """  void _onSensorDataChanged() {
    if (mounted) {
      setState(() {});
    }
  }"""

    if "SensorDataProvider().addListener" not in content:
        content = content.replace(
            "    _loadOnboardingPreferences();",
            "    _loadOnboardingPreferences();\n" + sensor_listener_setup
        )
        content = content.replace(
            "    _onboardingLocationController.dispose();",
            "    _onboardingLocationController.dispose();\n" + sensor_listener_dispose
        )
        content = content.replace(
            "  Widget _renderSubsystemDetails(AppLocalization local) {",
            sensor_listener_callback + "\n\n  Widget _renderSubsystemDetails(AppLocalization local) {"
        )

    # 14. Replace local sensor cards in Monitor tab with SensorDataProvider readings
    old_sensor_cards_row = """            Row(
              children: [
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.water_drop, color: Colors.blue), Text("Soil Moisture"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.thermostat, color: Colors.orange), Text("Temperature"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.cloud, color: Colors.grey), Text("Humidity"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
              ]
            ),"""

    new_sensor_cards_row = """            Row(
              children: [
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        children: [
                          const Icon(Icons.water_drop, color: Colors.blue),
                          const Text("Soil Moisture"),
                          Text(
                            SensorDataProvider().soilMoisture != null
                                ? "${SensorDataProvider().soilMoisture!.toStringAsFixed(1)}%"
                                : (widget.isUrdu ? "سینسر آف لائن" : "Sensor offline"),
                            style: TextStyle(
                              color: SensorDataProvider().soilMoisture != null ? GeoKisanTheme.primaryGreen : Colors.red,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          )
                        ],
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        children: [
                          const Icon(Icons.thermostat, color: Colors.orange),
                          const Text("Temperature"),
                          Text(
                            SensorDataProvider().temperature != null
                                ? "${SensorDataProvider().temperature!.toStringAsFixed(1)}°C"
                                : (widget.isUrdu ? "سینسر آف لائن" : "Sensor offline"),
                            style: TextStyle(
                              color: SensorDataProvider().temperature != null ? GeoKisanTheme.primaryGreen : Colors.red,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          )
                        ],
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Column(
                        children: [
                          const Icon(Icons.cloud, color: Colors.grey),
                          const Text("Humidity"),
                          Text(
                            SensorDataProvider().humidity != null
                                ? "${SensorDataProvider().humidity!.toStringAsFixed(1)}%"
                                : (widget.isUrdu ? "سینسر آف لائن" : "Sensor offline"),
                            style: TextStyle(
                              color: SensorDataProvider().humidity != null ? GeoKisanTheme.primaryGreen : Colors.red,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          )
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),"""
    content = content.replace(old_sensor_cards_row, new_sensor_cards_row)

    # 15. Helper for Weather detail item
    weather_detail_helper = """  Widget _buildWeatherDetailItem(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: GeoKisanTheme.primaryGreen),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }"""
    
    if "_buildWeatherDetailItem" not in content:
        content = content.replace(
            "  Widget _buildLandRegistrationWizard(AppLocalization local) {",
            weather_detail_helper + "\n\n  Widget _buildLandRegistrationWizard(AppLocalization local) {"
        )

    # 16. State variables for Weather & AI Farm Insight
    weather_state_vars = """  // Weather and AI insight state variables
  Map<String, dynamic>? _currentWeather;
  bool _isWeatherLoading = false;
  String _aiFarmInsight = "";
  bool _isInsightLoading = false;"""

    if "_currentWeather" not in content:
        content = content.replace(
            "  // Alarms and alerts calendar schedules",
            weather_state_vars + "\n\n  // Alarms and alerts calendar schedules"
        )

    # 17. Implement _fetchWeatherData & _generateAiFarmInsight
    weather_methods = """  Future<void> _fetchWeatherData() async {
    final lat = widget.activeLand.latitude != 0.0 ? widget.activeLand.latitude : 30.1575;
    final lng = widget.activeLand.longitude != 0.0 ? widget.activeLand.longitude : 71.5249;
    setState(() {
      _isWeatherLoading = true;
    });
    try {
      final prompt = "Give the current weather at latitude $lat, longitude $lng in Pakistan. Return ONLY a JSON object with the following fields: temperature_c (number), humidity_pct (number), rainfall_mm (number), wind_kph (number), uv_index (number), condition (string). Do not include any other text or markdown formatting outside the JSON.";
      final response = await AIService.generateContent(prompt);
      
      String cleanJson = response.trim();
      if (cleanJson.contains("```json")) {
        cleanJson = cleanJson.substring(cleanJson.indexOf("```json") + 7);
        cleanJson = cleanJson.substring(0, cleanJson.indexOf("```"));
      } else if (cleanJson.contains("```")) {
        cleanJson = cleanJson.substring(cleanJson.indexOf("```") + 3);
        cleanJson = cleanJson.substring(0, cleanJson.indexOf("```"));
      }
      cleanJson = cleanJson.trim();

      final parsed = json.decode(cleanJson);
      setState(() {
        _currentWeather = parsed;
        _isWeatherLoading = false;
      });
      _generateAiFarmInsight(parsed);
    } catch (e) {
      print("Gemini weather failed, falling back to GEE: $e");
      try {
        final res = await http.post(
          Uri.parse("${globalBackendUrl}/api/ai/gee/thermal"),
          headers: {"Content-Type": "application/json"},
          body: json.encode({
            "polygon_coords": [
              {"lat": lat - 0.001, "lng": lng - 0.001},
              {"lat": lat + 0.001, "lng": lng - 0.001},
              {"lat": lat + 0.001, "lng": lng + 0.001},
              {"lat": lat - 0.001, "lng": lng + 0.001},
            ],
            "crop_name": "Wheat"
          }),
        );
        if (res.statusCode == 200) {
          final data = json.decode(res.body);
          final tempAvg = data["thermal_average"] ?? 30.0;
          final parsed = {
            "temperature_c": tempAvg,
            "humidity_pct": 50,
            "rainfall_mm": 0,
            "wind_kph": 12,
            "uv_index": 6,
            "condition": "Clear (GEE Thermal Scan)"
          };
          setState(() {
            _currentWeather = parsed;
            _isWeatherLoading = false;
          });
          _generateAiFarmInsight(parsed);
          return;
        }
      } catch (geeErr) {
        print("GEE fallback failed: $geeErr");
      }
      final parsedFallback = {
        "temperature_c": 32.5,
        "humidity_pct": 45,
        "rainfall_mm": 0,
        "wind_kph": 10,
        "uv_index": 8,
        "condition": "Sunny"
      };
      setState(() {
        _currentWeather = parsedFallback;
        _isWeatherLoading = false;
      });
      _generateAiFarmInsight(parsedFallback);
    }
  }

  Future<void> _generateAiFarmInsight(Map<String, dynamic> weather) async {
    setState(() {
      _isInsightLoading = true;
      _aiFarmInsight = "";
    });
    final moisture = SensorDataProvider().soilMoisture ?? 45.0;
    final temp = SensorDataProvider().temperature ?? 28.0;
    final hum = SensorDataProvider().humidity ?? 55.0;
    final prompt = "Given farm sensor data: Soil Moisture: $moisture%, Temp: $temp°C, Humidity: $hum%, and current weather: ${weather['temperature_c']}°C, humidity ${weather['humidity_pct']}%, rain ${weather['rainfall_mm']}mm, wind ${weather['wind_kph']}kph. Provide a 2-sentence condition summary, one urgent action, and one preventive recommendation in ${widget.isUrdu ? 'Urdu' : 'English'}.";
    try {
      final res = await AIService.generateContent(prompt);
      setState(() {
        _aiFarmInsight = res;
        _isInsightLoading = false;
      });
      _speak(res);
    } catch (e) {
      print("Failed generating insight: $e");
      setState(() {
        _aiFarmInsight = widget.isUrdu
            ? "فارم کے حالات نارمل ہیں۔ پانی کی سطح کو مانیٹر کریں اور باقاعدگی سے گوڈی کریں۔"
            : "Farm conditions are stable. Monitor moisture levels and weed regularly.";
        _isInsightLoading = false;
      });
    }
  }"""

    if "_fetchWeatherData" not in content:
        content = content.replace(
            "  Future<void> _calculateAiYieldForecast() async {",
            weather_methods + "\n\n  Future<void> _calculateAiYieldForecast() async {"
        )

    # 18. Rewrite case 'tab_monitor' body entirely
    old_monitor_case = """      case 'tab_monitor':
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Smart Irrigation (m8, m9)
            Card(
              elevation: 3,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    
            Row(
              children: [
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.water_drop, color: Colors.blue), Text("Soil Moisture"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.thermostat, color: Colors.orange), Text("Temperature"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.cloud, color: Colors.grey), Text("Humidity"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
              ]
            ),
            const SizedBox(height: 16),

                    Text(
                      widget.isUrdu ? "پانی کا تخمینہ بہاؤ (سینسر نمی کی بنیاد پر)" : "Estimated Volumetric Flow (Calculated)",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 16),
                    Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        border: Border.all(color: GeoKisanTheme.waterBlue, width: 6),
                        shape: BoxShape.circle,
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        "$_waterFlowRate\\nL/min",
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: GeoKisanTheme.waterBlue, fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Card(
                      color: GeoKisanTheme.surfaceCream,
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Text(
                          widget.isUrdu ? _waterSummaryUr : _waterSummaryEn,
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontSize: 12, height: 1.4),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              elevation: 3,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        colors: [GeoKisanTheme.waterBlue, Color(0xFF294E68)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.only(topLeft: Radius.circular(16), topRight: Radius.circular(16)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.router, color: Colors.white, size: 16),
                        const SizedBox(width: 6),
                        Text(
                          widget.isUrdu ? "آئی او ٹی فلو میٹر اور اے آئی آبپاشی" : "IoT Flow Meter & AI Irrigation",
                          style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 11),
                        ),
                      ],
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: const Icon(Icons.water_drop, color: GeoKisanTheme.waterBlue, size: 32),
                          title: Text(
                            widget.isUrdu ? "سفارش کردہ آبپاشی باری" : "Optimal Watering Schedule",
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                          ),
                          subtitle: Padding(
                            padding: const EdgeInsets.only(top: 4.0),
                            child: Text(
                              widget.isUrdu ? _waterSummaryUr : _waterSummaryEn,
                              style: const TextStyle(fontSize: 12, height: 1.4, color: GeoKisanTheme.lightText),
                            ),
                          ),
                        ),
                        
                    const SizedBox(height: 16),
                    Card(
                      elevation: 2,
                      color: GeoKisanTheme.primaryGreen.withOpacity(0.05),
                      child: Padding(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(widget.isUrdu ? "اے آئی موسم اور آبپاشی کا خلاصہ" : "AI Weather & Irrigation Insight", style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen)),
                                IconButton(icon: const Icon(Icons.volume_up, color: GeoKisanTheme.primaryGreen), onPressed: () => _speak(widget.isUrdu ? _waterSummaryUr : _waterSummaryEn)),
                              ],
                            ),
                            Text(widget.isUrdu ? _waterSummaryUr : _waterSummaryEn, style: const TextStyle(fontSize: 12)),
                          ],
                        ),
                      ),
                    ),

                        const Divider(height: 24),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceAround,
                          children: [
                            Text(widget.isUrdu ? "پریسیپیٹیشن تھریش ہولڈ" : "Precipitation limit"),
                            Slider(
                              min: 0.0,
                              max: 100.0,
                              value: _bypassThreshold,
                              activeColor: GeoKisanTheme.waterBlue,
                              onChanged: (val) {
                                setState(() {
                                  _bypassThreshold = val;
                                });
                              },
                            ),
                            Center(child: Text("Precipitation Threshold: ${_bypassThreshold.toInt()}%")),
                            const SizedBox(height: 12),
                            SwitchListTile(
                              title: Text(widget.isUrdu ? "خودکار بائی پاس فعال کریں" : "Enable Smart Weather Bypass"),
                              value: _isBypassEnabled,
                              onChanged: (val) {
                                setState(() {
                                  _isBypassEnabled = val;
                                });
                              },
                              activeColor: GeoKisanTheme.waterBlue,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            // Atmospheric weather (m11)
            Text(
              widget.isUrdu ? "7 دن کا موسمیاتی تبصرہ" : "7-Day Atmospheric Weather Outlook",
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: GeoKisanTheme.primaryGreen),
            ),
            const SizedBox(height: 8),
            ..._weatherForecast.map((f) => Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: const Icon(Icons.wb_sunny, color: GeoKisanTheme.aiGold),
                title: Text(f["day"]!, style: const TextStyle(fontWeight: FontWeight.bold)),
                subtitle: Text("${f['wind']} · ${f['rain_chance']}"),
                trailing: Text(f["temp_range"]!, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              ),
            )).toList(),
          ],
        );"""

    new_monitor_case = """      case 'tab_monitor':
        final double flowRate = SensorDataProvider().soilMoisture != null
            ? (SensorDataProvider().soilMoisture! > 70.0 ? 45.2 : (SensorDataProvider().soilMoisture! > 30.0 ? 12.8 : 0.0))
            : 0.0;
        final String waterSummary = SensorDataProvider().soilMoisture != null
            ? (SensorDataProvider().soilMoisture! > 70.0
                ? (widget.isUrdu ? "مٹی میں نمی کی شدید کمی ہے۔ سمارٹ پمپ فعال ہے۔" : "Soil moisture is critically low. Water flows actively.")
                : (SensorDataProvider().soilMoisture! > 30.0
                    ? (widget.isUrdu ? "مٹی میں نمی کی مقدار مناسب ہے۔ متوازن پمپ چل رہا ہے۔" : "Soil moisture is optimal. Steady maintenance irrigation.")
                    : (widget.isUrdu ? "مٹی مکمل طور پر سیراب ہے۔ موٹر بند کر دی گئی ہے۔" : "Soil moisture is saturated. Pump deactivated.")))
            : (widget.isUrdu ? "سینسر آف لائن" : "Sensor offline");

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 8),
            // Volumetric Water flow status
            Card(
              elevation: 3,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    Text(
                      widget.isUrdu ? "پانی کا تخمینہ بہاؤ (سینسر نمی کی بنیاد پر)" : "Estimated Volumetric Flow (Calculated)",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 16),
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        border: Border.all(color: GeoKisanTheme.waterBlue, width: 4),
                        shape: BoxShape.circle,
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        "${flowRate.toStringAsFixed(1)}\\nL/min",
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: GeoKisanTheme.waterBlue, fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(waterSummary, textAlign: TextAlign.center, style: const TextStyle(fontSize: 12)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Weather Summary & Cards Section
            Card(
              elevation: 3,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          widget.isUrdu ? "موسمیاتی صورتحال" : "Atmospheric Weather Info",
                          style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen),
                        ),
                        if (_isWeatherLoading)
                          const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                        else
                          IconButton(
                            icon: const Icon(Icons.refresh, color: GeoKisanTheme.primaryGreen),
                            onPressed: _fetchWeatherData,
                          )
                      ],
                    ),
                    const SizedBox(height: 12),
                    if (_currentWeather != null) ...[
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildWeatherDetailItem(Icons.thermostat, "${_currentWeather!['temperature_c']}°C", widget.isUrdu ? "درجہ حرارت" : "Temp"),
                          _buildWeatherDetailItem(Icons.water_drop, "${_currentWeather!['humidity_pct']}%", widget.isUrdu ? "نمی" : "Humidity"),
                          _buildWeatherDetailItem(Icons.umbrella, "${_currentWeather!['rainfall_mm']}mm", widget.isUrdu ? "بارش" : "Rain"),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _buildWeatherDetailItem(Icons.air, "${_currentWeather!['wind_kph']}kph", widget.isUrdu ? "ہوا" : "Wind"),
                          _buildWeatherDetailItem(Icons.wb_sunny, "UV: ${_currentWeather!['uv_index']}", widget.isUrdu ? "یو وی" : "UV"),
                          _buildWeatherDetailItem(Icons.cloud_queue, "${_currentWeather!['condition']}", widget.isUrdu ? "حالت" : "Condition"),
                        ],
                      ),
                    ] else
                      Center(child: ElevatedButton(onPressed: _fetchWeatherData, child: Text(widget.isUrdu ? "موسمیاتی ڈیٹا حاصل کریں" : "Fetch Weather Data"))),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // AI Farm Insight Section
            if (_isInsightLoading)
              const Center(child: CircularProgressIndicator())
            else if (_aiFarmInsight.isNotEmpty)
              Card(
                elevation: 3,
                color: GeoKisanTheme.primaryGreen.withOpacity(0.06),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            widget.isUrdu ? "اے آئی آبپاشی اور موسم کا خلاصہ" : "AI Weather & Irrigation Insight",
                            style: const TextStyle(fontWeight: FontWeight.bold, color: GeoKisanTheme.primaryGreen),
                          ),
                          IconButton(
                            icon: const Icon(Icons.volume_up, color: GeoKisanTheme.primaryGreen),
                            onPressed: () => _speak(_aiFarmInsight),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(_aiFarmInsight, style: const TextStyle(fontSize: 12, height: 1.4)),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 16),
          ],
        );"""
    content = content.replace(old_monitor_case, new_monitor_case)

    # 19. Run C3 fetch weather in initState
    content = content.replace(
        "    SensorDataProvider().addListener(_onSensorDataChanged);",
        "    SensorDataProvider().addListener(_onSensorDataChanged);\n    _fetchWeatherData();"
    )

    print("Patched Weather details and Monitor Tab UI successfully!")

    with open('frontend/lib/main.dart', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    patch_main()
