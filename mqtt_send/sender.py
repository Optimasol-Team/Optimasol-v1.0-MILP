
"""
sender.py – Publish a SETMODE command read from <client_dir>/decisions.txt.

The broker parameters are stored in a simple key-value text file
<project_root>/config/mqtt_config_send.txt, e.g.:

    host = test.mosquitto.org
    port = 1883
    user =                # optional
    pass =                # optional
"""

from pathlib import Path
import paho.mqtt.client as mqtt

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

def send_command(client_dir: str) -> None:
    """
    Read <client_dir>/decisions.txt, extract the numeric mode and publish it
    to topic "<client_name>/SETMODE".

    Parameters
    ----------
    client_dir : str
        Path to the client's directory containing decisions.txt.
    """
    client_path = Path(client_dir).resolve()
    decision_file = client_path / "decisions.txt"

    if not decision_file.is_file():
        raise FileNotFoundError(f"{decision_file} not found")

    content = decision_file.read_text(encoding="utf-8").strip()
    parts = content.split()

    if len(parts) != 2 or parts[0].upper() != "SETMODE" or not parts[1].isdigit():
        raise ValueError(
            f"Invalid decision format in {decision_file}: expected 'SETMODE <number>'"
        )

    mode = parts[1]                           # e.g. "10"
    topic = f"{client_path.name}/SETMODE"     # e.g. "client_A/SETMODE"

    _publish(topic, mode)

    # Optional debug – harmless on a headless server; comment out if undesired
    print(f"Published mode {mode} → {topic}")


