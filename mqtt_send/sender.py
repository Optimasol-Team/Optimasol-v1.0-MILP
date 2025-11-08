
"""
sender.py – Publish a SETMODE command read from <client_dir>/decisions.txt.

The broker parameters are stored in a simple key-value text file
<project_root>/config/mqtt_config_send.txt, e.g.:

    host = test.mosquitto.org
    port = 1883
    user =                # optional
    pass =                # optional
"""
# Auteur @lilya_sudo

from pathlib import Path
import paho.mqtt.client as mqtt
from data.com_bdd import get_client, get_immediate_decision_by_client

# ──────────────────────────────────────────────
# 1)  Load broker configuration **once** at import
# ──────────────────────────────────────────────

_CONF_FILE = (
    Path(__file__).resolve().parent.parent  # …/optimasol/
    / "config"
    / "mqtt_config_send.txt"
)


def _read_conf(path: Path) -> dict:
    """Parse a key = value text file (ignores blanks & '#' comments)."""
    cfg = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()  # strip comments & blanks
            if not line:
                continue
            key, val = (tok.strip() for tok in line.split("=", 1))
            cfg[key.lower()] = val
    return cfg


_BROKER = _read_conf(_CONF_FILE)


# ──────────────────────────────────────────────
# 2)  Helper that publishes a single MQTT message
# ──────────────────────────────────────────────

def _publish(topic: str, payload: str) -> None:
    """Open a short-lived MQTT connection and publish `payload`."""
    client = mqtt.Client()
    if _BROKER.get("user"):
        client.username_pw_set(_BROKER["user"], _BROKER.get("pass", ""))
    client.connect(
        _BROKER.get("host", "localhost"),
        int(_BROKER.get("port", 1883)),
        keepalive=60,
    )
    client.publish(topic, payload, qos=1, retain=False)
    client.disconnect()


# ──────────────────────────────────────────────
# 3)  Public entry point
# ──────────────────────────────────────────────

def send_command(client_id: str) -> None:
    """
    va chercher décision de client , extract the numeric mode and publish it
    to topic "<client_name>/SETMODE"."""
    client = get_client(client_id)
    decision = get_immediate_decision_by_client(client_id) # c'est un str

    if decision is None :
        raise FileNotFoundError(f"decision of {client_id} not found")

    topic = f"{client['router_id']}/SETMODE"     # e.g. "client_A/SETMODE"

    _publish(topic, decision)

    # Optional debug – harmless on a headless server; comment out if undesired
    print(f"Published mode {decision} → {topic}")


