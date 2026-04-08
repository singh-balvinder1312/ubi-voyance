import React, { useState, useRef } from 'react';
import axios from 'axios';
import './Dashboard.css';

function Dashboard() {
    const [file, setFile] = useState(null);
    const [wavelength, setWavelength] = useState(750);
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setStatus('');
            setError('');
            setResults(null);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const dropped = e.dataTransfer.files[0];
        if (dropped) {
            setFile(dropped);
            setStatus('');
            setError('');
            setResults(null);
        }
    };

    const handleSubmit = async () => {
        if (!file) {
            setError('Please select a VTU file first');
            return;
        }
        setLoading(true);
        setStatus('Running simulation...');
        setError('');
        setResults(null);

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
        } catch (err) {
            setError(err.response?.data?.error || err.message || 'Simulation failed');
            setStatus('');
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

                <div
                    className="upload-box"
                    onDrop={handleDrop}
                    onDragOver={(e) => e.preventDefault()}
                    onClick={() => fileInputRef.current.click()}
                >
                    <input
                        type="file"
                        accept=".vtu,.vtk,.stl"
                        onChange={handleFileChange}
                        ref={fileInputRef}
                    />
                    <label className="upload-label">
                        <span className="upload-icon">⬆</span>
                        {file ? (
                            <span className="file-selected">{file.name}</span>
                        ) : (
                            <>
                                <span>Drag and drop or <span className="highlight">browse</span></span>
                                <span style={{fontSize: '0.8rem', color: '#4b5563'}}>Supports .vtu .vtk .stl</span>
                            </>
                        )}
                    </label>
                </div>

                <div className="controls-row">
                    <div className="wavelength-selector">
                        <label>Wavelength</label>
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
                        {loading && <span className="spinner" />}
                        {loading ? 'Running...' : 'Run Simulation'}
                    </button>
                </div>

                {status && (
                    <p className={`status ${status === 'Simulation complete' ? 'success' : ''}`}>
                        {status}
                    </p>
                )}

                {error && (
                    <div className="error-box">
                        {error}
                    </div>
                )}
            </div>

            {results && (
                <div className="results-section">
                    <h2>Results</h2>

                    <p className="section-label">Haemoglobin</p>
                    <div className="results-grid">
                        <div className="result-card">
                            <h3>Total Hb</h3>
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

                    <p className="section-label">White Blood Cells</p>
                    <div className="results-grid">
                        <div className="result-card">
                            <h3>WBC Index</h3>
                            <p>{results.wbc_index ? results.wbc_index.toFixed(3) : 'N/A'}</p>
                        </div>
                        <div className="result-card">
                            <h3>WBC Level</h3>
                            <p className={results.wbc_level}>
                                {results.wbc_level ? results.wbc_level.toUpperCase() : 'N/A'}
                            </p>
                        </div>
                        <div className="result-card">
                            <h3>Absorbance 730nm</h3>
                            <p>{results.absorbance_730nm ? results.absorbance_730nm.toFixed(4) : 'N/A'}</p>
                        </div>
                        <div className="result-card">
                            <h3>Absorbance 850nm</h3>
                            <p>{results.absorbance_850nm ? results.absorbance_850nm.toFixed(4) : 'N/A'}</p>
                        </div>
                    </div>

                    <p className="section-label">Simulation Info</p>
                    <div className="results-grid">
                        <div className="result-card">
                            <h3>Total Voxels</h3>
                            <p>{results.total_voxels?.toLocaleString()}</p>
                        </div>
                        <div className="result-card">
                            <h3>Absorbed Voxels</h3>
                            <p>{results.absorbed_voxels?.toLocaleString()}</p>
                        </div>
                        <div className="result-card">
                            <h3>File</h3>
                            <p style={{fontSize: '0.9rem'}}>{results.filename}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;