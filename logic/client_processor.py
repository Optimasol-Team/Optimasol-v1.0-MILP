import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.com_bdd import (get_connection, get_CE_by_client, get_chauffe_eau,
                         get_system_configuration_by_client, get_latest_temperature_by_client,
                         get_configuration_prediction_by_chauffe_eau, get_previsions_by_client, add_decision)
from logic.optimizer.milp_solver import optimise
import json
from datetime import datetime

class Client:
    def __init__(self, client_id):
        self.client_id = client_id
        self.conn = get_connection()
        self.data = {}
        
        system_config = get_system_configuration_by_client(client_id)
        if system_config:
            self.data.update(system_config)
            if 'minimum_comfort_temperature' in self.data:
                self.data['minimum_comfort_temperature'] = float(self.data['minimum_comfort_temperature'])
        
        self.id_CE = get_CE_by_client(client_id)
        if self.id_CE:
            water_heater_data = get_chauffe_eau(self.id_CE)
            if water_heater_data:
                if 'puissance_kw' in water_heater_data:
                    water_heater_data['puissance_kw'] = float(water_heater_data['puissance_kw'])
                if 'capacite_litres' in water_heater_data:
                    water_heater_data['capacite_litres'] = int(water_heater_data['capacite_litres'])
                self.data["water_heater"] = water_heater_data
        
        temp_data = get_latest_temperature_by_client(client_id)
        self.data["t0"] = float(temp_data[0]) if temp_data else 50.0
        
        config_prevision = get_configuration_prediction_by_chauffe_eau(self.id_CE)
        if config_prevision:
            config = config_prevision[0]
            self.data["step_min"] = int(config[2]) if len(config) > 2 else 15
            self.data["horizon_h"] = int(config[3]) if len(config) > 3 else 24
        else:
            self.data["step_min"] = 15
            self.data["horizon_h"] = 24
        
        pv_previsions = get_previsions_by_client(client_id)
        N = self.data["horizon_h"] * 60 // self.data["step_min"]
        if pv_previsions and len(pv_previsions) >= N:
            self.data["pv_production"] = [float(p[2]) for p in pv_previsions[:N]]
        else:
            available = [float(p[2]) for p in pv_previsions] if pv_previsions else []
            missing = N - len(available)
            self.data["pv_production"] = available + [0.0] * missing
        
        self._load_water_consumption(system_config)
        
        if system_config:
            self.data["tariffs"] = {
                "contract_type": system_config.get("contract_type", "base"),
                "tariffs_eur_per_kwh": {
                    "base": float(system_config.get("base_tariff", 0.18)),
                    "hp": float(system_config.get("hp_tariff", 0.18)),
                    "hc": float(system_config.get("hc_tariff", 0.18)),
                    "sell": 0.10
                },
                "off_peak_hours": system_config.get("off_peak_hours", [])
            }
        else:
            self.data["tariffs"] = {
                "contract_type": "base",
                "tariffs_eur_per_kwh": {"base": 0.18, "hp": 0.18, "hc": 0.18, "sell": 0.10},
                "off_peak_hours": []
            }
        
        self.data["comfort_schedule"] = self._parse_comfort_schedule(system_config)
        self.data["minimum_comfort_temperature_enabled"] = system_config.get("minimum_comfort_temperature_enabled", False) if system_config else False

    def _load_water_consumption(self, system_config):
        if system_config and system_config.get('water_consumption'):
            water_data = system_config['water_consumption']
            if isinstance(water_data, str):
                try:
                    water_data = json.loads(water_data)
                except:
                    water_data = None
            
            if water_data and 'distribution' in water_data:
                self.data["water_consumption"] = self._distribution_to_series(
                    water_data['distribution'],
                    self.data["step_min"], 
                    self.data["horizon_h"]
                )
                return
        
        N = self.data["horizon_h"] * 60 // self.data["step_min"]
        self.data["water_consumption"] = [0] * N
    
    def _distribution_to_series(self, distribution, step_min, horizon_h):
        N = horizon_h * 60 // step_min
        consumption = [0] * N
        
        for event in distribution:
            hour = event.get("hour", 0)
            liters = event.get("liters", 0)
            
            start_index = (hour * 60) // step_min
            duration_slots = 60 // step_min
            liters_per_slot = liters / duration_slots
            
            for i in range(duration_slots):
                idx = start_index + i
                if idx < N:
                    consumption[idx] += liters_per_slot
        
        return consumption

    def _parse_comfort_schedule(self, system_config):
        if not system_config or not system_config.get('comfort_schedule'):
            return [
                {"time": "07:00", "target_temperature_celsius": 70},
                {"time": "19:00", "target_temperature_celsius": 65}
            ]
        
        comfort = system_config['comfort_schedule']
        if isinstance(comfort, list):
            return comfort
        if isinstance(comfort, str):
            try:
                return json.loads(comfort)
            except:
                pass
        
        return [
            {"time": "07:00", "target_temperature_celsius": 70},
            {"time": "19:00", "target_temperature_celsius": 65}
        ]

def process_client(client_id) -> None:
    try:
        client = Client(client_id)
    except Exception as e:
        print(f"Error initializing client {client_id}: {e}")
        return

    if not client.id_CE:
        print(f"Client {client_id} n'a pas de chauffe-eau")
        return
    
    if not client.data.get("water_heater"):
        print(f"Données chauffe-eau manquantes pour client {client_id}")
        return

    try:
        optimization_start = datetime.now()
        client.data["optimization_start_time"] = optimization_start
        
        decision_list = optimise(client.data)
        add_decision(
            client.id_CE, 
            decision_list, 
            step_min=client.data["step_min"],
            horizon_h=client.data["horizon_h"],
            heure_debut=optimization_start,
            conn=client.conn
        )
        print(f"Décision sauvegardée pour client {client_id}: {len(decision_list)} créneaux à partir de {optimization_start}")
    except Exception as e:
        print(f"Erreur optimisation client {client_id}: {e}")
    finally:
        if client.conn:
            client.conn.close()

if __name__ == "__main__":
    process_client(1)