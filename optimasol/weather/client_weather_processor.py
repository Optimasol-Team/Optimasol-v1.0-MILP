from client_reader import read_client_data
from client_result_writer import write_weather_result
from client_api_fetcher import get_client_production
from apis.open_meteo import get_forecast as get_open_meteo
from aggregator import aggregate_forecasts

import os

def process_client_weather(client_folder: str) -> None:
    """
    Process the weather forecast for a single client.

    Steps:
        - Load client configuration from data.json
        - If custom API is enabled, use it
        - Otherwise, use predefined weather sources and aggregate them
        - Save the result in weather.json
    """
    print(f"[Processor] Processing client: {client_folder}")

    data_path = os.path.join(client_folder, "data.json")
    client_data = read_client_data(data_path)

    forecast = {}

    if client_data["forecast_mode"] == "custom":
        print("[Processor] Using custom forecast API...")
        api_config = client_data["custom_api_config"]
        forecast = get_client_production(api_config)
    else:
        print("[Processor] Using default weather sources...")
        lat = client_data["location"]["latitude"]
        lon = client_data["location"]["longitude"]

        sources = []
        meteo = get_open_meteo(lat, lon)
        if meteo["irradiance"]:
            sources.append(meteo)

        # You can add more sources here (e.g. Solcast)

        forecast = aggregate_forecasts(sources)

    # Write result to weather.json
    write_weather_result(client_folder, forecast)
