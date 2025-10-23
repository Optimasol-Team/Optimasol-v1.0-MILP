"""
config_loader.py

Loads MQTT broker configuration from a text file and returns it as a dictionary.
Ensures required fields are present and values are correctly formatted.
"""

import os
from typing import Dict

REQUIRED_KEYS = {"host", "port"}

def load_mqtt_config(path: str = "config/mqtt_config_receive.txt") -> Dict[str, str]:
    """
    Reads and parses the MQTT configuration file.

    Args:
        path (str): Path to the configuration file.

    Returns:
        Dict[str, str]: Dictionary containing MQTT configuration.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If a required key is missing or malformed.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, "..", path)

    config = {}

    try:
        with open(full_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"MQTT config file not found: {full_path}")
    except Exception as e:
        raise ValueError(f"Error while reading MQTT config: {e}")

    # Validate required keys
    missing_keys = REQUIRED_KEYS - config.keys()
    if missing_keys:
        raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")

    try:
        config["port"] = int(config["port"])
    except ValueError:
        raise ValueError(f"Invalid port value: '{config['port']}' (must be an integer)")

    return config
