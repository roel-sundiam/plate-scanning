import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime, timedelta
from ultralytics import YOLO
import base64
import os

from config import (
    TESSERACT_CMD,
    CONFIDENCE_THRESHOLD,
    USE_PLATE_RECOGNIZER,
    PLATE_RECOGNIZER_TOKEN,
    OCR_SPACE_API_KEY,
    USE_OCR_SPACE_FALLBACK,
    YOLO_MODEL,
    DEBUG_MODE,
    SAVE_SNAPSHOTS,
    SNAPSHOT_DIR
)


class LicensePlateDetector:
    """Handles license plate detection and OCR"""
    
    def __init__(self):
        # Set Tesseract path
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD
        
        # Initialize YOLO model for license plate detection
        try:
            self.model = YOLO(YOLO_MODEL)
            print(f"✓ YOLO model loaded: {YOLO_MODEL}")
        except Exception as e:
            print(f"⚠ YOLO model error: {e}")
            print("  Will use basic contour detection as fallback")
            self.model = None
        
        # Recent detections cache for duplicate filtering
        self.recent_detections = {}
        
        # Create snapshot directory
        if SAVE_SNAPSHOTS and not os.path.exists(SNAPSHOT_DIR):
            os.makedirs(SNAPSHOT_DIR)
    
    def detect_plates(self, frame):
        """Detect license plate regions in the frame using contour detection"""
        # Use contour-based detection (proven to work with NBC1234)
        plates = self._detect_plates_contours(frame)
        return plates
    
    def _detect_plates_contours(self, frame):
        """Fallback method using contour detection"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply bilateral filter to reduce noise
        blur = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Edge detection - same as working test_real_plate.py
        edges = cv2.Canny(blur, 30, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]  # Top 30 contours
        
        plates = []
        
        for contour in contours:
            # Approximate the contour
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            # License plates are typically rectangular (exactly 4 corners)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)
                
                # Same criteria as test_real_plate.py
                if 2.0 <= aspect_ratio <= 6.0 and w > 80 and h > 20:
                    plates.append({
                        'bbox': (x, y, x + w, y + h),
                        'confidence': 0.85  # Good confidence for contour detection
                    })
        
        return plates
    
    def extract_text(self, plate_image):
        """Extract text from plate image using OCR"""
        
        if USE_PLATE_RECOGNIZER and PLATE_RECOGNIZER_TOKEN:
            return self._extract_text_api(plate_image)
        
        # Try Tesseract first
        text = self._extract_text_tesseract(plate_image)
        
        # If Tesseract fails or returns short result, try OCR.space as fallback
        if USE_OCR_SPACE_FALLBACK and OCR_SPACE_API_KEY and len(text) < 5:
            ocr_text = self._extract_text_ocrspace(plate_image)
            if len(ocr_text) > len(text):
                return ocr_text
        
        return text
    
    def _extract_text_tesseract(self, plate_image):
        """Extract text using Tesseract OCR"""
        # Preprocess the image
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        
        # Resize for better OCR (larger scale)
        scale_factor = 3
        width = int(gray.shape[1] * scale_factor)
        height = int(gray.shape[0] * scale_factor)
        gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)
        
        # Apply bilateral filter to reduce noise while keeping edges
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        
        # Try multiple thresholding methods
        results = []
        
        # Method 1: Otsu's thresholding
        _, thresh1 = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Method 2: Adaptive thresholding
        thresh2 = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
        
        # Method 3: Simple threshold
        _, thresh3 = cv2.threshold(filtered, 150, 255, cv2.THRESH_BINARY)
        
        # OCR configuration - PSM 7 for single line of text
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        
        # Try all methods and pick the best result
        for thresh in [thresh1, thresh2, thresh3]:
            text = pytesseract.image_to_string(thresh, config=custom_config)
            cleaned = self._clean_plate_text(text)
            if cleaned:
                results.append(cleaned)
        
        # Return the longest valid result
        if results:
            return max(results, key=len)
        
        return ""
    
    def _extract_text_api(self, plate_image):
        """Extract text using Plate Recognizer API"""
        import requests
        
        # Encode image
        _, buffer = cv2.imencode('.jpg', plate_image)
        
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            headers={'Authorization': f'Token {PLATE_RECOGNIZER_TOKEN}'},
            files={'upload': buffer.tobytes()}
        )
        
        if response.status_code == 201:
            result = response.json()
            if result['results']:
                return result['results'][0]['plate'].upper()
        
        return ""
    
    def _extract_text_ocrspace(self, plate_image):
        """Extract text using OCR.space API as fallback"""
        import requests
        
        # Encode image to base64
        _, buffer = cv2.imencode('.jpg', plate_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        try:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                data={
                    'apikey': OCR_SPACE_API_KEY,
                    'base64Image': f'data:image/jpeg;base64,{img_base64}',
                    'isOverlayRequired': False,
                    'OCREngine': 2,  # Engine 2 is better for license plates
                    'scale': True,
                    'isTable': False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ParsedResults') and len(result['ParsedResults']) > 0:
                    text = result['ParsedResults'][0].get('ParsedText', '')
                    cleaned = self._clean_plate_text(text)
                    if cleaned:
                        print(f"    🌐 OCR.space detected: {cleaned}")
                        return cleaned
        except Exception as e:
            print(f"    ⚠️ OCR.space API error: {e}")
        
        return ""
    
    def _extract_text_ocrspace(self, plate_image):
        """Extract text using OCR.space API as fallback"""
        import requests
        
        # Encode image to base64
        _, buffer = cv2.imencode('.jpg', plate_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        try:
            response = requests.post(
                'https://api.ocr.space/parse/image',
                data={
                    'apikey': OCR_SPACE_API_KEY,
                    'base64Image': f'data:image/jpeg;base64,{img_base64}',
                    'isOverlayRequired': False,
                    'OCREngine': 2,  # Engine 2 is better for license plates
                    'scale': True,
                    'isTable': False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ParsedResults') and len(result['ParsedResults']) > 0:
                    text = result['ParsedResults'][0].get('ParsedText', '')
                    cleaned = self._clean_plate_text(text)
                    if cleaned:
                        print(f"    🌐 OCR.space detected: {cleaned}")
                        return cleaned
        except Exception as e:
            print(f"    ⚠️ OCR.space API error: {e}")
        
        return ""
    
    def _clean_plate_text(self, text):
        """Clean and normalize plate text"""
        # Remove whitespace and special characters
        text = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Remove if too short or too long
        if len(text) < 4 or len(text) > 10:
            return ""
        
        return text
    
    def is_duplicate(self, plate_number, window_seconds=60):
        """Check if plate was recently detected"""
        if plate_number in self.recent_detections:
            last_time = self.recent_detections[plate_number]
            if datetime.now() - last_time < timedelta(seconds=window_seconds):
                return True
        
        # Update detection time
        self.recent_detections[plate_number] = datetime.now()
        
        # Clean old entries
        self._clean_old_detections(window_seconds)
        
        return False
    
    def _clean_old_detections(self, window_seconds):
        """Remove old entries from detection cache"""
        current_time = datetime.now()
        to_remove = []
        
        for plate, timestamp in self.recent_detections.items():
            if current_time - timestamp > timedelta(seconds=window_seconds * 2):
                to_remove.append(plate)
        
        for plate in to_remove:
            del self.recent_detections[plate]
    
    def save_snapshot(self, frame, plate_number, bbox):
        """Save snapshot with detected plate"""
        if not SAVE_SNAPSHOTS:
            return None
        
        # Draw bounding box on frame
        x1, y1, x2, y2 = bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, plate_number, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{plate_number}_{timestamp}.jpg"
        filepath = os.path.join(SNAPSHOT_DIR, filename)
        
        cv2.imwrite(filepath, frame)
        
        return filepath
    
    def frame_to_base64(self, frame):
        """Convert frame to base64 string"""
        _, buffer = cv2.imencode('.jpg', frame)
        return base64.b64encode(buffer).decode('utf-8')
    
    def annotate_frame(self, frame, plates, texts):
        """Draw detection results on frame"""
        for i, plate in enumerate(plates):
            x1, y1, x2, y2 = plate['bbox']
            confidence = plate['confidence']
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add text
            if i < len(texts) and texts[i]:
                label = f"{texts[i]} ({confidence:.2f})"
                cv2.putText(frame, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
