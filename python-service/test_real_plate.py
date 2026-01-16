import cv2
import pytesseract
import re
import os
import time
import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Try multiple DroidCam URL formats
IPHONE_IP = "192.168.68.101"
IPHONE_URLS = [
    f"http://{IPHONE_IP}:4747/video",
    f"http://{IPHONE_IP}:4747/mjpegfeed",
    f"http://{IPHONE_IP}:4747/cam/1/stream",
]
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Users\sundi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

API_URL = os.getenv("API_URL", "http://localhost:3000/api/plates")
GATE_ID = os.getenv("GATE_IDENTIFIER", "gate_01")

def find_plate_regions(frame):
    """Find rectangular regions that might be license plates"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Edge detection
    edged = cv2.Canny(gray, 30, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
    
    plate_regions = []
    
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        
        # License plates are typically rectangular (4 corners)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            
            # License plate aspect ratio is typically between 2:1 and 5:1
            aspect_ratio = w / float(h)
            
            # Check if dimensions and aspect ratio match license plate characteristics
            if 2.0 <= aspect_ratio <= 6.0 and w > 80 and h > 20:
                plate_regions.append((x, y, w, h, aspect_ratio))
    
    return plate_regions

def extract_plate_text(plate_img):
    """Extract text from a plate region"""
    # Resize for better OCR
    if plate_img.shape[1] < 200:
        scale = 200 / plate_img.shape[1]
        plate_img = cv2.resize(plate_img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    
    # Convert to grayscale
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # OCR configuration
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    
    try:
        text = pytesseract.image_to_string(thresh, config=custom_config)
        text = text.strip().upper()
        text = re.sub(r'[^A-Z0-9]', '', text)
        
        # License plates typically have 4-8 characters
        if 4 <= len(text) <= 8:
            return text
    except:
        pass
    
    return None

def main():
    print("=" * 60)
    print("Real License Plate Detection - iPhone via iVCam")
    print("=" * 60)
    
    # Try webcam devices (iVCam appears as webcam)
    cap = None
    camera_index = None
    
    for i in range(3):
        print(f"Trying camera {i}...")
        test_cap = cv2.VideoCapture(i)
        time.sleep(0.5)
        
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret and frame is not None:
                # Check resolution to identify iVCam (usually higher res)
                print(f"  Camera {i}: {frame.shape[1]}x{frame.shape[0]}")
                if camera_index is None or frame.shape[1] >= 640:
                    if cap:
                        cap.release()
                    cap = test_cap
                    camera_index = i
                else:
                    test_cap.release()
            else:
                test_cap.release()
        else:
            if test_cap:
                test_cap.release()
    
    if camera_index is None:
        print("[ERROR] Cannot connect to any camera")
        print("\nMake sure:")
        print("  1. iVCam PC client is running")
        print("  2. iVCam app is open on your iPhone")
        print("  3. iPhone and PC are connected")
        return
    
    print(f"[OK] Connected to Camera {camera_index}!")
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("1. Point your iPhone at an ACTUAL license plate")
    print("2. Get close enough so the plate is clearly visible")
    print("3. Hold steady for 2-3 seconds")
    print("4. The plate should fill a good portion of the screen")
    print("5. Make sure there's good lighting")
    print("6. Press 'q' in the video window to quit")
    print("=" * 60)
    print("\nLooking for license plates...\n")
    
    last_detection = None
    detection_count = 0
    frame_count = 0
    last_detection_time = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("[WARNING] Cannot read frame")
                break
            
            frame_count += 1
            
            # Process every 5th frame
            if frame_count % 5 == 0:
                # Find potential plate regions
                plate_regions = find_plate_regions(frame)
                
                current_time = time.time()
                
                for (x, y, w, h, aspect_ratio) in plate_regions:
                    # Extract the region
                    plate_roi = frame[y:y+h, x:x+w]
                    
                    # Try OCR
                    plate_text = extract_plate_text(plate_roi)
                    
                    if plate_text:
                        # Avoid duplicate detections within 5 seconds
                        if plate_text != last_detection or (current_time - last_detection_time) > 5:
                            detection_count += 1
                            last_detection = plate_text
                            last_detection_time = current_time
                            
                            print(f"\nDETECTED #{detection_count}: {plate_text}")
                            print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
                            print(f"   Position: ({x}, {y}), Size: {w}x{h}, Ratio: {aspect_ratio:.2f}")
                            
                            # Send to API
                            try:
                                plate_data = {
                                    'plateNumber': plate_text,
                                    'gateId': GATE_ID,
                                    'confidence': 0.85,
                                    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())
                                }
                                response = requests.post(API_URL, json=plate_data, timeout=5)
                                if response.status_code in [200, 201]:
                                    print(f"   [OK] Sent to database: {plate_text}")
                                else:
                                    print(f"   [ERROR] API error: {response.status_code}")
                            except Exception as e:
                                print(f"   [ERROR] API connection error: {e}")
                            
                            # Save snapshot
                            snapshot_path = f"snapshots/plate_{plate_text}_{int(time.time())}.jpg"
                            os.makedirs("snapshots", exist_ok=True)
                            
                            # Draw rectangle on frame and save
                            annotated = frame.copy()
                            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 3)
                            cv2.putText(annotated, plate_text, (x, y-10),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.imwrite(snapshot_path, annotated)
                            print(f"   [SAVED] Snapshot: {snapshot_path}\n")
                    
                    # Draw all potential plate regions (for debugging)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
            
            # Display frame
            display = frame.copy()
            
            # Add info overlay
            cv2.putText(display, f"Detections: {detection_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if last_detection:
                cv2.putText(display, f"Last: {last_detection}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.putText(display, "Press Q to quit", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.putText(display, "Yellow boxes = potential plates", (10, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            
            # Resize for display
            display_resized = cv2.resize(display, (960, 540))
            cv2.imshow('License Plate Detection - Point at Real Plate', display_resized)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nStopping detection...")
                break
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("Session Summary")
        print("=" * 60)
        print(f"Frames processed: {frame_count}")
        print(f"Plates detected: {detection_count}")
        print("=" * 60)
        print("\nDone!")

if __name__ == "__main__":
    main()
