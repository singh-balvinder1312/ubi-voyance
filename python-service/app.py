from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import numpy as np
from pipeline.haemoglobin import calculate_haemoglobin


app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/python/health', methods=['GET'])
def health():
    return jsonify({"status": "Python service is running"})

@app.route('/python/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return jsonify({
        "status": "File uploaded successfully",
        "filename": file.filename,
        "filepath": filepath
    })

@app.route('/python/haemoglobin', methods=['POST'])
def haemoglobin():
    data = request.get_json()
    I0 = data.get('I0')
    I = data.get('I')
    wavelength = data.get('wavelength', 750)
    path_length = data.get('path_length', 1.0)

    if I0 is None or I is None:
        return jsonify({"error": "I0 and I are required"}), 400

    result = calculate_haemoglobin(I0, I, wavelength, path_length)
    return jsonify(result)

@app.route('/python/absorption', methods=['POST'])
def absorption():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    absorption_data = np.load(filepath)
    vessel_vals = absorption_data[absorption_data > 0]

    return jsonify({
        "mean_absorption": float(vessel_vals.mean()),
        "max_absorption": float(vessel_vals.max()),
        "min_absorption": float(vessel_vals.min()),
        "total_voxels": int(vessel_vals.size)
    })

@app.route('/python/simulate', methods=['POST'])
def simulate():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    wavelength = int(request.form.get('wavelength', 750))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        from pipeline.vtu_to_mcx import read_vtu, voxelize, build_mcx_json
        import json

        data = read_vtu(filepath)
        points = data["points"]
        volume, origin = voxelize(points, resolution=0.25, padding=4)

        total_photons = int(volume.sum())
        absorbed_photons = int(total_photons * 0.25)

        result = calculate_haemoglobin(
            I0=total_photons,
            I=total_photons - absorbed_photons,
            wavelength=wavelength,
            path_length_cm=1.0
        )

        result["total_voxels"] = total_photons
        result["absorbed_voxels"] = absorbed_photons
        result["filename"] = file.filename

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)