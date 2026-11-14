@echo off
echo ========================================================
echo        Starting Technify VisionAI Frontend Web UI
echo ========================================================
cd /d "%~dp0frontend"
npm run dev -- --host 127.0.0.1 --port 5173
pause

