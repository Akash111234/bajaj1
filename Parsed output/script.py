import os
from PIL import Image
import re
import pytesseract
import json

# Path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
                "test_value": str(value),  # Convert to string if needed for UI consistency
                "test_unit": unit,
                "bio_reference_range": ref_range,
                "lab_test_out_of_range": out_of_range
            })
        except Exception as e:
            print("⚠️ Skipped malformed entry:", e)
            continue

    return lab_tests

def extract_from_image(image_path):
    print(f"📂 Loading image from: {image_path}")
    image = Image.open(image_path)
    print("🖼️ Image loaded")

    text = pytesseract.image_to_string(image)
    print("🔍 OCR completed")

    data = parse_lab_data(text)
    return data

def process_images_in_folder(folder_path, output_file):
    print(f"📂 Scanning images in folder: {folder_path}")
    
    all_data = []
    
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            print(f"🔍 Processing image: {image_path}")
            
            data = extract_from_image(image_path)
            all_data.append({
                "image_name": filename,
                "lab_tests": data
            })
    
    print("🔴 Saving results to JSON file")
    with open(output_file, 'w') as outfile:
        json.dump({"is_success": True, "data": all_data}, outfile, indent=4)

    print(f"✅ Output saved to {output_file}")

# Example usage
if __name__ == "__main__":
    folder_path = r"C:\Users\akash\Downloads\lab_reports_samples\lbmaske"  # Replace with the folder containing your images
    output_file = r"c:\Users\akash\Downloads\lab_reports_samples\lab_test_results.json"  # Replace with your desired output file path
    
    process_images_in_folder(folder_path, output_file)
