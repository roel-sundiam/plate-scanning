# Cloud Deployment Guide

## Architecture
```
[Local PC] → Python Detection → [Render API] → [MongoDB Atlas] ← [Netlify Frontend]
```

## Step 1: Deploy Backend to Render

1. **Go to**: https://render.com
2. **Sign in** with GitHub
3. **New Web Service**
4. **Connect repository**: `roel-sundiam/plate-scanning`
5. **Configure**:
   - Name: `license-plate-backend`
   - Root Directory: `backend`
   - Environment: `Node`
   - Build Command: `npm install`
   - Start Command: `npm start`
6. **Environment Variables** (Add these):
   ```
   NODE_ENV=production
   PORT=3000
   MONGODB_URI=mongodb+srv://admin:Helenbot04117777!1@mydb.zxr9i5k.mongodb.net/PLATES
   CORS_ORIGIN=*
   ```
7. **Create Web Service**
8. **Copy your Render URL**: `https://your-app-name.onrender.com`

## Step 2: Deploy Frontend to Netlify

1. **Go to**: https://app.netlify.com
2. **Sign in** with GitHub
3. **Add new site** → Import from Git
4. **Connect repository**: `roel-sundiam/plate-scanning`
5. **Build settings**:
   - Base directory: `frontend`
   - Build command: `npm install && npm run build`
   - Publish directory: `frontend/dist/browser`
6. **Deploy site**
7. **Copy your Netlify URL**: `https://your-app-name.netlify.app`

## Step 3: Update Environment Variables

### On Netlify (Frontend):
1. Go to **Site settings** → **Environment variables**
2. Add:
   ```
   API_URL=https://your-render-app.onrender.com/api
   ```
3. **Redeploy site**

### Local Python Service:
Update `python-service/.env`:
```env
API_URL=https://your-render-app.onrender.com/api/plates
GATE_IDENTIFIER=gate_01
```

## Step 4: Run Local Detection

On your PC:
```powershell
cd C:\Projects2\License_Plate_Scanning\python-service
python test_real_plate.py 1
```

This will:
- ✅ Detect plates locally via iPhone camera
- ✅ Send detections to Render API
- ✅ Data appears on Netlify dashboard automatically

## Important Notes

- **Backend**: Free tier may sleep after inactivity (wakes on first request)
- **Frontend**: Always active on Netlify
- **Python Service**: MUST run locally (needs camera access)
- **Database**: Already on MongoDB Atlas ✅

## Testing the Setup

1. **Test Backend API**:
   ```
   https://your-render-app.onrender.com/health
   ```

2. **Open Frontend**:
   ```
   https://your-app-name.netlify.app
   ```

3. **Start Local Detection**:
   - Point iPhone camera at plate
   - Watch dashboard update in real-time

## Cost
- **Render**: Free (750 hours/month)
- **Netlify**: Free (100GB bandwidth/month)
- **MongoDB Atlas**: Free (M0 cluster)
- **Total**: $0/month ✅
