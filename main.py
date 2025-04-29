from fastapi import FastAPI, UploadFile, File
from PIL import Image
import re
import pytesseract
import json
from io import BytesIO

# ✅ On Render, don't set this path. Tesseract must be installed via apt in render.yaml
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

def parse_lab_data(text):
    print("🔍 Parsing OCR text for lab tests...")
    
    lab_tests = []
    pattern = re.compile(
        r'(?P<test_name>[A-Za-z \-/()]+)[\s:]+(?P<value>[-+]?\d*\.?\d+)\s*(?P<unit>[a-zA-Z/%]*)[\s\-:]*\(?(?P<ref_range>\d+\.?\d*\s*[-–]\s*\d+\.?\d*)\)?',
        re.IGNORECASE
    )

    for match in pattern.finditer(text):
        try:
            test_name = match.group('test_name').strip()
            value = float(match.group('value'))
            unit = match.group('unit').strip()
            ref_range = match.group('ref_range').strip()
            low, high = map(lambda x: float(x.strip()), re.split(r'[-–]', ref_range))
            out_of_range = not (low <= value <= high)

            lab_tests.append({
                "test_name": test_name,
                "test_value": str(value),
                "test_unit": unit,
                "bio_reference_range": ref_range,
                "lab_test_out_of_range": out_of_range
            })
        except Exception as e:
            print("⚠️ Skipped malformed entry:", e)
            continue

    return lab_tests

def extract_from_image(image_bytes):
    print("📂 Loading image from uploaded file...")
    image = Image.open(BytesIO(image_bytes))
    print("🖼️ Image loaded")

    text = pytesseract.image_to_string(image)
    print("🔍 OCR completed")

    return parse_lab_data(text)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    print(f"📂 Received file: {file.filename}")
    image_bytes = await file.read()
    data = extract_from_image(image_bytes)

    return {
        "is_success": True,
        "data": data
    }
