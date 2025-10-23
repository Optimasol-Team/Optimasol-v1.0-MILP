import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.com_bdd import (get_connection, get_CE_by_client, get_chauffe_eau,
                         get_system_configuration_by_client, get_latest_temperature_by_client,
                         get_configuration_prediction_by_chauffe_eau, get_previsions_by_client, add_decision)
from logic.optimizer.milp_solver import optimise
import json

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

    def _parse_comfort_schedule(self, system_config):
        if not system_config or 'comfort_schedule' not in system_config:
            return self._default_comfort_schedule()
        
        comfort = system_config['comfort_schedule']
        if not comfort:
            return self._default_comfort_schedule()
            
        if isinstance(comfort, list):
            return comfort
            
        if isinstance(comfort, str):
            try:
                parsed = json.loads(comfort)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict):
                    return self._convert_comfort_dict_to_list(parsed)
            except:
                pass
        
        return self._default_comfort_schedule()
    
    def _convert_comfort_dict_to_list(self, comfort_dict):
        result = []
        
        if "morning" in comfort_dict:
            morning_time = self._extract_target_time(comfort_dict["morning"])
            result.append({"time": morning_time, "target_temperature_celsius": 70})
        
        if "evening" in comfort_dict:
            evening_time = self._extract_target_time(comfort_dict["evening"]) 
            result.append({"time": evening_time, "target_temperature_celsius": 65})
            
        if "weekday" in comfort_dict:
            result.append({"time": comfort_dict["weekday"], "target_temperature_celsius": 70})
        if "weekend" in comfort_dict:
            result.append({"time": comfort_dict["weekend"], "target_temperature_celsius": 70})
            
        return result or self._default_comfort_schedule()
    
    def _extract_target_time(self, time_range):
        if '-' in time_range:
            start, end = time_range.split('-')
            start_h = int(start.split(':')[0])
            end_h = int(end.split(':')[0])
            middle_h = (start_h + end_h) // 2
            return f"{middle_h:02d}:00"
        return time_range
    
    def _default_comfort_schedule(self):
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
        decision_list = optimise(client.data)
        add_decision(client.id_CE, decision_list, conn=client.conn)
        print(f"Décision sauvegardée pour client {client_id}: {len(decision_list)} créneaux")
    except Exception as e:
        print(f"Erreur optimisation client {client_id}: {e}")
    finally:
        if client.conn:
            client.conn.close()

if __name__ == "__main__":
    process_client(1)