import requests
from datetime import date, timedelta
from typing import Dict, Any

def get_forecast(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Standard forecast getter for [API NAME HERE].

    Parameters:
        latitude (float): Latitude of the client
        longitude (float): Longitude of the client

    Returns:
        dict: {
            "times": [ISO timestamps],
            "irradiance": [W/m² values],
            "temperature": [°C values or empty if not provided]
        }
    """
    # 1. URL de l’API (à changer selon le service)
    url = "https://api.example.com/v1/forecast"

    # 2. Calcul des dates
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # 3. Paramètres de la requête (à adapter)
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": today.isoformat(),
        "end_date": tomorrow.isoformat(),
        "hourly": "shortwave_radiation,temperature_2m",  # ou autre selon l’API
        "timezone": "auto"
    }

    # 4. En-têtes HTTP si besoin (API Key etc.)
    headers = {
        # "Authorization": "Bearer YOUR_API_KEY"   ← à activer si besoin
    }

    try:
        # 5. Envoi de la requête
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 6. Parsing des données (à adapter selon l'API)
        times = data["hourly"]["time"]
        irradiance = data["hourly"]["shortwave_radiation"]
        temperature = data["hourly"].get("temperature_2m", [])  # facultatif

        return {
            "times": times,
            "irradiance": irradiance,
            "temperature": temperature
        }

    except Exception as e:
        print(f"[API TEMPLATE] Error for ({latitude}, {longitude}) → {e}")
        return {
            "times": [],
            "irradiance": [],
            "temperature": []
        }
