from typing import List, Dict, Any

def aggregate_forecasts(forecast_dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregates a list of forecast dictionaries by averaging irradiance and temperature per hour.

    Parameters:
        forecast_dicts (List[Dict[str, Any]]): A list of standardized forecast outputs,
        each containing keys: "times", "irradiance", and optionally "temperature".

    Returns:
        Dict[str, Any]: A single dictionary containing:
            - "times": hourly timestamps (ISO format),
            - "irradiance": averaged irradiance values per hour,
            - "temperature": averaged temperature values per hour (or empty list if unavailable).
    """
    # Filter out empty or invalid forecast sources
    valid = [f for f in forecast_dicts if f["irradiance"] and f["times"]]

    # If no valid forecasts are available, return an empty result
    if not valid:
        print("[Aggregator] No valid forecast sources.")
        return {"times": [], "irradiance": [], "temperature": []}

    # Assume that all forecasts use the same hourly timestamps
    times = valid[0]["times"]

    # Collect irradiance lists from each valid source
    irr_lists = [f["irradiance"] for f in valid]
    avg_irr = average_lists(irr_lists)

    # Collect temperature lists if present
    temp_lists = [f["temperature"] for f in valid if f["temperature"]]
    avg_temp = average_lists(temp_lists) if temp_lists else []

    return {
        "times": times,
        "irradiance": avg_irr,
        "temperature": avg_temp
    }

def average_lists(list_of_lists: List[List[float]]) -> List[float]:
    """
    Computes the element-wise average of multiple aligned lists.

    Example:
        [[1, 2, 3], [4, 5, 6]] → [2.5, 3.5, 4.5]

    Parameters:
        list_of_lists (List[List[float]]): A list of lists containing numerical values.

    Returns:
        List[float]: A list with the average value at each position.
    """
    return [
        sum(values) / len(values)
        for values in zip(*list_of_lists)
    ]
