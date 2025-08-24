import mss
import cv2
import numpy as np
import pygetwindow as gw
import time

# 1. Find the Summoners War window
windows = gw.getWindowsWithTitle("Summoners War (Steam)")
if not windows:
    raise RuntimeError("Summoners War window not found")
win = windows[0]

# 2. Define rune capture offsets (adjust as needed)
offset_top = 300
offset_left = 800
width = 400
height = 200

with mss.mss() as sct:
    while True:
        bbox = {
            "top": win.top + offset_top,
            "left": win.left + offset_left,
            "width": width,
            "height": height,
        }

        # Grab screenshot
        screenshot = sct.grab(bbox)
        img = np.array(screenshot)[:, :, :3]  # BGRA → BGR

        # Show in window
        cv2.imshow("Rune Capture Preview", img)

        # Controls:
        key = cv2.waitKey(30) & 0xFF
        if key == ord("q"):  # press 'q' to quit
            break

    cv2.destroyAllWindows()
