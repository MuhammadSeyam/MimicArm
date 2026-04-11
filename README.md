
# Prosthetic Robot Hand (Computer Vision Controlled)

## Overview
This project is a computer vision-based system that detects hand gestures using a webcam and controls a 3D-printed prosthetic hand through an Arduino microcontroller and servo motors. The system enables real-time human-robot interaction by translating hand movements into mechanical actions.

---

## Objective
The objective of this project is to develop a simple and functional human-robot interaction system where hand gestures are used to control a robotic prosthetic hand in real time.

---

## System Architecture
The system follows this pipeline:

User Hand → Webcam → Python (Computer Vision) → Serial Communication → Arduino → Servo Motors → Prosthetic Hand

---

## Components

### Hardware
- Arduino Uno
- Servo motors
- 3D-printed prosthetic hand
- Jumper wires
- Power supply

### Software
- Python
- OpenCV
- cvzone
- MediaPipe
- Arduino IDE

---

## Implementation Steps

### 1. Hardware Setup
The servo motors are connected to the Arduino board and attached to the fingers of the prosthetic hand. Each servo is responsible for controlling one finger movement.

### 2. Arduino Control
The Arduino receives serial data from the Python application and maps the received values to servo motor positions.

### 3. Computer Vision
A webcam captures the user's hand in real time. The system detects hand landmarks and determines which fingers are open or closed.

### 4. Communication
Python sends binary values representing finger states to the Arduino using serial communication.

---

## Control Logic
The system uses a simple mapping between detected gestures and hand movement:

- Open hand gesture: prosthetic hand opens
- Closed hand gesture: prosthetic hand closes

More advanced versions can map individual finger movements.

---

## How It Works
1. The camera captures live video of the user’s hand
2. The computer vision model detects hand landmarks
3. Finger positions are analyzed
4. Data is converted into a binary format
5. Data is sent to Arduino via serial communication
6. Arduino controls servo motors based on received data

---

## Challenges
- Variations in lighting conditions
- Accuracy of hand detection
- Servo calibration and synchronization
- Real-time communication stability

---

## Future Improvements
- Independent control of each finger
- Improved gesture recognition accuracy
- Wireless communication (Bluetooth or WiFi)
- Integration with machine learning models for advanced gestures

---

## Requirements
Install the required Python libraries:

```bash
pip install opencv-python cvzone mediapipe pyserial
````

---

## Running the Project

Run the Python application:

```bash
python main.py
```

Ensure the Arduino is connected and the correct COM port is selected.

---

## Conclusion

This project demonstrates a basic implementation of a human-robot interaction system using computer vision and embedded systems. It provides a foundation for more advanced prosthetic control systems and gesture-based robotic applications.


