@echo off
REM License Plate Detection System - Quick Start
REM Double-click this file to start all services

echo ========================================
echo License Plate Detection System Startup
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0start-all.ps1"

pause
