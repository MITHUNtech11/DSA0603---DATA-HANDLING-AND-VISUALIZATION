@echo off
echo =======================================================
echo   Airline BI - Capstone Application Startup Script
echo =======================================================
echo.
cd %~dp0

echo 1. Seeding SQLite Database (schema.sql + 100 flights dataset)...
python backend/seed_database.py

echo.
echo 2. Launching FastAPI Backend on http://localhost:8000 in background window...
start "FastAPI Backend" cmd /k "python -m uvicorn backend.main:app --port 8000 --reload"

echo.
echo 3. Launching React Frontend on http://localhost:5173...
cd frontend
start "React Frontend" cmd /k "npm run dev"

echo.
echo Both servers launched successfully!
echo Open your browser at http://localhost:5173 to view the dashboard.
echo.
pause
