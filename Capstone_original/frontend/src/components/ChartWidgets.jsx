import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { BarChart3, AlertCircle } from 'lucide-react';

export default function ChartWidgets({ routeData = [], delayData = [] }) {
  // Format revenue numbers for chart tooltip
  const formatCurrencyTooltip = (value) => [
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value),
    'Revenue'
  ];

  // Process day of week delay breakdown
  const dayOrder = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  
  // Aggregate delay counts per day
  const dayDelayMap = {};
  dayOrder.forEach(day => {
    dayDelayMap[day] = { day, OnTime: 0, Delayed: 0, Cancelled: 0, Scheduled: 0 };
  });

  delayData.forEach(item => {
    if (dayDelayMap[item.day_of_week]) {
      const statusKey = item.status === 'On-Time' ? 'OnTime' : item.status;
      dayDelayMap[item.day_of_week][statusKey] = (dayDelayMap[item.day_of_week][statusKey] || 0) + item.flight_count;
    }
  });

  const formattedDelayData = dayOrder.map(day => dayDelayMap[day]);

  return (
    <div className="charts-grid">
      {/* Chart 1: Route Performance Bar Chart */}
      <div className="chart-card">
        <div className="chart-header">
          <h3 className="chart-title">
            <BarChart3 size={20} color="#2563eb" />
            Route Revenue & Performance
          </h3>
          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Top Routes by Revenue</span>
        </div>
        <div className="chart-container">
          {routeData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={routeData}
                margin={{ top: 10, right: 20, left: 10, bottom: 40 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="route" 
                  tick={{ fontSize: 11, fill: '#475569' }} 
                  interval={0}
                  angle={-20}
                  textAnchor="end"
                />
                <YAxis 
                  yAxisId="left"
                  orientation="left"
                  stroke="#2563eb"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(0)}k`}
                />
                <YAxis 
                  yAxisId="right"
                  orientation="right"
                  stroke="#10b981"
                  tick={{ fontSize: 11 }}
                />
                <Tooltip formatter={formatCurrencyTooltip} />
                <Legend wrapperStyle={{ paddingTop: 10 }} />
                <Bar yAxisId="left" dataKey="total_revenue" name="Total Revenue ($)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" dataKey="total_bookings" name="Bookings Count" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">No route performance data matches the search filter.</div>
          )}
        </div>
      </div>

      {/* Chart 2: Delay Distribution by Day of Week (Heatmap Widget) */}
      <div className="chart-card">
        <div className="chart-header">
          <h3 className="chart-title">
            <AlertCircle size={20} color="#f59e0b" />
            Weekly Operational Status Heatmap
          </h3>
          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Flight Count Breakdown</span>
        </div>
        <div className="chart-container">
          {formattedDelayData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={formattedDelayData}
                margin={{ top: 10, right: 10, left: 0, bottom: 25 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#475569' }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ paddingTop: 10 }} />
                <Bar dataKey="OnTime" name="On-Time" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Delayed" name="Delayed" stackId="a" fill="#f59e0b" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Cancelled" name="Cancelled" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
                <Bar dataKey="Scheduled" name="Scheduled" stackId="a" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">No status delay data available.</div>
          )}
        </div>
      </div>
    </div>
  );
}
