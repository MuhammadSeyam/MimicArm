#  Prosthetic Robot Hand (Computer Vision Controlled)

##  Overview

This project demonstrates a **robotic prosthetic hand** controlled using **computer vision**.
A webcam tracks the user’s hand in real-time and sends commands to an Arduino to control servo motors.

---

##  Objective

Build a **real-time human-robot interaction system** where hand gestures control a robotic hand.

---

##  System Architecture

```text
User Hand → Camera → Python (Computer Vision) → Arduino → Servo Motors → Prosthetic Hand
```

---

##  System Pipeline

![System Pipeline](https://upload.wikimedia.org/wikipedia/commons/3/3f/Computer_vision_pipeline.png)

---

##  Hand Tracking (Computer Vision)

![Hand Tracking](https://upload.wikimedia.org/wikipedia/commons/1/1f/Hand_tracking_example.jpg)

---

##  Prosthetic Hand Example

![Prosthetic Hand](https://upload.wikimedia.org/wikipedia/commons/5/5e/Prosthetic_hand.jpg)

---

##  Arduino + Servo Motors

![Arduino Setup](https://upload.wikimedia.org/wikipedia/commons/3/38/Arduino_Uno_-_R3.jpg)

---

##  Components

###  Hardware

* Arduino Uno
* Servo Motors
* 3D Printed Prosthetic Hand
* Jumper Wires
* Power Supply

###  Software

* Python
* OpenCV
* cvzone
* MediaPipe

---

##  Implementation Steps

###  Hardware Testing

* Test servo motors using Arduino
* Ensure all fingers move correctly

---

###  Serial Communication

* Connect Python with Arduino
* Send simple commands (0 / 1)

---

###  Computer Vision

* Detect hand using webcam
* Extract finger positions
* Send commands to Arduino

---

##  Control Logic

| Gesture       | Action      |
| ------------- | ----------- |
| Hand Open ✋   | Hand Opens  |
| Hand Closed ✊ | Hand Closes |

---

##  How It Works

1. Camera captures hand
2. Computer vision detects fingers
3. Data sent to Arduino
4. Arduino controls motors
5. Hand moves accordingly

---

##  Challenges

* Lighting conditions
* Detection accuracy
* Servo calibration

---

##  Future Improvements

* Control each finger separately
* Add gesture recognition
* Wireless control

---

##  Requirements

```bash
pip install opencv-python cvzone mediapipe pyserial
```

---

##  Run

```bash
python main.py
```

---

##  Conclusion

A simple and practical project demonstrating **real-time human-robot interaction using computer vision**.

---

## License

Educational use only.
