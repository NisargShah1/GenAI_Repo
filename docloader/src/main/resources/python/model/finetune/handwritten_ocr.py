import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import torch

# ========= CONFIG =========
image_path = "sample.png"

# Load image
image = Image.open(image_path).convert("RGB")
image = ImageOps.exif_transpose(image)

# ========= PRINTED OCR (Tesseract) =========
print("🔍 Running Tesseract for printed text...")
#printed_text = pytesseract.image_to_string(image, lang="eng")

# ========= HANDWRITTEN OCR (TrOCR) =========
print("✍️ Running TrOCR for handwritten text...")

#Preprocessing:
#Use thresholding or binarization (convert to black/white).
#Resize images to the model’s expected scale (usually 384×384 or 1024×512).
#Increase contrast, remove background noise.

image = image.convert("L")  # grayscale
image = image.point(lambda x: 0 if x < 140 else 255, '1')  # threshold
image = image.filter(ImageFilter.MedianFilter(3))
image = image.convert("RGB")
# Enhance and resize
enhanced = ImageEnhance.Contrast(image).enhance(2.5)
enhanced = ImageOps.grayscale(enhanced).convert("RGB")
enhanced = enhanced.resize((1024, 512))

# Load TrOCR model
model_dir = "./trocr-finetuned"  
processor = TrOCRProcessor.from_pretrained(model_dir)
model = VisionEncoderDecoderModel.from_pretrained(model_dir)
#processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
#model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Run inference
pixel_values = processor(images=enhanced, return_tensors="pt").pixel_values
generated_ids = model.generate(pixel_values, max_length=256)
handwritten_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

# ========= COMBINE RESULTS =========
print("\n🧾 COMBINED OCR OUTPUT\n" + "="*40)
#print("📘 Printed Text (Tesseract):\n", printed_text.strip())
print("\n✍️ Handwritten Text (TrOCR):\n", handwritten_text.strip())
print("="*40)
