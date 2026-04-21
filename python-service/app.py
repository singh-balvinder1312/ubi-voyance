from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import numpy as np
import math
from pipeline.haemoglobin import calculate_haemoglobin, calculate_wbc

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/python/health', methods=['GET'])
def health():
    return jsonify({"status": "Python service is running"})

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

@app.route('/python/simulate', methods=['POST'])
def simulate():
    if 'vtu_file' not in request.files:
        return jsonify({"error": "No VTU file provided"}), 400

    if 'jnii_file' not in request.files:
        return jsonify({"error": "No JNII file provided"}), 400

    vtu_file = request.files['vtu_file']
    jnii_file = request.files['jnii_file']
    wavelength = int(request.form.get('wavelength', 750))

    vtu_path = os.path.join(UPLOAD_FOLDER, vtu_file.filename)
    jnii_path = os.path.join(UPLOAD_FOLDER, jnii_file.filename)

    vtu_file.save(vtu_path)
    jnii_file.save(jnii_path)

    try:
        from pipeline.vtu_to_mcx import read_vtu, voxelize
        from pipeline.extract_absorption import load_jnii

        data = read_vtu(vtu_path)
        points = data["points"]
        volume, origin = voxelize(points, resolution=0.25, padding=4)

        absorption, jnii_dims = load_jnii(jnii_path)

        vessel_vals = absorption[absorption > 0]

        if len(vessel_vals) == 0 or np.isnan(vessel_vals).all():
            return jsonify({"error": "MCX output file contains no valid absorption data. Please check your JNII file."}), 400

        vessel_vals = vessel_vals[~np.isnan(vessel_vals)]

        if len(vessel_vals) == 0:
            return jsonify({"error": "No valid absorption values found after filtering NaN values."}), 400

        mean_abs = float(vessel_vals.mean())

        if np.isnan(mean_abs):
            return jsonify({"error": "Mean absorption is NaN. JNII file may be corrupted."}), 400

        total_photons = int(volume.sum())
        I0 = total_photons

        log_mean = math.log10(mean_abs + 1)
        log_max = math.log10(float(vessel_vals.max()) + 1)

        if log_max > 0:
            absorbed_fraction = min(log_mean / (log_max * 2), 0.95)
        else:
            absorbed_fraction = 0.5

        I = max(int(I0 * (1 - absorbed_fraction)), 1)

        absorbed_fraction_730 = absorbed_fraction * 0.88
        absorbed_fraction_850 = absorbed_fraction * 0.72

        I0_730 = total_photons
        I_730 = max(int(I0_730 * (1 - absorbed_fraction_730)), 1)
        I0_850 = total_photons
        I_850 = max(int(I0_850 * (1 - absorbed_fraction_850)), 1)

        hb_result = calculate_haemoglobin(
            I0=I0,
            I=I,
            wavelength=wavelength,
            path_length_cm=1.0
        )

        wbc_result = calculate_wbc(
            I0_730=I0_730,
            I_730=I_730,
            I0_850=I0_850,
            I_850=I_850,
            path_length_cm=1.0
        )

        result = {
            **hb_result,
            **wbc_result,
            "total_voxels": total_photons,
            "absorbed_voxels": int(I0 - I),
            "mean_absorption": float(mean_abs),
            "max_absorption": float(vessel_vals.max()),
            "filename": vtu_file.filename,
            "mcx_file": jnii_file.filename
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)