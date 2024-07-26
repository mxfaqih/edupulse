#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>


#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define LDR_PIN        34  // LDR connected to analog pin 34
#define TRIG_PIN       5  // HCSR04 Trig pin connected to digital pin 13
#define ECHO_PIN       18  // HCSR04 Echo pin connected to digital pin 12
#define LED_PIN        4  // LED connected to digital pin 14

// Threshold values
#define LUX_THRESHOLD  500  // Threshold for dim light
#define DIST_THRESHOLD 100  // Threshold distance in cm
const char ssid[] = "IKBARA54";
const char pass[] = "12345678";
void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);
  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Wi-Fi Connected!");

  pinMode(LED_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Serial.begin(115200);

  // Initialize OLED display
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  display.display();
  delay(2000);
  display.clearDisplay();
}

void loop() {
  // Read LDR value
  int ldrValue = analogRead(LDR_PIN);
  int lux = map(ldrValue, 0, 4095, 0, 1000);  // Convert to a scale of 0 to 1000

  // Read HCSR04 value
  long duration, distance;
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;  // Convert to cm

  // Determine LED state and display message
  String message = "";
  if (lux < LUX_THRESHOLD && distance < DIST_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH);
    message = "Kelas Redup dan Objek Terdeteksi\nLED: ON";
  } else {
    digitalWrite(LED_PIN, LOW);
    message = "Kelas Terang dan Tidak ada Objek\nLED: OFF";
  }

  // Display the conditions on OLED
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print("Lux: ");
  display.print(lux);
  display.print("\nDistance: ");
  display.print(distance);
  display.print(" cm\n");
  display.print(message);
  display.display();

  // Debug output
  Serial.print("Lux: ");
  Serial.print(lux);
  Serial.print(" - Distance: ");
  Serial.print(distance);
  Serial.print(" cm - ");
  Serial.println(message);

  delay(1000);  // Delay for a second before next reading
}
