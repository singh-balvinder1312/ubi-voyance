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

    total_Hb = concentration_HbO2 + concentration_Hb
    SpO2 = (concentration_HbO2 / total_Hb) * 100 if total_Hb > 0 else 0

    return {
        "absorbance": float(absorbance),
        "wavelength_nm": wavelength,
        "concentration_total_M": float(concentration_total),
        "concentration_HbO2_M": float(concentration_HbO2),
        "concentration_Hb_M": float(concentration_Hb),
        "SpO2_percent": float(SpO2),
        "path_length_cm": path_length_cm
    }

WBC_EXTINCTION = {
    730: {"HbO2": 390, "Hb": 1102.2},
    850: {"HbO2": 1058, "Hb": 691.32},
}

def calculate_wbc(I0_730, I_730, I0_850, I_850, path_length_cm=1.0):
    if I_730 <= 0 or I_850 <= 0:
        return {"error": "Invalid photon counts"}

    absorbance_730 = np.log10(I0_730 / I_730)
    absorbance_850 = np.log10(I0_850 / I_850)

    epsilon_730 = WBC_EXTINCTION[730]["HbO2"] + WBC_EXTINCTION[730]["Hb"]
    epsilon_850 = WBC_EXTINCTION[850]["HbO2"] + WBC_EXTINCTION[850]["Hb"]

    concentration_730 = absorbance_730 / (epsilon_730 * path_length_cm)
    concentration_850 = absorbance_850 / (epsilon_850 * path_length_cm)

    if concentration_850 > 0:
        wbc_index = concentration_730 / concentration_850
    else:
        wbc_index = 0

    if wbc_index < 0.8:
        wbc_level = "low"
    elif wbc_index <= 1.2:
        wbc_level = "normal"
    else:
        wbc_level = "high"

    return {
        "wbc_index": float(wbc_index),
        "wbc_level": wbc_level,
        "absorbance_730nm": float(absorbance_730),
        "absorbance_850nm": float(absorbance_850),
        "concentration_730nm_M": float(concentration_730),
        "concentration_850nm_M": float(concentration_850)
    }