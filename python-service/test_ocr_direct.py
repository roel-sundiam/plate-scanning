import sys
import cv2
import pytesseract
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Set Tesseract path
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Users\sundi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_plate_text(image_path):
    """Extract text directly from license plate image using OCR"""
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Cannot load image: {image_path}")
        return None
    
    print(f"✓ Image loaded: {img.shape[1]}x{img.shape[0]}")
    
    # Resize if too small
    if img.shape[1] < 200:
        scale = 200 / img.shape[1]
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        print(f"✓ Resized to: {img.shape[1]}x{img.shape[0]}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Try multiple preprocessing methods
    results = []
    
    # Method 1: Simple threshold
    _, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    text1 = pytesseract.image_to_string(thresh1, config=r'--oem 3 --psm 7')
    results.append(text1.strip().upper())
    print(f"  Method 1: {text1.strip()}")
    
    # Method 2: Otsu threshold
    _, thresh2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text2 = pytesseract.image_to_string(thresh2, config=r'--oem 3 --psm 7')
    results.append(text2.strip().upper())
    print(f"  Method 2: {text2.strip()}")
    
    # Method 3: Adaptive threshold
    thresh3 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    text3 = pytesseract.image_to_string(thresh3, config=r'--oem 3 --psm 7')
    results.append(text3.strip().upper())
    print(f"  Method 3: {text3.strip()}")
    
    # Find the longest non-empty result
    best_text = max(results, key=lambda x: len(x) if x else 0)
    
    # Clean up the text - keep only alphanumeric
    best_text = re.sub(r'[^A-Z0-9]', '', best_text)
    
    print(f"\n📝 Best OCR Result: {best_text}")
    return best_text if best_text else None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ocr_direct.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print("=" * 60)
    print("Testing Direct OCR on License Plate Image")
    print("=" * 60)
    
    plate_text = extract_plate_text(image_path)
    
    if plate_text:
        print(f"\n✅ Detected Plate Number: {plate_text}")
        
        # Send to API
        import requests
        api_url = "http://localhost:3000/api/plates"
        
        try:
            response = requests.post(api_url, json={
                'plateNumber': plate_text,
                'gateId': 'test_gate',
                'confidence': 0.95
            }, timeout=5)
            
            if response.status_code == 201:
                print(f"✅ Sent to API successfully!")
                print(f"   Check dashboard: http://localhost:4200")
            else:
                print(f"⚠️  API response: {response.status_code}")
        
        except Exception as e:
            print(f"⚠️  Could not send to API: {e}")
            print(f"   Make sure backend is running on http://localhost:3000")
    else:
        print("\n❌ Could not extract plate number")
    
    print("=" * 60)
