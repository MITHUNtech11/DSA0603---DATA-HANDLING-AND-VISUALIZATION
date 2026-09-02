import React from 'react';
import { Plane, CheckCircle2, AlertTriangle, XCircle, Calendar } from 'lucide-react';

export default function OperationalDataTable({ flights = [] }) {
  const getStatusBadge = (status, delay) => {
    switch (status) {
      case 'On-Time':
        return (
          <span className="status-badge on-time">
            <CheckCircle2 size={13} />
            On-Time
          </span>
        );
      case 'Delayed':
        return (
          <span className="status-badge delayed">
            <AlertTriangle size={13} />
            Delayed ({delay}m)
          </span>
        );
      case 'Cancelled':
        return (
          <span className="status-badge cancelled">
            <XCircle size={13} />
            Cancelled
          </span>
        );
      default:
        return (
          <span className="status-badge scheduled">
            <Calendar size={13} />
            Scheduled
          </span>
        );
    }
  };

  const formatCurrency = (val) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val || 0);
  };

  return (
    <div className="table-card">
      <div className="table-header">
        <h3 className="table-title">
          <Plane size={20} color="#2563eb" />
          Operational Flight Intelligence Grid
        </h3>
        <span className="table-badge-count">Showing {flights.length} Flights</span>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th>Flight No</th>
              <th>Airline</th>
              <th>Origin</th>
              <th>Destination</th>
              <th>Departure Time</th>
              <th>Aircraft</th>
              <th>Bookings / Cap</th>
              <th>Load Factor</th>
              <th>Total Revenue</th>
              {/* Flight Status is strictly designated as a column header in the table structure */}
              <th>Flight Status</th>
            </tr>
          </thead>
          <tbody>
            {flights.length > 0 ? (
              flights.map((flight) => (
                <tr key={flight.flight_id}>
                  <td style={{ fontWeight: 600, color: '#2563eb' }}>{flight.flight_number}</td>
                  <td style={{ fontWeight: 500 }}>{flight.airline_name}</td>
                  <td>{flight.origin}</td>
                  <td>{flight.destination}</td>
                  <td style={{ fontSize: '0.85rem', color: '#64748b' }}>{flight.departure_time}</td>
                  <td>{flight.aircraft_type}</td>
                  <td>
                    {flight.total_bookings} / {flight.capacity}
                  </td>
                  <td>
                    <span style={{
                      fontWeight: 600,
                      color: flight.load_factor_pct >= 80 ? '#10b981' : flight.load_factor_pct >= 60 ? '#3b82f6' : '#f59e0b'
                    }}>
                      {flight.load_factor_pct}%
                    </span>
                  </td>
                  <td style={{ fontWeight: 600 }}>{formatCurrency(flight.total_revenue)}</td>
                  <td>{getStatusBadge(flight.status, flight.delay_minutes)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="10" className="empty-state">
                  No matching flight records found in database. Try adjusting your search query.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
