import cv2
import time

print("Testing cameras...")
for i in [0, 1, 2]:
    print(f"\nTrying Camera {i}...")
    cap = cv2.VideoCapture(i)
    time.sleep(1)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✓ Camera {i} WORKING - Got frame {frame.shape}")
        else:
            print(f"✗ Camera {i} opened but can't read frames")
    else:
        print(f"✗ Camera {i} failed to open")
    
    cap.release()
    time.sleep(0.5)
