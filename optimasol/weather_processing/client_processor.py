# client_processor.py

"""
Client Processor Module

This module coordinates all steps for a single client:
- read irradiance data
- read PV system and location config
- compute solar power production
- write production.json

"""

from pathlib import Path
from weather_processing.irradiance_reader import read_irradiance
from weather_processing.client_config_reader import read_client_config
from weather_processing.irradiance_to_production import compute_production
from weather_processing.production_writer import write_production


def process_client(client_folder_path):
    """
    Process a single client: read data, compute production, write output.

    Parameters:
        client_folder_path (str or Path): Path to the client's folder

    Returns:
        None
    """
    client_folder_path = Path(client_folder_path)
    weather_file = client_folder_path / "weather.json"
    data_file = client_folder_path / "data.json"
    output_file = client_folder_path / "production.json"

    # Step 1: Read irradiance
    irradiance = read_irradiance(weather_file)

    # Step 2: Read configuration
    config = read_client_config(data_file)

    # Step 3: Compute power production
    production = compute_production(irradiance, config)

    # Step 4: Write output
    write_production(production, output_file)
