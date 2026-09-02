from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.dirname(__file__))

from database import get_kpis, get_route_performance, get_delay_heatmap, get_flights

app = FastAPI(
    title="Airline BI REST API",
    description="FastAPI Backend for Airline Business Intelligence Dashboard",
    version="1.0.0"
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
        "endpoints": ["/api/kpis", "/api/route-performance", "/api/delay-heatmap", "/api/flights"]
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
