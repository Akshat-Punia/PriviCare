@echo off
title PriviCare - Doctor Clinical Intelligence & Secure RAG Suite
cls
echo ============================================================================
echo               PRIVICARE - DOCTOR CLINICAL INTELLIGENCE SUITE
echo                         "CARE IN EVERY DATA BEAT"
echo ============================================================================
echo [1/3] Checking local Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.9+ is not found in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/3] Initializing local storage at %%LOCALAPPDATA%%\PriviCare\data ...
echo [3/3] Launching PriviCare Native Desktop Window (Local Machine Execution) ...
echo.
python desktop_app.py

pause
