import os
from .client_weather_processor import process_client_weather

def main_weather():
    # Get the absolute path to the "Clients" folder (which is at the same level as "weather/")
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Clients"))

    if not os.path.isdir(base_path):
        print(f"[Main] Client folder not found: {base_path}")
        return

    print("[Main] Starting weather forecast processing...\n")

    for client_name in os.listdir(base_path):
        client_folder = os.path.join(base_path, client_name)
        if not os.path.isdir(client_folder):
            continue

        try:
            print(f"→ Processing {client_name}")
            process_client_weather(client_folder)
        except Exception as e:
            print(f"[Main] Failed to process {client_name}: {e}")

    print("\n[Main] Forecast processing completed.")

if __name__ == "__main__":
    main_weather()
