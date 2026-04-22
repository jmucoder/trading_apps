@echo off
REM Trading Application Startup Script for Windows

echo.
echo ====================================
echo Trading Dashboard Startup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo Checking dependencies...
pip list | findstr streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed.
) else (
    echo Dependencies already installed.
)

echo.
echo ====================================
echo Starting Trading Dashboard...
echo ====================================
echo.
echo The dashboard will open in your default browser.
echo Press Ctrl+C to stop the server.
echo.

REM Run the app
streamlit run app.py

pause
