# client_config_reader.py

"""
Client Configuration Reader Module

This module reads relevant photovoltaic and location parameters
from a client's data.json file, used for production simulation.

"""

import json
from pathlib import Path

def read_client_config(data_file_path):
    """
    Read client photovoltaic and location configuration.

    Parameters:
        data_file_path (str or Path): Path to the client's data.json file

    Returns:
        dict: Dictionary containing 'pv_system' and 'location' configuration
    """
    data_file_path = Path(data_file_path)

    if not data_file_path.exists():
        raise FileNotFoundError(f"data.json not found at: {data_file_path}")

    with open(data_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    try:
        return {
            "pv_system": {
                "surface_m2": data["pv_system"]["surface_m2"],
                "panel_efficiency": data["pv_system"]["panel_efficiency"],
                "system_efficiency": data["pv_system"]["system_efficiency"]
            },
            "location": {
                "latitude": data["location"]["latitude"],
                "longitude": data["location"]["longitude"],
                "tilt": data["location"]["tilt"],
                "azimuth": data["location"]["azimuth"]
            }
        }
    except KeyError as e:
        raise KeyError(f"Missing expected field in data.json: {e}")
