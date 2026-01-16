# Test iPhone Camera Connection for License Plate Detection
# Usage: .\test-iphone-camera.ps1 -IPhoneIP "192.168.1.100"

param(
    [string]$IPhoneIP = ""
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "iPhone Camera Test - License Plate Detection" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Get iPhone IP if not provided
if ($IPhoneIP -eq "") {
    Write-Host "📱 Step 1: Get your iPhone IP from DroidCam app" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Open DroidCam on your iPhone and look for:" -ForegroundColor White
    Write-Host "  WiFi IP: http://192.168.X.XXX:4747" -ForegroundColor White
    Write-Host ""
    $IPhoneIP = Read-Host "Enter the IP address (e.g., 192.168.1.100)"
}

# Remove http:// and port if included
$IPhoneIP = $IPhoneIP -replace "http://", "" -replace ":4747", "" -replace "/video", ""

$FullURL = "http://${IPhoneIP}:4747/video"

Write-Host ""
Write-Host "🔍 Testing connection to: $FullURL" -ForegroundColor Cyan
Write-Host ""

# Test if iPhone camera is accessible
try {
    $response = Invoke-WebRequest -Uri $FullURL -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ SUCCESS! iPhone camera is accessible!" -ForegroundColor Green
        Write-Host ""
    }
} catch {
    Write-Host "❌ ERROR: Cannot connect to iPhone camera" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Make sure DroidCam app is open on your iPhone" -ForegroundColor White
    Write-Host "  2. Press the 'Start' button in DroidCam (camera icon should be active)" -ForegroundColor White
    Write-Host "  3. Verify iPhone and PC are on the same WiFi network" -ForegroundColor White
    Write-Host "  4. Try opening this URL in your browser: $FullURL" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Update Python service configuration
Write-Host "📝 Updating camera configuration..." -ForegroundColor Cyan

$envContent = @"
# Camera Configuration
IPHONE_URL=$FullURL

# API Configuration
API_URL=http://localhost:3000/api/plates

# Detection Settings
CONFIDENCE_THRESHOLD=0.5
DUPLICATE_WINDOW_SECONDS=60
GATE_IDENTIFIER=gate_01

# Frame Processing
FRAME_SKIP=3
RESIZE_WIDTH=640

# OCR Settings
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Image Storage
SAVE_SNAPSHOTS=true
SNAPSHOT_DIR=./snapshots

# Model Paths
YOLO_MODEL=yolov8n.pt

# Debug Settings
DEBUG_MODE=true
SHOW_VIDEO_WINDOW=true
"@

$envContent | Out-File -FilePath "python-service\.env" -Encoding UTF8
Write-Host "✅ Configuration updated!" -ForegroundColor Green
Write-Host ""

# Check if services are running
Write-Host "🔍 Checking services..." -ForegroundColor Cyan
Write-Host ""

$backendRunning = $false
$frontendRunning = $false

try {
    $null = Invoke-WebRequest -Uri "http://localhost:3000/api/plates" -TimeoutSec 2 -UseBasicParsing
    $backendRunning = $true
    Write-Host "✅ Backend API is running (http://localhost:3000)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend API is not running" -ForegroundColor Yellow
}

try {
    $null = Invoke-WebRequest -Uri "http://localhost:4200" -TimeoutSec 2 -UseBasicParsing
    $frontendRunning = $true
    Write-Host "✅ Frontend Dashboard is running (http://localhost:4200)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Frontend Dashboard is not running" -ForegroundColor Yellow
}

Write-Host ""

if (-not $backendRunning -or -not $frontendRunning) {
    Write-Host "❗ Starting required services..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run this command to start all services:" -ForegroundColor Cyan
    Write-Host "  .\start.ps1" -ForegroundColor White
    Write-Host ""
    $startNow = Read-Host "Do you want to start services now? (y/n)"
    
    if ($startNow -eq "y" -or $startNow -eq "Y") {
        Write-Host ""
        Write-Host "Starting services... This will take a moment..." -ForegroundColor Cyan
        Start-Process powershell -ArgumentList "-NoExit", "-File", ".\start.ps1"
        Start-Sleep -Seconds 15
    } else {
        Write-Host ""
        Write-Host "Please start services first, then run:" -ForegroundColor Yellow
        Write-Host "  python python-service\main.py --source iphone" -ForegroundColor White
        exit 0
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🎬 Ready to Start Detection!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open Dashboard: http://localhost:4200" -ForegroundColor White
Write-Host "  2. Run the detection service:" -ForegroundColor White
Write-Host ""
Write-Host "     cd python-service" -ForegroundColor Cyan
Write-Host "     python main.py --source iphone" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Point your iPhone camera at a license plate" -ForegroundColor White
Write-Host "  4. Watch for detections in the console and dashboard!" -ForegroundColor White
Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  - Keep DroidCam app open on your iPhone" -ForegroundColor White
Write-Host "  - Good lighting helps detection accuracy" -ForegroundColor White
Write-Host "  - Hold steady for a few seconds" -ForegroundColor White
Write-Host "  - If no detections, try a printed license plate image" -ForegroundColor White
Write-Host ""

# Ask if user wants to start detection now
$startDetection = Read-Host "Start detection service now? (y/n)"

if ($startDetection -eq "y" -or $startDetection -eq "Y") {
    Write-Host ""
    Write-Host "Starting license plate detection..." -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    
    Set-Location python-service
    python main.py --source iphone
}
