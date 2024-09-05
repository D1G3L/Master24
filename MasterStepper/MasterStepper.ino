#define DIR_PIN     4
#define STEP_PIN    5

volatile bool stopMotor = false;  
int setupDelays[200];

void setup() {
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);
}

void move(int steps, int MODE, int startSpeed, int maxSpeed) {
  int delays[steps];
  float angle = 1;
  float accel = 0.01;
  float c0 = startSpeed * sqrt(2 * angle / accel) * 0.67703;
  float lastDelay = 0;
  int highSpeed = maxSpeed;

  for (int i = 0; i < steps; i++) {
    float d = c0;
    if (i > 0) {
      d = lastDelay - (2 * lastDelay) / (4 * i + 1);
    }
    if (d < highSpeed) {
      d = highSpeed;
    }
    delays[i] = d;
    lastDelay = d;
  }

  digitalWrite(DIR_PIN, MODE);

  for (int i = 0; i < steps; i++) {
    checkForStopCommand();
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(delays[i]);
    digitalWrite(STEP_PIN, LOW);
  }

  for (int i = 0; i < steps; i++) {
    checkForStopCommand();
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(delays[steps-i-1]);
    digitalWrite(STEP_PIN, LOW);
  }
}

void moveWithAccelOnly(int steps, int MODE, int startSpeed, int maxSpeed) {
  float angle = 1;
  float accel = 0.01;
  float c0 = startSpeed * sqrt(2 * angle / accel) * 0.67703;
  float lastDelay = 0;
  int highSpeed = maxSpeed;

  for (int i = 0; i < steps; i++) {
    float d = c0;
    if (i > 0) {
      d = lastDelay - (2 * lastDelay) / (4 * i + 1);
    }
    if (d < highSpeed) {
      d = highSpeed;
    }
    setupDelays[i] = d;
    lastDelay = d;
  }

  digitalWrite(DIR_PIN, MODE);

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(setupDelays[i]);
    digitalWrite(STEP_PIN, LOW);
  }
}

void moveWithConstantSpeed(int steps, int MODE, int speed) {
  int delayTime = 3990000 / speed; 

  digitalWrite(DIR_PIN, MODE);

  for (int i = 0; i < steps; i++) {
    checkForStopCommand();
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(delayTime);
    digitalWrite(STEP_PIN, LOW);
  }
}

void moveWithDecelOnly(int steps, int MODE, int startSpeed, int maxSpeed) {
  int delayTime = 4000000 / maxSpeed;

  digitalWrite(DIR_PIN, MODE);

  for (int i = 0; i < steps/2; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(delayTime);
    digitalWrite(STEP_PIN, LOW);
  }

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(setupDelays[steps-i-1]);
    digitalWrite(STEP_PIN, LOW);
  }
}

void checkForStopCommand() {
  if (Serial.available() > 0) {
    int command = Serial.read();
    if (command == 'b') {
      stopMotor = true;
    }
  }
}

void loop() {
  if (Serial.available() > 0) {
    char mode = Serial.read();
    
    switch (mode) {
      //rotation clockwise
      case 'q':
        moveWithAccelOnly(200, LOW, 4000, 2000);
        while(!stopMotor) {
          moveWithConstantSpeed(25, LOW, 2000);
        }
        moveWithDecelOnly(200, LOW, 4000, 2000);
        break;
      //rotation counterclockwise
      case 'w':
        moveWithAccelOnly(200, HIGH, 4000, 2000);
        while(!stopMotor) {
          moveWithConstantSpeed(25, HIGH, 2000);
        }
        moveWithDecelOnly(200, HIGH, 4000, 2000);
        break;
      //small steps clockwise
      case 'a':
        while(!stopMotor) {
          move(5, LOW, 4000, 4000);
          delay(250);
        }
        break;
      //small steps counterclockwise
      case 's':
        while(!stopMotor) {
          move(5, HIGH, 4000, 4000);
          delay(250);
        }
        break;
      //swing clockwise
      case 'y':
        while(!stopMotor) {
          move(32, LOW, 3500, 2000);
          delay(250);
        }
        break;
      //swing counterclockwise
      case 'x':
        while(!stopMotor) {
          move(32, HIGH, 3500, 2000);
          delay(250);
        }
        break;
      default:
        Serial.println("Invalid mode selected.");
        break;
    }
    stopMotor = false;
  }
}
