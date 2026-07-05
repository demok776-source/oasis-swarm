@echo off
title OASIS SYSTEM CORE - Launcher
echo ===========================================
echo Starting OASIS SYSTEM CORE Local Servers...
echo ===========================================

:: Enable local SQLite database fallback mode
set USE_SQLITE=true

echo Starting App-Tier Backend on http://127.0.0.1:8080...
cd app-tier
start "OASIS App-Tier Backend" ".venv\Scripts\python.exe" -m uvicorn src.main:app --host 127.0.0.1 --port 8080 --reload
cd ..

echo Starting Mock Server on http://127.0.0.1:8000...
start "OASIS Mock Server" "app-tier\.venv\Scripts\python.exe" mock-server/server.py

echo.
echo Launch complete!
echo --------------------------------------------------------
echo Access the Event Dashboard at: http://127.0.0.1:8000/dashboard.html
echo Access the Main Landing Page at: http://127.0.0.1:8000/index.html
echo --------------------------------------------------------
echo.
pause
