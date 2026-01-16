#!/usr/bin/env pwsh
# License Plate Detection System - Start All Services
# This script starts the backend API, Python detection service, and frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "License Plate Detection System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if services are already running
$backendRunning = Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*License_Plate_Scanning*" }
$pythonRunning = Get-Process python -ErrorAction SilentlyContinue

if ($backendRunning -or $pythonRunning) {
    Write-Host "⚠️  Some services are already running!" -ForegroundColor Yellow
    Write-Host "Do you want to stop them and restart? (Y/N): " -NoNewline
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Stopping existing services..." -ForegroundColor Yellow
        Stop-Process -Name node -Force -ErrorAction SilentlyContinue
        Stop-Process -Name python -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
}

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Green
Write-Host ""

# 1. Start Backend API
Write-Host "[1/3] Starting Backend API..." -ForegroundColor Cyan
Push-Location "$PSScriptRoot\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Normal
Pop-Location
Write-Host "✓ Backend API starting on http://localhost:3000" -ForegroundColor Green
Start-Sleep -Seconds 3

# 2. Start Python Detection Service (optional - can be started manually when needed)
Write-Host ""
Write-Host "[2/3] Python detection service available" -ForegroundColor Cyan
Write-Host "   To start camera detection, run:" -ForegroundColor Yellow
Write-Host "   cd python-service" -ForegroundColor Yellow
Write-Host "   python test_real_plate.py 1" -ForegroundColor Yellow
Write-Host ""

# 3. Start Frontend
Write-Host "[3/3] Starting Frontend..." -ForegroundColor Cyan
Push-Location "$PSScriptRoot\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ng serve --open" -WindowStyle Normal
Pop-Location
Write-Host "✓ Frontend starting on http://localhost:4200" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ System Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Access points:" -ForegroundColor Cyan
Write-Host "   Frontend:  http://localhost:4200" -ForegroundColor White
Write-Host "   Backend:   http://localhost:3000" -ForegroundColor White
Write-Host "   API Docs:  http://localhost:3000/api" -ForegroundColor White
Write-Host ""
Write-Host "💡 The frontend will open automatically in your browser" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
