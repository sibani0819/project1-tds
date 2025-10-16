@echo off
REM LLM Code Deployment API Startup Script for Windows

echo 🚀 Starting LLM Code Deployment API...

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo Please copy env.example to .env and configure your environment variables:
    echo copy env.example .env
    echo Then edit .env with your actual values.
    pause
    exit /b 1
)

echo ✅ Environment file found

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Create logs directory
if not exist logs mkdir logs

echo 🔧 Starting application...
echo API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo Health check at: http://localhost:8000/ping
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python main.py

pause
