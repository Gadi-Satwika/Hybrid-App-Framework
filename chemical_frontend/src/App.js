import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import './App.css';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  
  const [file, setFile] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);

  // This creates the auth object based on what the user typed in the login form
  const authHeader = {
    auth: { username: user, password: pass }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // We "test" the credentials by trying to fetch history
      const res = await axios.get('https://hybrid-app-framework.onrender.com/api/upload/', authHeader);
      setHistory(res.data);
      setIsLoggedIn(true);
    } catch (err) {
      alert("Unauthorized: Invalid Username or Password");
    }
  };

  const handleUpload = async () => {
    if (!file) return alert("Select a CSV first");
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await axios.post('https://hybrid-app-framework.onrender.com/api/upload/', formData, authHeader);
      setAnalytics(res.data);
      fetchHistory();
    } catch (err) { alert("Upload failed. Check file format."); }
  };

  const fetchHistory = async () => {
    const res = await axios.get('https://hybrid-app-framework.onrender.com/api/upload/', authHeader);
    setHistory(res.data);
  };

  const downloadPDF = async (id) => {
    const res = await axios.get(`https://hybrid-app-framework.onrender.com/api/report/${id}/`, { ...authHeader, responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Report_${id}.pdf`);
    document.body.appendChild(link);
    link.click();
  };

  const deleteRecord = async (id) => {
    if (!window.confirm("Delete this record?")) return;
    await axios.delete(`https://hybrid-app-framework.onrender.com/api/delete/${id}/`, authHeader);
    fetchHistory();
    setAnalytics(null);
  };

  const chartData = analytics ? {
    labels: Object.keys(analytics.type_distribution),
    datasets: [{ label: 'Units', data: Object.values(analytics.type_distribution), backgroundColor: '#2563eb' }]
  } : null;

  // LOGIN SCREEN
  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <div className="login-card">
          <div className="login-header">
            <h2>Industrial Portal</h2>
            <p>Authorized Personnel Only</p>
          </div>
          <form onSubmit={handleLogin}>
            <input 
              type="text" 
              placeholder="Username" 
              className="login-input" 
              onChange={e => setUser(e.target.value)} 
              required
            />
            <input 
              type="password" 
              placeholder="Password" 
              className="login-input" 
              onChange={e => setPass(e.target.value)} 
              required
            />
            <button 
              type="submit" 
              style={{ width: '100%', marginTop: '15px', padding: '12px' }}
            >
              Secure Login
            </button>
          </form>
          <div style={{ marginTop: '20px', fontSize: '12px', color: '#94a3b8' }}>
            © 2026 Chemical Equipment Analytics v1.0
          </div>
        </div>
      </div>
    );
  }

  // MAIN DASHBOARD (Only shown if isLoggedIn is true)
  return (
    <div className="dashboard-container">
      <header className="card">
        <h2 style={{ color: '#1e3a8a' }}>Chemical Equipment Analytics</h2>
        <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
          <input type="file" onChange={e => setFile(e.target.files[0])} />
          <button onClick={handleUpload}>Upload & Analyze</button>
        </div>
      </header>

      {analytics && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <h3>Analysis Result</h3>
            <span style={{ color: analytics.health_score > 80 ? 'green' : 'red' }}>Health: {analytics.health_score}%</span>
          </div>
          <div className="stats-grid">
            <div className="stat-card"><h4>Avg Temp</h4><p>{analytics.avg_temp?.toFixed(1)}°C</p></div>
            <div className="stat-card"><h4>Avg Press</h4><p>{analytics.avg_pressure?.toFixed(1)} bar</p></div>
          </div>
          <div style={{ height: '300px', marginTop: '20px' }}><Bar data={chartData} options={{ maintainAspectRatio: false }} /></div>
        </div>
      )}

      <div className="card">
        <h3>Server History</h3>
        <table>
          <thead><tr><th>File</th><th>Date</th><th>Action</th></tr></thead>
          <tbody>
            {history.map(item => (
              <tr key={item.id}>
                <td>{item.file_name}</td>
                <td>{item.date}</td>
                <td>
                  <button onClick={() => setAnalytics(item.summary)} style={{ marginRight: '5px' }}>View</button>
                  <button onClick={() => downloadPDF(item.id)} style={{ background: '#f59e0b', marginRight: '5px' }}>PDF</button>
                  <button onClick={() => deleteRecord(item.id)} style={{ background: '#ef4444' }}>Del</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;