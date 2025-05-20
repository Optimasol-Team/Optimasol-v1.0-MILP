"""
message_handler.py

Processes incoming MQTT messages by writing the payload to a client's
router_data.json file under the /clients directory.
"""

import os
import json
from datetime import datetime
from typing import Dict

def handle_message(client_id: str, payload: Dict, base_dir: str = "clients") -> None:
    """
    Handles an incoming MQTT message for a specific client.

    Args:
        client_id (str): The client/router ID (e.g., 'PV0001').
        payload (dict): The JSON payload received from the MQTT broker.
        base_dir (str): The root directory where client folders are located.

    This function will:
    - Ensure the client folder exists
    - Write the payload to 'router_data.json' with a timestamp
    """
    client_path = os.path.join(base_dir, client_id)
    os.makedirs(client_path, exist_ok=True)

    router_data_path = os.path.join(client_path, "router_data.json")

    data_to_write = {
        "last_update": datetime.now().isoformat(),
        "data": payload
    }

    try:
        with open(router_data_path, "w") as f:
            json.dump(data_to_write, f, indent=2)
        print(f"[INFO] Updated router_data.json for {client_id}")
    except Exception as e:
        print(f"[ERROR] Failed to write router_data.json for {client_id}: {e}")
