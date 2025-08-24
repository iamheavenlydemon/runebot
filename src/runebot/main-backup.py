import mss
from PIL import Image, ImageDraw
import pygetwindow as gw
import pytesseract

# 1. Get the game window
windows = gw.getWindowsWithTitle("Summoners War (Steam)")
if not windows:
    raise RuntimeError("Summoners War window not found")
win = windows[0]

# 2. Define rune capture relative to window
# Example offsets (adjust according to rune area in your window)
offset_top = 40
offset_left = 850
width = 420
height = 275

bbox = {
    'top': win.top + offset_top,
    'left': win.left + offset_left,
    'width': width,
    'height': height
}

grade_offset_top = 80
grade_offset_left = 1180
grade_width = 100
grade_height = 35

rune_grade = {
    'top': win.top + grade_offset_top,
    'left': win.left + grade_offset_left,
    'width': grade_width,
    'height': grade_height
}

# 3. Capture with mss
with mss.mss() as sct:
    screenshot = sct.grab(bbox)
    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
    # img.save("rune_capture.png")

    rune_grade_ss = sct.grab(rune_grade)
    rune_grade_img = Image.frombytes('RGB', rune_grade_ss.size, rune_grade_ss.rgb)

    rune_grade_img.show()
    grade_text = pytesseract.image_to_string(rune_grade_img)
    print(grade_text)
    draw = ImageDraw.Draw(img)

    # Example: black box from (x1,y1) to (x2,y2)
    # x1, y1 = 300, 78
    x1, y1 = 300, 45
    x2, y2 = 450, 300
    draw.rectangle([x1, y1, x2, y2], fill="black")  # fill solid black
    draw.rectangle([0, 0, 75, 30], fill="black")  # top left
    draw.rectangle([390, 0, 475, 30], fill="black")

    text = pytesseract.image_to_string(img)
    img.show()

# print(f"Captured rune image at {bbox}")
print(text)
