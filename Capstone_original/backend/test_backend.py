import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(__file__))

from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_get_kpis():
    response = client.get("/api/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "total_bookings" in data
    assert "avg_load_factor" in data
    assert "on_time_rate" in data
    assert data["total_bookings"] > 0

def test_get_route_performance():
    response = client.get("/api/route-performance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "route" in data[0]
    assert "total_revenue" in data[0]

def test_get_delay_heatmap():
    response = client.get("/api/delay-heatmap")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "day_of_week" in data[0]
    assert "flight_count" in data[0]

def test_get_flights():
    response = client.get("/api/flights")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 100
    flight = data[0]
    assert "flight_number" in flight
    assert "status" in flight
    assert "load_factor_pct" in flight
    assert "total_revenue" in flight

def test_kpis_filtered():
    response = client.get("/api/kpis?search=Delta")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert data["total_flights"] > 0
