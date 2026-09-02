import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, X, RefreshCw, PlaneTakeoff, Layers } from 'lucide-react';
import KPICards from './KPICards';
import ChartWidgets from './ChartWidgets';
import OperationalDataTable from './OperationalDataTable';

export default function DashboardLayout() {
  // Global filter state: single unified search field for airline or route
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

  // useEffect hook triggers asynchronous axios requests whenever search input changes (with debounce)
  useEffect(() => {
    const handler = setTimeout(() => {
      fetchData(searchTerm);
    }, 300);

    return () => clearTimeout(handler);
  }, [searchTerm]);

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
            <span className="brand-subtitle">Airline Business Intelligence & Analytics Dashboard</span>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          <span>FastAPI + SQLite SQL Views Connected</span>
        </div>
      </header>

      {/* Main Dashboard Layout Content */}
      <main className="dashboard-body">
        {/* Filter Toolbar with Single Unified Search Field */}
        <section className="filter-toolbar">
          <div className="filter-info">
            <h2 className="filter-title">Business Intelligence Query Console</h2>
            <p className="filter-desc">
              Filter metrics dynamically across all views by typing an airline name (e.g. "Delta"), flight code ("DL101"), or airport city ("New York").
            </p>
          </div>

          {/* Single Unified Search Field (No separate display name input) */}
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

        {/* Global Loading Spinner / Error Banner */}
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
            Loading analytical metrics...
          </div>
        ) : (
          <>
            {/* KPI Summary Cards */}
            <KPICards data={kpiData} />

            {/* Recharts Analytics Widgets */}
            <ChartWidgets routeData={routeData} delayData={delayData} />

            {/* Operational Flight Data Table Grid */}
            <OperationalDataTable flights={flightsData} />
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
