@echo off
echo =======================================================
echo   Airline BI - Capstone Application Startup Script
echo =======================================================
echo.
cd /d "%~dp0"

IF EXIST "%~dp0..\.venv\Scripts\python.exe" (
    SET "PYTHON_BIN=%~dp0..\.venv\Scripts\python.exe"
) ELSE IF EXIST "%~dp0.venv\Scripts\python.exe" (
    SET "PYTHON_BIN=%~dp0.venv\Scripts\python.exe"
) ELSE (
    SET "PYTHON_BIN=python"
)

echo Using Python executable: %PYTHON_BIN%
echo.
echo 1. Seeding SQLite Database & Generating user_data.xlsx...
"%PYTHON_BIN%" backend/seed_database.py

echo.
echo 2. Launching FastAPI Backend on http://localhost:8000 in background window...
start "Airline BI - FastAPI Backend" cmd /k "cd /d "%~dp0" && "%PYTHON_BIN%" -m uvicorn backend.main:app --port 8000 --reload"

echo.
echo 3. Launching React Frontend on http://localhost:5173 in background window...
start "Airline BI - React Frontend" cmd /k "cd /d "%~dp0\frontend" && npm run dev"

echo.
echo =======================================================
echo Both servers launched successfully!
echo Open your browser at http://localhost:5173 to view the dashboard.
echo =======================================================
echo.
pause

