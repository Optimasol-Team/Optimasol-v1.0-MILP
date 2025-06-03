"""
weather.py

A utility module for parsing outdoor temperature data from a JSON file.

- Attempts to read a "weather.json" file containing a "temperature_celsius" list.
- If the file is missing or the key does not exist, returns a constant list of 20.0°C.
- Always produces a fixed-length temperature list of size `n` and wraps it in a dict.

Usage example:
    from logic.data_preparation.weather import parse
    from pathlib import Path

    path_to_weather = Path("data/weather.json")
    n_points = 24
    weather_data = parse(path_to_weather, n_points)
    # weather_data == {"temperature": [float, float, ..., float]}

"""

from pathlib import Path
from typing import Dict, List

# Import helper to read JSON file with clear error messages
from .base import read_json
# Import ensure_length to pad or truncate the temperature list
from .utils import ensure_length


def parse(path: Path, n: int) -> Dict[str, List[float]]:
    """
    Extract only outdoor temperature from weather.json into a fixed-size list.

    This function:
      1. Tries to read the JSON at `path`.
      2. Retrieves the "temperature_celsius" key (a list of floats) if present.
      3. Uses `ensure_length` to pad with 20.0°C or truncate so the list has exactly `n` elements.
      4. If the file is not found, creates a list of n entries, each 20.0°C.
      5. Returns a dict: {"temperature": [float, float, ..., float]}.

    Parameters:
        path (Path): Path object pointing to the weather JSON file.
        n (int): Desired length of the output temperature list.

    Returns:
        Dict[str, List[float]]: A dictionary with one key "temperature" and a list of `n` floats.

    Raises:
        None explicitly, since FileNotFoundError is caught internally to provide defaults.
    """
    try:
        # Attempt to read the JSON file
        raw = read_json(path)

        # Get "temperature_celsius" list from JSON; default to empty list if key missing
        temps = raw.get("temperature_celsius", [])

        # Ensure the list has exactly n elements, padding with 20.0°C if too short
        temp = ensure_length(temps, n, filler=20.0)
    except FileNotFoundError:
        # If the file doesn't exist, create a list of n entries all at 20.0°C
        temp = [20.0] * n

    # Return the result wrapped in a dictionary for consistency
    return {"temperature": temp}
