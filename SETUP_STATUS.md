# System Setup Complete! ✅

## What I've Done For You

### ✓ Installation Complete

1. **Python Service**
   - ✓ Virtual environment created
   - ✓ All dependencies installed (OpenCV, YOLO, Tesseract, etc.)
   - ✓ Environment file created

2. **Backend API**
   - ✓ Node.js dependencies installed
   - ✓ Uploads directory created
   - ✓ Environment file created

3. **Frontend Dashboard**
   - ✓ Angular dependencies installed
   - ✓ Configuration files ready

4. **Database**
   - ✓ MongoDB service is running

---

## ⚠️ Important: Required Configuration

Before starting the services, you need to configure these items:

### 1. Install Tesseract OCR (REQUIRED)

Tesseract is needed for reading license plate text.

**Download and Install:**
- Go to: https://github.com/UB-Mannheim/tesseract/wiki
- Download the Windows installer
- Install to: `C:\Program Files\Tesseract-OCR`
- **OR** use Chocolatey: `choco install tesseract`

### 2. Set Up Your iPhone Camera

**Install DroidCam on iPhone:**
- Download "DroidCam" from App Store (free)
- Open the app
- Note the IP address shown (e.g., `192.168.1.100:4747`)

**Update Configuration:**
Edit this file: `c:\Projects2\License_Plate_Scanning\python-service\.env`

Find this line:
```
IPHONE_URL=http://192.168.1.100:4747/video
```

Change `192.168.1.100` to YOUR iPhone's IP address.

**Test the connection:**
Open in your browser: `http://YOUR_IPHONE_IP:4747/video`
You should see your camera feed!

---

## 🚀 Starting the System

Once Tesseract is installed and iPhone IP is configured, open **3 PowerShell terminals**:

### Terminal 1: Backend API
```powershell
cd c:\Projects2\License_Plate_Scanning\backend
npm start
```
Wait for: "✓ Connected to MongoDB"

### Terminal 2: Frontend Dashboard
```powershell
cd c:\Projects2\License_Plate_Scanning\frontend
ng serve
```
Wait for: "Angular Live Development Server is listening"

### Terminal 3: Python Detection Service
```powershell
cd c:\Projects2\License_Plate_Scanning\python-service
.\venv\Scripts\Activate.ps1
python main.py --source iphone
```
Wait for: "✓ Connected to iPhone camera"

---

## 🌐 Access the Dashboard

Open your browser: **http://localhost:4200**

---

## 🧪 Quick Test

1. Point your iPhone camera at a license plate
2. Watch Terminal 3 for detection messages
3. Check the dashboard - plates should appear!

---

## 📝 Optional: Use Plate Recognizer API (Better Accuracy)

If you want better OCR accuracy, sign up for a free account:

1. Go to: https://platerecognizer.com
2. Get your API token
3. Edit `python-service\.env`:
   ```
   USE_PLATE_RECOGNIZER=true
   PLATE_RECOGNIZER_TOKEN=your_token_here
   ```

---

## 🔧 Configuration Files Created

All `.env` files have been created with default values:

- `python-service\.env` - Camera URLs and detection settings
- `backend\.env` - MongoDB connection and API settings

You can edit these files to customize the system.

---

## 📚 Next Steps After Starting

1. **Test with printed license plate images**
2. **Adjust confidence threshold** if needed (in `python-service\.env`)
3. **Configure RTSP camera** when ready (switch from iPhone)
4. **Review the dashboard** features (search, filter, manual corrections)

---

## 🆘 Troubleshooting

**If Tesseract not found:**
- Verify it's installed: `Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe"`
- Update path in `python-service\.env` if installed elsewhere

**If camera won't connect:**
- Ensure iPhone and PC are on same WiFi
- Test URL in browser first
- Check Windows Firewall

**If ports are in use:**
- Backend uses port 3000
- Frontend uses port 4200
- Check with: `netstat -ano | findstr :3000`

---

## 🎯 What You Need to Do Right Now

1. **Install Tesseract OCR** (5 minutes)
2. **Set up iPhone camera** with DroidCam (2 minutes)
3. **Update the IP address** in `python-service\.env` (30 seconds)
4. **Start the 3 services** (1 minute)
5. **Open http://localhost:4200** and enjoy! 🎉

---

**Everything is ready! Just complete the configuration steps above and you're good to go!**
