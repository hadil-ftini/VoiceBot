#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>

// Replace with your network credentials
const char* ssid = "Redmi";
const char* password = "azertyyyy";

// Motor Pins (L298N)
const int IN1 = 18;
const int IN2 = 19;
const int IN3 = 5;
const int IN4 = 27;
const int ENA = 25;
const int ENB = 26;

// LED Pin
const int ledPin = 2;

// Servo Pin
const int servoPin = 14; // Change this to your actual servo pin
Servo myServo;

WebServer server(80);

void setup() {
  Serial.begin(115200);

  // Set LED pin as output
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW); // Start with LED off

  // Set motor pins as output
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  // Set motor speed (optional)
  analogWrite(ENA, 130);  // 200/255 = ~78% speed
  analogWrite(ENB, 130);

  // Attach servo
  myServo.attach(servoPin);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to Wi-Fi...");
  }

  // Turn on the LED after successful Wi-Fi connection
  digitalWrite(ledPin, HIGH);
  Serial.println("Connected to Wi-Fi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Handle root URL
  server.on("/", []() {
    server.send(200, "text/plain", "Hello from ESP32!");
  });

  // Handle /forward
  server.on("/forward", []() {
    moveForward();
    delay(3000);  // Move forward for 3 seconds
    stopMotors();
    server.send(200, "text/plain", "Moved Forward");
  });

  // Handle /backward
  server.on("/backward", []() {
    moveBackward();
    delay(3000);  // Move backward for 3 seconds
    stopMotors();
    server.send(200, "text/plain", "Moved Backward");
  });

  // Handle /left
  server.on("/left", []() {
    turnLeft();
    delay(3000);  // Turn left for 3 seconds
    stopMotors();
    server.send(200, "text/plain", "Turned Left");
  });

  // Handle /right
  server.on("/right", []() {
    turnRight();
    delay(3000);  // Turn right for 3 seconds
    stopMotors();
    server.send(200, "text/plain", "Turned Right");
  });

  // Start the server
  server.begin();

  // Initialize servo
  myServo.write(90); // Start at center position
}

void loop() {
  server.handleClient();

  // Rotate the servo (radar effect)
  rotateServo();
}

// Function to rotate the servo
void rotateServo() {
  for (int angle = 0; angle <= 180; angle += 1) {
    myServo.write(angle);
    delay(20); // Adjust delay for smoother rotation
  }

  for (int angle = 180; angle >= 0; angle -= 1) {
    myServo.write(angle);
    delay(20);
  }
}

// Motor functions
void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}