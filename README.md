# 🖐️ Gesture-Controlled Virtual Mouse

**Dual-Monitor & Media Edition**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-HandLandmarker-orange.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A fast, ergonomic, and lag-free virtual mouse powered by your webcam. Control your Windows PC hands-free: move your cursor smoothly across dual extended monitors, click, scroll web pages, navigate Instagram Reels & YouTube Shorts, pause/play media, and capture instant screenshots using simple hand gestures.

Built with **Python**, **OpenCV**, **PyAutoGUI**, the **Windows native Win32 API (ctypes)**, and the modern **MediaPipe Tasks API (HandLandmarker)**.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [How It Works](#-how-it-works-under-the-hood)
- [Prerequisites](#-prerequisites)
- [Installation](#️-step-by-step-installation)
- [Gesture Controls Guide](#-complete-gesture-controls-guide)
- [Usage Tips](#-smart-usage--ergonomic-tips)
- [Customization](#️-customization--sensitivity-tuning)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)
- [License](#-license)

---

## ✨ Key Features

- 🖥️ **Automatic dual-monitor support** – Uses Windows `GetSystemMetrics` with DPI awareness to detect your full extended desktop (left, right, or multi-screen) automatically.
- ⚡ **Zero-lag native cursor movement** – Uses native Windows `SetCursorPos` instead of slower wrapper calls, paired with a locked 640×480 camera feed for high FPS.
- 🧠 **Anti-shake & physical mouse feel** – Combines exponential smoothing (`SMOOTHING`) with a pixel `DEADZONE`, so the cursor glides like a real mouse and stays rock-solid when you stop to click.
- 🛋️ **Ergonomic active control box** – Maps a compact purple box in the center of your webcam frame to your entire screen, so you can rest your elbow on your desk and control both monitors with tiny wrist movements.
- 📱 **Reels & Shorts navigation** – Jump to the next or previous Reel/Short without touching your keyboard.
- ⏯️ **Media play / pause** – Pause or resume videos instantly with a closed fist.
- 📜 **Smooth page scrolling** – Scroll up and down articles, code, or feeds.
- 📸 **Instant screenshots** – Capture and auto-save timestamped PNG screenshots to a dedicated folder.

---

<img width="1600" height="893" alt="demo" src="https://github.com/user-attachments/assets/f2aa1108-3025-4e02-8f3e-d26918d59dd9" />


## 🔬 How It Works (Under the Hood)

1. **Hand landmark detection (MediaPipe Tasks API)** – Unlike older tutorials that rely on the deprecated `mp.solutions.hands` API (removed in MediaPipe 0.10.30+), this project uses the modern `mediapipe.tasks.python.vision.HandLandmarker` model (`hand_landmarker.task`). It tracks 21 3D landmarks on your hand in real time.
2. **Finger state recognition** – The script checks whether your Index (8), Middle (12), Ring (16), and Pinky (20) fingertips are positioned above their middle joints (PIPs: 6, 10, 14, 18) to determine which fingers are raised.
3. **Pinch distance math** – The Euclidean distance (`math.hypot`) is calculated between your Thumb Tip (4) and each of the other four fingertips to detect precise pinches, with built-in cooldown timers to prevent accidental spam.
4. **Coordinate mapping & smoothing** – Your Index fingertip coordinates inside the centered purple control box are interpolated (`numpy.interp`) onto your full virtual desktop dimensions (`virt_x`, `virt_y`, `virt_w`, `virt_h`), then smoothed before moving the OS cursor.

---

## 📋 Prerequisites

| Requirement | Details |
|---|---|
| **Operating system** | Windows 10 / 11 (uses `ctypes.windll.user32` for multi-monitor cursor control) |
| **Python** | 3.9 or higher (compatible with Python 3.12 & 3.13+) |
| **Hardware** | Any standard built-in or USB webcam |

---

## 🛠️ Step-by-Step Installation

### 1. Clone the repository

```powershell
git clone https://github.com/<your-username>/Gesture-Controlled-Virtual-Mouse.git
cd Gesture-Controlled-Virtual-Mouse
```

### 2. Create & activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

You should see `(.venv)` appear at the start of your terminal prompt.

### 3. Install the required libraries

```powershell
pip install opencv-python mediapipe pyautogui numpy
```

### 4. Download the MediaPipe Hand Landmarker model

Run this command in PowerShell to download the required AI model file (`hand_landmarker.task`) directly into your project folder:

```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "hand_landmarker.task"
```

### 5. Run the virtual mouse

```powershell
python virtual_mouse.py
```

A webcam window titled **Gesture Control Virtual Mouse** will open, showing your live hand skeleton, the active purple control box, and your current gesture status in the top-left corner.

**To exit:** press the `q` key while the camera window is focused.

---

## ✋ Complete Gesture Controls Guide

Hold one hand up with your palm facing the webcam. The camera feed is mirrored, so moving your hand left, right, up, or down moves the cursor in the exact same direction.

| Feature | Hand gesture | Action triggered | Cooldown |
|---|---|---|---|
| **Move cursor** | Only Index finger up | Smoothly moves the cursor across screens | Real-time |
| **Left click (tap)** | Pinch Thumb + Middle | Performs a left mouse click | 0.5 s |
| **Scroll up** | 2 fingers up (Index + Middle) | Smoothly scrolls the page up | 0.04 s |
| **Scroll down** | 3 fingers up (Index + Middle + Ring) | Smoothly scrolls the page down | 0.04 s |
| **Next Reel / Short** | Pinch Thumb + Ring | Presses the Down Arrow key | 1.0 s |
| **Previous Reel / Short** | Pinch Thumb + Pinky | Presses the Up Arrow key | 1.0 s |
| **Play / Pause** | Closed fist (all 4 fingers down) | Presses the Spacebar | 1.5 s |
| **Take screenshot** | Pinch Thumb + Index ("OK" sign) | Saves a timestamped `.png` screenshot | 2.0 s |

---

## 💡 Smart Usage & Ergonomic Tips

- **Prevent hand fatigue** – Rest your elbow on your desk or chair armrest. Keep your Index finger inside the purple box; you only need small, relaxed wrist movements to reach every corner of both monitors.
- **Aim before clicking** – Point your Index finger over the button you want to tap, hold your hand still for a split second, then pinch Thumb + Middle and release.
- **Using with Instagram Reels / YouTube Shorts** – Click once inside your browser window so the video player has focus. After that, Thumb + Ring (Next), Thumb + Pinky (Previous), and Closed Fist (Play/Pause) will work seamlessly.
- **Good lighting = higher accuracy** – Make sure your hand is well lit from the front (avoid strong backlighting behind you) so MediaPipe tracks your fingertips smoothly without jitter.
- **Keep your thumb relaxed while moving** – Keep your thumb slightly away from your other fingers while moving the cursor so you don't accidentally trigger a pinch action.

---

## ⚙️ Customization & Sensitivity Tuning

Fine-tune the feel of the mouse by editing the settings at the top of `virtual_mouse.py`:

```python
# --- EASY SETTINGS (Medium / Physical Mouse Feel) ---
BOX_W = 340       # Smaller = faster / less hand movement | Larger = slower / more precision
BOX_H = 190       # Smaller = faster vertical movement   | Larger = slower vertical movement
SMOOTHING = 6.0   # Higher = smoother & heavier feel     | Lower = snappier response
DEADZONE = 5      # Pixels ignored to stop tiny finger shakes when clicking
```

**Screenshot save folder:** update `screenshot_path` in `virtual_mouse.py` to choose where screenshots are stored (the folder is created automatically if it doesn't exist):

```python
screenshot_path = "C:/Users/Admin/Desktop/Virtual"
```

---

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `AttributeError: module 'mediapipe' has no attribute 'solutions'` | You are running old code on MediaPipe 0.10.30+. Use the updated `virtual_mouse.py` from this repository, which uses the new HandLandmarker Tasks API. |
| `hand_landmarker.task` not found | Make sure `hand_landmarker.task` is saved in the same folder as `virtual_mouse.py`, and run the script from inside that folder. |
| Webcam window doesn't open | Close other apps using your camera (Zoom, Teams, browser tabs). If you have multiple cameras, change `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`. |
| Cursor feels too fast or too slow | Adjust `BOX_W` and `BOX_H` in `virtual_mouse.py`: increase them for slower, more precise movement, or decrease them for faster movement. |

---

## 📂 Project Structure

```text
├── virtual_mouse.py       # Main application script
├── hand_landmarker.task   # MediaPipe hand tracking model (downloaded in setup)
├── .gitignore             # Ignores .venv, cache, and generated screenshots
├── LICENSE                # MIT License
└── README.md              # Project documentation
```

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by **Ali Khan**
