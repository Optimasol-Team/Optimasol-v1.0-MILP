# main_production.py
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from weather_processing.client_processor import process_client
from data.com_bdd import get_client_ids

def main_production():
    clients = get_client_ids()
    for client_id in clients:
        print(f"Processing client: {client_id}")
        try:
            process_client(client_id)
            print(f" Done for {client_id}")
        except Exception as e:
            print(f" Error processing {client_id}: {e}")

if __name__ == "__main__":
    main_production()