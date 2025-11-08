import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from weather.client_weather_processor import process_client_weather
from data.com_bdd import get_client_ids

def main_weather():
    
   
    print("[Main] Starting weather forecast processing...\n")
    clients = get_client_ids()
    for client_id in clients:
        try:
            print(f"→ Processing {client_id}")
            process_client_weather(client_id)
        except Exception as e:
            print(f"[Main] Failed to process {client_id}: {e}")

    print("\n[Main] Forecast processing completed.")

if __name__ == "__main__":
    main_weather()
