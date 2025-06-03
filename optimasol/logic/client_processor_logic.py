from pathlib import Path
from logic.data_preparation.factory import load_client
from logic.optimizer.runner import run_optimizer
from logic.decision_engine.engine import format_decision


def process_client(folder: Path, profile: str = "setmode") -> dict:
    """
    Processes one client folder:
      - loads data
      - runs optimizer
      - formats MQTT commands

    Parameters:
        folder (Path): Path to the client's folder with JSON data.
        profile (str): Decision profile name (e.g., "setmode" or "dimmer").

    Returns:
        dict: {
            "mqtt_commands": Dict[str, str],
            "optimizer_output": Dict[str, Any]
        }
    """
    # Step 1: load data from folder
    client_data = load_client(folder)

    # Step 2: run optimizer
    result = run_optimizer(
        hyper=client_data["hyper"],
        production=client_data["production"],
        tariffs=client_data["tarifs"]
    )

    # Step 3: format MQTT commands from best combination
    n = client_data["hyper"]["n"]
    best_sequence = result["best_combination"]
    commands = format_decision(best_sequence, n=n, profile=profile)

    return {
        "mqtt_commands": commands,
        "optimizer_output": result
    }
