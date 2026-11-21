@echo off
REM ============================================================
REM Healthcare PII Anonymizer - Backend Setup Script (Windows)
REM ============================================================

echo ============================================
echo   Healthcare PII Anonymizer - Backend Setup
echo ============================================
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.9+ and try again.
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Found %PYTHON_VERSION%

REM Navigate to backend directory
cd /d "%~dp0"

echo.
echo 📁 Working directory: %CD%
echo.

REM Create virtual environment
echo 🐍 Creating virtual environment...
if exist "venv" (
    echo    Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    echo    Virtual environment created successfully.
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
pip install --upgrade pip --quiet

REM Install requirements
echo 📦 Installing requirements...
pip install -r requirements.txt --quiet
echo    Requirements installed successfully.

REM Download spaCy model
echo 🧠 Downloading spaCy language model (en_core_web_sm)...
python -m spacy download en_core_web_sm --quiet
echo    spaCy model downloaded successfully.

REM Create .env from .env.example if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 Creating .env from .env.example...
        copy .env.example .env >nul
        echo    .env file created. Please update it with your API keys.
    ) else (
        echo ⚠️  No .env.example found. Skipping .env creation.
    )
) else (
    echo 📝 .env file already exists. Skipping.
)

REM Create sample_data directory if needed
if not exist "sample_data" mkdir sample_data

echo.
echo ============================================
echo   ✅ Setup complete!
echo ============================================
echo.
echo Next steps:
echo   1. Update backend\.env with your API keys
echo   2. Run the server: uvicorn main:app --reload
echo.

pause
