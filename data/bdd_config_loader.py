"""
fichier vérifé foncttionnell
bdd_loader.py

Loads la bdd configuration from a text file and returns it as a dictionary.
Ensures required fields are present and values are correctly formatted.
"""

import os
from typing import Dict

REQUIRED_KEYS = {"host", "user","password","database"}

def load_bdd_config(filename: str = "bdd_config.txt") -> Dict[str, str]:
    """
    Reads and parses the BDD figuration file.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If a required key is missing or malformed.
    """
   # Chemin du dossier racine du projet (on part du dossier du script)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # remonte d'un niveau
    config_dir = os.path.join(base_dir, "config")
    full_path = os.path.join(config_dir, filename)

    config = {}

    try:
        with open(full_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()

# Vérification

    except FileNotFoundError: # vérifie que le fichier est présent
        raise FileNotFoundError(f"BDD config file not found: {full_path}")
    except Exception as e:
        raise ValueError(f"Error while reading BDD config: {e}")

    # vérifie que toute les clés sont présentes
    missing_keys = REQUIRED_KEYS - config.keys()
    if missing_keys:
        raise ValueError(f"Missing required config keys: {', '.join(missing_keys)}")

    return config

