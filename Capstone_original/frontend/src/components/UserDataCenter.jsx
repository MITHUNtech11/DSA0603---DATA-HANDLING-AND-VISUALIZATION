import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Users, UserCheck, UserX, Clock, DollarSign, Search, Filter,
  FileSpreadsheet, RefreshCw, Edit3, X, Check, AlertCircle, ArrowDownToLine,
  TrendingUp, ShieldCheck, CheckCircle2, AlertTriangle, XCircle, ChevronRight
} from 'lucide-react';
import {
  ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend
} from 'recharts';

export default function UserDataCenter() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [userKpis, setUserKpis] = useState(null);
  const [userRecords, setUserRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [notification, setNotification] = useState(null);

  // Status update modal state
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [modalStatus, setModalStatus] = useState('Booked');
  const [modalDelay, setModalDelay] = useState(0);
  const [modalReason, setModalReason] = useState('');
  const [modalRefund, setModalRefund] = useState(0);

  const fetchUserData = async () => {
    setLoading(true);
    try {
      const [kpiRes, recordsRes] = await Promise.all([
        axios.get(`/api/user-data/kpis?search=${encodeURIComponent(searchTerm)}&status=${encodeURIComponent(statusFilter)}`),
        axios.get(`/api/user-data/records?search=${encodeURIComponent(searchTerm)}&status=${encodeURIComponent(statusFilter)}&limit=150`)
      ]);
      setUserKpis(kpiRes.data);
      setUserRecords(recordsRes.data);
    } catch (err) {
      console.error('Error fetching user data:', err);
      showNotification('Failed to fetch user data. Check FastAPI server.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handler = setTimeout(() => {
      fetchUserData();
    }, 250);
    return () => clearTimeout(handler);
  }, [searchTerm, statusFilter]);

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleOpenUpdateModal = (record) => {
    setSelectedRecord(record);
    setModalStatus(record.user_status);
    setModalDelay(record.delay_minutes || 0);
    setModalReason(record.cancellation_reason || '');
    setModalRefund(record.refund_amount || (record.user_status === 'Cancelled' ? record.ticket_price : 0));
  };

  const handleSaveStatusUpdate = async () => {
    if (!selectedRecord) return;
    try {
      const payload = {
        user_data_id: selectedRecord.user_data_id,
        user_status: modalStatus,
        delay_minutes: parseInt(modalDelay) || 0,
        cancellation_reason: modalStatus === 'Cancelled' ? modalReason : null,
        refund_amount: modalStatus === 'Cancelled' ? parseFloat(modalRefund) : 0.0
      };

      const res = await axios.post('/api/user-data/update-status', payload);
      if (res.data.status === 'success') {
        showNotification(`User record ${selectedRecord.user_id} updated to '${modalStatus}' in single table & user_data.xlsx!`);
        setSelectedRecord(null);
        fetchUserData();
      }
    } catch (err) {
      console.error('Error updating user status:', err);
      showNotification('Failed to update status record.', 'error');
    }
  };

  const handleSyncExcel = async () => {
    setSyncing(true);
    try {
      const res = await axios.post('/api/user-data/sync-excel');
      showNotification(`Excel Sync Complete: ${res.data.total_records || 0} user records updated from user_data.xlsx!`);
      fetchUserData();
    } catch (err) {
      console.error('Excel sync error:', err);
      showNotification('Excel sync failed.', 'error');
    } finally {
      setSyncing(false);
    }
  };

  const handleDownloadExcel = () => {
    window.open('/api/user-data/export-excel', '_blank');
    showNotification('Downloading single-table master Excel dataset (user_data.xlsx)...');
  };

  // Status Badge renderer
  const getStatusBadge = (status, delay) => {
    switch (status) {
      case 'Booked':
        return (
          <span className="status-badge on-time" style={{ backgroundColor: '#ecfdf5', color: '#059669', borderColor: '#a7f3d0' }}>
            <CheckCircle2 size={13} />
            Booked
          </span>
        );
      case 'Delayed':
        return (
          <span className="status-badge delayed" style={{ backgroundColor: '#fffbeb', color: '#d97706', borderColor: '#fde68a' }}>
            <AlertTriangle size={13} />
            Delayed ({delay}m)
          </span>
        );
      case 'Cancelled':
        return (
          <span className="status-badge cancelled" style={{ backgroundColor: '#fef2f2', color: '#dc2626', borderColor: '#fecaca' }}>
            <XCircle size={13} />
            Cancelled
          </span>
        );
      case 'Completed':
        return (
          <span className="status-badge scheduled" style={{ backgroundColor: '#eff6ff', color: '#2563eb', borderColor: '#bfdbfe' }}>
            <ShieldCheck size={13} />
            Completed
          </span>
        );
      default:
        return <span className="status-badge">{status}</span>;
    }
  };

  // Chart data calculations
  const statusPieData = [
    { name: 'Booked', value: userKpis?.total_booked || 0, color: '#10b981' },
    { name: 'Delayed', value: userKpis?.total_delayed || 0, color: '#f59e0b' },
    { name: 'Cancelled', value: userKpis?.total_cancelled || 0, color: '#ef4444' },
    { name: 'Completed', value: userKpis?.total_completed || 0, color: '#3b82f6' }
  ];

  // Group user records by Airline for Bar Chart
  const airlineCounts = userRecords.reduce((acc, rec) => {
    const al = rec.airline_name || 'Other';
    if (!acc[al]) acc[al] = { name: al, Booked: 0, Cancelled: 0, Delayed: 0, Completed: 0 };
    acc[al][rec.user_status] = (acc[al][rec.user_status] || 0) + 1;
    return acc;
  }, {});
  const airlineBarData = Object.values(airlineCounts);

  const formatUSD = (num) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num || 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner & Control Toolbar */}
      <section className="filter-toolbar" style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={24} color="#2563eb" />
            Unified Passenger Data & Operations Hub
          </h2>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
            Single master table updates for Bookings, Delays, Cancellations, and Completed flights stored in <strong>user_data.xlsx</strong>.
          </p>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', alignItems: 'center' }}>
          {/* Search Box */}
          <div className="search-box-wrapper" style={{ width: '280px' }}>
            <Search className="search-icon-inside" size={18} />
            <input
              type="text"
              className="search-input"
              placeholder="Search passenger, email, PNR..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button className="clear-search-btn" onClick={() => setSearchTerm('')}>
                <X size={16} />
              </button>
            )}
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '0.6rem 1rem',
              borderRadius: '8px',
              border: '1px solid #cbd5e1',
              backgroundColor: '#ffffff',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: '#334155',
              cursor: 'pointer'
            }}
          >
            <option value="">All User Statuses</option>
            <option value="Booked">Booked</option>
            <option value="Delayed">Delayed</option>
            <option value="Cancelled">Cancelled</option>
            <option value="Completed">Completed</option>
          </select>

          {/* Sync & Download Buttons */}
          <button
            onClick={handleSyncExcel}
            disabled={syncing}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.6rem 1.2rem',
              backgroundColor: '#f1f5f9',
              border: '1px solid #cbd5e1',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#1e293b',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <RefreshCw size={16} className={syncing ? 'spin-animation' : ''} />
            {syncing ? 'Syncing...' : 'Sync Excel'}
          </button>

          <button
            onClick={handleDownloadExcel}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.6rem 1.2rem',
              backgroundColor: '#10b981',
              border: 'none',
              borderRadius: '8px',
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#ffffff',
              cursor: 'pointer',
              boxShadow: '0 2px 4px rgba(16, 185, 129, 0.2)'
            }}
          >
            <FileSpreadsheet size={16} />
            Download Excel (.xlsx)
          </button>
        </div>
      </section>

      {/* Toast Notification */}
      {notification && (
        <div style={{
          backgroundColor: notification.type === 'error' ? '#fef2f2' : '#ecfdf5',
          border: `1px solid ${notification.type === 'error' ? '#fecaca' : '#a7f3d0'}`,
          color: notification.type === 'error' ? '#991b1b' : '#065f46',
          padding: '0.875rem 1.25rem',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          fontSize: '0.9rem',
          fontWeight: 500,
          boxShadow: 'var(--shadow-sm)'
        }}>
          {notification.type === 'error' ? <AlertCircle size={20} /> : <CheckCircle2 size={20} />}
          <span>{notification.msg}</span>
        </div>
      )}

      {/* User Master KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-content">
            <span className="kpi-label">Total Users Managed</span>
            <span className="kpi-value">{userKpis?.total_users || 0}</span>
            <span className="kpi-subtext">Single unified table records</span>
          </div>
          <div className="kpi-icon-wrapper" style={{ backgroundColor: '#eff6ff', color: '#2563eb' }}>
            <Users size={24} />
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-content">
            <span className="kpi-label">Active Bookings</span>
            <span className="kpi-value" style={{ color: '#10b981' }}>{userKpis?.total_booked || 0}</span>
            <span className="kpi-subtext">Ticketed & confirmed passengers</span>
          </div>
          <div className="kpi-icon-wrapper" style={{ backgroundColor: '#ecfdf5', color: '#10b981' }}>
            <UserCheck size={24} />
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-content">
            <span className="kpi-label">Cancelled Operations</span>
            <span className="kpi-value" style={{ color: '#ef4444' }}>{userKpis?.total_cancelled || 0}</span>
            <span className="kpi-subtext">Refunds paid: {formatUSD(userKpis?.total_refund_payout)}</span>
          </div>
          <div className="kpi-icon-wrapper" style={{ backgroundColor: '#fef2f2', color: '#ef4444' }}>
            <UserX size={24} />
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-content">
            <span className="kpi-label">Delayed Passengers</span>
            <span className="kpi-value" style={{ color: '#f59e0b' }}>{userKpis?.total_delayed || 0}</span>
            <span className="kpi-subtext">Avg Delay: {userKpis?.avg_delay_mins || 0} mins</span>
          </div>
          <div className="kpi-icon-wrapper" style={{ backgroundColor: '#fffbeb', color: '#f59e0b' }}>
            <Clock size={24} />
          </div>
        </div>
      </div>

      {/* Visual Analytics Widgets (Pie Donut & Bar Chart) */}
      <div className="charts-grid">
        {/* Widget 1: Donut Chart for Status Distribution */}
        <div className="chart-card">
          <div className="chart-header">
            <h3 className="chart-title">Passenger Status Breakdown</h3>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Unified Data Distribution</span>
          </div>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {statusPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value, name) => [`${value} Passengers`, name]} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Widget 2: Bar Chart by Airline */}
        <div className="chart-card">
          <div className="chart-header">
            <h3 className="chart-title">User Operations by Airline</h3>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Booked vs Cancelled vs Delayed</span>
          </div>
          <div style={{ width: '100%', height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={airlineBarData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Booked" fill="#10b981" stackId="a" />
                <Bar dataKey="Delayed" fill="#f59e0b" stackId="a" />
                <Bar dataKey="Cancelled" fill="#ef4444" stackId="a" />
                <Bar dataKey="Completed" fill="#3b82f6" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Master Single Table for User Data */}
      <div className="table-card">
        <div className="table-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 className="table-title">
            <Users size={20} color="#2563eb" />
            Master Consolidated User Operations Grid
          </h3>
          <span className="table-badge-count">
            Showing {userRecords.length} Master User Rows
          </span>
        </div>

        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Passenger Name</th>
                <th>Contact Info</th>
                <th>PNR / Flight</th>
                <th>Route & Time</th>
                <th>Class & Fare</th>
                <th>User Status</th>
                <th>Delay / Refund</th>
                <th>Last Updated</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {userRecords.length > 0 ? (
                userRecords.map((record) => (
                  <tr key={record.user_data_id}>
                    <td style={{ fontWeight: 600, color: '#2563eb', fontSize: '0.85rem' }}>{record.user_id}</td>
                    <td style={{ fontWeight: 600, color: '#0f172a' }}>{record.passenger_name}</td>
                    <td>
                      <div style={{ fontSize: '0.8rem', color: '#475569' }}>{record.passenger_email}</div>
                      <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{record.passenger_phone}</div>
                    </td>
                    <td>
                      <span style={{ fontWeight: 700, backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px', fontSize: '0.8rem' }}>
                        {record.booking_reference}
                      </span>
                      <div style={{ fontSize: '0.8rem', color: '#2563eb', marginTop: '2px', fontWeight: 600 }}>
                        {record.flight_number} ({record.airline_name})
                      </div>
                    </td>
                    <td style={{ fontSize: '0.825rem' }}>
                      <div style={{ fontWeight: 500 }}>{record.route}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Dep: {record.departure_time}</div>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.8rem', fontWeight: 500 }}>{record.fare_class} (Seat {record.seat_number})</span>
                      <div style={{ fontWeight: 700, color: '#0f172a' }}>{formatUSD(record.ticket_price)}</div>
                    </td>
                    <td>{getStatusBadge(record.user_status, record.delay_minutes)}</td>
                    <td style={{ fontSize: '0.8rem' }}>
                      {record.user_status === 'Delayed' && (
                        <span style={{ color: '#d97706', fontWeight: 600 }}>+{record.delay_minutes} min delay</span>
                      )}
                      {record.user_status === 'Cancelled' && (
                        <div>
                          <span style={{ color: '#dc2626', fontWeight: 600 }}>Refund: {formatUSD(record.refund_amount)}</span>
                          {record.cancellation_reason && (
                            <div style={{ fontSize: '0.725rem', color: '#94a3b8', maxWidth: '140px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={record.cancellation_reason}>
                              {record.cancellation_reason}
                            </div>
                          )}
                        </div>
                      )}
                      {(record.user_status === 'Booked' || record.user_status === 'Completed') && (
                        <span style={{ color: '#64748b' }}>Standard</span>
                      )}
                    </td>
                    <td style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{record.last_updated}</td>
                    <td>
                      <button
                        onClick={() => handleOpenUpdateModal(record)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          padding: '4px 10px',
                          backgroundColor: '#eff6ff',
                          color: '#2563eb',
                          border: '1px solid #bfdbfe',
                          borderRadius: '6px',
                          fontSize: '0.775rem',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        <Edit3 size={13} />
                        Update
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="10" className="empty-state">
                    No matching user records found in single master table.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* In-Place Status Update Modal */}
      {selectedRecord && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            width: '460px',
            maxWidth: '90%',
            padding: '1.5rem',
            boxShadow: 'var(--shadow-lg)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>
                Update Single Table Record: {selectedRecord.user_id}
              </h3>
              <button onClick={() => setSelectedRecord(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ fontSize: '0.85rem', color: '#475569', backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '8px' }}>
              <div><strong>Passenger:</strong> {selectedRecord.passenger_name} ({selectedRecord.booking_reference})</div>
              <div><strong>Flight & Route:</strong> {selectedRecord.flight_number} | {selectedRecord.route}</div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>Select New User Status:</label>
              <select
                value={modalStatus}
                onChange={(e) => setModalStatus(e.target.value)}
                style={{ padding: '0.6rem', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
              >
                <option value="Booked">Booked (Confirmed)</option>
                <option value="Delayed">Delayed (Flight Delay)</option>
                <option value="Cancelled">Cancelled (Flight/User Cancellation)</option>
                <option value="Completed">Completed (Journey Finished)</option>
              </select>

              {modalStatus === 'Delayed' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>Delay Duration (Minutes):</label>
                  <input
                    type="number"
                    value={modalDelay}
                    onChange={(e) => setModalDelay(e.target.value)}
                    style={{ padding: '0.6rem', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
                    min="5"
                  />
                </div>
              )}

              {modalStatus === 'Cancelled' && (
                <>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>Cancellation Reason:</label>
                    <input
                      type="text"
                      placeholder="e.g. Schedule change by airline"
                      value={modalReason}
                      onChange={(e) => setModalReason(e.target.value)}
                      style={{ padding: '0.6rem', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
                    />
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>Refund Amount ($ USD):</label>
                    <input
                      type="number"
                      value={modalRefund}
                      onChange={(e) => setModalRefund(e.target.value)}
                      style={{ padding: '0.6rem', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
                    />
                  </div>
                </>
              )}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button
                onClick={() => setSelectedRecord(null)}
                style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid #cbd5e1', backgroundColor: '#ffffff', cursor: 'pointer' }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveStatusUpdate}
                style={{ padding: '0.5rem 1.25rem', borderRadius: '8px', border: 'none', backgroundColor: '#2563eb', color: '#ffffff', fontWeight: 600, cursor: 'pointer' }}
              >
                Save & Update Excel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
