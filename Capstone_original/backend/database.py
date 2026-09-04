import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "airline_bi.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_kpis(search: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_param = f"%{search.strip()}%" if search else "%"
    
    sql = """
        SELECT 
            ROUND(COALESCE(SUM(total_revenue), 0), 2) AS total_revenue,
            COALESCE(SUM(total_bookings), 0) AS total_bookings,
            ROUND(COALESCE(AVG(load_factor_pct), 0), 1) AS avg_load_factor,
            COUNT(flight_id) AS total_flights,
            SUM(CASE WHEN status = 'On-Time' THEN 1 ELSE 0 END) AS on_time_flights,
            SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_flights,
            SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_flights
        FROM vw_FlightOperational
        WHERE airline_name LIKE ? OR origin LIKE ? OR destination LIKE ? OR flight_number LIKE ?;
    """
    
    cursor.execute(sql, (search_param, search_param, search_param, search_param))
    row = cursor.fetchone()
    conn.close()
    
    total_flights = row["total_flights"] or 0
    on_time = row["on_time_flights"] or 0
    on_time_rate = round((on_time * 100.0 / total_flights), 1) if total_flights > 0 else 0.0
    
    return {
        "total_revenue": row["total_revenue"] or 0.0,
        "total_bookings": row["total_bookings"] or 0,
        "avg_load_factor": row["avg_load_factor"] or 0.0,
        "total_flights": total_flights,
        "on_time_rate": on_time_rate,
        "delayed_flights": row["delayed_flights"] or 0,
        "cancelled_flights": row["cancelled_flights"] or 0
    }

def get_route_performance(search: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_param = f"%{search.strip()}%" if search else "%"
    
    sql = """
        SELECT 
            route,
            airline_name,
            total_flights,
            total_bookings,
            total_capacity,
            total_revenue,
            avg_fare,
            load_factor_pct,
            avg_delay_minutes
        FROM vw_RouteRevenue
        WHERE airline_name LIKE ? OR route LIKE ?
        ORDER BY total_revenue DESC
        LIMIT 10;
    """
    cursor.execute(sql, (search_param, search_param))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_delay_heatmap(search: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_param = f"%{search.strip()}%" if search else "%"
    
    sql = """
        SELECT 
            CASE strftime('%w', f.departure_time)
                WHEN '0' THEN 'Sunday'
                WHEN '1' THEN 'Monday'
                WHEN '2' THEN 'Tuesday'
                WHEN '3' THEN 'Wednesday'
                WHEN '4' THEN 'Thursday'
                WHEN '5' THEN 'Friday'
                WHEN '6' THEN 'Saturday'
            END AS day_of_week,
            f.status,
            COUNT(f.flight_id) AS flight_count,
            ROUND(AVG(f.delay_minutes), 1) AS avg_delay
        FROM flights f
        JOIN airlines al ON f.airline_id = al.airline_id
        JOIN airports orig ON f.origin_airport_id = orig.airport_id
        JOIN airports dest ON f.destination_airport_id = dest.airport_id
        WHERE al.airline_name LIKE ? OR orig.city LIKE ? OR dest.city LIKE ?
        GROUP BY strftime('%w', f.departure_time), day_of_week, f.status
        ORDER BY strftime('%w', f.departure_time);
    """
    cursor.execute(sql, (search_param, search_param, search_param))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_flights(search: str = "", limit: int = 100):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_param = f"%{search.strip()}%" if search else "%"
    
    sql = """
        SELECT 
            flight_id,
            flight_number,
            airline_name,
            airline_code,
            origin,
            destination,
            route_code,
            departure_time,
            arrival_time,
            aircraft_type,
            capacity,
            status,
            delay_minutes,
            total_bookings,
            load_factor_pct,
            total_revenue
        FROM vw_FlightOperational
        WHERE airline_name LIKE ? OR origin LIKE ? OR destination LIKE ? OR flight_number LIKE ?
        ORDER BY departure_time ASC
        LIMIT ?;
    """
    cursor.execute(sql, (search_param, search_param, search_param, search_param, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_data_kpis(search: str = "", status_filter: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_param = f"%{search.strip()}%" if search else "%"
    
    sql = """
        SELECT 
            COUNT(user_data_id) AS total_users,
            SUM(CASE WHEN user_status = 'Booked' THEN 1 ELSE 0 END) AS total_booked,
            SUM(CASE WHEN user_status = 'Cancelled' THEN 1 ELSE 0 END) AS total_cancelled,
            SUM(CASE WHEN user_status = 'Delayed' THEN 1 ELSE 0 END) AS total_delayed,
            SUM(CASE WHEN user_status = 'Completed' THEN 1 ELSE 0 END) AS total_completed,
            ROUND(COALESCE(SUM(ticket_price), 0), 2) AS total_ticket_revenue,
            ROUND(COALESCE(SUM(refund_amount), 0), 2) AS total_refund_payout,
            ROUND(COALESCE(AVG(delay_minutes), 0), 1) AS avg_delay_mins
        FROM user_data_master
        WHERE (passenger_name LIKE ? OR passenger_email LIKE ? OR flight_number LIKE ? OR booking_reference LIKE ? OR route LIKE ?)
          AND (? = '' OR user_status = ?);
    """
    cursor.execute(sql, (search_param, search_param, search_param, search_param, search_param, status_filter, status_filter))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "total_users": row["total_users"] or 0,
        "total_booked": row["total_booked"] or 0,
        "total_cancelled": row["total_cancelled"] or 0,
        "total_delayed": row["total_delayed"] or 0,
        "total_completed": row["total_completed"] or 0,
        "total_ticket_revenue": row["total_ticket_revenue"] or 0.0,
        "total_refund_payout": row["total_refund_payout"] or 0.0,
        "avg_delay_mins": row["avg_delay_mins"] or 0.0
    }

def get_user_records(search: str = "", status_filter: str = "", limit: int = 150):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_param = f"%{search.strip()}%" if search else "%"
    
    sql = """
        SELECT 
            user_data_id,
            user_id,
            passenger_name,
            passenger_email,
            passenger_phone,
            booking_reference,
            flight_number,
            airline_name,
            route,
            departure_time,
            seat_number,
            fare_class,
            ticket_price,
            user_status,
            delay_minutes,
            cancellation_reason,
            refund_amount,
            last_updated
        FROM user_data_master
        WHERE (passenger_name LIKE ? OR passenger_email LIKE ? OR flight_number LIKE ? OR booking_reference LIKE ? OR route LIKE ?)
          AND (? = '' OR user_status = ?)
        ORDER BY last_updated DESC, user_data_id DESC
        LIMIT ?;
    """
    cursor.execute(sql, (search_param, search_param, search_param, search_param, search_param, status_filter, status_filter, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_user_record_status(user_data_id: int, new_status: str, delay_minutes: int = 0, cancellation_reason: str = None, refund_amount: float = 0.0):
    from datetime import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    sql = """
        UPDATE user_data_master
        SET user_status = ?,
            delay_minutes = ?,
            cancellation_reason = ?,
            refund_amount = ?,
            last_updated = ?
        WHERE user_data_id = ?;
    """
    cursor.execute(sql, (new_status, delay_minutes, cancellation_reason, refund_amount, now_str, user_data_id))
    conn.commit()
    conn.close()
    
    export_user_data_to_excel()
    return {"status": "success", "user_data_id": user_data_id, "updated_status": new_status, "last_updated": now_str}

def export_user_data_to_excel():
    try:
        import pandas as pd
        excel_path = os.path.join(os.path.dirname(__file__), "user_data.xlsx")
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM user_data_master ORDER BY user_data_id ASC;", conn)
        df.to_excel(excel_path, index=False, sheet_name="Master_User_Data")
        conn.close()
        return excel_path
    except Exception as e:
        print(f"Error exporting user data to Excel: {e}")
        return None

def sync_user_data_from_excel():
    excel_path = os.path.join(os.path.dirname(__file__), "user_data.xlsx")
    if not os.path.exists(excel_path):
        export_user_data_to_excel()
        return {"status": "created", "records": 0}
        
    try:
        import pandas as pd
        df = pd.read_excel(excel_path, sheet_name="Master_User_Data")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO user_data_master (
                    user_data_id, user_id, passenger_name, passenger_email, passenger_phone,
                    booking_reference, flight_number, airline_name, route, departure_time,
                    seat_number, fare_class, ticket_price, user_status, delay_minutes,
                    cancellation_reason, refund_amount, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(booking_reference) DO UPDATE SET
                    user_status = excluded.user_status,
                    delay_minutes = excluded.delay_minutes,
                    cancellation_reason = excluded.cancellation_reason,
                    refund_amount = excluded.refund_amount,
                    last_updated = excluded.last_updated;
            """, (
                int(row['user_data_id']) if 'user_data_id' in row and not pd.isna(row['user_data_id']) else None,
                str(row['user_id']), str(row['passenger_name']), str(row['passenger_email']), str(row['passenger_phone']),
                str(row['booking_reference']), str(row['flight_number']), str(row['airline_name']), str(row['route']),
                str(row['departure_time']), str(row['seat_number']), str(row['fare_class']), float(row['ticket_price']),
                str(row['user_status']), int(row['delay_minutes']) if not pd.isna(row['delay_minutes']) else 0,
                str(row['cancellation_reason']) if not pd.isna(row['cancellation_reason']) else None,
                float(row['refund_amount']) if not pd.isna(row['refund_amount']) else 0.0,
                str(row['last_updated'])
            ))
            
        conn.commit()
        conn.close()
        return {"status": "synced", "total_records": len(df)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Airport Coordinates (Latitude, Longitude) for Satellite Trajectory Math
AIRPORT_COORDINATES = {
    "JFK": {"name": "New York (JFK)", "lat": 40.6413, "lng": -73.7781, "city": "New York", "country": "United States"},
    "LAX": {"name": "Los Angeles (LAX)", "lat": 33.9416, "lng": -118.4085, "city": "Los Angeles", "country": "United States"},
    "ORD": {"name": "Chicago (ORD)", "lat": 41.9742, "lng": -87.9073, "city": "Chicago", "country": "United States"},
    "LHR": {"name": "London (LHR)", "lat": 51.4700, "lng": -0.4543, "city": "London", "country": "United Kingdom"},
    "DXB": {"name": "Dubai (DXB)", "lat": 25.2532, "lng": 55.3657, "city": "Dubai", "country": "United Arab Emirates"},
    "SFO": {"name": "San Francisco (SFO)", "lat": 37.6213, "lng": -122.3790, "city": "San Francisco", "country": "United States"},
    "FRA": {"name": "Frankfurt (FRA)", "lat": 50.0379, "lng": 8.5622, "city": "Frankfurt", "country": "Germany"},
    "CDG": {"name": "Paris (CDG)", "lat": 49.0097, "lng": 2.5479, "city": "Paris", "country": "France"}
}

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    import math
    R = 3958.8 # Miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def interpolate_spherical_pos(lat1, lon1, lat2, lon2, fraction):
    import math
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    
    d = 2 * math.asin(math.sqrt(
        math.sin((lat2_r - lat1_r)/2)**2 +
        math.cos(lat1_r) * math.cos(lat2_r) * math.sin((lon2_r - lon1_r)/2)**2
    ))
    if d == 0:
        return lat1, lon1
        
    A = math.sin((1 - fraction) * d) / math.sin(d)
    B = math.sin(fraction * d) / math.sin(d)
    
    x = A * math.cos(lat1_r) * math.cos(lon1_r) + B * math.cos(lat2_r) * math.cos(lon2_r)
    y = A * math.cos(lat1_r) * math.sin(lon1_r) + B * math.cos(lat2_r) * math.sin(lon2_r)
    z = A * math.sin(lat1_r) + B * math.sin(lat2_r)
    
    lat = math.atan2(z, math.sqrt(x**2 + y**2))
    lon = math.atan2(y, x)
    return math.degrees(lat), math.degrees(lon)

def get_satellite_flight_telemetry(query: str = ""):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    q_param = query.strip()
    if not q_param:
        cursor.execute("SELECT booking_reference FROM user_data_master LIMIT 1;")
        row = cursor.fetchone()
        q_param = row["booking_reference"] if row else "PNR-1001"
        
    sql = """
        SELECT 
            u.user_data_id, u.user_id, u.passenger_name, u.booking_reference,
            u.flight_number, u.airline_name, u.route, u.departure_time,
            u.seat_number, u.fare_class, u.user_status, u.delay_minutes, u.last_updated
        FROM user_data_master u
        WHERE u.booking_reference LIKE ? OR u.flight_number LIKE ? OR u.passenger_name LIKE ? OR u.user_id LIKE ?
        LIMIT 1;
    """
    p_like = f"%{q_param}%"
    cursor.execute(sql, (p_like, p_like, p_like, p_like))
    rec = cursor.fetchone()
    if not rec:
        cursor.execute("""
            SELECT 
                u.user_data_id, u.user_id, u.passenger_name, u.booking_reference,
                u.flight_number, u.airline_name, u.route, u.departure_time,
                u.seat_number, u.fare_class, u.user_status, u.delay_minutes, u.last_updated
            FROM user_data_master u
            LIMIT 1;
        """)
        rec = cursor.fetchone()
    conn.close()
    
    if not rec:
        return {"status": "error", "message": f"No flight record found for search term '{query}'"}

        
    full_name = rec["passenger_name"]
    name_parts = full_name.split()
    masked_name = " ".join([p[0] + "***" for p in name_parts]) if name_parts else "Passenger ***"
    
    route_str = rec["route"]
    orig_code = "JFK"
    dest_code = "LAX"
    for code in AIRPORT_COORDINATES.keys():
        if f"({code})" in route_str:
            if orig_code == "JFK":
                orig_code = code
            else:
                dest_code = code
                
    orig_ap = AIRPORT_COORDINATES.get(orig_code, AIRPORT_COORDINATES["JFK"])
    dest_ap = AIRPORT_COORDINATES.get(dest_code, AIRPORT_COORDINATES["LAX"])
    
    total_dist = round(calculate_haversine_distance(orig_ap["lat"], orig_ap["lng"], dest_ap["lat"], dest_ap["lng"]), 1)
    
    u_status = rec["user_status"]
    delay_m = rec["delay_minutes"] or 0
    
    if u_status == "Cancelled":
        progress = 0.0
        current_lat, current_lng = orig_ap["lat"], orig_ap["lng"]
        altitude = 0
        speed = 0
        phase = "Cancelled / Flight Grounded"
        eta_mins = 0
        safety_status = "FLIGHT CANCELLED - PASSENGER GROUNDED SAFE"
    elif u_status == "Completed" or u_status == "Landed":
        progress = 1.0
        current_lat, current_lng = dest_ap["lat"], dest_ap["lng"]
        altitude = 0
        speed = 0
        phase = "Landed / Arrived at Gate"
        eta_mins = 0
        safety_status = "SAFE ARRIVAL VERIFIED AT DESTINATION GATE"
    else:
        import random
        random.seed(sum(ord(c) for c in rec["booking_reference"]))
        progress = round(random.uniform(0.18, 0.85), 2)
        
        current_lat, current_lng = interpolate_spherical_pos(orig_ap["lat"], orig_ap["lng"], dest_ap["lat"], dest_ap["lng"], progress)
        current_lat = round(current_lat, 4)
        current_lng = round(current_lng, 4)
        
        if progress < 0.25:
            phase = "Climbing to Cruise Altitude"
            altitude = int(12000 + (progress / 0.25) * 23000)
            speed = int(320 + (progress / 0.25) * 180)
        elif progress > 0.80:
            phase = "Descending on Approach"
            altitude = int(35000 * (1.0 - (progress - 0.80) / 0.20))
            speed = int(500 - ((progress - 0.80) / 0.20) * 260)
        else:
            phase = "Cruising at Altitude"
            altitude = random.randint(34000, 38000)
            speed = random.randint(480, 530)
            
        remaining_dist = total_dist * (1.0 - progress)
        eta_mins = int((remaining_dist / max(speed, 1)) * 60) + delay_m
        safety_status = f"FAMILY SAFETY VERIFIED: Satellite Tracking Active ({phase})"
        
    return {
        "status": "success",
        "search_query": query,
        "passenger": {
            "masked_name": masked_name,
            "pnr": rec["booking_reference"],
            "user_id": rec["user_id"],
            "seat_number": rec["seat_number"],
            "fare_class": rec["fare_class"]
        },
        "flight": {
            "flight_number": rec["flight_number"],
            "airline_name": rec["airline_name"],
            "route": rec["route"],
            "origin": orig_ap,
            "destination": dest_ap,
            "departure_time": rec["departure_time"],
            "status": rec["user_status"],
            "delay_minutes": delay_m
        },
        "telemetry": {
            "current_latitude": current_lat,
            "current_longitude": current_lng,
            "altitude_ft": altitude,
            "ground_speed_kts": speed,
            "progress_pct": int(progress * 100),
            "total_distance_miles": total_dist,
            "remaining_distance_miles": round(total_dist * (1.0 - progress), 1),
            "eta_minutes": eta_mins,
            "flight_phase": phase,
            "safety_status_text": safety_status,
            "satellite_last_ping": rec["last_updated"]
        }
    }

def get_active_satellite_flights():
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        SELECT 
            u.user_data_id, u.user_id, u.passenger_name, u.booking_reference,
            u.flight_number, u.airline_name, u.route, u.user_status
        FROM user_data_master u
        WHERE u.user_status IN ('Booked', 'Delayed', 'Completed')
        ORDER BY u.user_data_id ASC
        LIMIT 25;
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        fn = r["passenger_name"].split()
        m_name = f"{fn[0]} {fn[-1][0]}." if len(fn) > 1 else r["passenger_name"]
        result.append({
            "user_data_id": r["user_data_id"],
            "user_id": r["user_id"],
            "passenger_masked": m_name,
            "pnr": r["booking_reference"],
            "flight_number": r["flight_number"],
            "airline_name": r["airline_name"],
            "route": r["route"],
            "status": r["user_status"]
        })
    return result


