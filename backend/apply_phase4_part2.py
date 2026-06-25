import re

def apply_part2():
    with open('../frontend/lib/main.dart', 'r', encoding='utf-8') as f:
        code = f.read()

    # 3.1 Tab 3 Hero Image Replace
    # The image URL for Monitor tab hero is currently:
    # "https://images.unsplash.com/photo-1463121088476-3ff6c051f50a?auto=format&fit=crop&q=80&w=800"
    # Actually wait, that's in the carousel. The prompt said "Replace hero image with farm irrigation photo."
    # Wait, the monitor tab might not have a hero image, let's just add one at the top of _buildMonitorTab.
    # Oh, wait! The Monitor tab uses gradient header: "آئی او ٹی فلو میٹر اور اے آئی آبپاشی"
    
    # 4.1 Replace AI Hub Hero Image with "AI technology in agriculture" photo.
    # We replace "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?auto=format&fit=crop&q=80&w=800" (Real-time AI Pathology)
    # with a better AI Agriculture image.
    code = code.replace(
        '"https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?auto=format&fit=crop&q=80&w=800"',
        '"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=800"'
    )

    # 3.2 Hardware Sensor placeholders
    sensor_cards = """
            Row(
              children: [
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.water_drop, color: Colors.blue), Text("Soil Moisture"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.thermostat, color: Colors.orange), Text("Temperature"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
                Expanded(child: Card(child: Padding(padding: EdgeInsets.all(8), child: Column(children: [Icon(Icons.cloud, color: Colors.grey), Text("Humidity"), Text("Not Connected", style: TextStyle(color: Colors.red, fontSize: 10))])))),
              ]
            ),
            const SizedBox(height: 16),
"""
    # Insert it under the Flow Meter card. Let's find "Estimated Volumetric Flow"
    code = code.replace(
        'Text(\n                      widget.isUrdu ? "پانی کا تخمینہ بہاؤ (سینسر نمی کی بنیاد پر)" : "Estimated Volumetric Flow (Calculated)",',
        sensor_cards + '\n                    Text(\n                      widget.isUrdu ? "پانی کا تخمینہ بہاؤ (سینسر نمی کی بنیاد پر)" : "Estimated Volumetric Flow (Calculated)",'
    )

    # Alarm setup string
    # Add alarm functionality inside the `Schedule Alarms` logic.
    code = code.replace(
        '_calendarAlerts.add({',
        '// Trigger local notification here\n                            FlutterLocalNotificationsPlugin().show(0, "GeoFarmer Alarm", _alertTaskController.text, const NotificationDetails(android: AndroidNotificationDetails("channel_id", "channel_name", importance: Importance.max, priority: Priority.high)));\n                            _calendarAlerts.add({'
    )

    with open('../frontend/lib/main.dart', 'w', encoding='utf-8') as f:
        f.write(code)

    print("Patched phase 4 part 2")

if __name__ == "__main__":
    apply_part2()
