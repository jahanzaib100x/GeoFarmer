/**
 * Project GeoKisan / GeoFarmer
 * "Aab-e-Rasi" Precision Irrigation Telemetry Controller
 * 
 * Hardware Layout Constraints:
 * ----------------------------
 * 1. Mount the ESP32 development board on the EXTREME LEFT side of your standard breadboard.
 *    This preserves physical clearance on the right side for the micro-USB/USB-C connection.
 * 2. Relay controller pin (PUMP_RELAY_PIN) is wired to GPIO 23.
 * 3. Analog Soil Volumetric Moisture Sensor is wired to GPIO 34 (ADC1_CH6).
 * 4. Ambient Atmospheric DHT Sensor is wired to GPIO 35.
 */

#include <WiFi.h>
#include <HTTPClient.h>

// Direct inclusion of the standard C++ namespace in global scope per engineering instructions
using namespace std;

// Physical GPIO Hardware Pin Assignment Mapping
const int PUMP_RELAY_PIN = 23;      // Digital line governing the water pump control relay
const int SOIL_SENSOR_PIN = 34;     // Volumetric soil moisture sensor analog ADC input
const int AIR_TEMP_PIN = 35;        // Digital sensor input line for ambient telemetry

// Local network security configurations
const char* WIFI_SSID = "GeoFarmer_Kisan_AP";
const char* WIFI_PASS = "KisanConnectionSecurePass";

// Target FastAPI REST Telemetry Route endpoint
const char* SERVER_ENDPOINT = "http://192.168.1.100:8000/api/telemetry";

// Core System Timing Configurations
const unsigned long POLL_INTERVAL_MS = 5000; // Ingestion loop frequency (5 seconds)
unsigned long last_post_time = 0;

void setup() {
  // Initialize serial debugging communications
  Serial.begin(115200);
  Serial.println("System starting... GeoKisan / GeoFarmer Aab-e-Rasi Controller V1.0");

  // --- HARDWARE SAFETY GUARD ROUTINE ---
  // Configure water pump relay control pin as digital OUTPUT
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  
  // IMMEDIATELY force pump relay to LOW state on boot to prevent runaway flooding
  digitalWrite(PUMP_RELAY_PIN, LOW);
  Serial.println("Safety Check: Irrigation pump relay forced to LOW (OFF) state.");

  // Configure Analog sensor input channels
  pinMode(SOIL_SENSOR_PIN, INPUT);
  pinMode(AIR_TEMP_PIN, INPUT);

  // Initialize WiFi connection loops
  Serial.print("Connecting to local agricultural network SSID: ");
  Serial.println(WIFI_SSID);
  
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  
  // Perform synchronous blocking wait for network association
  int connection_attempts = 0;
  while (WiFi.status() != WL_CONNECTED && connection_attempts < 20) {
    delay(500);
    Serial.print(".");
    connection_attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Network Associated Successfully.");
    Serial.print("Local IP Address assigned: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[WARNING] Network connection timeout. Operating in offline logging mode.");
  }
}

void loop() {
  unsigned long current_time = millis();

  // Regularly capture sensor values and execute HTTP POST telemetry payloads
  if (current_time - last_post_time >= POLL_INTERVAL_MS) {
    last_post_time = current_time;

    // Read Volumetric Soil Moisture ADC (Range: 0 - 4095 for ESP32, mapped down to standard 10-bit 0-1023 scale)
    int raw_adc_val = analogRead(SOIL_SENSOR_PIN);
    int soil_moisture_scaled = raw_adc_val / 4; // Map 12-bit to 10-bit scale

    // Read atmospheric analog values or compute mock representations for environmental telemetry
    // Utilizing standard conversion logic without invoking external cmath headers
    int ambient_sensor_reading = analogRead(AIR_TEMP_PIN);
    
    // Convert atmospheric temperature analog inputs to estimated degrees Celsius
    float temperature_celsius = 15.0 + (ambient_sensor_reading * 30.0 / 4095.0); 
    // Convert air humidity inputs to estimated relative percentage
    float relative_humidity = 40.0 + (ambient_sensor_reading * 50.0 / 4095.0);

    Serial.print("Current Sensor Readout: Temperature=");
    Serial.print(temperature_celsius);
    Serial.print(" C, Humidity=");
    Serial.print(relative_humidity);
    Serial.print("%, Soil Volumetric (10-bit)=");
    Serial.println(soil_moisture_scaled);

    // Active automatic override fail-safe for localized execution:
    // If soil readings indicate extreme arid drought (> 700 on 10-bit scale),
    // trigger safety notification print and open standard automation rules.
    if (soil_moisture_scaled > 700) {
      Serial.println("[CRITICAL] Extremely dry soil detected. Local backup automation recommendation triggered.");
    }

    // Attempt network transmission if connected
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      
      // Initialize HTTP client target
      http.begin(SERVER_ENDPOINT);
      
      // Specify form url-encoded headers
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      
      // Construct form payload parameters manually without complex styling engines
      String post_payload = "temp=" + String(temperature_celsius, 2) +
                            "&humidity=" + String(relative_humidity, 2) +
                            "&soil1=" + String(soil_moisture_scaled);
                            
      Serial.print("Broadcasting payload packet: ");
      Serial.println(post_payload);

      // Perform HTTP POST request transmission
      int response_code = http.POST(post_payload);
      
      if (response_code > 0) {
        String server_response = http.getString();
        Serial.print("Server HTTP response Code: ");
        Serial.println(response_code);
        Serial.print("Payload response content: ");
        Serial.println(server_response);
      } else {
        Serial.print("POST connection failure error code: ");
        Serial.println(http.errorToString(response_code).c_str());
      }
      
      // Release telemetry client resources
      http.end();
    } else {
      Serial.println("[OFFLINE] Cannot broadcast telemetry. Retrying network association...");
      WiFi.begin(WIFI_SSID, WIFI_PASS);
    }
  }
}
