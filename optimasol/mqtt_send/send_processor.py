"""
send_processor.py

Handles the full sending logic for one client: selects the latest past command
from the decisions file and sends it via MQTT.
"""

import os
import json
from datetime import datetime
from typing import Optional
from mqtt_send.sender import send_command

def process_client(client_id: str, config: dict, base_dir: str = "clients") -> None:
    """
    Processes and sends the most recent valid command for the specified client.

    Args:
        client_id (str): The client folder name (e.g., 'PV0001').
        config (dict): MQTT connection parameters.
        base_dir (str): Root path of the clients folder.
    """
    path = os.path.join(base_dir, client_id, "decisions.json")

    if not os.path.exists(path):
        print(f"[SKIP] No decision file for {client_id}")
        return

    try:
        with open(path, "r") as f:
            decisions = json.load(f)
    except Exception as e:
        print(f"[ERROR] Cannot read decision file for {client_id}: {e}")
        return

    now = datetime.now().strftime("%H:%M")
    all_times = sorted(decisions.keys())

    # Find the latest past or current hour <= now
    latest_time = None
    for t in all_times:
        if t <= now:
            latest_time = t
        else:
            break

    if not latest_time:
        print(f"[INFO] No applicable command yet for {client_id} (now = {now})")
        return

    raw_command = decisions.get(latest_time)
    if not isinstance(raw_command, str) or " " not in raw_command:
        print(f"[ERROR] Invalid command format at {latest_time} for {client_id}: {raw_command}")
        return

    try:
        cmd_type, cmd_value = raw_command.split(maxsplit=1)
        if "." in cmd_value:
            cmd_value = float(cmd_value)
        else:
            cmd_value = int(cmd_value)
    except Exception as e:
        print(f"[ERROR] Failed to parse command for {client_id} at {latest_time}: {e}")
        return

    command = {
        "type": cmd_type,
        "value": cmd_value
    }

    send_command(client_id, command, config)
