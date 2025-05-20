import json
from typing import Dict, Any


def read_client_data(path: str) -> Dict[str, Any]:
    """
    Reads and parses the client's data.json file.

    Returns a structured dictionary containing:
        - router_id
        - location (latitude, longitude, etc.)
        - pv_system (surface, efficiency, etc.)
        - forecast_mode: "custom" or "meteo"
        - custom_api_config: dict or None
        - raw: the full original JSON data

    If any required field is missing, raises an exception.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate required top-level keys
    if "location" not in data or "latitude" not in data["location"]:
        raise ValueError("Missing 'location.latitude' in client data")

    if "pv_system" not in data or "surface_m2" not in data["pv_system"]:
        raise ValueError("Missing 'pv_system.surface_m2' in client data")

    # Check if custom forecast API is enabled
    custom_api_block = data.get("custom_forecast_source", {})
    forecast_mode = "custom" if custom_api_block.get("enabled") else "meteo"

    return {
        "router_id": data.get("router_id", "UNKNOWN"),
        "location": data.get("location", {}),
        "pv_system": data.get("pv_system", {}),
        "forecast_mode": forecast_mode,
        "custom_api_config": custom_api_block if forecast_mode == "custom" else None,
        "raw": data  # keep full data for optional access/logs
    }
