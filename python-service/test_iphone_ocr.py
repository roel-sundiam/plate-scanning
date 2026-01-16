import cv2
import pytesseract
import re
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Configuration
IPHONE_URL = os.getenv("IPHONE_URL", "http://192.168.68.101:4747/video")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Users\sundi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def extract_plate_text(frame):
    """Extract license plate text from frame using OCR"""
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold for better OCR
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # OCR configuration for license plates
    custom_config = r'--oem 3 --psm 7'
    
    try:
        text = pytesseract.image_to_string(thresh, config=custom_config)
        text = text.strip().upper()
        
        # Clean - keep only alphanumeric
        text = re.sub(r'[^A-Z0-9]', '', text)
        
        # Filter: license plates typically have 4+ characters
        if len(text) >= 4:
            return text
        return None
    except:
        return None


def main():
    print("=" * 60)
    print("📱 iPhone License Plate Detection - Live OCR")
    print("=" * 60)
    print(f"Connecting to: {IPHONE_URL}")
    
    # Connect to iPhone camera
    cap = cv2.VideoCapture(IPHONE_URL)
    
    if not cap.isOpened():
        print("❌ Cannot connect to iPhone camera")
        print("\nMake sure:")
        print("  1. DroidCam app is open on your iPhone")
        print("  2. Both devices are on the same WiFi")
        return
    
    print("✅ Connected to iPhone camera!")
    print("\n" + "=" * 60)
    print("📸 INSTRUCTIONS:")
    print("=" * 60)
    print("1. Point your iPhone at the license plate image")
    print("2. Hold steady for 2-3 seconds")
    print("3. Make sure the plate is clearly visible and well-lit")
    print("4. Press 'q' to quit")
    print("=" * 60)
    print("\n🔍 Scanning for license plates...\n")
    
    last_detection = None
    detection_count = 0
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("⚠️  Cannot read frame")
                break
            
            frame_count += 1
            
            # Process every 10th frame to reduce CPU load
            if frame_count % 10 == 0:
                plate_text = extract_plate_text(frame)
                
                if plate_text and plate_text != last_detection:
                    detection_count += 1
                    last_detection = plate_text
                    
                    print(f"🎯 DETECTED #{detection_count}: {plate_text}")
                    print(f"   Timestamp: {time.strftime('%H:%M:%S')}")
                    
                    # Save snapshot
                    snapshot_path = f"snapshots/plate_{plate_text}_{int(time.time())}.jpg"
                    os.makedirs("snapshots", exist_ok=True)
                    cv2.imwrite(snapshot_path, frame)
                    print(f"   📷 Saved: {snapshot_path}\n")
                
                # Show frame count every 30 frames
                if frame_count % 30 == 0:
                    print(f"   Processing... ({frame_count} frames)")
            
            # Display frame (optional - can disable if slow)
            small_frame = cv2.resize(frame, (640, 360))
            cv2.putText(small_frame, f"Detections: {detection_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(small_frame, "Press Q to quit", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if last_detection:
                cv2.putText(small_frame, f"Last: {last_detection}", (10, 110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.imshow('iPhone Camera - License Plate Detection', small_frame)
            
            # Check for quit key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n👋 Stopping detection...")
                break
    
    except KeyboardInterrupt:
        print("\n\n⏹  Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("📊 Session Summary")
        print("=" * 60)
        print(f"Frames processed: {frame_count}")
        print(f"Plates detected: {detection_count}")
        print("=" * 60)
        print("\n✅ Done!")


if __name__ == "__main__":
    main()
