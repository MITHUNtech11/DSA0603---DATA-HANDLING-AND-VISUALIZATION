-- Airline Business Intelligence Schema for SQLite
DROP VIEW IF EXISTS vw_RouteRevenue;
DROP VIEW IF EXISTS vw_DelayHeatmap;
DROP VIEW IF EXISTS vw_FlightOperational;

DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS fares;
DROP TABLE IF EXISTS flights;
DROP TABLE IF EXISTS airports;
DROP TABLE IF EXISTS airlines;

-- Airlines Table
CREATE TABLE airlines (
    airline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airline_name TEXT NOT NULL,
    iata_code TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL
);

-- Airports Table
CREATE TABLE airports (
    airport_id INTEGER PRIMARY KEY AUTOINCREMENT,
    airport_name TEXT NOT NULL,
    iata_code TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL,
    country TEXT NOT NULL
);

-- Flights Table
CREATE TABLE flights (
    flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT NOT NULL,
    airline_id INTEGER NOT NULL,
    origin_airport_id INTEGER NOT NULL,
    destination_airport_id INTEGER NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    aircraft_type TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Scheduled', 'On-Time', 'Delayed', 'Cancelled')),
    delay_minutes INTEGER DEFAULT 0,
    FOREIGN KEY (airline_id) REFERENCES airlines(airline_id),
    FOREIGN KEY (origin_airport_id) REFERENCES airports(airport_id),
    FOREIGN KEY (destination_airport_id) REFERENCES airports(airport_id)
);

-- Fares Table
CREATE TABLE fares (
    fare_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER NOT NULL,
    fare_class TEXT NOT NULL CHECK(fare_class IN ('Economy', 'Business', 'First Class')),
    price REAL NOT NULL,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
);

-- Bookings Table
CREATE TABLE bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER NOT NULL,
    fare_id INTEGER NOT NULL,
    passenger_name TEXT NOT NULL,
    booking_date DATETIME NOT NULL,
    seat_number TEXT NOT NULL,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    FOREIGN KEY (fare_id) REFERENCES fares(fare_id)
);

-- Optimized Analytical View 1: vw_RouteRevenue
CREATE VIEW vw_RouteRevenue AS
SELECT 
    orig.city || ' (' || orig.iata_code || ') -> ' || dest.city || ' (' || dest.iata_code || ')' AS route,
    orig.iata_code AS origin_code,
    dest.iata_code AS dest_code,
    al.airline_name,
    COUNT(DISTINCT f.flight_id) AS total_flights,
    COUNT(b.booking_id) AS total_bookings,
    SUM(f.capacity) AS total_capacity,
    ROUND(COALESCE(SUM(fr.price), 0), 2) AS total_revenue,
    ROUND(AVG(fr.price), 2) AS avg_fare,
    ROUND(CASE 
        WHEN SUM(f.capacity) > 0 THEN (COUNT(b.booking_id) * 100.0 / SUM(f.capacity))
        ELSE 0 
    END, 1) AS load_factor_pct,
    ROUND(AVG(f.delay_minutes), 1) AS avg_delay_minutes
FROM flights f
JOIN airlines al ON f.airline_id = al.airline_id
JOIN airports orig ON f.origin_airport_id = orig.airport_id
JOIN airports dest ON f.destination_airport_id = dest.airport_id
LEFT JOIN bookings b ON f.flight_id = b.flight_id
LEFT JOIN fares fr ON b.fare_id = fr.fare_id
GROUP BY orig.iata_code, dest.iata_code, al.airline_name;

-- Optimized Analytical View 2: vw_DelayHeatmap
CREATE VIEW vw_DelayHeatmap AS
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
    strftime('%w', f.departure_time) AS day_index,
    f.status,
    COUNT(f.flight_id) AS flight_count,
    ROUND(AVG(f.delay_minutes), 1) AS avg_delay
FROM flights f
GROUP BY day_index, day_of_week, f.status
ORDER BY day_index;

-- Optimized Analytical View 3: vw_FlightOperational
CREATE VIEW vw_FlightOperational AS
SELECT 
    f.flight_id,
    f.flight_number,
    al.airline_name,
    al.iata_code AS airline_code,
    orig.city || ' (' || orig.iata_code || ')' AS origin,
    dest.city || ' (' || dest.iata_code || ')' AS destination,
    orig.iata_code || '-' || dest.iata_code AS route_code,
    f.departure_time,
    f.arrival_time,
    f.aircraft_type,
    f.capacity,
    f.status,
    f.delay_minutes,
    COUNT(b.booking_id) AS total_bookings,
    ROUND(CASE 
        WHEN f.capacity > 0 THEN (COUNT(b.booking_id) * 100.0 / f.capacity)
        ELSE 0 
    END, 1) AS load_factor_pct,
    ROUND(COALESCE(SUM(fr.price), 0), 2) AS total_revenue
FROM flights f
JOIN airlines al ON f.airline_id = al.airline_id
JOIN airports orig ON f.origin_airport_id = orig.airport_id
JOIN airports dest ON f.destination_airport_id = dest.airport_id
LEFT JOIN bookings b ON f.flight_id = b.flight_id
LEFT JOIN fares fr ON b.fare_id = fr.fare_id
GROUP BY f.flight_id;
