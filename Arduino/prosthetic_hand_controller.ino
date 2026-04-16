/*
 * ============================================================
 *  PROSTHETIC HAND CONTROLLER — Arduino Mega/Uno
 *  Real-time 5-servo control via serial hand tracking data
 *  Format received: "T,I,M,R,P\n"  (e.g. "1,0,1,1,0\n")
 *  1 = OPEN (0°), 0 = CLOSED (180°)  — inverted for physical servo orientation
 * ============================================================
 */

#include <Servo.h>

// ── Pin assignments ──────────────────────────────────────────
#define PIN_THUMB   3
#define PIN_INDEX   5
#define PIN_MIDDLE  6
#define PIN_RING    9
#define PIN_PINKY   10

// ── Servo angle targets ──────────────────────────────────────
#define ANGLE_OPEN     0    // inverted: open  = 0°
#define ANGLE_CLOSED 180    // inverted: closed = 180°

// ── Smooth motion settings ───────────────────────────────────
#define SMOOTH_STEP    4      // degrees per update tick
#define SMOOTH_INTERVAL 8     // ms between ticks (125 Hz inner loop)

// ── Serial ───────────────────────────────────────────────────
#define BAUD_RATE  115200
#define SERIAL_TIMEOUT 2      // ms — non-blocking read window

// ─────────────────────────────────────────────────────────────

Servo servos[5];
const uint8_t pins[5] = {
  PIN_THUMB, PIN_INDEX, PIN_MIDDLE, PIN_RING, PIN_PINKY
};

int currentAngle[5];   // live angle (for smooth sweep)
int targetAngle[5];    // desired angle from Python

char serialBuf[32];
uint8_t bufIdx = 0;
unsigned long lastSmoothTick = 0;

// ─────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(SERIAL_TIMEOUT);

  for (uint8_t i = 0; i < 5; i++) {
    servos[i].attach(pins[i]);
    currentAngle[i] = ANGLE_CLOSED;
    targetAngle[i]  = ANGLE_CLOSED;
    servos[i].write(ANGLE_CLOSED);
  }

  // Handshake — Python waits for this before sending data
  Serial.println("READY");
}

// ─────────────────────────────────────────────────────────────
void loop() {
  readSerial();
  smoothUpdate();
}

// ── Non-blocking serial reader ────────────────────────────────
void readSerial() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      serialBuf[bufIdx] = '\0';
      parseCommand(serialBuf);
      bufIdx = 0;
    } else if (c != '\r') {
      if (bufIdx < sizeof(serialBuf) - 1) {
        serialBuf[bufIdx++] = c;
      } else {
        // Overflow guard — discard corrupted frame
        bufIdx = 0;
      }
    }
  }
}

// ── Parse "1,0,1,1,0" into targetAngle[] ─────────────────────
void parseCommand(const char* cmd) {
  // Validate: must contain exactly 4 commas
  uint8_t commas = 0;
  for (uint8_t i = 0; cmd[i] != '\0'; i++) {
    if (cmd[i] == ',') commas++;
  }
  if (commas != 4) return;   // bad frame — ignore

  char tmp[32];
  strncpy(tmp, cmd, sizeof(tmp) - 1);
  tmp[sizeof(tmp) - 1] = '\0';

  char* token = strtok(tmp, ",");
  for (uint8_t i = 0; i < 5 && token != NULL; i++) {
    int val = atoi(token);
    targetAngle[i] = (val == 1) ? ANGLE_OPEN : ANGLE_CLOSED;
    token = strtok(NULL, ",");
  }
}

// ── Smooth easing toward target angles ───────────────────────
void smoothUpdate() {
  unsigned long now = millis();
  if (now - lastSmoothTick < SMOOTH_INTERVAL) return;
  lastSmoothTick = now;

  for (uint8_t i = 0; i < 5; i++) {
    int diff = targetAngle[i] - currentAngle[i];
    if (diff == 0) continue;

    // Move SMOOTH_STEP degrees toward target
    int step = (diff > 0) ? SMOOTH_STEP : -SMOOTH_STEP;
    if (abs(diff) <= SMOOTH_STEP) {
      currentAngle[i] = targetAngle[i];
    } else {
      currentAngle[i] += step;
    }
    servos[i].write(currentAngle[i]);
  }
}
