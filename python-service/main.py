#!/usr/bin/env python3
"""
License Plate Scanner - Main Entry Point

This script captures video from a camera source (iPhone, RTSP, or webcam),
detects license plates, performs OCR, and sends results to the backend API.
"""

import cv2
import argparse
import time
import requests
from datetime import datetime

from camera_sources import get_camera_source
from detector import LicensePlateDetector
from config import (
    API_URL,
    GATE_IDENTIFIER,
    DUPLICATE_WINDOW_SECONDS,
    FRAME_SKIP,
    RESIZE_WIDTH,
    DEBUG_MODE,
    SHOW_VIDEO_WINDOW
)


def send_to_api(plate_data):
    """Send detected plate to backend API"""
    try:
        response = requests.post(API_URL, json=plate_data, timeout=5)
        
        if response.status_code in [200, 201]:
            print(f"  ✓ Sent to API: {plate_data['plateNumber']}")
            return True
        else:
            print(f"  ⚠ API error ({response.status_code}): {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"  ⚠ API connection error: {e}")
        return False


def process_video_stream(camera_source, detector):
    """Main video processing loop"""
    
    print("\n" + "="*60)
    print("🎥 License Plate Scanner Started")
    print("="*60)
    print(f"Gate ID: {GATE_IDENTIFIER}")
    print(f"API URL: {API_URL}")
    print(f"Duplicate window: {DUPLICATE_WINDOW_SECONDS}s")
    print(f"Frame skip: {FRAME_SKIP}")
    print("Press 'q' to quit")
    print("="*60 + "\n")
    
    frame_count = 0
    detection_count = 0
    
    try:
        while camera_source.is_opened():
            frame = camera_source.get_frame()
            
            if frame is None:
                print("⚠ Failed to grab frame, retrying...")
                time.sleep(1)
                continue
            
            frame_count += 1
            
            # Process every Nth frame
            if frame_count % FRAME_SKIP != 0:
                continue
            
            # Resize frame for faster processing
            height, width = frame.shape[:2]
            if width > RESIZE_WIDTH:
                scale = RESIZE_WIDTH / width
                frame = cv2.resize(frame, None, fx=scale, fy=scale)
            
            # Detect license plates
            plates = detector.detect_plates(frame)
            
            if plates:
                plate_texts = []
                
                for plate in plates:
                    x1, y1, x2, y2 = plate['bbox']
                    confidence = plate['confidence']
                    
                    # Extract plate region
                    plate_img = frame[y1:y2, x1:x2]
                    
                    if plate_img.size == 0:
                        continue
                    
                    # Perform OCR
                    plate_text = detector.extract_text(plate_img)
                    plate_texts.append(plate_text)
                    
                    if plate_text:
                        # Check for duplicates
                        if detector.is_duplicate(plate_text, DUPLICATE_WINDOW_SECONDS):
                            if DEBUG_MODE:
                                print(f"  ⊘ Duplicate: {plate_text} (skipped)")
                            continue
                        
                        # New detection
                        detection_count += 1
                        print(f"\n[{detection_count}] 🚗 Detected: {plate_text} (confidence: {confidence:.2f})")
                        
                        # Save snapshot
                        snapshot_path = detector.save_snapshot(frame.copy(), plate_text, plate['bbox'])
                        
                        # Prepare data for API
                        plate_data = {
                            'plateNumber': plate_text,
                            'gateId': GATE_IDENTIFIER,
                            'confidence': float(confidence),
                            'timestamp': datetime.now().isoformat(),
                        }
                        
                        # Add image if snapshot was saved
                        if snapshot_path:
                            with open(snapshot_path, 'rb') as f:
                                import base64
                                plate_data['image'] = base64.b64encode(f.read()).decode('utf-8')
                        
                        # Send to API
                        send_to_api(plate_data)
                
                # Annotate frame
                if SHOW_VIDEO_WINDOW:
                    frame = detector.annotate_frame(frame, plates, plate_texts)
            
            # Display video (optional)
            if SHOW_VIDEO_WINDOW:
                # Add info overlay
                cv2.putText(frame, f"Frame: {frame_count} | Detections: {detection_count}",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow('License Plate Scanner', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n⏹ Stopping...")
                    break
    
    except KeyboardInterrupt:
        print("\n⏹ Interrupted by user")
    
    finally:
        camera_source.release()
        cv2.destroyAllWindows()
        
        print("\n" + "="*60)
        print(f"📊 Session Summary")
        print("="*60)
        print(f"Frames processed: {frame_count}")
        print(f"Plates detected: {detection_count}")
        print("="*60)


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(description='License Plate Scanner')
    parser.add_argument(
        '--source',
        type=str,
        default='iphone',
        choices=['iphone', 'rtsp', 'webcam'],
        help='Camera source type'
    )
    parser.add_argument(
        '--url',
        type=str,
        help='Custom camera URL (for iPhone or RTSP)'
    )
    parser.add_argument(
        '--device',
        type=int,
        default=0,
        help='Webcam device ID'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize camera source
        if args.url:
            camera = get_camera_source(args.source, url=args.url)
        elif args.source == 'webcam':
            camera = get_camera_source(args.source, device_id=args.device)
        else:
            camera = get_camera_source(args.source)
        
        # Initialize detector
        detector = LicensePlateDetector()
        
        # Start processing
        process_video_stream(camera, detector)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
