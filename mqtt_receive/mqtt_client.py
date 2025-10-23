"""
mqtt_client.py

Initializes and runs the MQTT client that listens to router data messages
and delegates them to the message handler.
"""

import paho.mqtt.client as mqtt
import json
from mqtt_receive.message_handler import handle_message
from typing import Dict

def start_mqtt_client(config: Dict) -> mqtt.Client:
    """
    Starts and returns a configured MQTT client that listens to all <client_id>/DATA topics.

    Args:
        config (dict): MQTT configuration with keys: host, port, user, pass, refresh.

    Returns:
        mqtt.Client: The initialized and connected MQTT client.
    """
    client = mqtt.Client()

    if config.get("user") and config.get("pass"):
        client.username_pw_set(config["user"], config["pass"])

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("[INFO] Connected to MQTT broker.")
            # Subscribe to all data topics (e.g. PV0001/DATA)
            client.subscribe("+/DATA")
            print("[INFO] Subscribed to topics: +/DATA")
        else:
            print(f"[ERROR] MQTT connection failed with code {rc}")

    def on_message(client, userdata, msg):
        try:
            topic = msg.topic  # ex: PV0001/DATA
            payload = json.loads(msg.payload.decode())
            client_id = topic.split("/")[0]
            handle_message(client_id, payload)
        except Exception as e:
            print(f"[ERROR] Failed to process message on topic {msg.topic}: {e}")

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(config["host"], config.get("port", 1883), keepalive=30)
    except Exception as e:
        print(f"[FATAL] Could not connect to MQTT broker: {e}")
        raise

    return client
