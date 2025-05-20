# production_writer.py

"""
Production Writer Module

This module writes the calculated solar power production
dictionary into a production.json file in the client's directory.
"""

import json
from pathlib import Path

def write_production(production_dict, output_file_path):
    """
    Write production data to production.json.

    Parameters:
        production_dict (dict): {timestamp (str): power (float)}
        output_file_path (str or Path): Path to the output production.json file

    Returns:
        None
    """
    output_file_path = Path(output_file_path)

    # Ensure parent directory exists
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(production_dict, f, indent=2, ensure_ascii=False)
