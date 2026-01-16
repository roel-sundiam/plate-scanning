import sys
import os
import cv2
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from detector import LicensePlateDetector
import requests
from dotenv import load_dotenv

load_dotenv()

def test_image(image_path):
    """Test license plate detection on a single image"""
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return
    
    print(f"📸 Testing image: {image_path}")
    print("=" * 60)
    
    # Load image
    frame = cv2.imread(image_path)
    if frame is None:
        print("❌ Error: Could not load image")
        return
    
    print(f"✓ Image loaded: {frame.shape[1]}x{frame.shape[0]} pixels")
    
    # Initialize detector
    detector = LicensePlateDetector()
    print("✓ Detector initialized")
    
    # Detect plates
    plates = detector.detect_plates(frame)
    print(f"\n🔍 Detection Results:")
    print(f"   Plates found: {len(plates)}")
    
    if len(plates) == 0:
        print("   ℹ️  No license plates detected in this image")
        print("   Try with a clearer image or adjust confidence threshold")
        return
    
    # Process each detected plate
    for i, plate_data in enumerate(plates, 1):
        # plate_data is a dictionary with 'bbox' and 'confidence'
        bbox = plate_data['bbox']
        confidence = plate_data['confidence']
        
        # bbox is (x1, y1, x2, y2) format
        x1, y1, x2, y2 = bbox
        w = x2 - x1
        h = y2 - y1
        
        print(f"\n📋 Plate #{i}:")
        print(f"   Position: ({x1}, {y1})")
        print(f"   Size: {w}x{h}")
        print(f"   Confidence: {confidence:.2%}")
        
        # Extract plate region
        plate_img = frame[y1:y2, x1:x2]
        
        # OCR
        try:
            plate_text = detector.extract_text(plate_img)
            print(f"   Text: {plate_text if plate_text else '(empty)'}")
            
            if plate_text:
                # Save to API
                api_url = os.getenv('API_URL', 'http://localhost:3000/api/plates')
                data = {
                    'plateNumber': plate_text,
                    'gateId': 'test_gate',
                    'confidence': confidence
                }
                
                try:
                    response = requests.post(api_url, json=data)
                    if response.status_code == 201:
                        print(f"   ✅ Saved to database!")
                    else:
                        print(f"   ⚠️  API response: {response.status_code}")
                except Exception as e:
                    print(f"   ⚠️  Could not save to API: {e}")
            
            # Save annotated image
            output_path = image_path.replace('.jpg', '_detected.jpg').replace('.png', '_detected.png')
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if plate_text:
                cv2.putText(frame, plate_text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.9, (0, 255, 0), 2)
            cv2.imwrite(output_path, frame)
            print(f"   💾 Annotated image saved: {output_path}")
            
        except Exception as e:
            print(f"   ❌ OCR Error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Test complete!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_image.py <path_to_image>")
        print("\nExample:")
        print("  python test_image.py test-images/sample-plate.jpg")
        print("  python test_image.py C:/path/to/your/image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    test_image(image_path)
