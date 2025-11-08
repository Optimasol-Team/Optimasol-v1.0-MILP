# weather/apis/solcast.py

import requests
from typing import Dict, Any
from datetime import datetime

def get_forecast(site_url: str, api_key: str) -> Dict[str, Any]:
    """
    Get 24h GHI forecast from Solcast Rooftop API (based on a registered site URL).

    Parameters:
        site_url (str): Full Solcast site URL provided by their dashboard
        api_key (str): Your Solcast API key

    Returns:
        dict: {
            "times": [...],        # ISO timestamps
            "irradiance": [...],   # GHI in W/m²
            "temperature": []      # Not provided by Solcast
        }
    """
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(site_url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        forecasts = data.get("estimated_actuals", [])

        now = datetime.utcnow()
        times = []
        irradiance = []

        for f in forecasts:
            time_str = f["period_end"]
            time_dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            if (time_dt - now).total_seconds() < 86400:
                times.append(time_str)
                irradiance.append(f["ghi"])

        return {
            "times": times,
            "irradiance": irradiance,
            "temperature": []  # Solcast doesn't provide temperature
        }

    except Exception as e:
        print(f"[Solcast] Error for site {site_url} → {e}")
        return {"times": [], "irradiance": [], "temperature": []}

if __name__ == "__main__":
    site_url = "https://api.solcast.com.au/rooftop_sites/fa1f-2c98-04fa-7784/estimated_actuals?format=json"
    api_key = "VOTRE_CLÉ_API_SOLCAST"
    forecast = get_forecast(site_url, api_key)

    for t, ghi in zip(forecast["times"], forecast["irradiance"]):
        print(f"{t} → {ghi} W/m²")
