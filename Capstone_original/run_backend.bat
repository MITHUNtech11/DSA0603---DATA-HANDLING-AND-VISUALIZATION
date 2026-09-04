@echo off
echo =======================================================
echo   Airline BI - FastAPI Backend Server Startup
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

echo Using Python: %PYTHON_BIN%
echo.
echo 1. Seeding SQLite Database & Exporting user_data.xlsx...
"%PYTHON_BIN%" backend/seed_database.py

echo.
echo 2. Launching FastAPI Server on http://localhost:8000...
"%PYTHON_BIN%" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause

