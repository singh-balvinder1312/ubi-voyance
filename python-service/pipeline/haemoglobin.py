import numpy as np

HB_EXTINCTION = {
    700: {"HbO2": 290, "Hb": 1794.28},
    750: {"HbO2": 518, "Hb": 1405.24},
    800: {"HbO2": 816, "Hb": 761.72},
    850: {"HbO2": 1058, "Hb": 691.32},
}

def calculate_haemoglobin(I0, I, wavelength, path_length_cm=1.0):
    if I <= 0 or I0 <= 0:
        return {"error": "Invalid photon counts"}

    absorbance = np.log10(I0 / I)

    epsilon = HB_EXTINCTION.get(wavelength)
    if epsilon is None:
        return {"error": f"No extinction data for {wavelength}nm"}

    epsilon_HbO2 = epsilon["HbO2"]
    epsilon_Hb = epsilon["Hb"]
    epsilon_total = epsilon_HbO2 + epsilon_Hb

    concentration_total = absorbance / (epsilon_total * path_length_cm)
    concentration_HbO2 = absorbance / (epsilon_HbO2 * path_length_cm)
    concentration_Hb = absorbance / (epsilon_Hb * path_length_cm)

    SpO2 = (concentration_HbO2 / concentration_total) * 100 if concentration_total > 0 else 0

    return {
        "absorbance": float(absorbance),
        "wavelength_nm": wavelength,
        "concentration_total_M": float(concentration_total),
        "concentration_HbO2_M": float(concentration_HbO2),
        "concentration_Hb_M": float(concentration_Hb),
        "SpO2_percent": float(SpO2),
        "path_length_cm": path_length_cm
    }