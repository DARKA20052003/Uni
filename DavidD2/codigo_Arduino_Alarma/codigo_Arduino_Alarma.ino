#include <Servo.h>

// Pines
const int ledPin = 2;
const int buzzerPin = 4;
const int servoPin = 3;

Servo miServo;

bool alarmaActiva = false;
unsigned long buzzerStartTime = 0;
bool buzzerActivo = false;

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  miServo.attach(servoPin);
  miServo.write(0);  // Posición inicial
}

void loop() {
  // Lectura del puerto serial
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '1') {
      alarmaActiva = true;
      buzzerActivo = true;
      buzzerStartTime = millis();
      miServo.write(180);  // Girar motor
      Serial.println("Alarma activada");
    } 
    else if (comando == '0') {
      alarmaActiva = false;
      buzzerActivo = false;
      digitalWrite(buzzerPin, LOW);
      digitalWrite(ledPin, LOW);
      miServo.write(0);  // Regresar motor
      Serial.println("Alarma cancelada");
    }
  }

  // Parpadeo LED si la alarma está activa
  if (alarmaActiva) {
    static unsigned long previousMillis = 0;
    unsigned long currentMillis = millis();
    static bool ledState = false;

    if (currentMillis - previousMillis >= 500) {  // Cada 0.5 segundos
      previousMillis = currentMillis;
      ledState = !ledState;
      digitalWrite(ledPin, ledState);
    }
  }

  // Activar buzzer por 5 segundos solo una vez
  if (buzzerActivo) {
    digitalWrite(buzzerPin, HIGH);
    if (millis() - buzzerStartTime >= 5000) {
      digitalWrite(buzzerPin, LOW);
      buzzerActivo = false;
    }
  }
}
