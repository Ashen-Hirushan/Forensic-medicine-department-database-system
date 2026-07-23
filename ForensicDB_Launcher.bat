@echo off
title ForensicDB Launcher
color 0B

echo ====================================================================
echo                 Forensic Medicine Database System
echo                      One-Click Launcher
echo ====================================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH!
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo CRITICAL: Make sure to check the box "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Run the start.py script which handles pip installs and DB initialization automatically
echo [INFO] Python found. Launching system startup sequence...
echo.
python start.py

:: 3. Pause if the server stops or crashes
echo.
echo [INFO] The server has stopped.
pause
