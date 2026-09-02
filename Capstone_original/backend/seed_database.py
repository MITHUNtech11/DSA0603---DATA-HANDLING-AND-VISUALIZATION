import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "airline_bi.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def seed_db():
    print(f"Initializing database at: {DB_PATH}")
    
    # Random seed for deterministic data generation
    random.seed(42)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read schema.sql and execute
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    
    cursor.executescript(schema_sql)
    print("Schema and views created successfully.")
    
    # 1. Seed Airlines
    airlines_data = [
        ("Delta Air Lines", "DL", "United States"),
        ("United Airlines", "UA", "United States"),
        ("American Airlines", "AA", "United States"),
        ("Lufthansa", "LH", "Germany"),
        ("Emirates", "EK", "United Arab Emirates")
    ]
    cursor.executemany(
        "INSERT INTO airlines (airline_name, iata_code, country) VALUES (?, ?, ?);",
        airlines_data
    )
    
    # 2. Seed Airports
    airports_data = [
        ("John F. Kennedy International Airport", "JFK", "New York", "United States"),
        ("Los Angeles International Airport", "LAX", "Los Angeles", "United States"),
        ("O'Hare International Airport", "ORD", "Chicago", "United States"),
        ("London Heathrow Airport", "LHR", "London", "United Kingdom"),
        ("Dubai International Airport", "DXB", "Dubai", "United Arab Emirates"),
        ("San Francisco International Airport", "SFO", "San Francisco", "United States"),
        ("Frankfurt Airport", "FRA", "Frankfurt", "Germany"),
        ("Paris Charles de Gaulle Airport", "CDG", "Paris", "France")
    ]
    cursor.executemany(
        "INSERT INTO airports (airport_name, iata_code, city, country) VALUES (?, ?, ?, ?);",
        airports_data
    )
    
    # Retrieve generated IDs
    cursor.execute("SELECT airline_id, iata_code FROM airlines;")
    airlines = {code: aid for aid, code in cursor.fetchall()}
    
    cursor.execute("SELECT airport_id, iata_code FROM airports;")
    airports = {code: apid for apid, code in cursor.fetchall()}
    airport_codes = list(airports.keys())
    
    aircraft_types = ["Boeing 737-800", "Airbus A320", "Boeing 787 Dreamliner", "Airbus A350", "Boeing 777-300ER"]
    statuses = ["On-Time", "On-Time", "On-Time", "Delayed", "Scheduled", "Cancelled"]
    
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]
    
    base_time = datetime(2026, 9, 1, 6, 0, 0)
    
    # 3. Seed 100 Flights
    flights_inserted = 0
    fare_id_counter = 1
    
    for i in range(1, 101):
        al_code = random.choice(list(airlines.keys()))
        al_id = airlines[al_code]
        
        orig_code, dest_code = random.sample(airport_codes, 2)
        orig_id = airports[orig_code]
        dest_id = airports[dest_code]
        
        flight_num = f"{al_code}{random.randint(100, 999)}"
        aircraft = random.choice(aircraft_types)
        capacity = random.choice([150, 180, 220, 300])
        
        # Flight schedule
        dep_offset_hours = random.randint(0, 168) # over 7 days
        flight_duration_hours = random.randint(2, 14)
        dep_time = base_time + timedelta(hours=dep_offset_hours, minutes=random.choice([0, 15, 30, 45]))
        arr_time = dep_time + timedelta(hours=flight_duration_hours)
        
        status = random.choice(statuses)
        delay_min = random.randint(15, 120) if status == "Delayed" else 0
        
        cursor.execute("""
            INSERT INTO flights 
            (flight_number, airline_id, origin_airport_id, destination_airport_id, departure_time, arrival_time, aircraft_type, capacity, status, delay_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (flight_num, al_id, orig_id, dest_id, dep_time.strftime("%Y-%m-%d %H:%M:%S"), arr_time.strftime("%Y-%m-%d %H:%M:%S"), aircraft, capacity, status, delay_min))
        
        flight_id = cursor.lastrowid
        flights_inserted += 1
        
        # Create Fares for this flight
        fares = [
            (flight_id, "Economy", round(random.uniform(120, 450), 2)),
            (flight_id, "Business", round(random.uniform(600, 1500), 2)),
            (flight_id, "First Class", round(random.uniform(1800, 3500), 2))
        ]
        cursor.executemany("INSERT INTO fares (flight_id, fare_class, price) VALUES (?, ?, ?);", fares)
        
        # Get fare IDs for this flight
        cursor.execute("SELECT fare_id, fare_class FROM fares WHERE flight_id = ?;", (flight_id,))
        flight_fare_map = {fclass: fid for fid, fclass in cursor.fetchall()}
        
        # Create Bookings according to simulated load factor (50% to 95% capacity)
        if status != "Cancelled":
            target_bookings = int(capacity * random.uniform(0.5, 0.95))
            bookings_list = []
            
            for b in range(target_bookings):
                passenger = f"{random.choice(first_names)} {random.choice(last_names)}"
                fclass = random.choices(["Economy", "Business", "First Class"], weights=[0.8, 0.15, 0.05])[0]
                fid = flight_fare_map[fclass]
                seat = f"{random.randint(1, 40)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
                b_date = (dep_time - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d %H:%M:%S")
                
                bookings_list.append((flight_id, fid, passenger, b_date, seat))
                
            cursor.executemany("INSERT INTO bookings (flight_id, fare_id, passenger_name, booking_date, seat_number) VALUES (?, ?, ?, ?, ?);", bookings_list)
            
    conn.commit()
    conn.close()
    print(f"Successfully seeded database with {flights_inserted} flights, fares, and bookings!")

if __name__ == "__main__":
    seed_db()
