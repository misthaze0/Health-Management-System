@echo off
chcp 65001 >nul
title Health Management System Launcher
color 0B
cls

echo.
echo ========================================
echo   Health Management System Launcher
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if PowerShell script exists
if not exist "start-all.ps1" (
    echo [ERROR] start-all.ps1 not found
    pause
    exit /b 1
)

echo [INFO] Checking system configuration...
echo [INFO] Project path: %cd%
echo.

REM Check PowerShell version
powershell -Command "if ($PSVersionTable.PSVersion.Major -lt 5) { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] PowerShell version is too old, recommend upgrading to 5.0+
)

echo.
echo ========================================
echo   Starting Health Management System
echo ========================================
echo.
echo [INFO] Features:
echo   - Auto-check and start MySQL database
echo   - Auto-initialize database if not exists
echo   - Start Backend (Spring Boot) on port 19001
echo   - Start AI Service (Python) on port 19002
echo   - Start Frontend (Vue.js) on port 19000
echo.
echo [INFO] Please do not close this window during startup
echo [INFO] Press Q in the menu to stop all services and exit
echo.
echo ========================================
echo.

REM Execute PowerShell script
echo [INFO] Launching PowerShell startup script...
powershell -ExecutionPolicy Bypass -NoExit -File "start-all.ps1" -SkipBrowser

echo.
echo ========================================
echo   Services stopped
echo ========================================
pause
