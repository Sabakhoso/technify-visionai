@echo off
echo ========================================================
echo        Starting Technify VisionAI Backend Server
echo ========================================================
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
    echo Error: Python virtual environment not found in backend\.venv
    echo Please run backend setup first.
    pause
    exit /b 1
)
call .venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause

