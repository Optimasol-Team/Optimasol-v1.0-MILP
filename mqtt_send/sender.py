
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
from data.com_bdd import get_client, get_immediate_decision_by_client,get_CE_by_client
from decision_executor import get_current_decision, format_command

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


def send_command(client_id):
    """Envoie la commande actuelle pour un client"""
    # Récupérer le chauffe-eau du client
    ce_id = get_CE_by_client(client_id)
    client = get_client(client_id)
    routeur_id = client.get("router_id")
    if not ce_id:
        print(f"Client {client_id} sans chauffe-eau")
        return

    current_decision = get_current_decision(ce_id)
    
    if current_decision is None:
        print(f"Aucune décision valide pour client {client_id}")
        return

    command = format_command(current_decision)
    print(f"Envoi commande client {client_id}: {command}")
    topic = f"{router_id}/SETMODE" # ???
    try:
        # Envoi effectif de la commande via MQTT
        _publish(topic, command)
        print(f"Commande envoyée avec succès sur le topic: {topic}")
    except Exception as e:
        print(f"Erreur lors de l'envoi MQTT: {e}")
    
