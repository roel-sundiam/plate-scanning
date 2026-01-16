# License Plate Scanning System - Quick Start Guide

## Installation & Setup

### Prerequisites

Ensure you have the following installed:
- **Python 3.8+** (for detection service)
- **Node.js 18+** (for backend API)
- **MongoDB 5.0+** (for database)
- **Angular CLI 17+** (for frontend)
- **Tesseract OCR** (for text recognition)

### Step 1: Clone or Download the Project

```bash
cd c:\Projects2\License_Plate_Scanning
```

### Step 2: Set Up iPhone Camera (DroidCam)

1. Install **DroidCam** or **IP Webcam** on your iPhone from App Store
2. Open the app and note the IP address (e.g., `192.168.1.100:4747`)
3. Ensure your computer and iPhone are on the same WiFi network
4. Test the stream: Open `http://192.168.1.100:4747/video` in a browser

### Step 3: Install Tesseract OCR (Windows)

1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. Verify installation:
   ```powershell
   & "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
   ```

### Step 4: Set Up Python Detection Service

```powershell
# Navigate to python service directory
cd python-service

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy environment file
Copy-Item .env.example .env

# Edit .env file and update IPHONE_URL with your iPhone's IP
notepad .env
# Change: IPHONE_URL=http://YOUR_IPHONE_IP:4747/video
```

### Step 5: Set Up Backend API

```powershell
# Navigate to backend directory
cd ..\backend

# Install dependencies
npm install

# Copy environment file
Copy-Item .env.example .env

# Create uploads directory
New-Item -ItemType Directory -Path uploads -Force
```

### Step 6: Set Up Frontend Dashboard

```powershell
# Navigate to frontend directory
cd ..\frontend

# Install dependencies
npm install

# Install Angular CLI globally (if not installed)
npm install -g @angular/cli
```

### Step 7: Start MongoDB

#### Option A: MongoDB Installed Locally
```powershell
# Start MongoDB service (if installed as service)
Start-Service MongoDB
```

#### Option B: MongoDB with Docker
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

#### Option C: MongoDB Atlas (Cloud)
1. Create free account at https://www.mongodb.com/atlas
2. Create cluster and get connection string
3. Update `backend\.env` with your connection string

### Step 8: Start All Services

Open **3 separate PowerShell terminals**:

#### Terminal 1: Backend API
```powershell
cd c:\Projects2\License_Plate_Scanning\backend
npm start
```
✓ Backend should start on http://localhost:3000

#### Terminal 2: Frontend Dashboard
```powershell
cd c:\Projects2\License_Plate_Scanning\frontend
ng serve
```
✓ Frontend should start on http://localhost:4200

#### Terminal 3: Python Detection Service
```powershell
cd c:\Projects2\License_Plate_Scanning\python-service
.\venv\Scripts\Activate.ps1
python main.py --source iphone
```
✓ Detection service should connect to camera and start processing

### Step 9: Access the Dashboard

Open your browser and navigate to: **http://localhost:4200**

You should see the dashboard displaying detected license plates in real-time!

---

## Testing the System

### Test with iPhone Camera

1. Ensure iPhone camera app is running
2. Point camera at a license plate or a printed image of one
3. Watch the Python terminal for detections
4. Check the dashboard for new entries

### Test with Sample Image

Create a test script:

```python
# test_detection.py
import cv2
from detector import LicensePlateDetector

detector = LicensePlateDetector()

# Load sample image
image = cv2.imread('sample_plate.jpg')

# Detect plates
plates = detector.detect_plates(image)

for plate in plates:
    x1, y1, x2, y2 = plate['bbox']
    plate_img = image[y1:y2, x1:x2]
    text = detector.extract_text(plate_img)
    print(f"Detected: {text} (confidence: {plate['confidence']})")
```

---

## Configuration

### Python Service Configuration

Edit `python-service\.env`:

```env
# Your iPhone camera URL
IPHONE_URL=http://192.168.1.100:4747/video

# Backend API URL
API_URL=http://localhost:3000/api/plates

# Detection settings
CONFIDENCE_THRESHOLD=0.5
DUPLICATE_WINDOW_SECONDS=60
GATE_IDENTIFIER=gate_01

# Performance settings
FRAME_SKIP=3
RESIZE_WIDTH=640

# Tesseract path (Windows)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Backend Configuration

Edit `backend\.env`:

```env
PORT=3000
MONGODB_URI=mongodb://localhost:27017/license_plates
DUPLICATE_WINDOW=60
IMAGE_STORAGE_PATH=./uploads
```

### Frontend Configuration

Edit `frontend\src\environments\environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api'
};
```

---

## Common Issues & Solutions

### Issue: Python can't connect to iPhone camera

**Solution:**
- Ensure both devices are on same WiFi
- Check firewall settings
- Test URL in browser first: `http://IPHONE_IP:4747/video`
- Try restarting the camera app

### Issue: Tesseract not found

**Solution:**
```powershell
# Check if Tesseract is installed
Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"

# If not installed, download from:
# https://github.com/UB-Mannheim/tesseract/wiki
```

### Issue: MongoDB connection failed

**Solution:**
```powershell
# Check if MongoDB is running
Get-Service MongoDB

# Or start MongoDB manually
mongod --dbpath C:\data\db
```

### Issue: Port already in use

**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :3000

# Kill the process
Stop-Process -Id <PID> -Force

# Or change the port in .env files
```

### Issue: Poor OCR accuracy

**Solutions:**
- Increase lighting conditions
- Adjust camera angle and distance
- Lower `CONFIDENCE_THRESHOLD` in config
- Consider using Plate Recognizer API:
  ```env
  USE_PLATE_RECOGNIZER=true
  PLATE_RECOGNIZER_TOKEN=your_token_here
  ```

---

## Switching to RTSP Camera

When you're ready to use a real IP camera:

1. Update `python-service\.env`:
   ```env
   RTSP_URL=rtsp://username:password@camera-ip:554/stream
   ```

2. Start with RTSP source:
   ```powershell
   python main.py --source rtsp
   ```

That's it! The system will seamlessly switch to the RTSP camera.

---

## Docker Deployment (Alternative)

For a simplified deployment using Docker:

```powershell
# Make sure Docker Desktop is running
docker --version

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

Access:
- Frontend: http://localhost:4200
- Backend API: http://localhost:3000
- MongoDB: localhost:27017

---

## API Testing

Test the API directly:

```powershell
# Health check
curl http://localhost:3000/health

# Get all plates
curl http://localhost:3000/api/plates

# Search for a plate
curl http://localhost:3000/api/plates/search/ABC123

# Get statistics
curl http://localhost:3000/api/plates/statistics
```

---

## Development Mode

### Backend with Auto-Reload
```powershell
cd backend
npm run dev
```

### Frontend with Live Reload
```powershell
cd frontend
ng serve --open
```

### Python with Debug Mode
```powershell
cd python-service
$env:DEBUG_MODE="true"
$env:SHOW_VIDEO_WINDOW="true"
python main.py --source iphone
```

---

## Next Steps

1. **Improve Accuracy**: Train custom YOLO model with local plate samples
2. **Add Features**: Implement whitelist/blacklist functionality
3. **Add Notifications**: Real-time alerts for specific plates
4. **Mobile App**: Create mobile interface for guards
5. **Analytics**: Add reporting and analytics dashboard
6. **Access Control**: Integrate with gate control systems

---

## Support

If you encounter issues:

1. Check the logs in each terminal
2. Verify all environment variables are set correctly
3. Ensure all services are running
4. Check network connectivity between services

For additional help, refer to the main [README.md](README.md) file.

---

**Congratulations!** 🎉 Your license plate scanning system is now running!
