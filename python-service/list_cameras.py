"""List all available camera devices"""
import cv2

print("\n🔍 Scanning for camera devices...\n")
print("=" * 50)

available_cameras = []

# Check devices 0-5
for i in range(6):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            height, width = frame.shape[:2]
            available_cameras.append(i)
            print(f"✓ Device {i}: {width}x{height} pixels")
        cap.release()

print("=" * 50)

if available_cameras:
    print(f"\n✓ Found {len(available_cameras)} camera(s): {available_cameras}")
    print("\nTo use a specific camera, run:")
    for cam in available_cameras:
        if cam == 0:
            print(f"  python main.py --source webcam (device {cam})")
        else:
            print(f"  python main.py --source {cam}")
else:
    print("\n❌ No cameras found!")
    print("\nTroubleshooting:")
    print("1. Make sure DroidCam Client is running on PC")
    print("2. Check that it shows 'Connected' status")
    print("3. Try closing and reopening DroidCam Client")

print()
