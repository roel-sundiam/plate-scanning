import cv2
import pytesseract
import re
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
IMAGE_PATH = r"C:\Users\sundi\Downloads\2018_Philippine_new_plates.png"
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Users\sundi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
API_URL = os.getenv("API_URL", "http://localhost:3000/api/plates")
GATE_ID = os.getenv("GATE_IDENTIFIER", "gate_01")

def find_plate_regions(frame):
    """Find rectangular regions that might be license plates"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
    
    plate_regions = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if 2.0 <= aspect_ratio <= 6.0 and w > 80 and h > 20:
                plate_regions.append((x, y, w, h, aspect_ratio))
    return plate_regions

def extract_plate_text(plate_img):
    """Extract text from a plate region"""
    if plate_img.shape[1] < 200:
        scale = 200 / plate_img.shape[1]
        plate_img = cv2.resize(plate_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    try:
        text = pytesseract.image_to_string(thresh, config=custom_config)
        text = text.strip().upper()
        text = re.sub(r'[^A-Z0-9]', '', text)
        if 4 <= len(text) <= 8:
            return text
    except:
        pass
    return None

print("=" * 60)
print("🚗 Testing License Plate Detection with Image File")
print("=" * 60)
print(f"Image: {IMAGE_PATH}")
print(f"API: {API_URL}")
print("=" * 60)

# Read the image
frame = cv2.imread(IMAGE_PATH)
if frame is None:
    print("❌ Cannot read image file")
    exit(1)

print(f"✓ Image loaded: {frame.shape[1]}x{frame.shape[0]}")

# Find plate regions
plate_regions = find_plate_regions(frame)
print(f"✓ Found {len(plate_regions)} potential plate regions")

# Try OCR on each region
for i, (x, y, w, h, aspect_ratio) in enumerate(plate_regions):
    plate_roi = frame[y:y+h, x:x+w]
    plate_text = extract_plate_text(plate_roi)
    
    if plate_text:
        print(f"\n🎯 DETECTED: {plate_text}")
        print(f"   Position: ({x}, {y}), Size: {w}x{h}, Ratio: {aspect_ratio:.2f}")
        
        # Send to API
        try:
            plate_data = {
                'plateNumber': plate_text,
                'gateId': GATE_ID,
                'confidence': 0.85,
                'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
            }
            print(f"   📤 Sending to API...")
            response = requests.post(API_URL, json=plate_data, timeout=5)
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS! Saved to database: {plate_text}")
                print(f"   📊 Response: {response.json()}")
            else:
                print(f"   ⚠️ API error: {response.status_code}")
                print(f"   {response.text}")
        except Exception as e:
            print(f"   ❌ API connection error: {e}")
        
        break  # Only send the first detection

print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)
print(f"Check frontend at: http://localhost:4200")
print(f"Check API at: {API_URL}")
