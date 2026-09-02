import React from 'react';
import { DollarSign, Ticket, Percent, Clock } from 'lucide-react';

export default function KPICards({ data }) {
  const {
    total_revenue = 0,
    total_bookings = 0,
    avg_load_factor = 0,
    on_time_rate = 0,
    total_flights = 0
  } = data || {};

  const formattedRevenue = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0
  }).format(total_revenue);

  const formattedBookings = new Intl.NumberFormat('en-US').format(total_bookings);

  return (
    <div className="kpi-grid">
      {/* KPI 1: Revenue */}
      <div className="kpi-card">
        <div className="kpi-content">
          <span className="kpi-label">Total Revenue</span>
          <span className="kpi-value">{formattedRevenue}</span>
          <span className="kpi-subtext">Pre-aggregated SQL View metrics</span>
        </div>
        <div className="kpi-icon-wrapper" style={{ backgroundColor: '#eff6ff', color: '#2563eb' }}>
          <DollarSign size={24} />
        </div>
      </div>

      {/* KPI 2: Bookings */}
      <div className="kpi-card">
        <div className="kpi-content">
          <span className="kpi-label">Total Bookings</span>
          <span className="kpi-value">{formattedBookings}</span>
          <span className="kpi-subtext">Passenger reservations ticketed</span>
        </div>
        <div className="kpi-icon-wrapper" style={{ backgroundColor: '#f0fdf4', color: '#16a34a' }}>
          <Ticket size={24} />
        </div>
      </div>

      {/* KPI 3: Load Factor */}
      <div className="kpi-card">
        <div className="kpi-content">
          <span className="kpi-label">Avg Load Factor</span>
          <span className="kpi-value">{avg_load_factor}%</span>
          <span className="kpi-subtext">Flight capacity utilization rate</span>
        </div>
        <div className="kpi-icon-wrapper" style={{ backgroundColor: '#faf5ff', color: '#9333ea' }}>
          <Percent size={24} />
        </div>
      </div>

      {/* KPI 4: On-Time Performance */}
      <div className="kpi-card">
        <div className="kpi-content">
          <span className="kpi-label">On-Time Rate</span>
          <span className="kpi-value">{on_time_rate}%</span>
          <span className="kpi-subtext">Across {total_flights} total flights</span>
        </div>
        <div className="kpi-icon-wrapper" style={{ backgroundColor: '#fff7ed', color: '#ea580c' }}>
          <Clock size={24} />
        </div>
      </div>
    </div>
  );
}
