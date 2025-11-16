#client_processor.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.com_bdd import ( get_connection,get_CE_by_client, get_chauffe_eau,
                         get_system_configuration_by_client, get_latest_temperature_by_client,
                         get_configuration_prediction_by_chauffe_eau, get_previsions_by_client, add_decision)
from logic.optimizer.milp_solver import milp_analysis
import json
from datetime import datetime
from utils import load_water_consumption, distribution_to_series, parse_comfort_schedule, verif

class Client:
    def __init__(self, client_id):
        self.client_id = client_id
        self.data = {}
        self.id_CE = get_CE_by_client(client_id)
        system_config = get_system_configuration_by_client(client_id)

   
        config_prevision = get_configuration_prediction_by_chauffe_eau(self.id_CE)
        if config_prevision:
            self.config = config_prevision
            config = config_prevision[0]
            self.data["step_min"] = int(config[2])
        else:
            self.data["step_min"] = 15  # Valeur par défaut

        if system_config:
            self.data.update(system_config)
            self.data['minimum_comfort_temperature'] = float(self.data.get('minimum_comfort_temperature', 50.0))
            self.data['cold_water_temperature'] = float(self.data.get('cold_water_temperature', 12.0))
            self.data["tariffs"] = {
                "contract_type": system_config.get("contract_type", "base"),
                "tariffs_eur_per_kwh": {
                    "base": float(system_config.get("base_tariff", 0.18)),
                    "hp": float(system_config.get("hp_tariff", 0.18)),
                    "hc": float(system_config.get("hc_tariff", 0.18)),
                    "sell_tariff": float(system_config.get("sell_tariff", 0.1))
                },
                "off_peak_hours": system_config.get("off_peak_hours", [])
            }

       
            water_consumption = load_water_consumption(system_config, self.data['step_min'])
            self.data['water_consumption'] = water_consumption

      
            N = 24 * 60 // self.data["step_min"]
            self.data["comfort_schedule"] = parse_comfort_schedule(system_config, N)
        else:
            self.data["tariffs"] = {
                "contract_type": "base",
                "tariffs_eur_per_kwh": {"base": 0.18, "hp": 0.18, "hc": 0.18, "sell_tariff": 0.10},
                "off_peak_hours": []
            }
         
            N = 24 * 60 // self.data["step_min"]
            self.data["comfort_schedule"] = [50.0] * N
            self.data['water_consumption'] = [0] * N

        self.data["minimum_comfort_temperature_enabled"] = system_config.get("minimum_comfort_temperature_enabled", False) if system_config else False

        water_heater_data = get_chauffe_eau(self.id_CE)
        if water_heater_data:
            water_heater_data['puissance_kw'] = float(water_heater_data['puissance_kw'])
            water_heater_data['capacite_litres'] = int(water_heater_data['capacite_litres'])
            self.data["water_heater"] = water_heater_data

        temp_data = get_latest_temperature_by_client(client_id)
        self.data["t0"] = float(temp_data[0]) if temp_data else 50.0

    def _load_pv_production(self, start_time):
        pv_previsions = get_previsions_by_client(self.client_id)
        N = 24 * 60 // self.data["step_min"]
        
        if pv_previsions:
            
            start_hour = start_time.hour
            start_index = start_hour * (60 // self.data["step_min"])
            
            pv_series = [float(p[2]) for p in pv_previsions]
            
            aligned_pv = pv_series[start_index:] + pv_series[:start_index]
            self.data["pv_production"] = aligned_pv[:N]
        else:
            self.data["pv_production"] = [0.0] * N

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
        
    
        client._load_pv_production(optimization_start)

        success, u_values, T_values, metrics = milp_analysis(client.data)
        if success and u_values is not None:
            add_decision(
                client.id_CE, 
                u_values, # les décisions
                step_min=client.data["step_min"],
                heure_debut=optimization_start,
            )
            print(f"Décision sauvegardée pour client {client_id}: {len(u_values)} créneaux à partir de {optimization_start}")

        else:
            print(f"❌ Optimisation échouée pour client {client_id}")
            
    except Exception as e:
        print(f"Erreur optimisation client {client_id}: {e}")

def process_all_clients(clients):
    for i in range(len(clients)):
        process_client(clients[i])

if __name__ == "__main__":

    process_client(13)
