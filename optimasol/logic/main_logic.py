from pathlib import Path
from logic.client_processor_logic import process_client
import json


def main():
    """
    Main script to process all client folders inside the `clients/` directory.
    For each client, generates MQTT commands using the full optimization pipeline.
    """
    base_dir = Path("clients")
    client_dirs = [f for f in base_dir.iterdir() if f.is_dir()]

    for client_path in client_dirs:
        print(f"Processing client: {client_path.name}")

        result = process_client(client_path, profile="setmode")  # or "dimmer"

        # Output MQTT commands as JSON (example save)
        output_file = client_path / "mqtt_commands.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(result["mqtt_commands"], f, indent=2)

        print(f"  → Commands written to {output_file}")


if __name__ == "__main__":
    main()
