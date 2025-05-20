"""
main_receive.py

Main entry point for the mqtt_receive module.
It loads the MQTT config, starts the MQTT client, and enters an infinite loop
to listen for incoming data from PV routers.
"""

import sys
import os

# Ensure project root is in Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mqtt_receive.config_loader import load_mqtt_config
from mqtt_receive.mqtt_client import start_mqtt_client

def main():
    try:
        config = load_mqtt_config("config/mqtt_config_receive.txt")
    except Exception as e:
        print(f"[FATAL] Failed to load MQTT config: {e}")
        return

    try:
        client = start_mqtt_client(config)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[INFO] MQTT listener stopped manually.")
    except Exception as e:
        print(f"[FATAL] Error in MQTT client loop: {e}")

if __name__ == "__main__":
    main()
