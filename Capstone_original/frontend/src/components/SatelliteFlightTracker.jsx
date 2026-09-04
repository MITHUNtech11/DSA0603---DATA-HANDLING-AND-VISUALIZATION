import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Search, ShieldCheck, Radio, Plane, Compass, Navigation, MapPin,
  Clock, AlertTriangle, XCircle, CheckCircle2, RefreshCw, Layers, Lock
} from 'lucide-react';

export default function SatelliteFlightTracker() {
  const [searchQuery, setSearchQuery] = useState('');
  const [telemetryData, setTelemetryData] = useState(null);
  const [activeFlights, setActiveFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTelemetry = async (query = '') => {
    setLoading(true);
    setError(null);
    try {
      const url = query && query.trim() ? `/api/satellite-tracker/telemetry/${encodeURIComponent(query.trim())}` : '/api/satellite-tracker/telemetry';
      const res = await axios.get(url);
      if (res.data.status === 'success') {
        setTelemetryData(res.data);
      } else {
        setError(res.data.message || 'No telemetry record found.');
      }
    } catch (err) {
      console.error('Error fetching satellite telemetry:', err);
      setError('Unable to retrieve satellite flight telemetry.');
    } finally {
      setLoading(false);
    }
  };


  const fetchActiveFlights = async () => {
    try {
      const res = await axios.get('/api/satellite-tracker/active');
      setActiveFlights(res.data || []);
    } catch (err) {
      console.error('Error fetching active satellite flights:', err);
    }
  };

  useEffect(() => {
    fetchActiveFlights();
    fetchTelemetry('');
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      fetchTelemetry(searchQuery);
    }
  };

  const handleSelectActiveFlight = (pnr) => {
    setSearchQuery(pnr);
    fetchTelemetry(pnr);
  };

  const { passenger, flight, telemetry } = telemetryData || {};
  const { origin, destination } = flight || {};

  // Standard Map Coordinate Projections (SVG Map Canvas)
  // Map dimensions: 800 x 360
  const mapWidth = 800;
  const mapHeight = 360;

  const projectToMap = (lat, lng) => {
    // Mercator-style linear projection for standard map canvas
    const x = ((lng + 180) / 360) * mapWidth;
    const y = ((90 - lat) / 180) * mapHeight;
    return { x, y };
  };

  const origPos = origin ? projectToMap(origin.lat, origin.lng) : { x: 200, y: 180 };
  const destPos = destination ? projectToMap(destination.lat, destination.lng) : { x: 600, y: 180 };
  const currentPos = telemetry ? projectToMap(telemetry.current_latitude, telemetry.current_longitude) : origPos;

  // Control points for curved SVG arc line
  const midX = (origPos.x + destPos.x) / 2;
  const midY = Math.min(origPos.y, destPos.y) - 60;
  const pathD = `M ${origPos.x} ${origPos.y} Q ${midX} ${midY} ${destPos.x} ${destPos.y}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner & Family Search Console */}
      <section className="filter-toolbar" style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Radio size={24} color="#2563eb" />
            Satellite Flight Radar & Family Safety Tracking Hub
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
            Real-time satellite trajectory & flight safety telemetry for passenger family members.
          </p>
        </div>

        {/* PNR / Flight Lookup Console */}
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div className="search-box-wrapper" style={{ width: '320px' }}>
            <Search className="search-icon-inside" size={18} />
            <input
              type="text"
              className="search-input"
              placeholder="Enter PNR or Flight No (e.g. PNR-8F92A)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <button
            type="submit"
            style={{
              padding: '0.6rem 1.25rem',
              backgroundColor: '#2563eb',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer'
            }}
          >
            Track Flight
          </button>
        </form>
      </section>

      {/* Privacy Safeguard & Verified Family Safety Banner */}
      {telemetry && (
        <div style={{
          backgroundColor: flight?.status === 'Cancelled' ? '#fef2f2' : '#ecfdf5',
          border: `1px solid ${flight?.status === 'Cancelled' ? '#fecaca' : '#a7f3d0'}`,
          color: flight?.status === 'Cancelled' ? '#991b1b' : '#065f46',
          padding: '1rem 1.25rem',
          borderRadius: '10px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <ShieldCheck size={26} color={flight?.status === 'Cancelled' ? '#ef4444' : '#10b981'} />
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{telemetry.safety_status_text}</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.9, marginTop: '2px' }}>
                <Lock size={12} style={{ display: 'inline', marginRight: '4px' }} />
                Passenger Personal Location Privacy Protected: <strong>{passenger?.masked_name}</strong> ({passenger?.pnr}) | Seat {passenger?.seat_number} ({passenger?.fare_class})
              </div>
            </div>
          </div>
          <span style={{ fontSize: '0.775rem', backgroundColor: 'rgba(255,255,255,0.7)', padding: '4px 10px', borderRadius: '6px', fontWeight: 600 }}>
            Satellite Ping: {telemetry.satellite_last_ping}
          </span>
        </div>
      )}

      {loading ? (
        <div className="loading-spinner">
          <RefreshCw size={24} className="spin-animation" style={{ marginRight: 8 }} />
          Connecting to Satellite Flight Telemetry Stream...
        </div>
      ) : error ? (
        <div style={{ backgroundColor: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', padding: '1rem 1.5rem', borderRadius: '10px', fontWeight: 500 }}>
          {error}
        </div>
      ) : telemetryData ? (
        <>
          {/* Telemetry Cards Grid */}
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-content">
                <span className="kpi-label">Current Altitude</span>
                <span className="kpi-value" style={{ color: '#2563eb' }}>
                  {telemetry.altitude_ft.toLocaleString()} <span style={{ fontSize: '0.9rem', color: '#64748b' }}>FT</span>
                </span>
                <span className="kpi-subtext">Phase: {telemetry.flight_phase}</span>
              </div>
              <div className="kpi-icon-wrapper" style={{ backgroundColor: '#eff6ff', color: '#2563eb' }}>
                <Compass size={24} />
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-content">
                <span className="kpi-label">Ground Speed</span>
                <span className="kpi-value" style={{ color: '#10b981' }}>
                  {telemetry.ground_speed_kts} <span style={{ fontSize: '0.9rem', color: '#64748b' }}>KTS</span>
                </span>
                <span className="kpi-subtext">Satellite Speed Measurement</span>
              </div>
              <div className="kpi-icon-wrapper" style={{ backgroundColor: '#ecfdf5', color: '#10b981' }}>
                <Navigation size={24} />
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-content">
                <span className="kpi-label">Satellite Coordinates</span>
                <span className="kpi-value" style={{ fontSize: '1.1rem', color: '#0f172a' }}>
                  {telemetry.current_latitude}°, {telemetry.current_longitude}°
                </span>
                <span className="kpi-subtext">Progress: {telemetry.progress_pct}% Completed</span>
              </div>
              <div className="kpi-icon-wrapper" style={{ backgroundColor: '#faf5ff', color: '#9333ea' }}>
                <MapPin size={24} />
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-content">
                <span className="kpi-label">Distance & Time to Arrival</span>
                <span className="kpi-value" style={{ color: '#f59e0b' }}>
                  {telemetry.remaining_distance_miles} <span style={{ fontSize: '0.85rem', color: '#64748b' }}>MI</span>
                </span>
                <span className="kpi-subtext">ETA: ~{telemetry.eta_minutes} mins remaining</span>
              </div>
              <div className="kpi-icon-wrapper" style={{ backgroundColor: '#fffbeb', color: '#f59e0b' }}>
                <Clock size={24} />
              </div>
            </div>
          </div>

          {/* Standard Map & Info View Section */}
          <div className="table-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div>
                <h3 className="table-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Plane size={20} color="#2563eb" />
                  Flight {flight.flight_number} Telemetry Trajectory ({flight.airline_name})
                </h3>
                <p style={{ fontSize: '0.825rem', color: '#64748b', marginTop: '2px' }}>
                  Origin: <strong>{origin.name}</strong> &rarr; Destination: <strong>{destination.name}</strong>
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.85rem' }}>
                <span style={{ backgroundColor: '#f1f5f9', padding: '4px 10px', borderRadius: '6px', fontWeight: 600 }}>
                  Departure: {flight.departure_time}
                </span>
              </div>
            </div>

            {/* Standard SVG Flight Map Canvas */}
            <div style={{
              position: 'relative',
              width: '100%',
              height: '360px',
              backgroundColor: '#0f172a',
              borderRadius: '12px',
              overflow: 'hidden',
              boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.5)'
            }}>
              <svg width="100%" height="100%" viewBox={`0 0 ${mapWidth} ${mapHeight}`} style={{ display: 'block' }}>
                {/* Map Grid Lines */}
                <defs>
                  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />

                {/* Great Circle Flight Trajectory Arc */}
                <path d={pathD} fill="none" stroke="#3b82f6" strokeWidth="3" strokeDasharray="6 4" />

                {/* Origin Airport Pin */}
                <g transform={`translate(${origPos.x}, ${origPos.y})`}>
                  <circle r="8" fill="#10b981" />
                  <circle r="14" fill="none" stroke="#10b981" strokeWidth="1.5" opacity="0.6" />
                  <text y="24" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="700">
                    {origin.city} ({origin.name.split('(')[1]?.replace(')', '') || 'DEP'})
                  </text>
                </g>

                {/* Destination Airport Pin */}
                <g transform={`translate(${destPos.x}, ${destPos.y})`}>
                  <circle r="8" fill="#ef4444" />
                  <circle r="14" fill="none" stroke="#ef4444" strokeWidth="1.5" opacity="0.6" />
                  <text y="24" textAnchor="middle" fill="#ffffff" fontSize="12" fontWeight="700">
                    {destination.city} ({destination.name.split('(')[1]?.replace(')', '') || 'ARR'})
                  </text>
                </g>

                {/* Current Satellite Airplane Position Marker */}
                {flight.status !== 'Cancelled' && (
                  <g transform={`translate(${currentPos.x}, ${currentPos.y})`}>
                    {/* Pulsing satellite marker */}
                    <circle r="16" fill="rgba(59, 130, 246, 0.35)" />
                    <circle r="6" fill="#38bdf8" />
                    <Plane size={18} color="#ffffff" style={{ transform: 'translate(-9px, -9px)' }} />
                    <text y="-20" textAnchor="middle" fill="#38bdf8" fontSize="11" fontWeight="700" backgroundColor="#000000">
                      🛰️ {flight.flight_number} ({telemetry.altitude_ft.toLocaleString()} FT)
                    </text>
                  </g>
                )}
              </svg>

              {/* Map Footer Overlay */}
              <div style={{
                position: 'absolute',
                bottom: '12px',
                left: '16px',
                right: '16px',
                display: 'flex',
                justify: 'space-between',
                backgroundColor: 'rgba(15, 23, 42, 0.85)',
                backdropFilter: 'blur(4px)',
                padding: '8px 16px',
                borderRadius: '8px',
                color: '#94a3b8',
                fontSize: '0.8rem',
                border: '1px solid rgba(255,255,255,0.1)'
              }}>
                <span><strong>Origin:</strong> {origin.name} ({origin.city}, {origin.country})</span>
                <span><strong>Current Coordinates:</strong> {telemetry.current_latitude}°, {telemetry.current_longitude}°</span>
                <span><strong>Destination:</strong> {destination.name} ({destination.city}, {destination.country})</span>
              </div>
            </div>
          </div>
        </>
      ) : null}

      {/* Active Flights Quick Selector List */}
      <div className="table-card">
        <div className="table-header">
          <h3 className="table-title">
            <Radio size={20} color="#2563eb" />
            Active Satellite Flights Available for Family Tracking
          </h3>
          <span className="table-badge-count">Showing {activeFlights.length} Active Flights</span>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Flight No</th>
                <th>Airline</th>
                <th>Passenger (Masked)</th>
                <th>PNR Tracking Code</th>
                <th>Route</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {activeFlights.length > 0 ? (
                activeFlights.map((af) => (
                  <tr key={af.user_data_id}>
                    <td style={{ fontWeight: 700, color: '#2563eb' }}>{af.flight_number}</td>
                    <td>{af.airline_name}</td>
                    <td style={{ fontWeight: 600 }}>{af.passenger_masked}</td>
                    <td>
                      <span style={{ backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px', fontWeight: 700, fontSize: '0.8rem' }}>
                        {af.pnr}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.85rem' }}>{af.route}</td>
                    <td>
                      <span className={`status-badge ${af.status === 'Booked' ? 'on-time' : af.status === 'Delayed' ? 'delayed' : 'scheduled'}`}>
                        {af.status}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => handleSelectActiveFlight(af.pnr)}
                        style={{
                          padding: '4px 12px',
                          backgroundColor: '#2563eb',
                          color: '#ffffff',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '0.775rem',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        Track Satellite Radar
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="empty-state">No active satellite flight records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
