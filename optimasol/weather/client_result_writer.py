import json
import os
from typing import Dict, Any

def write_weather_result(client_folder: str, forecast: Dict[str, Any]) -> None:
    """
    Writes the forecast result into a weather.json file in the given client folder.

    Parameters:
        client_folder (str): Path to the folder containing the client's data.json
        forecast (Dict): The forecast result to save, with keys:
            - "times": list of timestamps
            - "irradiance": list of W/m² values
            - "temperature": list of °C values
    """
    output_path = os.path.join(client_folder, "weather.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(forecast, f, indent=2, ensure_ascii=False)

    print(f"[Client Writer] Weather result saved to: {output_path}")
