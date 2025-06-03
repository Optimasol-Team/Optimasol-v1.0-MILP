"""
hhmm_utils.py

A small utility module for working with time strings and list sizes.

- Provides a function to convert an "HH:MM" time string into a decimal hour (e.g., "06:30" → 6.5).
- Provides a function to ensure a list of floats has exactly N elements by truncating or padding with a filler.

Usage example:
    from hhmm_utils import hhmm_to_float, ensure_length

    # Convert "06:30" to 6.5
    decimal_time = hhmm_to_float("06:30")

    # Ensure a list has exactly 5 elements, padding with 0.0 if needed
    data = [1.2, 3.4]
    fixed_length = ensure_length(data, 5, filler=0.0)
"""

from typing import List


def hhmm_to_float(hhmm: str) -> float:
    """
    Convert a time string "HH:MM" to a decimal hour.

    This function takes a string representing hours and minutes separated by a colon,
    parses it into integers, and returns the equivalent time in decimal hours.

    Parameters:
        hhmm (str): Time in "HH:MM" format (e.g., "06:30", "14:45").

    Returns:
        float: Equivalent time in hours as a float (e.g., "06:30" → 6.5, "14:45" → 14.75).

    Raises:
        ValueError: If the input string is not in the correct "HH:MM" format or
                    if hours/minutes cannot be converted to integers.
    """
    # Split the string on ":" and convert both parts to integers
    h, m = map(int, hhmm.split(":"))

    # Compute decimal hours: hours + (minutes / 60)
    return h + m / 60


def ensure_length(seq: List[float], n: int, filler: float = 0.0) -> List[float]:
    """
    Adjust a list of floats to have exactly n elements by truncating or padding.

    If the input list has length >= n, it will be truncated to the first n elements.
    If the input list has length < n, it will be extended with copies of 'filler'
    until it reaches length n.

    Parameters:
        seq (List[float]): Original list of floats.
        n (int): Desired length of the resulting list.
        filler (float, optional): Value to append if 'seq' is shorter than 'n'. Defaults to 0.0.

    Returns:
        List[float]: A new list of length exactly n.

    Examples:
        >>> ensure_length([1.0, 2.0, 3.0], 5)
        [1.0, 2.0, 3.0, 0.0, 0.0]

        >>> ensure_length([5.5, 6.5, 7.5, 8.5], 2)
        [5.5, 6.5]
    """
    current_len = len(seq)

    # If already at or above the desired length, truncate
    if current_len >= n:
        return seq[:n]

    # Otherwise, pad with 'filler' up to length n
    num_missing = n - current_len
    return seq + [filler] * num_missing
