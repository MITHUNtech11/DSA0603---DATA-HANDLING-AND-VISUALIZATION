from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(__file__))

from database import (
    get_kpis, get_route_performance, get_delay_heatmap, get_flights,
    get_user_data_kpis, get_user_records, update_user_record_status,
    export_user_data_to_excel, sync_user_data_from_excel,
    get_satellite_flight_telemetry, get_active_satellite_flights
)

class UserStatusUpdateRequest(BaseModel):
    user_data_id: int
    user_status: str
    delay_minutes: Optional[int] = 0
    cancellation_reason: Optional[str] = None
    refund_amount: Optional[float] = 0.0

app = FastAPI(
    title="Airline BI REST API",
    description="FastAPI Backend for Airline Business Intelligence Dashboard & Satellite Flight Radar",
    version="1.2.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Airline BI FastAPI Server Running",
        "endpoints": [
            "/api/kpis", "/api/route-performance", "/api/delay-heatmap", "/api/flights",
            "/api/user-data/kpis", "/api/user-data/records", "/api/user-data/update-status",
            "/api/user-data/export-excel", "/api/user-data/sync-excel",
            "/api/satellite-tracker/telemetry/{query}", "/api/satellite-tracker/active"
        ]
    }

@app.get("/api/kpis")
def kpis_endpoint(search: Optional[str] = Query("", description="Search term for airline or route")):
    return get_kpis(search=search)

@app.get("/api/route-performance")
def route_performance_endpoint(search: Optional[str] = Query("", description="Search term for airline or route")):
    return get_route_performance(search=search)

@app.get("/api/delay-heatmap")
def delay_heatmap_endpoint(search: Optional[str] = Query("", description="Search term for airline or route")):
    return get_delay_heatmap(search=search)

@app.get("/api/flights")
def flights_endpoint(
    search: Optional[str] = Query("", description="Search term for airline or route"),
    limit: Optional[int] = Query(100, description="Max records to return")
):
    return get_flights(search=search, limit=limit)

# Unified User Data Center Endpoints
@app.get("/api/user-data/kpis")
def user_data_kpis_endpoint(
    search: Optional[str] = Query("", description="Search term"),
    status: Optional[str] = Query("", description="Status filter")
):
    return get_user_data_kpis(search=search, status_filter=status)

@app.get("/api/user-data/records")
def user_data_records_endpoint(
    search: Optional[str] = Query("", description="Search term"),
    status: Optional[str] = Query("", description="Status filter"),
    limit: Optional[int] = Query(150, description="Record limit")
):
    return get_user_records(search=search, status_filter=status, limit=limit)

@app.post("/api/user-data/update-status")
def user_data_update_status_endpoint(req: UserStatusUpdateRequest):
    if req.user_status not in ["Booked", "Cancelled", "Delayed", "Completed"]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    return update_user_record_status(
        user_data_id=req.user_data_id,
        new_status=req.user_status,
        delay_minutes=req.delay_minutes or 0,
        cancellation_reason=req.cancellation_reason,
        refund_amount=req.refund_amount or 0.0
    )

@app.get("/api/user-data/export-excel")
def user_data_export_excel_endpoint():
    file_path = export_user_data_to_excel()
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Excel file export failed")
    return FileResponse(
        path=file_path,
        filename="user_data_master.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.post("/api/user-data/sync-excel")
def user_data_sync_excel_endpoint():
    return sync_user_data_from_excel()

# Live Satellite Flight Radar & Family Safety Endpoints
@app.get("/api/satellite-tracker/telemetry")
@app.get("/api/satellite-tracker/telemetry/{query}")
def satellite_tracker_telemetry_endpoint(query: Optional[str] = ""):
    return get_satellite_flight_telemetry(query=query or "")

@app.get("/api/satellite-tracker/active")
def satellite_tracker_active_endpoint():
    return get_active_satellite_flights()



