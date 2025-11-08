# client_processor.py 
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.com_bdd import get_client, get_meteo, add_prevision_production, get_CE_by_client, get_configuration_prediction_by_chauffe_eau
from weather_processing.irradiance_to_production import compute_production

def safe_float(value, default=0.0):
    if value is None: return default
    try:
        if isinstance(value, str) and value == 'default': return default
        return float(value)
    except: return default

def process_client(client_id):
    print(f"Production Client {client_id}")
    
    client_data = get_client(client_id)
    if not client_data: return print("Client non trouvé")
    
    ce_id = get_CE_by_client(client_id)
    if not ce_id: return print("Pas de chauffe-eau")
    
    configs = get_configuration_prediction_by_chauffe_eau(ce_id)
    if not configs: return print("Pas de config PV")
    
    config = configs[0]
    pv_config = {
        "surface_m2": safe_float(config[6], 10.0),
        "panel_efficiency": safe_float(config[7], 0.18),
        "system_efficiency": safe_float(config[8], 0.85)
    }
    
    meteo_data = get_meteo(client_id)
    if not meteo_data: return print("Pas de données météo")
    
    irradiance_dict = {}
    for m in meteo_data:
        if isinstance(m, tuple) and len(m) >= 10:
            irradiance, heure_debut = m[8], m[9]
            if irradiance is not None and heure_debut is not None:
                try:
                    key = heure_debut if isinstance(heure_debut, str) else heure_debut.isoformat()
                    irradiance_dict[key] = safe_float(irradiance, 0.0)
                except: continue
    
    if not irradiance_dict: return print("Pas d'irradiance valide")
    
    try:
        full_config = {
            "location": {
                "latitude": safe_float(client_data.get("latitude", 48.8)),
                "longitude": safe_float(client_data.get("longitude", 2.3)),
                "tilt": safe_float(client_data.get("tilt", 30)),
                "azimuth": safe_float(client_data.get("azimuth", 180)),
            },
            "pv_system": pv_config
        }
        
        production_dict = compute_production(irradiance_dict, full_config)
        
        for heure_str, puissance_w in production_dict.items(): 
            add_prevision_production(client_id, puissance_w / 1000, heure_str)

        print(f"OK: {len(production_dict)} prévisions")
    
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    process_client(1)