import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import ctypes
import math
import numpy as np
import time
import os

# Disable PyAutoGUI default delay
pyautogui.PAUSE = 0

# --- EASY SETTINGS (Medium / Physical Mouse Feel) ---
BOX_W = 340       # Medium horizontal speed (was 200)
BOX_H = 190       # Medium vertical speed (was 110)
SMOOTHING = 6.0   # Smooth, steady weight like a real mouse (was 3.5)
DEADZONE = 5      # Keeps cursor rock-solid when stopping to click
# ----------------------------------------------------

# Make Windows DPI-aware so multi-monitor coordinates are exact
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()

# Get full virtual desktop bounds across ALL extended monitors
virt_x = user32.GetSystemMetrics(76)  # Leftmost X (can be negative)
virt_y = user32.GetSystemMetrics(77)  # Topmost Y
virt_w = user32.GetSystemMetrics(78)  # Combined width of all screens
virt_h = user32.GetSystemMetrics(79)  # Combined height of all screens

# Hand skeleton connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (0, 17)                                # Palm base
]

# Initialize MediaPipe HandLandmarker
base_options = python.BaseOptions(model_asset_path="hand_landmarker.task")
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
detector = vision.HandLandmarker.create_from_options(options)

# Lock camera to 640x480 for fast, lag-free FPS
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Start cursor tracking from center of virtual desktop
ploc_x = virt_x + virt_w / 2
ploc_y = virt_y + virt_h / 2

# Cooldown trackers
last_click_time = 0
last_screenshot_time = 0
last_play_pause_time = 0
last_reel_time = 0
last_scroll_time = 0

# Screenshot directory
screenshot_path = "C:/Users/Admin/Desktop/Virtual"
os.makedirs(screenshot_path, exist_ok=True)


def get_fingers_up(lm):
    """Returns [Index, Middle, Ring, Pinky] as 1 (up) or 0 (down)."""
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    return [1 if lm[tip][1] < lm[pip][1] else 0 for tip, pip in zip(tips, pips)]


while cap.isOpened():
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=imgRGB)

    # Centered compact control box (keeps your hand relaxed)
    x_min = (w - BOX_W) // 2
    x_max = (w + BOX_W) // 2
    y_min = (h - BOX_H) // 2
    y_max = (h + BOX_H) // 2
    cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (255, 0, 255), 2)

    results = detector.detect(mp_image)
    status_text = "No Hand"

    if results.hand_landmarks:
        for handLms in results.hand_landmarks:
            landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in handLms]

            # Draw skeleton and landmark dots
            for start_idx, end_idx in HAND_CONNECTIONS:
                cv2.line(img, landmarks[start_idx], landmarks[end_idx], (255, 255, 255), 2)
            for cx, cy in landmarks:
                cv2.circle(img, (cx, cy), 4, (0, 0, 255), -1)

            fingers = get_fingers_up(landmarks)
            now = time.time()

            # Fingertip coordinates
            x4, y4 = landmarks[4]    # Thumb
            x8, y8 = landmarks[8]    # Index
            x12, y12 = landmarks[12] # Middle
            x16, y16 = landmarks[16] # Ring
            x20, y20 = landmarks[20] # Pinky

            # Pinch distances
            dist_screenshot = math.hypot(x8 - x4, y8 - y4)
            dist_click = math.hypot(x12 - x4, y12 - y4)
            dist_next_reel = math.hypot(x16 - x4, y16 - y4)
            dist_prev_reel = math.hypot(x20 - x4, y20 - y4)

            # 1. Play / Pause: Closed Fist
            if fingers == [0, 0, 0, 0]:
                status_text = "Fist: Play / Pause"
                if now - last_play_pause_time > 1.5:
                    pyautogui.press("space")
                    last_play_pause_time = now

            # 2. Smooth Scroll Up: Index + Middle Up
            elif fingers == [1, 1, 0, 0]:
                status_text = "Scrolling Up"
                if now - last_scroll_time > 0.04:
                    pyautogui.scroll(80)
                    last_scroll_time = now

            # 3. Smooth Scroll Down: Index + Middle + Ring Up
            elif fingers == [1, 1, 1, 0]:
                status_text = "Scrolling Down"
                if now - last_scroll_time > 0.04:
                    pyautogui.scroll(-80)
                    last_scroll_time = now

            # 4. Ultra-Smooth Dual-Screen Cursor: Only Index Up
            elif fingers == [1, 0, 0, 0]:
                status_text = "Moving Cursor"
                # Map small purple box to ALL extended monitors
                target_x = np.interp(x8, (x_min, x_max), (virt_x, virt_x + virt_w))
                target_y = np.interp(y8, (y_min, y_max), (virt_y, virt_y + virt_h))

                # Smooth interpolation
                cloc_x = ploc_x + (target_x - ploc_x) / SMOOTHING
                cloc_y = ploc_y + (target_y - ploc_y) / SMOOTHING

                # Only move if beyond deadzone (prevents jitter)
                if math.hypot(cloc_x - ploc_x, cloc_y - ploc_y) > DEADZONE:
                    user32.SetCursorPos(int(cloc_x), int(cloc_y))
                    ploc_x, ploc_y = cloc_x, cloc_y

            # 5. Left Click: Thumb + Middle Pinch
            if dist_click < 35 and (now - last_click_time > 0.5):
                status_text = "Left Click"
                pyautogui.click()
                last_click_time = now

            # 6. Next Reel / Short: Thumb + Ring Pinch
            elif dist_next_reel < 35 and (now - last_reel_time > 1.0):
                status_text = "Next Reel"
                pyautogui.press("down")
                last_reel_time = now

            # 7. Previous Reel / Short: Thumb + Pinky Pinch
            elif dist_prev_reel < 35 and (now - last_reel_time > 1.0):
                status_text = "Previous Reel"
                pyautogui.press("up")
                last_reel_time = now

            # 8. Screenshot: Thumb + Index Pinch
            elif dist_screenshot < 30 and (now - last_screenshot_time > 2.0):
                status_text = "Screenshot!"
                pyautogui.screenshot(f"{screenshot_path}/screenshot_{int(now)}.png")
                last_screenshot_time = now

    cv2.putText(img, status_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    cv2.imshow("Gesture Control Virtual Mouse", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()