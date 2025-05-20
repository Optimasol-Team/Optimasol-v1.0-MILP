"""
config_loader.py

Loads MQTT broker configuration from a text file and returns it as a dictionary.
Ensures required fields are present and values are correctly formatted.
"""

from typing import Dict

REQUIRED_KEYS = {"host", "port"}

def load_mqtt_config(path: str = "config/mqtt_config_send.txt") -> Dict[str, str]:
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
    config = {}

    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(f"Malformed line in config file: '{line}'")

                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()

    except FileNotFoundError:
        raise FileNotFoundError(f"MQTT config file not found: {path}")

    except Exception as e:
        raise ValueError(f"Error while reading MQTT config: {e}")

    # Validate required keys
    missing_keys = REQUIRED_KEYS - config.keys()
    if missing_keys:
        raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")

    # Optional: validate port is integer
    try:
        config["port"] = int(config["port"])
    except ValueError:
        raise ValueError(f"Invalid port value: '{config['port']}' (must be an integer)")

    return config
