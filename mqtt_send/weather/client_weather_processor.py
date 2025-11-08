# client_weather_processor.py - VERSION FINALE CORRIGÉE
from .client_api_fetcher import get_client_production
from .apis.open_meteo import get_forecast as get_open_meteo
from .aggregator import aggregate_forecasts
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.com_bdd import get_client, add_prevision_production

def process_client_weather(client_id: str) -> None:
    print(f"[Processor] Processing client: {client_id}")

    client_data = get_client(client_id)
    if not client_data:
        print(f"[Processor] Client {client_id} non trouvé")
        return

    latitude = client_data.get('latitude')
    longitude = client_data.get('longitude')
    
    if latitude is None or longitude is None:
        print(f"[Processor] Client {client_id} n'a pas de coordonnées GPS")
        return

    print(f"[Processor] Localisation: {latitude}, {longitude}")

    forecast_mode = "default"
    forecast = {}

    if forecast_mode == "custom":
        print("[Processor] Using custom forecast API...")
        api_config = {}
        forecast = get_client_production(api_config)
    else:
        print("[Processor] Using default weather sources...")
        sources = []
        meteo = get_open_meteo(latitude, longitude)
        if meteo["irradiance"]:
            sources.append(meteo)

        forecast = aggregate_forecasts(sources)

    if forecast and forecast["irradiance"]:
        for i, (timestamp, irradiance) in enumerate(zip(forecast["times"], forecast["irradiance"])):
            puissance_kw = irradiance / 1000
            
            add_prevision_production(client_id, puissance_kw, timestamp)
        
        print(f"[Processor] {len(forecast['irradiance'])} prévisions sauvegardées pour client {client_id}")
    else:
        print(f"[Processor] Aucune donnée de prévision à sauvegarder pour client {client_id}")