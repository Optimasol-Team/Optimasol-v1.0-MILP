"""
generate_decisions.py

Generates a test decisions.json file for each client in the 'clients/' directory.
Each file contains 24 time entries (00:00 to 23:00) with dummy command strings.
"""

import os
import json

def generate_decision_data():
    decisions = {}
    for hour in range(24):
        hour_str = f"{hour:02d}:00"
        if hour % 2 == 0:
            decisions[hour_str] = f"SETMODE {10 + hour}"
        else:
            decisions[hour_str] = f"DIMMER1 {hour * 4.5}"
    return decisions

def main():
    base_dir = "clients"

    if not os.path.exists(base_dir):
        print(f"[ERROR] Clients folder not found: {base_dir}")
        return

    for client_id in os.listdir(base_dir):
        client_path = os.path.join(base_dir, client_id)
        if os.path.isdir(client_path):
            decisions_path = os.path.join(client_path, "decisions.json")
            decisions = generate_decision_data()

            try:
                with open(decisions_path, "w") as f:
                    json.dump(decisions, f, indent=2)
                print(f"[OK] Created decisions.json for {client_id}")
            except Exception as e:
                print(f"[ERROR] Failed to write for {client_id}: {e}")

if __name__ == "__main__":
    main()
