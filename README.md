# Hand Gesture Virtual Mouse (MediaPipe + OpenCV + PyAutoGUI)

This project lets you control your laptop cursor using **hand gestures via webcam**. It uses:

- **MediaPipe Tasks Hand Landmarker** for real-time hand landmark detection [web:21][web:29].
- **OpenCV** to read frames from the webcam and preprocess images [web:91][web:94].
- **PyAutoGUI** to move the OS mouse cursor and perform clicks programmatically [web:66][web:80].

The goal is to create a fast, gaming-style virtual mouse where your **index finger** moves the cursor and **thumb pinch** triggers clicks.

---

## Features

- Real-time cursor control using index fingertip.
- Ultra-fast horizontal movement (gaming style).
- Smooth but responsive vertical movement.
- Left-click via thumb–index pinch gesture.
- Easy to extend with right-click, drag, and scroll gestures.

---

## Workflow

The system follows a typical AI virtual mouse workflow used in MediaPipe-based projects [web:91][web:94][web:92]:

1. **Capture webcam frames**  
   - Use OpenCV’s `VideoCapture(0)` to stream frames from the laptop webcam.

2. **Preprocess frames**  
   - Flip horizontally (`cv2.flip`) so movement feels natural like a mirror.  
   - Convert BGR to RGB (`cv2.cvtColor`) for MediaPipe’s expected image format [web:94].

3. **Hand landmark detection (MediaPipe Tasks)**  
   - Load the `hand_landmarker.task` model using `BaseOptions(model_asset_buffer=...)`.  
   - Use `HandLandmarker.detect_for_video()` to get 21 hand landmarks per frame [web:21][web:29].  
   - Extract key points:
     - Index fingertip (landmark 8).
     - Thumb fingertip (landmark 4).
     - Index MCP (landmark 5).

4. **Map hand position to screen coordinates**  
   - Clamp the finger coordinates to the central region of the camera image.  
   - Use `np.interp` to map this region to full screen width/height.  
   - Apply **asymmetric smoothing**:
     - High responsiveness horizontally (`alpha_x` high).
     - Slight smoothing vertically (`alpha_y` lower) for stable control [web:10][web:72].

5. **Control mouse with PyAutoGUI**  
   - Call `pyautogui.moveTo(x, y)` to move the mouse instantly to the computed screen coordinates [web:66][web:82].  
   - Detect gestures by measuring distances between thumb and index fingertip:
     - If distance < threshold → perform mouse click via `pyautogui.click()` [web:73][web:94].

6. **Visual feedback & exit**  
   - Draw circles on the tracked finger points with OpenCV so you can see what the model detects.  
   - Display the webcam feed in a window titled “Hand Mouse”.  
   - Press `Esc` to exit cleanly.

---

## Requirements

Install dependencies:

```bash
pip install opencv-python mediapipe pyautogui numpy
```

Python 3.9+ is recommended. Make sure your webcam works with OpenCV on Windows.

---

## Getting the `hand_landmarker.task` model

You need the Hand Landmarker model file from the official MediaPipe docs:

- MediaPipe Hand Landmarker (Python guide):  
  https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker/python [web:29]

From there, download the **hand landmarker task model** and save it as:

```text
hand_landmarker.task
```

in the **same folder** as `hand_mouse.py`.

> Note: The model file can be large; many projects mention it in the README but don’t commit it to GitHub. You can instruct users to download it themselves [web:21][web:29].

---

## How to run

1. Clone this repository:

```bash
git clone https://github.com/<your-username>/hand-gesture-virtual-mouse.git
cd hand-gesture-virtual-mouse
```

2. Install dependencies:

```bash
pip install opencv-python mediapipe pyautogui numpy
```

3. Download `hand_landmarker.task` from the MediaPipe Hand Landmarker Python guide and place it in the project folder.

4. Run the script:

```bash
python hand_mouse.py
```

The webcam window will open, and the cursor will start following your index finger.

---

## Gestures

- **Move cursor**: Point with your index finger and move your hand.  
- **Left click**: Pinch thumb and index fingertip together briefly.  
- **Exit**: Press `Esc`.

You can easily extend this:
- Right click: Thumb + middle fingertip pinch.  
- Drag: Hold pinch for > 0.5s then move.  
- Scroll: Index + middle together, move hand up/down [web:6][web:73][web:79].

---

## Code overview

- `VideoCapture` loop: reads frames, flips, and converts to RGB.  
- `HandLandmarker`: finds hand landmarks and returns normalized coordinates for each finger joint [web:21][web:29].  
- `np.interp`: maps local camera coordinates to global screen coordinates (sensitivity control).  
- Asymmetric smoothing:
  - `alpha_x` high → faster horizontal movement.
  - `alpha_y` lower → smoother vertical control.

The result is a fast, intuitive virtual mouse controlled entirely by hand gestures.


```text
MIT License
Copyright (c) 2026 Aryan Bhalsing
```
