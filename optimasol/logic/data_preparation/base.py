"""
A small utility module for reading JSON files with a clear error message.

- Defines `read_json(path)` which loads and parses a JSON file at the given Path.
- Raises FileNotFoundError with a descriptive message if the file does not exist.

Usage example:
    from json_utils import read_json
    data = read_json(Path("config/settings.json"))

Author: [Your Name]
Date: 2025-06-03
License: MIT (or specify whichever applies)
"""

import json
from pathlib import Path
from typing import Dict, Any


def read_json(path: Path) -> Dict[str, Any]:
    """
    Read and parse a JSON file, raising a clear error if the file is missing.

    Parameters:
        path (Path): Path object pointing to the JSON file to load.

    Returns:
        Dict[str, Any]: The parsed JSON content as a Python dictionary.

    Raises:
        FileNotFoundError: If the file at `path` does not exist.
        json.JSONDecodeError: If the file exists but contains invalid JSON.
    """
    # Check that the file actually exists before trying to open it
    if not path.exists():
        # Raise a FileNotFoundError with a descriptive message
        raise FileNotFoundError(f"JSON file not found: {path}")

    # Open the file with UTF-8 encoding to support non-ASCII characters
    with path.open(encoding="utf-8") as f:
        # Parse the JSON content and return it as a dict
        return json.load(f)
