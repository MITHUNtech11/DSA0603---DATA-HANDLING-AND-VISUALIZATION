import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, X, RefreshCw, PlaneTakeoff, Layers, Users, Radio } from 'lucide-react';
import KPICards from './KPICards';
import ChartWidgets from './ChartWidgets';
import OperationalDataTable from './OperationalDataTable';
import UserDataCenter from './UserDataCenter';
import SatelliteFlightTracker from './SatelliteFlightTracker';

export default function DashboardLayout() {
  const [activeTab, setActiveTab] = useState('satellite-tracker'); // Default tab set to Satellite Flight Radar
  const [searchTerm, setSearchTerm] = useState('');
  
  // Data states fetched from FastAPI endpoints
  const [kpiData, setKpiData] = useState(null);
  const [routeData, setRouteData] = useState([]);
  const [delayData, setDelayData] = useState([]);
  const [flightsData, setFlightsData] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch data sequence from FastAPI backend
  const fetchData = async (search = '') => {
    setLoading(true);
    setError(null);
    try {
      const [kpiRes, routeRes, delayRes, flightsRes] = await Promise.all([
        axios.get(`/api/kpis?search=${encodeURIComponent(search)}`),
        axios.get(`/api/route-performance?search=${encodeURIComponent(search)}`),
        axios.get(`/api/delay-heatmap?search=${encodeURIComponent(search)}`),
        axios.get(`/api/flights?search=${encodeURIComponent(search)}&limit=100`)
      ]);

      setKpiData(kpiRes.data);
      setRouteData(routeRes.data);
      setDelayData(delayRes.data);
      setFlightsData(flightsRes.data);
    } catch (err) {
      console.error('Error fetching data from FastAPI backend:', err);
      setError('Unable to fetch BI metrics. Please check if the FastAPI backend is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'flight-ops') {
      const handler = setTimeout(() => {
        fetchData(searchTerm);
      }, 300);

      return () => clearTimeout(handler);
    }
  }, [searchTerm, activeTab]);

  return (
    <div className="app-container">
      {/* Top Navbar */}
      <header className="navbar">
        <div className="brand-section">
          <div className="brand-icon">
            <PlaneTakeoff size={22} />
          </div>
          <div>
            <h1 className="brand-title">SkyMetrics BI</h1>
            <span className="brand-subtitle">Airline BI, Single-Table Operations & Satellite Radar</span>
          </div>
        </div>

        {/* Tab Navigation Switcher */}
        <div style={{ display: 'flex', gap: '0.4rem', backgroundColor: '#f1f5f9', padding: '4px', borderRadius: '10px' }}>
          <button
            onClick={() => setActiveTab('satellite-tracker')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '0.5rem 1.1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'satellite-tracker' ? '#ffffff' : 'transparent',
              color: activeTab === 'satellite-tracker' ? '#2563eb' : '#64748b',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              boxShadow: activeTab === 'satellite-tracker' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.2s'
            }}
          >
            <Radio size={17} />
            Satellite Flight Radar
          </button>

          <button
            onClick={() => setActiveTab('user-data')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '0.5rem 1.1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'user-data' ? '#ffffff' : 'transparent',
              color: activeTab === 'user-data' ? '#2563eb' : '#64748b',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              boxShadow: activeTab === 'user-data' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.2s'
            }}
          >
            <Users size={17} />
            Unified User Data Hub
          </button>

          <button
            onClick={() => setActiveTab('flight-ops')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '0.5rem 1.1rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'flight-ops' ? '#ffffff' : 'transparent',
              color: activeTab === 'flight-ops' ? '#2563eb' : '#64748b',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              boxShadow: activeTab === 'flight-ops' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              transition: 'all 0.2s'
            }}
          >
            <PlaneTakeoff size={17} />
            Flight Operations BI
          </button>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          <span>FastAPI + Satellite Radar Live</span>
        </div>
      </header>

      {/* Main Dashboard Layout Content */}
      <main className="dashboard-body">
        {activeTab === 'satellite-tracker' ? (
          <SatelliteFlightTracker />
        ) : activeTab === 'user-data' ? (
          <UserDataCenter />
        ) : (
          <>
            {/* Filter Toolbar for Flight Ops */}
            <section className="filter-toolbar">
              <div className="filter-info">
                <h2 className="filter-title">Flight Operations Query Console</h2>
                <p className="filter-desc">
                  Filter metrics dynamically across all views by typing an airline name (e.g. "Delta"), flight code ("DL101"), or airport city ("New York").
                </p>
              </div>

              <div className="search-box-wrapper">
                <Search className="search-icon-inside" size={18} />
                <input
                  type="text"
                  className="search-input"
                  placeholder="Search airline or route..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
                {searchTerm && (
                  <button
                    className="clear-search-btn"
                    onClick={() => setSearchTerm('')}
                    title="Clear Search"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            </section>

            {error && (
              <div style={{
                backgroundColor: '#fef2f2',
                border: '1px solid #fecaca',
                color: '#991b1b',
                padding: '1rem 1.5rem',
                borderRadius: '10px',
                fontSize: '0.9rem',
                fontWeight: 500
              }}>
                {error}
              </div>
            )}

            {loading && !kpiData ? (
              <div className="loading-spinner">
                <RefreshCw size={24} className="spin-animation" style={{ marginRight: 8 }} />
                Loading operational metrics...
              </div>
            ) : (
              <>
                <KPICards data={kpiData} />
                <ChartWidgets routeData={routeData} delayData={delayData} />
                <OperationalDataTable flights={flightsData} />
              </>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        Capstone Project - Airline Business Intelligence & Data Handling Platform | Built with React, FastAPI & SQLite
      </footer>
    </div>
  );
}


