import os
import json

def generate_clients(prefix="PV", count=10):
    # Get absolute path to the root project (Optimasol)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    clients_path = os.path.join(project_root, "Clients")
    os.makedirs(clients_path, exist_ok=True)

    template_data = {
        "mqtt": {
            "username": "",
            "password": "monmotdepasse"
        },
        "location": {
            "latitude": 50.63,
            "longitude": 3.14,
            "altitude": None,
            "tilt": 30,
            "azimuth": 180
        },
        "water_heater": {
            "volume_liters": 200,
            "power_watts": 3000,
            "comfort_schedule": [
                {"time": "06:30", "target_temperature_celsius": 70},
                {"time": "20:00", "target_temperature_celsius": 65}
            ]
        },
        "pv_system": {
            "surface_m2": 6.0,
            "panel_efficiency": 0.20,
            "system_efficiency": 0.85
        },
        "electricity_contract": {
            "contract_type": "HPHC",
            "tariffs_eur_per_kwh": {
                "base": 0.2016,
                "hp": 0.2146,
                "hc": 0.1696
            },
            "custom_tariffs": {
                "base": None,
                "hp": None,
                "hc": None
            },
            "off_peak_hours": [
                {"start": "22:30", "end": "06:30"}
            ]
        },
        "user_info": {
            "name": "Client",
            "email": "client@example.com"
        }
    }

    for i in range(1, count + 1):
        client_id = f"{prefix}{i:04d}"
        client_folder = os.path.join(clients_path, client_id)
        os.makedirs(client_folder, exist_ok=True)

        # Copy and customize data
        data = json.loads(json.dumps(template_data))  # deep copy
        data["router_id"] = client_id
        data["mqtt"]["username"] = client_id
        data["location"]["latitude"] += i * 0.01
        data["location"]["longitude"] += i * 0.01

        # Optionally add a custom API config to every 3rd client
        if i % 3 == 0:
            data["custom_forecast_source"] = {
                "enabled": True,
                "mode": "api",
                "format": "json",
                "url": f"https://example.com/api/{client_id}",
                "auth_token": f"Bearer token-{client_id}",
                "field_mapping": {
                    "irradiance": "ghi",
                    "times": "timestamp"
                }
            }

        # Write to data.json
        with open(os.path.join(client_folder, "data.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Created: {client_id}")

generate_clients()
