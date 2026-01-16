# 🚀 Quick Testing Guide - License Plate Scanner

## ✅ What's Working Now
- ✅ Backend API running on http://localhost:3000
- ✅ Angular Dashboard running on http://localhost:4200
- ✅ MongoDB connected and storing data
- ✅ iPhone camera connected (192.168.68.101:4747)
- ✅ YOLO model downloaded and loaded
- ✅ Python detection service can process video frames

## ⚠️ Current Issue
- ❌ Tesseract OCR not found (needed to read plate text)

---

## 🎯 Option 1: Quick Test WITHOUT Tesseract (Recommended for Testing)

You can test the detection system without OCR by using test images or simple patterns.

### Test with Simulated Plates:

```powershell
# Add a manual plate detection via API
curl http://localhost:3000/api/plates -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"plateNumber":"ABC1234","gateId":"gate_01","confidence":0.95}'
```

Then check the dashboard at http://localhost:4200 to see it appear!

---

## 🎯 Option 2: Complete Setup WITH Tesseract OCR

### Step 1: Locate Your Tesseract Installation

Run this to find where you installed Tesseract:

```powershell
# Search for tesseract.exe
Get-ChildItem "C:\" -Filter "tesseract.exe" -Recurse -ErrorAction SilentlyContinue -Depth 4 | Select-Object FullName
```

Common locations:
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Users\YourName\AppData\Local\Programs\Tesseract-OCR\tesseract.exe`
- `C:\Tesseract-OCR\tesseract.exe`

### Step 2: Update Configuration

Once you find it, update the `.env` file:

```powershell
# Example if found at custom location
$tesseractPath = "C:\YOUR\PATH\tesseract.exe"  # Replace with your actual path

# Update .env file
(Get-Content "python-service\.env") -replace 'TESSERACT_CMD=.*', "TESSERACT_CMD=$tesseractPath" | Set-Content "python-service\.env"
```

### Step 3: Install Fresh Tesseract (If Not Found)

```powershell
# Download and install Tesseract
winget install UB-Mannheim.TesseractOCR

# Or install via installer
Start-Process "tesseract_installer.exe" -Wait

# Then update .env with the installation path
```

---

## 🎬 Testing Detection

### Method 1: Live iPhone Camera Test

```powershell
# Make sure DroidCam is running on your iPhone
# Then start the detection service:

cd c:\Projects2\License_Plate_Scanning\python-service
python main.py --source iphone
```

**What to do:**
1. Point your iPhone camera at a license plate (or printed image of one)
2. Watch the console for detections
3. Check dashboard at http://localhost:4200 for new entries

### Method 2: Webcam Test (If Available)

```powershell
cd c:\Projects2\License_Plate_Scanning\python-service
python main.py --source webcam
```

### Method 3: Test with Image File

```powershell
cd c:\Projects2\License_Plate_Scanning\python-service
python main.py --source test-plate-image.jpg
```

---

## 📊 Monitoring Results

### Check the Dashboard
- Open: http://localhost:4200
- View statistics and recent detections
- Navigate to "Plates" tab for full list

### Check the API Directly
```powershell
# Get all plates
curl http://localhost:3000/api/plates

# Get statistics
curl http://localhost:3000/api/plates/statistics

# Search for specific plate
curl http://localhost:3000/api/plates/search/ABC123
```

### Check MongoDB
```powershell
# Connect to MongoDB
mongosh
use license_plates
db.plates.find().pretty()
```

---

## 🔧 Troubleshooting

### "Tesseract not found" Error
- Tesseract OCR is not installed or path is wrong
- Solutions:
  1. Install Tesseract: `winget install UB-Mannheim.TesseractOCR`
  2. Update `python-service\.env` with correct path
  3. Or test without OCR using manual API calls

### "Cannot connect to camera" Error
- Make sure DroidCam is running on your iPhone
- Check WiFi connection (both devices on same network)
- Test URL in browser: http://192.168.68.101:4747/video
- Update IP in `python-service\.env` if changed

### "ModuleNotFoundError" Errors
```powershell
# Reinstall Python dependencies
cd python-service
python -m pip install -r requirements.txt --upgrade
```

### Port Already in Use
```powershell
# Stop existing processes
Get-Process node,python | Stop-Process -Force

# Or change ports in .env files
```

---

## 🎯 Next Steps After Testing

1. **Fine-tune Detection**
   - Adjust `CONFIDENCE_THRESHOLD` in `.env` (currently 0.5)
   - Modify `FRAME_SKIP` for performance vs accuracy

2. **Add More Gates**
   - Update `GATE_IDENTIFIER` for different entrances
   - Run multiple detection instances

3. **Enhance Frontend**
   - Add manual plate entry form
   - Add plate editing capabilities
   - Export reports

4. **Production Deployment**
   - See `DEPLOYMENT_GUIDE.md`
   - Use proper RTSP cameras
   - Set up reverse proxy (nginx)
   - Add authentication

---

## 📝 Quick Reference Commands

```powershell
# Start Backend
cd backend
npm start

# Start Frontend
cd frontend
npm start

# Start Detection (iPhone)
cd python-service
python main.py --source iphone

# View Logs
Get-Content backend\logs\app.log -Tail 50 -Wait

# Check System Status
# Backend: http://localhost:3000/health
# Frontend: http://localhost:4200
# MongoDB: mongosh --eval "db.adminCommand('ping')"
```

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Dashboard shows statistics updating
- ✅ New plates appear in the plates list
- ✅ Console shows "Plate detected" messages
- ✅ Images saved in `backend/uploads/plates/`
- ✅ MongoDB has plate records

Happy testing! 🚗📸
