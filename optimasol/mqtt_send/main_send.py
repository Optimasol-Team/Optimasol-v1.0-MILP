"""
main_send.py

Main entry point for the mqtt_send module.
Executed once per hour (via OS scheduler), it loads the MQTT config,
iterates over all client folders in /clients, reads the command for the current time,
and sends it to the appropriate MQTT topic using send_processor.
"""

import os
from mqtt_send.config_loader import load_mqtt_config
from mqtt_send.send_processor import process_client

def main():
    # Load MQTT configuration
    try:
        config = load_mqtt_config()
    except Exception as e:
        print(f"[FATAL] Failed to load MQTT config: {e}")
        return

    # Detect client folders
    clients_dir = "clients"
    if not os.path.exists(clients_dir):
        print(f"[FATAL] Clients directory not found: {clients_dir}")
        return

    for client_id in os.listdir(clients_dir):
        client_path = os.path.join(clients_dir, client_id)
        if os.path.isdir(client_path):
            print(f"[INFO] Processing client: {client_id}")
            process_client(client_id, config)

if __name__ == "__main__":
    main()
