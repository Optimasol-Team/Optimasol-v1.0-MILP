# main_production.py

"""
Main script to generate production.json for all clients.

This script scans the 'clients' directory, identifies valid
clients (those having data.json and weather.json), and runs
the full solar production pipeline.

"""

from pathlib import Path
from weather_processing.client_processor import process_client


def main_production():
    clients_root = Path("clients")

    if not clients_root.exists():
        print("No 'clients' directory found.")
        return

    for client_dir in clients_root.iterdir():
        if not client_dir.is_dir():
            continue

        data_file = client_dir / "data.json"
        weather_file = client_dir / "weather.json"

        if data_file.exists() and weather_file.exists():
            print(f"Processing client: {client_dir.name}")
            try:
                process_client(client_dir)
                print(f"✔ Done for {client_dir.name}")
            except Exception as e:
                print(f"❌ Error processing {client_dir.name}: {e}")
        else:
            print(f"Skipping {client_dir.name} (missing data or weather file)")

if __name__ == "__main__":
    main_production()
