"""
sender.py

This module is responsible for sending a single MQTT command to a specific PV router.
It is used by the mqtt_send module, which executes hourly to apply precomputed client decisions.
"""

import paho.mqtt.client as mqtt
from typing import Dict

def send_command(client_id: str, command: Dict, config: Dict) -> None:
    """
    Publishes a command to a given MQTT topic based on the client ID and command type/value.

    Args:
        client_id (str): The unique ID of the PV router (e.g., 'PV0001').
        command (dict): A dictionary with at least {"type": ..., "value": ...}.
        config (dict): MQTT broker configuration (host, port, user, pass).

    Raises:
        Exception: If the MQTT publish fails.
    """
    topic = f"{client_id}/{command['type']}"
    payload = str(command["value"])

    host = config.get("host", "localhost")
    port = int(config.get("port", 1883))
    user = config.get("user", "")
    password = config.get("pass", "")

    client = mqtt.Client()

    if user and password:
        client.username_pw_set(user, password)

    try:
        client.connect(host, port, keepalive=10)

        result = client.publish(topic, payload, qos=0)
        result.wait_for_publish()

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            raise Exception(f"MQTT publish failed with code {result.rc}")

        print(f"[OK] Command sent to topic '{topic}' with payload '{payload}'.")

    except Exception as e:
        print(f"[ERROR] Failed to send command to '{topic}': {e}")

    finally:
        client.disconnect()
