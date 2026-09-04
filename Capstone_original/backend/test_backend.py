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

def test_get_user_data_kpis():
    response = client.get("/api/user-data/kpis")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_booked" in data
    assert "total_cancelled" in data
    assert "total_delayed" in data
    assert data["total_users"] > 0

def test_get_user_records():
    response = client.get("/api/user-data/records")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    record = data[0]
    assert "user_id" in record
    assert "passenger_name" in record
    assert "booking_reference" in record
    assert "user_status" in record

def test_update_user_record_status():
    # First get a record ID
    get_res = client.get("/api/user-data/records?limit=1")
    assert get_res.status_code == 200
    records = get_res.json()
    assert len(records) > 0
    target_id = records[0]["user_data_id"]

    # Perform update
    update_payload = {
        "user_data_id": target_id,
        "user_status": "Cancelled",
        "delay_minutes": 0,
        "cancellation_reason": "Customer cancellation test",
        "refund_amount": 250.0
    }
    post_res = client.post("/api/user-data/update-status", json=update_payload)
    assert post_res.status_code == 200
    res_json = post_res.json()
    assert res_json["status"] == "success"
    assert res_json["updated_status"] == "Cancelled"

def test_sync_user_data_from_excel():
    response = client.post("/api/user-data/sync-excel")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["synced", "created"]

def test_satellite_tracker_telemetry():
    response = client.get("/api/satellite-tracker/telemetry/PNR-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "passenger" in data
    assert "telemetry" in data
    assert "current_latitude" in data["telemetry"]
    assert "altitude_ft" in data["telemetry"]

def test_satellite_tracker_active():
    response = client.get("/api/satellite-tracker/active")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "pnr" in data[0]


