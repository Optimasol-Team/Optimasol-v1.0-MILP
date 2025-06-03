"""
factory.py

A factory module that centralizes data loading and preprocessing for a client.

- Reads and parses:
    • data.json        → water heater specs, electricity contract, user metadata
    • production.json  → time-series of power production in watts
    • weather.json     → outdoor temperature data (currently read but not used)
- Builds:
    • `hyper`: parameters for the optimizer (power, volume, heating slopes, comfort points, pricing, etc.)
    • `tarifs`: structured tariffs information (off-peak vs. peak prices)
    • `meta`: user metadata (router ID, name, email)

Public API:
    load_client(folder: Path, n: int = 24) -> Dict[str, Any]

Usage example:
    from logic.data_preparation.factory import load_client
    from pathlib import Path

    client_folder = Path("path/to/client_folder")
    n_points = 24
    client_data = load_client(client_folder, n_points)

    # client_data["hyper"], client_data["production"], client_data["tarifs"], client_data["meta"]
"""

from pathlib import Path
import numpy as np
from typing import Dict, Any

# Import parsing functions from sibling modules
from . import data_meta, production, weather
from .utils import hhmm_to_float


# ───────────────────────── helpers internes ─────────────────────────

def _build_hyper(
    w_heater: Dict[str, Any],
    contract: Dict[str, Any],
    n: int,
    t0: float
) -> Dict[str, Any]:
    """
    Build optimizer hyperparameters based on water heater specs and electricity contract.

    Parameters:
        w_heater (Dict[str, Any]):
            Dictionary containing water heater info:
                {
                    "volume_l": <float>,
                    "power_w": <float>,
                    "comfort": [
                        {"time": "<HH:MM>", "target_temperature_celsius": <float>},
                        ...
                    ]
                }
        contract (Dict[str, Any]):
            Dictionary containing contract info:
                {
                    "kind": <"BASE" or "HPHC">,
                    "tariffs": { <tariff_label>: <price_per_kWh>, ... },
                    "off_peak": [(<start_HH:MM>, <end_HH:MM>), ...]
                }
        n (int): Desired length for the production/time-series arrays.
        t0 (float): Initial temperature reference for the optimizer.

    Returns:
        Dict[str, Any]: A dictionary of hyperparameters for the optimizer:
            {
                "P": <power_w>,
                "volume": <volume_l>,
                "pente_negative": -0.2,          # fixed negative slope
                "pente_positive": <calculated>,
                "liste_point": { <hour_float>: <target_temp>, ... },
                "horaire_douche": [ <hour_float>, ... ],
                "douche_delta": 7.0,             # temperature delta for shower
                "n": <n>,
                "t0": <t0>,
                "prix_vente_pv": <pv_price>
            }
    """
    # Calculate positive heating slope: power (W) → °C per hour using specific heat of water (4.18 kJ/kg·°C)
    # volume_l is liters → kg, so division by (4.18 * volume_l) gives °C per second; then adjust units.
    pente_pos = w_heater["power_w"] / 4.18 / w_heater["volume_l"]

    # Build a dict mapping each comfort time (in decimal hours) to its target temperature
    points = {
        hhmm_to_float(c["time"]): c["target_temperature_celsius"]
        for c in w_heater["comfort"]
    }

    # Extract a sorted list of decimal-hour time points for showers
    horaires = [hhmm_to_float(c["time"]) for c in w_heater["comfort"]]

    # Determine base electricity price:
    #   If contract has a "base" tariff key, use it; otherwise fall back to "hp" (high-price) or default 0.20 €/kWh
    base_price = contract["tariffs"].get("base", contract["tariffs"].get("hp", 0.20))

    # Calculate a photovoltaic (PV) sale price as 25% of base price (rounded to 3 decimal places)
    pv_price = round(base_price * 0.25, 3)

    return {
        "P": w_heater["power_w"],             # heating power in Watts
        "volume": w_heater["volume_l"],       # volume in liters
        "pente_negative": -0.2,               # fixed negative slope (°C/hour)
        "pente_positive": pente_pos,          # computed positive slope (°C/hour)
        "liste_point": points,                # comfort schedule as {hour_float: target_temperature}
        "horaire_douche": horaires,           # times (in hours) for shower comfort targets
        "douche_delta": 7.0,                  # temperature drop during shower (°C)
        "n": n,                               # number of time slots
        "t0": t0,                             # initial temperature
        "prix_vente_pv": pv_price,            # PV selling price (€/kWh)
    }


def _build_tarifs(contract: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Convert raw contract data into structured tariffs for off-peak and peak periods.

    If the contract kind is "HPHC" (Heures Pleines / Heures Creuses) and off-peak hours exist,
    this returns:
        {
            "creuse": {"debut": <start_time>, "fin": <end_time>, "prix": <hc_price>},
            "pleine": {"prix": <hp_price>}
        }
    Otherwise (BASE tariff), it returns:
        {
            "creuse": {"debut": "00:00", "fin": "00:00", "prix": 0.0},
            "pleine": {"prix": <base_price>}
        }

    Parameters:
        contract (Dict[str, Any]):
            {
                "kind": <"BASE" or "HPHC">,
                "tariffs": {
                    "base": <price>,
                    "hp": <price>,
                    "hc": <price>,
                    ...
                },
                "off_peak": [(<start_HH:MM>, <end_HH:MM>), ...]
            }

    Returns:
        Dict[str, Dict[str, Any]]: Structured tariffs dictionary.
    """
    if contract["kind"] == "HPHC" and contract["off_peak"]:
        # Take the first off-peak period (assumes only one continuous block)
        debut, fin = contract["off_peak"][0]
        return {
            "creuse": {
                "debut": debut,
                "fin": fin,
                "prix": contract["tariffs"]["hc"]
            },
            "pleine": {
                "prix": contract["tariffs"]["hp"]
            },
        }

    # Fallback for BASE tariff or missing off_peak: no real off-peak hours
    return {
        "creuse": {
            "debut": "00:00",
            "fin": "00:00",
            "prix": 0.0
        },
        "pleine": {
            "prix": contract["tariffs"]["base"]
        },
    }


# ─────────────────────── API publique ───────────────────────

def load_client(folder: Path, n: int = 12) -> Dict[str, Any]:
    """
    Main entry point for client data preparation.

    Reads the necessary JSON files from the given folder, processes them,
    and returns a dictionary containing:
        {
            "hyper":      <optimizer parameters dict>,
            "production": <np.ndarray of shape (n,) with production in Watts>,
            "tarifs":     <structured tariffs dict>,
            "meta":       <user metadata dict>
        }

    Parameters:
        folder (Path): Path to the client folder containing:
            - data.json
            - production.json
            - weather.json (optional)
        n (int, optional): Desired length for time-series arrays (default: 24).

    Returns:
        Dict[str, Any]:
            {
                "hyper":      { ... },
                "production": np.ndarray(shape=(n,), dtype=float),
                "tarifs":     { ... },
                "meta":       { ... }
            }
    """
    # Parse data.json → returns (water_heater, contract, meta) as dictionaries
    w_heater, contract, meta = data_meta.parse(folder / "data.json")

    # Parse production.json → returns a NumPy array of length n (watts)
    prod_np = production.parse(folder / "production.json", n)

    # Parse weather.json (currently not used downstream, but we still read it to enforce structure)
    _ = weather.parse(folder / "weather.json", n)

    # Build hyperparameters for the optimizer.
    # We choose t0 as (first target comfort temperature – 10) by convention.
    initial_t0 = w_heater["comfort"][0]["target_temperature_celsius"] - 10
    hyper = _build_hyper(w_heater, contract, n, t0=initial_t0)

    # Build structured tariffs dict from raw contract
    tarifs = _build_tarifs(contract)

    # Return everything in a single dictionary
    return {
        "hyper": hyper,
        "production": prod_np,
        "tarifs": tarifs,
        "meta": meta,
    }



if __name__ == "__main__":
    import sys, pprint

    # Allow running as: python -m logic.data_preparation.factory <path_to_client_folder>
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    prepared = load_client(folder)

    pprint.pp(prepared["hyper"])
    print("production shape:", prepared["production"].shape)
    pprint.pp(prepared["tarifs"])
