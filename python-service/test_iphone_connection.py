import cv2
import sys

# Test connection to iPhone camera
iphone_url = "http://192.168.68.101:4747/video"

print(f"Testing connection to: {iphone_url}")
print("Please wait...")

cap = cv2.VideoCapture(iphone_url)

if not cap.isOpened():
    print("❌ ERROR: Cannot open camera connection")
    print("\nTroubleshooting:")
    print("1. Make sure DroidCam app is open on your iPhone")
    print("2. Press the START button in DroidCam (camera should be active)")
    print("3. Check that both devices are on the same WiFi")
    sys.exit(1)

# Try to read a frame
ret, frame = cap.read()

if ret and frame is not None:
    print("✅ SUCCESS! Camera is connected!")
    print(f"   Frame size: {frame.shape[1]}x{frame.shape[0]}")
    print("\nCamera is working! You can now run the detection service.")
else:
    print("❌ ERROR: Can connect but cannot read frames")
    print("   Try restarting the DroidCam app")

cap.release()
