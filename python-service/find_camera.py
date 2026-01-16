import cv2

print("Searching for available cameras...")
print("=" * 60)

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✅ Camera {i}: WORKING - {frame.shape[1]}x{frame.shape[0]}")
        else:
            print(f"⚠️  Camera {i}: Opens but no frames")
        cap.release()
    else:
        print(f"❌ Camera {i}: Not available")

print("=" * 60)
print("\niVCam should be one of the working cameras above.")
