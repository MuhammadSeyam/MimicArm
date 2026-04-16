"""
=============================================================
  PROSTHETIC HAND — Python Controller
  Pipeline: Webcam → MediaPipe → Finger States → Serial → Arduino
  Run:  python prosthetic_hand.py
  Deps: pip install opencv-python mediapipe pyserial
=============================================================
"""

import cv2
import mediapipe as mp
import serial
import serial.tools.list_ports
import time
import sys

# ── CONFIG ────────────────────────────────────────────────────
SERIAL_PORT   = "COM3"      # ← Change to your Arduino port
BAUD_RATE     = 115200
CAMERA_INDEX  = 0
FRAME_W, FRAME_H = 1280, 720
TARGET_FPS    = 30
SEND_COOLDOWN = 0.04        # min seconds between serial writes (~25Hz cap)
# ─────────────────────────────────────────────────────────────


# ── Auto-detect Arduino port ──────────────────────────────────
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        desc = (p.description or "").lower()
        if any(kw in desc for kw in ["arduino", "ch340", "cp210", "ftdi", "usb serial"]):
            print(f"[Serial] Auto-detected: {p.device} — {p.description}")
            return p.device
    return None


# ── MediaPipe hand setup ──────────────────────────────────────
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_styles  = mp.solutions.drawing_styles

hands_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.60,
)

# Landmark indices
WRIST      = 0
THUMB_TIP  = 4;  THUMB_IP   = 3
INDEX_TIP  = 8;  INDEX_PIP  = 6
MIDDLE_TIP = 12; MIDDLE_PIP = 10
RING_TIP   = 16; RING_PIP   = 14
PINKY_TIP  = 20; PINKY_PIP  = 18


def get_finger_states(lm, handedness_label):
    """
    Returns [thumb, index, middle, ring, pinky] — 1=open, 0=closed
    Works correctly for both Left and Right hand.
    """
    states = [0] * 5

    # ── Thumb: compare x-position of tip vs IP joint (mirrored for each hand)
    if handedness_label == "Right":
        states[0] = 1 if lm[THUMB_TIP].x < lm[THUMB_IP].x else 0
    else:
        states[0] = 1 if lm[THUMB_TIP].x > lm[THUMB_IP].x else 0

    # ── Four fingers: tip y above PIP y = extended (open)
    for tip, pip, idx in [
        (INDEX_TIP,  INDEX_PIP,  1),
        (MIDDLE_TIP, MIDDLE_PIP, 2),
        (RING_TIP,   RING_PIP,   3),
        (PINKY_TIP,  PINKY_PIP,  4),
    ]:
        states[idx] = 1 if lm[tip].y < lm[pip].y else 0

    return states


def draw_overlay(frame, states, fps, port_name, connected):
    """Draws HUD overlay on the camera frame."""
    labels   = ["THUMB", "INDEX", "MIDDLE", "RING", "PINKY"]
    colors   = {1: (0, 230, 100), 0: (0, 60, 220)}
    bar_x    = 30
    bar_y    = 80
    bar_h    = 36
    bar_gap  = 12
    bar_maxw = 180

    # Background panel
    cv2.rectangle(frame, (15, 20), (260, 280), (10, 10, 10), -1)
    cv2.rectangle(frame, (15, 20), (260, 280), (60, 60, 60), 1)

    # Title
    cv2.putText(frame, "PROSTHETIC CTRL", (22, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

    for i, (label, state) in enumerate(zip(labels, states)):
        y    = bar_y + i * (bar_h + bar_gap)
        col  = colors[state]
        text = f"{label}: {'OPEN' if state else 'CLOSED'}"
        w    = bar_maxw if state else bar_maxw // 2

        cv2.rectangle(frame, (bar_x, y), (bar_x + w, y + bar_h - 2), col, -1)
        cv2.putText(frame, text, (bar_x + 6, y + bar_h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    # FPS + port
    cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 130, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)
    status_col = (0, 230, 100) if connected else (0, 80, 230)
    status_txt = f"Serial: {port_name}" if connected else "Serial: DISCONNECTED"
    cv2.putText(frame, status_txt, (frame.shape[1] - 280, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, status_col, 1)

    return frame


# ── Serial connection ─────────────────────────────────────────
def connect_serial():
    port = find_arduino_port() or SERIAL_PORT
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2.0)  # wait for Arduino reset
        # Wait for READY handshake (up to 5 s)
        deadline = time.time() + 5
        while time.time() < deadline:
            if ser.in_waiting:
                line = ser.readline().decode(errors="ignore").strip()
                if line == "READY":
                    print(f"[Serial] Arduino ready on {port}")
                    break
        else:
            print("[Serial] Warning: no READY signal — continuing anyway")
        ser.reset_input_buffer()
        return ser, port, True
    except serial.SerialException as e:
        print(f"[Serial] FAILED: {e}")
        print("[Serial] Running in CAMERA-ONLY mode (no serial output)")
        return None, port, False


# ── MAIN ──────────────────────────────────────────────────────
def main():
    ser, port_name, ser_ok = connect_serial()

    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    cap.set(cv2.CAP_PROP_FPS,          TARGET_FPS)
    cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)  # minimize latency

    if not cap.isOpened():
        print("[Camera] ERROR: Could not open webcam.")
        sys.exit(1)

    prev_states   = [-1, -1, -1, -1, -1]
    last_send_ts  = 0.0
    fps_timer     = time.time()
    frame_count   = 0
    fps_display   = 0.0

    print("[System] Running — press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Camera] Frame read failed — retrying...")
            time.sleep(0.01)
            continue

        frame = cv2.flip(frame, 1)  # mirror so it feels natural
        rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # ── MediaPipe inference ──────────────────────────────
        rgb.flags.writeable = False
        result = hands_detector.process(rgb)
        rgb.flags.writeable = True

        states = [0, 0, 0, 0, 0]

        if result.multi_hand_landmarks:
            hand_lm    = result.multi_hand_landmarks[0]
            handedness = result.multi_handedness[0].classification[0].label

            # Draw skeleton
            mp_drawing.draw_landmarks(
                frame, hand_lm, mp_hands.HAND_CONNECTIONS,
                mp_styles.get_default_hand_landmarks_style(),
                mp_styles.get_default_hand_connections_style(),
            )

            lm     = hand_lm.landmark
            states = get_finger_states(lm, handedness)

        # ── Serial: send only on state change + cooldown ─────
        now = time.time()
        if states != prev_states and (now - last_send_ts) >= SEND_COOLDOWN:
            payload = ",".join(str(s) for s in states) + "\n"
            if ser_ok and ser:
                try:
                    ser.write(payload.encode())
                    ser.flush()
                except serial.SerialException as e:
                    print(f"[Serial] Write error: {e}")
                    ser_ok = False
            prev_states  = states[:]
            last_send_ts = now
            print(f"[Send] {payload.strip()}  — T:{states[0]} I:{states[1]} M:{states[2]} R:{states[3]} P:{states[4]}")

        # ── FPS calculation ───────────────────────────────────
        frame_count += 1
        elapsed = time.time() - fps_timer
        if elapsed >= 0.5:
            fps_display  = frame_count / elapsed
            frame_count  = 0
            fps_timer    = time.time()

        # ── HUD overlay ───────────────────────────────────────
        frame = draw_overlay(frame, states, fps_display, port_name, ser_ok)
        cv2.imshow("Prosthetic Hand Controller", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # ── Cleanup ───────────────────────────────────────────────
    print("[System] Shutting down...")
    if ser_ok and ser:
        ser.write(b"0,0,0,0,0\n")  # close all fingers on exit
        ser.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
