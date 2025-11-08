import requests
from typing import Dict, Any

def get_client_production(api_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetches solar production or forecast data from the client's own API.

    The API must return a JSON list of objects containing at least:
        - irradiance values (e.g. GHI in W/m²)
        - time information (ISO 8601 format)

    Parameters:
        api_config (dict): configuration block from client data.json

    Returns:
        dict: {
            "times": [...],          # list of timestamps (strings)
            "irradiance": [...],     # list of floats (W/m²)
            "temperature": []        # always empty
        }
    """
    url = api_config.get("url")
    token = api_config.get("auth_token", "")
    field_map = api_config.get("field_mapping", {})
    field_time = field_map.get("times", "timestamp")
    field_irr = field_map.get("irradiance", "ghi")

    headers = {}
    if token:
        headers["Authorization"] = token

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        times = [entry[field_time] for entry in data]
        irradiance = [entry[field_irr] for entry in data]

        return {
            "times": times,
            "irradiance": irradiance,
            "temperature": []  # Not supported via custom API
        }

    except Exception as e:
        print(f"[Custom API] Error fetching from {url} → {e}")
        return {
            "times": [],
            "irradiance": [],
            "temperature": []
        }
