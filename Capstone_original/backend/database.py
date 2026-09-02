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
