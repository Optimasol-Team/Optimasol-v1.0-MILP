# irradiance_reader.py

"""
Irradiance Reader Module

This module is responsible for reading the solar irradiance values
from a weather.json file and returning them in a dictionary format
where each key is a timestamp (ISO 8601) and the value is the
corresponding irradiance (in W/m²).

"""

import json
from pathlib import Path

def read_irradiance(weather_file_path):
    """
    Read irradiance data from a weather.json file.

    Parameters:
        weather_file_path (str or Path): Path to the weather.json file

    Returns:
        dict: A dictionary mapping timestamps to irradiance values
              Format: { "YYYY-MM-DDTHH:MM": irradiance (float) }
    """
    weather_file_path = Path(weather_file_path)

    if not weather_file_path.exists():
        raise FileNotFoundError(f"weather.json not found at: {weather_file_path}")

    with open(weather_file_path, 'r', encoding='utf-8') as file:
        weather_data = json.load(file)

    times = weather_data.get("times", [])
    irradiances = weather_data.get("irradiance", [])

    if len(times) != len(irradiances):
        raise ValueError("Mismatch between number of timestamps and irradiance values.")

    irradiance_dict = {
        timestamp: irradiance
        for timestamp, irradiance in zip(times, irradiances)
    }

    return irradiance_dict
