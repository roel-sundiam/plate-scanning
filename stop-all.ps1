#!/usr/bin/env pwsh
# Stop all License Plate Detection services

Write-Host "Stopping all services..." -ForegroundColor Yellow

Stop-Process -Name node -Force -ErrorAction SilentlyContinue
Stop-Process -Name python -Force -ErrorAction SilentlyContinue

Write-Host "✓ All services stopped" -ForegroundColor Green
Start-Sleep -Seconds 2
