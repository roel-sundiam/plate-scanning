"""Test what the camera is seeing and what YOLO detects"""
import cv2
from detector import LicensePlateDetector

print("\n📸 Capturing frame from iPhone camera (device 1)...")
print("=" * 60)

# Open camera
cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ Cannot open camera device 1")
    exit(1)

# Capture a frame
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Failed to capture frame")
    exit(1)

h, w = frame.shape[:2]
print(f"✓ Frame captured: {w}x{h} pixels")

# Save the raw frame
cv2.imwrite("camera_view.jpg", frame)
print("✓ Saved: camera_view.jpg")

# Initialize detector
detector = LicensePlateDetector()
print("✓ Detector initialized\n")

# Run YOLO detection
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model(frame, verbose=False)

print("🔍 YOLO Detection Results:")
print("=" * 60)

for result in results:
    boxes = result.boxes
    if len(boxes) == 0:
        print("❌ No objects detected!")
        print("\nPossible reasons:")
        print("  - Camera is pointing at blank area")
        print("  - Image is too dark/bright")
        print("  - No recognizable objects in view")
        print("  - License plate too small/far")
    else:
        print(f"✓ Found {len(boxes)} object(s):\n")
        for i, box in enumerate(boxes, 1):
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = model.names[cls]
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            
            print(f"  {i}. {class_name}")
            print(f"     Confidence: {conf:.1%}")
            print(f"     Position: ({x1},{y1}) to ({x2},{y2})")
            print(f"     Size: {x2-x1}x{y2-y1} pixels\n")
            
            # Draw on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{class_name} {conf:.1%}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Save annotated frame
cv2.imwrite("camera_view_detected.jpg", frame)
print("=" * 60)
print("✓ Saved annotated image: camera_view_detected.jpg")
print("\nTo view the images, open File Explorer and navigate to:")
print("C:\\Projects2\\License_Plate_Scanning\\python-service\\")
print()
