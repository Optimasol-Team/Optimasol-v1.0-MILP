import itertools
from .model import ParameterClient
from .constraints import filter_combinations
from .cost import compute_cost
from .temperature import simulate_temperature
import numpy as np


def run_optimizer(hyper: dict, production: np.ndarray, tariffs: dict) -> dict:
    """
    Main entry point for running the optimization process.

    Given the preprocessed client data (hyperparameters, production, and tariff info),
    this function finds the optimal ON/OFF heating schedule minimizing the net cost.

    Parameters:
        hyper (dict): Contains client-specific thermal and economic parameters.
        production (np.ndarray): Time-series of solar production in watts.
        tariffs (dict): Dictionary defining off-peak and peak tariffs.

    Returns:
        dict: {
            "best_combination": List[int],
            "temperature_curve": List[float],
            "cost": float
        }
    """
    client = ParameterClient(
        Tamb=20,  # can be adjusted or extracted from weather
        P=hyper["P"],
        volume=hyper["volume"],
        k=0.5,  # thermal loss coefficient (fixed or externalized later)
        max_temp=80,
        schedule=hyper["liste_point"],
        slope_cooling=hyper["pente_negative"],
        shower_times=hyper["horaire_douche"],
        shower_drop=hyper["douche_delta"],
        n=hyper["n"],
        t0=hyper["t0"],
        pv_price=hyper["prix_vente_pv"]
    )

    all_combinations = list(itertools.product([0, 1], repeat=client.n - 1))
    valid_combinations = filter_combinations(all_combinations, client)

    if not valid_combinations:
        return {
            "best_combination": [],
            "temperature_curve": [],
            "cost": float("inf")
        }

    best = min(valid_combinations, key=lambda seq: compute_cost(seq, client, production, tariffs))
    return {
        "best_combination": best,
        "temperature_curve": simulate_temperature(best, client),
        "cost": compute_cost(best, client, production, tariffs)
    }
