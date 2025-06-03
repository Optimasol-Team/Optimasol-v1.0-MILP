"""
production.py

A utility module for parsing production data from a JSON file into a fixed-size NumPy array.

- Reads a JSON file where keys are ISO timestamps and values are power in watts.
- Sorts entries by timestamp and produces a NumPy array of length `n`, padding or truncating as needed.

Usage example:
    from logic.data_preparation.production import parse
    from pathlib import Path

    path_to_json = Path("data/production.json")
    n_points = 1440  # e.g., one entry per minute for 24 hours
    production_array = parse(path_to_json, n_points)

"""

from pathlib import Path
import numpy as np

# Import helper to read JSON with clear error messages
from .base import read_json
# Import ensure_length to pad or truncate the list of values
from .utils import ensure_length


def parse(path: Path, n: int) -> np.ndarray:
    """
    Parse a JSON file of production data into a NumPy array of fixed length.

    The input JSON is expected to have the structure:
        {
            "<ISO_timestamp>": <power_in_watts>,
            ...
        }

    This function:
      1. Reads and parses the JSON file.
      2. Sorts the entries by timestamp (ascending).
      3. Extracts the power values in sorted order.
      4. Pads the list with zeros or truncates it to length `n`.
      5. Converts the result to a NumPy array of floats.

    Parameters:
        path (Path): Path object pointing to production JSON file.
        n (int): Desired length of the output array.

    Returns:
        np.ndarray: A one-dimensional array of length `n` containing power values in watts.
                    If the JSON has fewer than `n` entries, zeros are appended. If more, extra
                    entries are dropped.

    Raises:
        FileNotFoundError: If the JSON file does not exist (raised by read_json).
        json.JSONDecodeError: If the JSON is invalid (raised by read_json).
    """
    # Load raw JSON data: keys are timestamps, values are watts
    raw = read_json(path)

    # Sort the (timestamp, value) pairs by timestamp string
    # Then build a list containing only the values, in chronological order
    values = [v for _, v in sorted(raw.items())]

    # Pad with zeros or truncate so that the list has exactly n elements
    fixed_length = ensure_length(values, n)

    # Convert to a NumPy array of floats and return
    return np.array(fixed_length, dtype=float)
