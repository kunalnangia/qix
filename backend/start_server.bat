@echo off
:: Batch script to start the FastAPI backend server

echo Starting FastAPI Backend Server...
echo =================================

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python is installed

:: Install required packages if not already installed
echo Checking/Installing required Python packages...
pip install fastapi uvicorn[standard] sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install required packages
    pause
    exit /b 1
)

echo.
echo Starting FastAPI server...
echo API will be available at: http://127.0.0.1:8001
echo API Documentation: http://127.0.0.1:8001/api/docs
echo.
echo Press Ctrl+C to stop the server
echo =================================

:: Start the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Failed to start the server
    echo Make sure you're in the backend directory and all dependencies are installed
    pause
    exit /b 1
)

pause
