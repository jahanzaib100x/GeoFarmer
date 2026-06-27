/**
 * Project GeoKisan / GeoFarmer
 * "Aab-e-Rasi" Precision Irrigation Telemetry Controller
 * 
 * Hardware Layout Constraints:
 * ----------------------------
 * 1. Mount the ESP32 development board on the EXTREME LEFT side of your standard breadboard.
 *    This preserves physical clearance on the right side for the micro-USB/USB-C connection.
 * 2. Relay controller pin (PUMP_RELAY_PIN) is wired to GPIO 5 (D5).
 * 3. Analog Soil Volumetric Moisture Sensor 1 is wired to GPIO 34 (D34).
 * 4. Analog Soil Volumetric Moisture Sensor 2 is wired to GPIO 35 (D35).
 * 5. Ambient Atmospheric DHT22 Sensor is wired to GPIO 4 (D4).
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// Direct inclusion of the standard C++ namespace in global scope per engineering instructions
using namespace std;

// --- HARDWARE CONFIGURATION ---
const int PUMP_RELAY_PIN = 5;       // Digital line governing the water pump control relay (wired to D5)
const int SOIL_SENSOR_1_PIN = 34;   // Volumetric soil moisture sensor 1 (wired to D34)
const int SOIL_SENSOR_2_PIN = 35;   // Volumetric soil moisture sensor 2 (wired to D35)
const int DHT_PIN = 4;              // DHT22 temperature and humidity sensor data line (wired to D4)

// --- RELAY ACTIVE STATE CONFIGURATION ---
// Set this to true if your relay turns ON when writing LOW (most common for Arduino relay modules).
// Set this to false if your relay turns ON when writing HIGH.
const bool RELAY_ACTIVE_LOW = true; 

// --- WIFI CONFIGURATION ---
const char* WIFI_SSID = "Super";
const char* WIFI_PASS = "100200100";

// --- API SERVER CONFIGURATION ---
// Change 192.168.1.100 to the actual local IP address of your running FastAPI server.
const char* SERVER_ENDPOINT = "https://geofarmer-backend.onrender.com/api/telemetry";

// Core System Timing Configurations
const unsigned long POLL_INTERVAL_MS = 5000; // Ingestion loop frequency (5 seconds)
unsigned long last_post_time = 0;

// Initialize DHT Sensor
DHT dht(DHT_PIN, DHT22);

// Helper function to set the pump state correctly based on relay polarity
void setPumpRelay(bool turnOn) {
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(PUMP_RELAY_PIN, turnOn ? LOW : HIGH);
  } else {
    digitalWrite(PUMP_RELAY_PIN, turnOn ? HIGH : LOW);
  }
}

void setup() {
  // Initialize serial debugging communications
  Serial.begin(115200);
  Serial.println("System starting... GeoKisan / GeoFarmer Aab-e-Rasi Controller V1.1");

  // Configure PUMP Relay pin
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  
  // IMMEDIATELY force pump relay to OFF state on boot to prevent runaway flooding
  setPumpRelay(false);
  Serial.print("Safety Check: Irrigation pump relay forced to OFF state. Polarity: ");
  Serial.println(RELAY_ACTIVE_LOW ? "ACTIVE-LOW" : "ACTIVE-HIGH");

  // Configure analog input pins
  pinMode(SOIL_SENSOR_1_PIN, INPUT);
  pinMode(SOIL_SENSOR_2_PIN, INPUT);

  // Initialize DHT sensor
  dht.begin();

  // Initialize WiFi connection loops
  Serial.print("Connecting to local agricultural network SSID: ");
  Serial.println(WIFI_SSID);
  
  WiFi.setAutoReconnect(true);
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
    Serial.println("\n[WARNING] Network connection timeout. Operating in offline fallback mode.");
  }
}

void loop() {
  unsigned long current_time = millis();

  // Regularly capture sensor values and execute HTTP POST telemetry payloads
  if (current_time - last_post_time >= POLL_INTERVAL_MS) {
    last_post_time = current_time;

    // Read both Soil Sensors and average their values to send to the server
    int raw_soil1 = analogRead(SOIL_SENSOR_1_PIN);
    int raw_soil2 = analogRead(SOIL_SENSOR_2_PIN);
    
    // Scale 12-bit (0-4095) down to 10-bit (0-1023)
    int soil1_10bit = raw_soil1 / 4;
    int soil2_10bit = raw_soil2 / 4;
    int average_soil = (soil1_10bit + soil2_10bit) / 2;

    // Read actual DHT22 sensor values
    float temp_val = dht.readTemperature();
    float hum_val = dht.readHumidity();

    // Fallback if sensor read fails (e.g. disconnected pin)
    if (isnan(temp_val) || isnan(hum_val)) {
      Serial.println("[ERROR] Failed to read from DHT22!");
      Serial.println("[TIP 1] If you are using a blue DHT11 instead of a white DHT22, change the sensor constructor in this sketch from DHT22 to DHT11.");
      Serial.println("[TIP 2] Check if the sensor VCC is on 3V3, GND to GND, and Data is connected firmly to GPIO 4 (D4).");
      Serial.println("[TIP 3] Ensure a 4.7k or 10k pull-up resistor is installed between Data and VCC if your module lacks one.");
      Serial.println("Using fallback simulated environment.");
      temp_val = 27.5;
      hum_val = 60.0;
    }

    Serial.print("Sensors -> Temp: ");
    Serial.print(temp_val);
    Serial.print(" C | Hum: ");
    Serial.print(hum_val);
    Serial.print("% | Soil1 (D34): ");
    Serial.print(soil1_10bit);
    Serial.print(" | Soil2 (D35): ");
    Serial.print(soil2_10bit);
    Serial.print(" | Avg Soil: ");
    Serial.println(average_soil);

    // Active automatic override fail-safe for localized execution
    if (average_soil > 700) {
      Serial.println("[CRITICAL] Dry soil detected. Local backup irrigation rule ready.");
    }

    // Attempt network transmission if connected
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      
      // Initialize HTTP client target
      http.begin(SERVER_ENDPOINT);
      
      // Specify form url-encoded headers
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      
      // Construct form payload parameters manually
      String post_payload = "temp=" + String(temp_val, 2) +
                            "&humidity=" + String(hum_val, 2) +
                            "&soil1=" + String(average_soil);
                            
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
        
        // Wirelessly trigger physical irrigation pump relay pin based on server command
        // We support multiple variations of the pump_active parameter (with or without spaces, string or boolean)
        bool cmd_active = false;
        if (server_response.indexOf("\"pump_active\":\"true\"") != -1 ||
            server_response.indexOf("\"pump_active\": \"true\"") != -1 ||
            server_response.indexOf("\"pump_active\":true") != -1 ||
            server_response.indexOf("\"pump_active\": true") != -1) {
          cmd_active = true;
        }

        if (cmd_active) {
          setPumpRelay(true);
          Serial.println("[PUMP RELAY] Forced to ON by server command. Relay pin set to: " + String(RELAY_ACTIVE_LOW ? "LOW" : "HIGH"));
        } else {
          setPumpRelay(false);
          Serial.println("[PUMP RELAY] Forced to OFF by server command. Relay pin set to: " + String(RELAY_ACTIVE_LOW ? "HIGH" : "LOW"));
        }
      } else {
        Serial.print("POST connection failure error code: ");
        Serial.println(http.errorToString(response_code).c_str());
      }
      
      // Release telemetry client resources
      http.end();
    } else {
      Serial.println("[OFFLINE] Cannot broadcast telemetry. Waiting for automatic WiFi reconnect...");
    }
  }
}
