"""
data_meta.py

A utility module for parsing a JSON file containing water heater, electricity contract,
and user metadata. Exposes a single function `parse(path)` that returns three dictionaries:
    - water_heater: volume, power, and comfort schedule
    - contract: type, tariffs, and off-peak hours
    - meta: router ID, user name, and email

Usage example:
    from logic.data_preparation.data_meta import parse
    path_to_json = Path("config/data.json")
    water_heater, contract, meta = parse(path_to_json)

"""

from pathlib import Path
from typing import Dict, Tuple, List

# We import read_json from our local base module, which already handles file-not-found and JSON parsing.
from .base import read_json


def parse(path: Path) -> Tuple[Dict, Dict, Dict]:
    """
    Parse a JSON file and extract three dictionaries: water_heater, contract, and meta.

    The expected JSON structure is:
    {
        "water_heater": {
            "volume_liters": <number>,
            "power_watts": <number>,
            "comfort_schedule": [
                {"time": "<HH:MM>", "target_temperature_celsius": <number>},
                ...
            ]
        },
        "electricity_contract": {
            "contract_type": "<string: BASE or HPHC>",
            "tariffs_eur_per_kwh": {<hour>: <price>, ...},
            "off_peak_hours": [  # optional, present only for HPHC contracts
                {"start": "<HH:MM>", "end": "<HH:MM>"},
                ...
            ]
        },
        "router_id": "<string>",
        "user_info": {  # optional
            "name": "<string>",
            "email": "<string>"
        }
    }

    Parameters:
        path (Path): Path object pointing to the JSON file to parse.

    Returns:
        Tuple[Dict, Dict, Dict]:
            - water_heater: {
                  "volume_l": <number>,
                  "power_w": <number>,
                  "comfort": [  # same as comfort_schedule from JSON
                      {"time": "<HH:MM>", "target_temperature_celsius": <number>},
                      ...
                  ]
              }
            - contract: {
                  "kind": <string: uppercase contract type ("BASE" or "HPHC")>,
                  "tariffs": <dict of hourly tariffs>,
                  "off_peak": List[Tuple[str, str]]  # list of (start, end) pairs as strings
              }
            - meta: {
                  "router_id": <string>,
                  "name": <string or "unknown">,
                  "email": <string or None>
              }

    Raises:
        FileNotFoundError: If the JSON file is not found (handled by read_json).
        json.JSONDecodeError: If the JSON is malformed (handled by read_json).
    """
    # Load the raw JSON data as a Python dict using our helper.
    raw = read_json(path)

    # Extract and rename water heater parameters:
    water_heater = {
        # volume in liters, directly mapped from "volume_liters"
        "volume_l": raw["water_heater"]["volume_liters"],
        # power in watts, mapped from "power_watts"
        "power_w": raw["water_heater"]["power_watts"],
        # comfort schedule is a list of dicts each with "time" and "target_temperature_celsius"
        "comfort": raw["water_heater"]["comfort_schedule"],
    }

    # Extract contract-related data
    c_raw = raw["electricity_contract"]
    contract = {
        # Uppercase the contract_type (e.g., "base" → "BASE")
        "kind": c_raw["contract_type"].upper(),
        # Directly map the tariffs dict (keys: hours or labels, values: price per kWh)
        "tariffs": c_raw["tariffs_eur_per_kwh"],
        # Off-peak hours might be missing for a "BASE" contract, so we use get(..., []).
        # Then build a list of tuples (start_time, end_time) for each off-peak period.
        "off_peak": [
            (hp["start"], hp["end"])
            for hp in c_raw.get("off_peak_hours", [])
        ],
    }

    # Extract metadata about the router and the user (if present)
    meta = {
        # router_id is mandatory in the JSON, so we take it directly
        "router_id": raw["router_id"],
        # user_info may be missing, so we default name to "unknown" if not provided
        "name": raw.get("user_info", {}).get("name", "unknown"),
        # email can be None if not present
        "email": raw.get("user_info", {}).get("email"),
    }

    return water_heater, contract, meta
