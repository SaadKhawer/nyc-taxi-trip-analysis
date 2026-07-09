import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Activity, Clock, MapPin, AlertTriangle, TrendingUp, CalendarDays, Download, CloudRain, Calendar, Map as MapIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import './index.css';

// Fix leaflet icon issue in React
import * as L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

const API_BASE = 'http://127.0.0.1:5000/api';

const TOP_ZONES = [
  { id: 142, name: 'Lincoln Square East', lat: 40.7738, lng: -73.9822 },
  { id: 161, name: 'Midtown Center', lat: 40.7577, lng: -73.9798 },
  { id: 186, name: 'Penn Station', lat: 40.7506, lng: -73.9935 },
  { id: 236, name: 'Upper East Side North', lat: 40.7736, lng: -73.9566 },
  { id: 237, name: 'Upper East Side South', lat: 40.7675, lng: -73.9614 }
];

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', color: 'red', background: '#fee2e2', borderRadius: '8px', margin: '2rem' }}>
          <h2>Dashboard Crashed!</h2>
          <p>{this.state.error && this.state.error.toString()}</p>
          <pre style={{ fontSize: '10px', marginTop: '1rem', overflowX: 'auto' }}>
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

function Dashboard() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // CSV Data State
  const [csvType, setCsvType] = useState('hour');
  const [csvData, setCsvData] = useState([]);
  
  // Predictor & Chart State
  const [zoneId, setZoneId] = useState('142');
  const [targetTime, setTargetTime] = useState('2024-01-26 22:00');
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [error, setError] = useState('');
  const [chartData, setChartData] = useState([]);

  // Future Toggles
  const [weatherEnabled, setWeatherEnabled] = useState(false);
  const [eventsEnabled, setEventsEnabled] = useState(false);

  const dashboardRef = useRef();

  useEffect(() => {
    // Fetch Results
    axios.get(`${API_BASE}/results`)
      .then(res => {
        setResults(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setError('Failed to load evaluation results. Is the Flask API running?');
        setLoading(false);
      });
      
    fetchChartData(zoneId);
  }, []);

  useEffect(() => {
    axios.get(`${API_BASE}/data/csv?type=${csvType}`)
      .then(res => setCsvData(res.data))
      .catch(err => console.error(err));
  }, [csvType]);

  const fetchChartData = (zone) => {
    axios.get(`${API_BASE}/data/chart?zone_id=${zone}`)
      .then(res => setChartData(res.data))
      .catch(err => console.error(err));
  };

  const handlePredict = async (e) => {
    if (e) e.preventDefault();
    setPredicting(true);
    setError('');
    setPrediction(null);
    
    try {
      const res = await axios.post(`${API_BASE}/predict`, {
        zone_id: zoneId,
        target_time: targetTime
      });
      setPrediction(res.data.predicted_demand);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get prediction');
    }
    setPredicting(false);
  };

  const handleZoneSelect = (id) => {
    setZoneId(id.toString());
    fetchChartData(id);
    // Optionally trigger prediction automatically
  };

  const downloadPDF = () => {
    const input = dashboardRef.current;
    html2canvas(input, { scale: 2 }).then((canvas) => {
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('NYC_Taxi_Demand_Report.pdf');
    });
  };

  if (loading) return <div className="loading">Loading Dashboard...</div>;

  return (
    <div className="dashboard-container" ref={dashboardRef}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ textAlign: 'left' }}>
          <h1>NYC Taxi Demand Forecaster</h1>
          <p>AI-powered predictions to optimize fleet availability across 265 zones.</p>
        </div>
        <button className="btn" style={{ width: 'auto', background: 'var(--text-main)' }} onClick={downloadPDF}>
          <Download size={18} /> Download PDF Report
        </button>
      </header>

      {/* Map Section */}
      <div className="card" style={{ marginBottom: '2rem', padding: '1rem' }}>
        <div className="card-title" style={{ marginBottom: '1rem' }}>
          <MapIcon size={24} />
          Interactive NYC Map (Top Demand Zones)
        </div>
        <div style={{ height: '350px', borderRadius: '12px', overflow: 'hidden', border: '1px solid var(--card-border)' }}>
          <MapContainer center={[40.76, -73.97]} zoom={13} style={{ height: '100%', width: '100%' }}>
            <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />
            {TOP_ZONES.map(zone => (
              <Marker 
                key={zone.id} 
                position={[zone.lat, zone.lng]}
                eventHandlers={{ click: () => handleZoneSelect(zone.id) }}
              >
                <Popup>
                  <strong>{zone.name} (Zone {zone.id})</strong><br/>
                  Click to analyze demand.
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.5rem', textAlign: 'center' }}>
          Click on a map marker to automatically load its forecasting data.
        </p>
      </div>

      <div className="grid">
        {/* Live Predictor Card */}
        <div className="card">
          <div className="card-title">
            <Activity size={24} />
            Live AI Predictor
          </div>
          <form onSubmit={handlePredict}>
            <div className="input-group">
              <label>Zone ID (1-265)</label>
              <input 
                type="number" 
                value={zoneId} 
                onChange={e => {
                  setZoneId(e.target.value);
                  if (e.target.value.length > 0) fetchChartData(e.target.value);
                }} 
                min="1" max="265" required 
              />
            </div>
            <div className="input-group">
              <label>Target Date & Time</label>
              <input 
                type="text" 
                value={targetTime} 
                onChange={e => setTargetTime(e.target.value)} 
                placeholder="YYYY-MM-DD HH:00" required 
              />
            </div>
            <button type="submit" className="btn" disabled={predicting}>
              {predicting ? 'Predicting...' : 'Generate Forecast'}
            </button>
          </form>

          {error && <p style={{color: 'red', marginTop: '1rem', fontSize: '0.9rem'}}>{error}</p>}

          {prediction !== null && (
            <div className="prediction-result">
              <h3>Expected Pickups</h3>
              <div className="number">{prediction}</div>
            </div>
          )}
        </div>

        {/* Model Evaluation Card */}
        {results && (
          <div className="card">
            <div className="card-title">
              <TrendingUp size={24} />
              Model Performance
            </div>
            <p style={{color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem'}}>
              Random Forest Regressor Evaluation
            </p>
            <div className="metrics-grid">
              <div className="metric-item">
                <div className="metric-label">RMSE</div>
                <div className="metric-val">{results.evaluation.RandomForest.RMSE.toFixed(2)}</div>
              </div>
              <div className="metric-item">
                <div className="metric-label">MAE</div>
                <div className="metric-val">{results.evaluation.RandomForest.MAE.toFixed(2)}</div>
              </div>
            </div>
            
            <div style={{marginTop: '2rem'}}>
              <h4 style={{marginBottom: '1rem', color: 'var(--text-main)'}}>Baseline Comparison</h4>
              <ul>
                <li style={{display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem'}}>
                  <span>Naive Baseline RMSE</span>
                  <span className="badge">{results.evaluation.Baseline.RMSE.toFixed(2)}</span>
                </li>
                <li style={{display: 'flex', justifyContent: 'space-between'}}>
                  <span>Linear Reg. RMSE</span>
                  <span className="badge">{results.evaluation.LinearRegression.RMSE.toFixed(2)}</span>
                </li>
              </ul>
            </div>
          </div>
        )}

        {/* Future Scope Toggles */}
        <div className="card">
          <div className="card-title">
            <TrendingUp size={24} />
            Future Scope (Beta)
          </div>
          <p style={{color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem'}}>
            Features planned for the next sprint based on Failure Analysis.
          </p>
          
          <div className="toggle-row">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                <CloudRain size={18} color="var(--primary)"/> Weather API Integration
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Adjusts demand for rain/snow shocks.</p>
            </div>
            <label className="switch">
              <input type="checkbox" checked={weatherEnabled} onChange={(e) => {
                setWeatherEnabled(e.target.checked);
                if(e.target.checked) alert("Simulating Weather API connection... (Mockup Demo)");
              }} />
              <span className="slider round"></span>
            </label>
          </div>

          <div className="toggle-row" style={{ marginTop: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                <Calendar size={18} color="var(--primary)"/> Public Events & Concerts
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Captures massive nightlife demand spikes.</p>
            </div>
            <label className="switch">
              <input type="checkbox" checked={eventsEnabled} onChange={(e) => {
                setEventsEnabled(e.target.checked);
                if(e.target.checked) alert("Simulating MSG/Broadway Events API... (Mockup Demo)");
              }} />
              <span className="slider round"></span>
            </label>
          </div>
        </div>

        {/* Failure Analysis Card */}
        {results && (
          <div className="card">
            <div className="card-title">
              <AlertTriangle size={24} />
              Failure Analysis Findings
            </div>
            
            <div style={{marginBottom: '1.5rem'}}>
              <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem'}}>
                <Clock size={16} /> Worst Performing Hours
              </h4>
              <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
                {Object.keys(results.failure_analysis.worst_hours).map(h => (
                  <span key={h} className="badge">{h}:00</span>
                ))}
              </div>
            </div>

            <div style={{marginBottom: '1.5rem'}}>
              <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem'}}>
                <CalendarDays size={16} /> Worst Performing Days
              </h4>
              <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
                {Object.keys(results.failure_analysis.worst_days).map(d => (
                  <span key={d} className="badge">{d}</span>
                ))}
              </div>
            </div>

            <div>
              <h4 style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem'}}>
                <MapPin size={16} /> Worst Performing Zones
              </h4>
              <div style={{display: 'flex', gap: '0.5rem', flexWrap: 'wrap'}}>
                {Object.keys(results.failure_analysis.worst_zones).map(z => (
                  <span key={z} className="badge">Zone {z}</span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recharts Live Visualization */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-title">
          Live Forecasting Graph: Zone {zoneId}
        </div>
        <div style={{ height: '400px', width: '100%' }}>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="time" minTickGap={50} tick={{fontSize: 12}} />
                <YAxis />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: 'var(--shadow-md)' }}
                />
                <Legend />
                <Line type="monotone" dataKey="actual" stroke="#64748b" strokeWidth={2} dot={false} name="Actual Pickups" />
                <Line type="monotone" dataKey="predicted" stroke="#2563eb" strokeWidth={3} dot={false} name="AI Prediction" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-muted)' }}>
              No chart data available for this zone.
            </div>
          )}
        </div>
      </div>

      {/* CSV Data Explorer */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <div className="card-title" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <Activity size={24} />
            Data Explorer (CSV Data)
          </div>
          <select 
            className="csv-select"
            value={csvType} 
            onChange={(e) => setCsvType(e.target.value)}
          >
            <option value="hour">Averages by Hour</option>
            <option value="day">Averages by Day</option>
            <option value="weekend">Averages by Weekend</option>
          </select>
        </div>
        
        <div className="table-container">
          {csvData.length > 0 ? (
            <table className="data-table">
              <thead>
                <tr>
                  {Object.keys(csvData[0]).map(key => (
                    <th key={key}>{key.replace('_', ' ').toUpperCase()}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {csvData.map((row, i) => (
                  <tr key={i}>
                    {Object.values(row).map((val, j) => (
                      <td key={j}>{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{color: 'var(--text-muted)'}}>Loading data...</p>
          )}
        </div>
      </div>

    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  );
}

export default App;
