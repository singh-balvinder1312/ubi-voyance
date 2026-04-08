import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [backendStatus, setBackendStatus] = useState('Checking...');

  useEffect(() => {
    axios.get('http://localhost:8080/api/health')
        .then(response => {
          setBackendStatus(response.data);
        })
        .catch(error => {
          setBackendStatus('Backend not connected');
        });
  }, []);

  return (
      <div className="App">
        <h1>Ubi-voyance</h1>
        <p>Biophotonics Simulation Pipeline</p>
        <p>Backend status: {backendStatus}</p>
      </div>
  );
}

export default App;