from PIL import Image, ImageDraw
import pytesseract
import pygetwindow as gw
import mss

# Optional: if Tesseract is not in your PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load image
image = Image.open("manage-rune.png")

# OCR
text = pytesseract.image_to_string(image)

print(text)


windows = gw.getWindowsWithTitle("Summoners War (Steam)")
window_right = 0
window_top = 0

if windows:
    win = windows[0]  # Get the first matching window
    print(f"Title: {win.title}")
    print(f"Position: ({win.right}, {win.top})")
    window_right = win.right
    window_top = win.top
    print(f"Size: {win.width}x{win.height}")
else:
    print("Window not found.")



with mss.mss() as sct:
    region = {'top': window_top, 'left': win.right-400, 'width': 400, 'height': 290}
    screenshot = sct.grab(region)

    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
    # Step 2: Draw on the image
    draw = ImageDraw.Draw(img)


    # Draw it on an image
    draw.rectangle([(270, 80), (390, 285)],fill="black")
    draw.rectangle([(5, 40), (75, 70)],fill="black")


    img.show()
    text = pytesseract.image_to_string(img)

    print(text)
    print("-- done --")

#######################

    # data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    # draw = ImageDraw.Draw(img)

    # n_boxes = len(data['level'])
    # for i in range(n_boxes):
    #     (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
    #     text = data['text'][i].strip()
    #     conf = int(data['conf'][i])
        
    #     # Only draw boxes for confident text (optional)
    #     if conf > 60 and text != '':
    #         draw.rectangle([x, y, x + w, y + h], outline='red', width=2)

    # img.show()

