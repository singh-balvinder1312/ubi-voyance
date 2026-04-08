import React, { useState } from 'react';
import axios from 'axios';
import './Dashboard.css';

function Dashboard() {
    const [file, setFile] = useState(null);
    const [wavelength, setWavelength] = useState(750);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setStatus('File selected: ' + e.target.files[0].name);
    };

    const handleSubmit = async () => {
        if (!file) {
            setStatus('Please select a file first');
            return;
        }
        setLoading(true);
        setStatus('Running simulation...');

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('wavelength', wavelength);

            const response = await axios.post(
                'http://localhost:8080/api/pipeline/simulate',
                formData
            );
            setResults(response.data);
            setStatus('Simulation complete');
        } catch (error) {
            setStatus('Error: ' + error.message);
        }
        setLoading(false);
    };

    return (
        <div className="dashboard">
            <div className="header">
                <h1>Ubi-voyance</h1>
                <p>Biophotonics Simulation Pipeline</p>
            </div>

            <div className="upload-section">
                <h2>Upload VTU File</h2>
                <div className="upload-box">
                    <input
                        type="file"
                        accept=".vtu,.vtk,.stl"
                        onChange={handleFileChange}
                    />
                </div>

                <div className="wavelength-selector">
                    <label>Wavelength (nm):</label>
                    <select
                        value={wavelength}
                        onChange={(e) => setWavelength(Number(e.target.value))}
                    >
                        <option value={700}>700 nm</option>
                        <option value={750}>750 nm</option>
                        <option value={800}>800 nm</option>
                        <option value={850}>850 nm</option>
                    </select>
                </div>

                <button
                    className="run-button"
                    onClick={handleSubmit}
                    disabled={loading}
                >
                    {loading ? 'Running...' : 'Run Simulation'}
                </button>

                <p className="status">{status}</p>
            </div>

            {results && (
                <div className="results-section">
                    <h2>Results</h2>
                    <div className="results-grid">
                        <div className="result-card">
                            <h3>Haemoglobin</h3>
                            <p>{(results.concentration_total_M * 1000).toFixed(4)} mM</p>
                        </div>
                        <div className="result-card">
                            <h3>HbO2</h3>
                            <p>{(results.concentration_HbO2_M * 1000).toFixed(4)} mM</p>
                        </div>
                        <div className="result-card">
                            <h3>Deoxy-Hb</h3>
                            <p>{(results.concentration_Hb_M * 1000).toFixed(4)} mM</p>
                        </div>
                        <div className="result-card">
                            <h3>SpO2</h3>
                            <p>{results.SpO2_percent.toFixed(1)} %</p>
                        </div>
                        <div className="result-card">
                            <h3>Absorbance</h3>
                            <p>{results.absorbance.toFixed(4)}</p>
                        </div>
                        <div className="result-card">
                            <h3>Wavelength</h3>
                            <p>{results.wavelength_nm} nm</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;