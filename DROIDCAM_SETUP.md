# Quick Setup Guide - DroidCam & Testing

## Step 1: Install DroidCam on iPhone (2 minutes)

1. **Open App Store** on your iPhone
2. **Search for**: "DroidCam Webcam"
3. **Download and install** the free version
4. **Open the app**

You'll see a screen showing:
```
WiFi IP: http://192.168.X.XXX:4747
```

**Write down this IP address!** (Example: 192.168.1.105:4747)

---

## Step 2: Test Camera Connection

Once you have the IP address from DroidCam:

1. **Make sure your iPhone and PC are on the same WiFi network**
2. **Open your web browser** (Chrome, Edge, etc.)
3. **Type this URL**: `http://YOUR_IPHONE_IP:4747/video`
   - Example: `http://192.168.1.105:4747/video`
4. **You should see your iPhone camera feed!**

If you see the camera feed in your browser, you're ready! ✓

---

## Step 3: Quick Start Script

I'll create a start script that will:
- Update the iPhone IP automatically
- Start all 3 services for you
- Open the dashboard

Just tell me your iPhone IP address and I'll set everything up!

---

## Alternative: Test Without Camera First

If you want to test the system first without the camera, I can:
1. Start the backend API
2. Start the frontend dashboard
3. Show you the interface
4. Add some test data manually

Then later, when you have DroidCam set up, we'll connect the camera.

**What would you like to do?**
- A) Set up DroidCam now and get the IP (tell me when ready)
- B) Start without camera and test the dashboard first
