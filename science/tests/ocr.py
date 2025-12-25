from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "" # redacted

# path to your image
image_path = "tmp/test.png"

# open image
img = Image.open(image_path)

# extract text
text = pytesseract.image_to_string(img)

print(text)
