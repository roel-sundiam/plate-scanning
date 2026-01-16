# License Plate Detection - Testing Guide

## Prerequisites Checklist

Before testing the detection system, ensure you have:

- [x] Backend API running on port 3000
- [x] Frontend dashboard running on port 4200
- [x] MongoDB running
- [x] iPhone camera with DroidCam (192.168.68.101:4747)
- [ ] **Tesseract OCR installed** ⚠️ Required!

## Step 1: Install Tesseract OCR (Required)

You downloaded the Tesseract installer. Now you need to install it:

### Installation Steps:

1. **Run the installer:**
   ```powershell
   .\tesseract_installer.exe
   ```

2. **During installation:**
   - Choose installation path: `C:\Program Files\Tesseract-OCR`
   - Make sure to check "Add to PATH" option
   - Install additional language data if prompted

3. **Verify installation:**
   ```powershell
   tesseract --version
   ```
   
   You should see something like:
   ```
   tesseract 5.3.3
   ```

4. **If not in PATH, update the Python service config manually:**
   Edit `python-service/.env` and set:
   ```
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

---

## Step 2: Verify Your Camera Connection

Make sure your iPhone camera is streaming:

```powershell
# Test camera connectivity
Invoke-WebRequest -Uri "http://192.168.68.101:4747/video" -TimeoutSec 5 -UseBasicParsing | Select-Object StatusCode
```

**Expected:** `StatusCode: 200`

**If camera fails:**
- Open DroidCam on your iPhone
- Verify WiFi connection (same network as PC)
- Check IP address matches: 192.168.68.101
- Try accessing http://192.168.68.101:4747/video in browser

---

## Step 3: Start the Detection Service

Once Tesseract is installed, start the Python detection service:

```powershell
cd c:\Projects2\License_Plate_Scanning\python-service
.\venv\Scripts\Activate.ps1
python main.py --source iphone
```

### What You Should See:

```
Loading YOLO model...
Camera source: iPhone (DroidCam)
Connecting to http://192.168.68.101:4747/video...
Camera connected successfully!
Starting detection...
```

### Command Options:

- `--source iphone` - Use iPhone camera via DroidCam
- `--source rtsp` - Use RTSP camera (configure RTSP_URL in .env)
- `--source webcam` - Use built-in webcam (index 0)
- `--debug` - Show detection visualization window

**Example with debug window:**
```powershell
python main.py --source iphone --debug
```

---

## Step 4: Monitor Live Detections

Open your browser to watch real-time detections:

### Dashboard Views:

1. **Statistics Dashboard:** http://localhost:4200
   - View total detections, unique plates, confidence scores
   - See most frequent plates
   - Monitor recent activity

2. **Plates List:** http://localhost:4200/plates
   - Detailed list of all detections
   - Search and filter capabilities
   - View detection images
   - Edit/verify plates

### What Happens During Detection:

1. **Camera captures frame** (30 FPS)
2. **YOLO detects license plate region** in the frame
3. **Tesseract performs OCR** on detected region
4. **System validates plate format** (optional)
5. **Duplicate check** - Ignores same plate within 60 seconds
6. **Saves to MongoDB** with:
   - Plate number
   - Confidence score
   - Timestamp
   - Gate ID
   - Cropped image
7. **Dashboard updates automatically** via API polling

---

## Step 5: Test with Sample Plates

### Option A: Use Physical License Plates

1. Hold a license plate in front of your iPhone camera
2. Keep it well-lit and at a reasonable distance (1-3 meters)
3. Hold steady for 1-2 seconds
4. Watch the console for detection logs
5. Check dashboard for new entry

### Option B: Use Printed Images

1. Print high-quality images of license plates
2. Display them to the camera
3. Ensure good lighting and focus

### Option C: Use Test Images

```powershell
# Test with static image (if you have plate images)
python main.py --source image --image-path "path/to/plate.jpg"
```

---

## Step 6: Verify Detection Results

### Check Console Output:

```
[2026-01-15 14:35:22] Plate detected: ABC123 (confidence: 0.92)
[2026-01-15 14:35:22] Saved to database: ABC123 at Gate-1
```

### Check Dashboard:

1. Open http://localhost:4200/plates
2. Look for new entries with:
   - Detected plate number
   - Confidence percentage (color-coded)
   - Timestamp
   - Gate ID
   - Thumbnail image

### Check Database Directly:

```powershell
# Using MongoDB shell or Compass
# Connect to: mongodb://localhost:27017/license_plates
# Collection: plates
```

---

## Troubleshooting Common Issues

### 1. No Detections Appearing

**Check:**
- Python service is running without errors
- Camera feed is active (green light in console)
- Backend API is responding: http://localhost:3000/api/plates
- Plates are visible and well-lit in camera frame

**Solution:**
```powershell
# Restart detection service with debug mode
python main.py --source iphone --debug
```

### 2. Low Confidence Scores

**Causes:**
- Poor lighting
- Plate too far or too close
- Motion blur
- Dirty/damaged plates

**Solution:**
- Improve lighting conditions
- Adjust camera distance (1.5-2.5 meters optimal)
- Keep plates steady
- Clean camera lens

### 3. Wrong Plate Numbers (OCR Errors)

**Common misreads:**
- O ↔ 0 (letter O vs zero)
- I ↔ 1 (letter I vs one)
- S ↔ 5
- B ↔ 8

**Solution:**
- Use manual verification in dashboard
- Edit incorrect plates via UI
- Improve image quality
- Fine-tune Tesseract parameters in `detector.py`

### 4. Tesseract Not Found Error

```
Error: Tesseract is not installed or not in PATH
```

**Solution:**
```powershell
# Add Tesseract to PATH manually
$env:PATH += ";C:\Program Files\Tesseract-OCR"

# Or set in .env file:
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 5. Camera Connection Failed

```
Error: Could not connect to camera
```

**Solution:**
```powershell
# Test camera URL
curl http://192.168.68.101:4747/video

# Update .env if IP changed
# IPHONE_URL=http://YOUR_NEW_IP:4747/video
```

### 6. Duplicate Plates Not Showing

This is **normal behavior**! The system filters duplicates within 60 seconds to avoid spam.

**To change duplicate window:**
Edit `backend/.env`:
```
DUPLICATE_WINDOW=60  # seconds (change to 30 for faster re-detection)
```

---

## Performance Optimization

### Adjust Detection Settings

Edit `python-service/config.py`:

```python
# Detection confidence threshold (0.0 - 1.0)
CONFIDENCE_THRESHOLD = 0.7  # Lower = more detections, less accurate

# Frame processing rate
PROCESS_EVERY_N_FRAMES = 3  # Process every 3rd frame for performance

# Image preprocessing
RESIZE_WIDTH = 640  # Lower for faster processing
```

### Monitor Resource Usage

```powershell
# Check CPU/GPU usage
Get-Process python | Select-Object CPU, WorkingSet
```

---

## Real-World Testing Scenarios

### Scenario 1: Guard House Gate

1. Mount iPhone at gate entrance (2-3 meters height)
2. Point camera at vehicle license plate area
3. Ensure good lighting (add LED if needed)
4. Test with approaching vehicles at slow speed (5-10 km/h)

### Scenario 2: Parking Entry

1. Position camera at parking barrier
2. Vehicles should stop briefly (2-3 seconds)
3. Plate should be front-facing
4. Distance: 1.5-2.5 meters optimal

### Scenario 3: Multiple Gates

Edit `python-service/.env` for each gate:
```
GATE_ID=Gate-Main
# or Gate-North, Gate-South, Gate-Parking, etc.
```

---

## Expected Detection Rates

**Good Conditions (Daylight, Clean Plates):**
- Detection Rate: 90-95%
- False Positives: <5%
- Average Confidence: 85-92%

**Medium Conditions (Indoor, Normal Lighting):**
- Detection Rate: 75-85%
- False Positives: 5-10%
- Average Confidence: 75-85%

**Poor Conditions (Night, Dirty Plates):**
- Detection Rate: 50-70%
- False Positives: 10-20%
- Average Confidence: 60-75%

---

## Next Steps After Testing

1. **Review Results:** Check detection accuracy in dashboard
2. **Adjust Settings:** Fine-tune confidence thresholds
3. **Train Model:** Collect failed detections for model improvement
4. **Add Notifications:** Implement alerts for specific plates
5. **Database Backup:** Set up regular MongoDB backups
6. **Deploy Production:** Use deployment guide for 24/7 operation

---

## Quick Test Commands

### Full System Check:
```powershell
# 1. Check backend
curl http://localhost:3000/api/plates/health

# 2. Check MongoDB
mongosh mongodb://localhost:27017/license_plates --eval "db.plates.countDocuments()"

# 3. Check camera
Invoke-WebRequest http://192.168.68.101:4747/video -UseBasicParsing | Select StatusCode

# 4. Start detection (in python-service directory)
python main.py --source iphone --debug
```

### View Latest Detections:
```powershell
# API endpoint
curl http://localhost:3000/api/plates?limit=5

# Dashboard
start http://localhost:4200/plates
```

---

## Support & Debugging

**Enable detailed logging:**
Edit `python-service/main.py` to set logging level:
```python
logging.basicConfig(level=logging.DEBUG)
```

**Check logs:**
- Python service: Console output
- Backend API: `backend/logs/` (if configured)
- Frontend: Browser DevTools Console (F12)

**Common log locations:**
- Python errors: Console where `python main.py` runs
- Backend errors: Terminal where `npm start` runs in backend/
- Frontend errors: Browser console (F12 → Console tab)

---

## Success Indicators

✅ **System is working correctly when:**
- Python console shows "Camera connected successfully"
- Detections appear in console: "Plate detected: ABC123"
- Dashboard updates with new plates within 5 seconds
- Confidence scores are >70%
- Images are saved and viewable in dashboard
- No duplicate detections within 60 seconds
- API responds at http://localhost:3000/api/plates

**Ready to test! Start with Step 1: Installing Tesseract OCR** 🚀
