import pytesseract
from PIL import ImageGrab
import time

def capture_rune_screenshot():
    print("Capturing screenshot in 3 seconds...")
    time.sleep(3)
    screenshot = ImageGrab.grab()
    screenshot.save("rune_screenshot.png")
    print("Screenshot saved as rune_screenshot.png")

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    print("Extracted Text:")
    print(text)
    return text

def main():
    capture_rune_screenshot()
    text = extract_text_from_image("rune_screenshot.png")
    # Here you can add logic to parse text and evaluate runes

if __name__ == "__main__":
    main()