@echo off
title Technify VisionAI - Launcher
echo ========================================================
echo        Technify VisionAI - Starting All Services
echo ========================================================
echo.
echo [1/3] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Technify VisionAI - Backend API" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Waiting 4 seconds for backend to initialize ...
timeout /t 4 /nobreak >nul

echo [3/3] Launching React Frontend on http://127.0.0.1:5173 ...
start "Technify VisionAI - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo ========================================================
echo All services launched!
echo Opening dashboard in your default browser...
echo ========================================================
timeout /t 2 /nobreak >nul
start http://localhost:5173

echo.
echo Press any key to close this launcher window (services keep running).
pause >nul

