int dist = 10;

// define servo objects, pins and buttons
#include <Servo.h>
Servo myservo1;
Servo myservo2;
const int pin1 = 2;
const int pin2 = 3;
const int pin3 = 4;
const int pin4 = 5;

#define servoPin1 13
#define servoPin2 12
#define echoPin 9 // attach pin D2 Arduino to pin Echo of HC-SR04
#define trigPin 10 //attach pin D3 Arduino to pin Trig of HC-SR04
long duration; // variable for the duration of sound wave travel
int distance; // variable for the distance measurement
int trash;

int buttonState1 = 0;         // variable for reading the pushbutton status
int buttonState2 = 0;
int buttonState3 = 0;
int buttonState4 = 0;

void setup() {
  myservo1.attach(servoPin1);
  myservo2.attach(servoPin2);
  pinMode(pin1, INPUT);
  pinMode(pin2, INPUT);
  pinMode(pin3, INPUT);
  pinMode(pin4, INPUT);

  pinMode(trigPin, OUTPUT); // Sets the trigPin as an OUTPUT
  pinMode(echoPin, INPUT); // Sets the echoPin as an INPUT
  Serial.begin(57600);

  myservo2.write(100);
  //myservo1.write(0);
  //myservo2.write(0);
  
}

// 1 -> glass , 2 -> metal , 3-> paper , 4 -> plastic

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  int laage = 0;

  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2; // Speed of sound wave divided by 2 (go and back)
  // Displays the distance on the Serial Monitor

  // if trash has been detected send message to python
  if (distance < 20) {
    Serial.print("8");
    trash = 1;
    delay(500);
  }

  // read incoming message from python
  if (Serial.available() > 0) {
    int k = Serial.read();
    k = k - 48;
  // Used for testing. k == 6 is only possible via serial monitor.
    if (k == 6) {
      myservo1.write(90);
      delay(1000);
      myservo1.write(180);
      delay(1000);
      myservo1.write(0);
      delay(1000);
      myservo1.write(90);
    }
    // Sort as glass
    if (k == 1) {
      myservo1.write(0);
      trash = 0;
      laage = 1;
    }
    // Sort as metal
    if (k == 2) {
      myservo1.write(50);
      trash = 0;
      laage = 1;
    }
    // Sort as paper
    if (k == 3) {
      myservo1.write(100);
      trash = 0;
      laage = 1;
    }
    // Sort as plastic
    if (k == 4) {
      myservo1.write(150);
      trash = 0;
      laage = 1;
    }
  }

  // Read button states. If states are active and trash has been detected, send label to python and sort trash.
  else if (digitalRead(pin1) == HIGH && trash == 1) {
    // Send label to python
    Serial.print("1");
    // Delay so python can take pictures
    delay(3000);
    // Sort the trash
    myservo1.write(0);
    trash = 0;
    laage = 1;
  }
  else if (digitalRead(pin2) == HIGH && trash == 1) {
    Serial.print("2");
    delay(3000);
    myservo1.write(50);
    trash = 0;
    laage = 1;
  }
  else if (digitalRead(pin3 ) == HIGH && trash == 1) {
    Serial.print("3");
    delay(3000);
    myservo1.write(100);
    trash = 0;
    laage = 1;
  }
  else if (digitalRead(pin4) == HIGH && trash == 1) {
    Serial.print("4");
    delay(3000);
    myservo1.write(150);
    trash = 0;
    laage = 1;
  }

  if (laage == 1) {
    delay(1500);
    myservo2.write(10);
    delay(2000);
    myservo2.write(100);
  }
}
