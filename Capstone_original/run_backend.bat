@echo off
echo Starting Airline BI FastAPI Backend Server on http://localhost:8000...
cd %~dp0
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
