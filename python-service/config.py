import os
from dotenv import load_dotenv

load_dotenv()

# Camera Configuration
IPHONE_URL = os.getenv("IPHONE_URL", "http://192.168.1.100:4747/video")
RTSP_URL = os.getenv("RTSP_URL", "rtsp://admin:password@192.168.1.50:554/stream")

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:3000/api/plates")

# Detection Settings
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
DUPLICATE_WINDOW_SECONDS = int(os.getenv("DUPLICATE_WINDOW_SECONDS", "60"))
GATE_IDENTIFIER = os.getenv("GATE_IDENTIFIER", "gate_01")

# Frame Processing
FRAME_SKIP = int(os.getenv("FRAME_SKIP", "3"))  # Process every Nth frame
RESIZE_WIDTH = int(os.getenv("RESIZE_WIDTH", "640"))

# OCR Settings
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")  # Windows
# TESSERACT_CMD = "/usr/bin/tesseract"  # Linux

# Plate Recognizer API (Optional)
USE_PLATE_RECOGNIZER = os.getenv("USE_PLATE_RECOGNIZER", "false").lower() == "true"
PLATE_RECOGNIZER_TOKEN = os.getenv("PLATE_RECOGNIZER_TOKEN", "")

# OCR.space API (Fallback OCR)
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "")
USE_OCR_SPACE_FALLBACK = os.getenv("USE_OCR_SPACE_FALLBACK", "true").lower() == "true"

# Image Storage
SAVE_SNAPSHOTS = os.getenv("SAVE_SNAPSHOTS", "true").lower() == "true"
SNAPSHOT_DIR = os.getenv("SNAPSHOT_DIR", "./snapshots")

# Model Paths
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")  # Will download automatically

# Debug Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"
SHOW_VIDEO_WINDOW = os.getenv("SHOW_VIDEO_WINDOW", "false").lower() == "true"
