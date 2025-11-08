# apis/open_meteo.py

import requests
from datetime import date, timedelta
from typing import Dict, Any

def get_forecast(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get 24h solar irradiance and temperature forecast from Open-Meteo.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    today = date.today()
    tomorrow = today + timedelta(days=1)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": today.isoformat(),
        "end_date": tomorrow.isoformat(),
        "hourly": "shortwave_radiation,temperature_2m",
        "timezone": "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "times": data["hourly"]["time"],
            "irradiance": data["hourly"]["shortwave_radiation"],
            "temperature": data["hourly"]["temperature_2m"]
        }

    except Exception as e:
        print(f"[Open-Meteo] Error → {e}")
        return {"times": [], "irradiance": [], "temperature": []}
