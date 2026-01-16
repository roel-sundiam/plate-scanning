# License Plate Scanner - Quick Start
# This script starts all services automatically

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "License Plate Scanner - Starting..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test camera connection first
Write-Host "[1/4] Testing iPhone camera connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://192.168.68.101:4747/video" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Camera connected successfully!" -ForegroundColor Green
} catch {
    Write-Host "⚠ Warning: Cannot connect to iPhone camera at 192.168.68.101:4747" -ForegroundColor Red
    Write-Host "  Make sure:" -ForegroundColor Yellow
    Write-Host "  - DroidCam app is running on iPhone" -ForegroundColor Yellow
    Write-Host "  - iPhone and PC are on same WiFi" -ForegroundColor Yellow
    Write-Host "  - iPhone IP is 192.168.68.101" -ForegroundColor Yellow
    Write-Host "`nPress Enter to continue anyway or Ctrl+C to exit..." -ForegroundColor Yellow
    Read-Host
}

Write-Host "`n[2/4] Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; Write-Host 'Backend API Starting...' -ForegroundColor Cyan; npm start"

Write-Host "[3/4] Starting Frontend Dashboard..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Frontend Dashboard Starting...' -ForegroundColor Cyan; ng serve"

Write-Host "[4/4] Starting Python Detection Service..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\python-service'; .\venv\Scripts\Activate.ps1; Write-Host 'Python Detection Service Starting...' -ForegroundColor Cyan; python main.py --source iphone"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✓ All services are starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nWait 30 seconds, then open: http://localhost:4200" -ForegroundColor Cyan
Write-Host "`nServices will open in separate windows." -ForegroundColor Yellow
Write-Host "To stop all services, close each window.`n" -ForegroundColor Yellow

# Wait and open browser
Start-Sleep -Seconds 20
Write-Host "Opening dashboard in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:4200"

Write-Host "`nPress any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
