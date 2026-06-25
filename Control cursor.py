import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

pyautogui.FAILSAFE = False

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "hand_landmarker.task"

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Missing model file: {MODEL_PATH}\n"
        f"Put hand_landmarker.task in this folder: {BASE_DIR}"
    )

with open(MODEL_PATH, "rb") as f:
    model_data = f.read()

base_options = python.BaseOptions(model_asset_buffer=model_data)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7,
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

last_click_time = 0
click_cooldown = 0.18  # very responsive clicks

# ULTRA-FAST SETTINGS
alpha_x = 0.7   # horizontal: very responsive (gaming-style)
alpha_y = 0.4   # vertical: smoother, less twitchy
prev_x = None
prev_y = None

def dist(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int(time.time() * 1000)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    if result.hand_landmarks:
        hand = result.hand_landmarks[0]

        index_tip = hand[8]
        thumb_tip = hand[4]
        index_mcp = hand[5]

        x = int(index_tip.x * w)
        y = int(index_tip.y * h)

        # Smaller margins = more sensitivity, especially horizontally
        margin_x = int(w * 0.15)   # horizontal active area = 70% of frame
        margin_y = int(h * 0.25)   # vertical active area = 50% of frame

        x_clamped = max(margin_x, min(w - margin_x, x))
        y_clamped = max(margin_y, min(h - margin_y, y))

        # Map camera to full screen (high sensitivity)
        target_x = np.interp(
            x_clamped,
            (margin_x, w - margin_x),
            (0, screen_w)
        )
        target_y = np.interp(
            y_clamped,
            (margin_y, h - margin_y),
            (0, screen_h)
        )

        # Asymmetric smoothing: fast horizontal, smoother vertical
        if prev_x is None:
            curr_x, curr_y = target_x, target_y
        else:
            curr_x = alpha_x * target_x + (1 - alpha_x) * prev_x
            curr_y = alpha_y * target_y + (1 - alpha_y) * prev_y

        pyautogui.moveTo(curr_x, curr_y)
        prev_x, prev_y = curr_x, curr_y

        thumb = (int(thumb_tip.x * w), int(thumb_tip.y * h))
        index = (int(index_tip.x * w), int(index_tip.y * h))

        if dist(thumb, index) < 35 and time.time() - last_click_time > click_cooldown:
            pyautogui.click()
            last_click_time = time.time()

        cv2.circle(frame, (x, y), 10, (0, 255, 255), cv2.FILLED)
        cv2.circle(frame, thumb, 10, (255, 0, 0), cv2.FILLED)
        cv2.putText(frame, "Gaming mode: fast X, smooth Y", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "No hand", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Hand Mouse", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
detector.close()