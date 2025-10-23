# apis/openweather_temp.py

import requests
from typing import Dict, Any

def get_forecast(latitude: float, longitude: float, api_key: str) -> Dict[str, Any]:
    """
    Get current temperature from OpenWeather.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "times": [data["dt"]],
            "irradiance": [],
            "temperature": [data["main"]["temp"]]
        }

    except Exception as e:
        print(f"[OpenWeather] Error → {e}")
        return {"times": [], "irradiance": [], "temperature": []}
