
# fisnish
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.com_bdd import get_meteo



def get_24h_irradiance_by_hour(client_id):
    """Version simplifiée avec fallback basique"""
    now = datetime.now()
    all_meteo = get_meteo(client_id)
    
    # Convertir tuples en dicts si nécessaire
    if all_meteo and isinstance(all_meteo[0], tuple):
        columns = ['id', 'client_id', 'temperature_ext', 'humidity', 'wind_speed', 
                  'precipitation', 'cloud_cover', 'weather_code', 'irradiance',
                  'heure_debut', 'heure_fin', 'source_meteo']
        all_meteo = [dict(zip(columns, row)) for row in all_meteo]
    
    # Récupérer données disponibles
    hourly_data = {}
    for meteo in all_meteo:
        if meteo['heure_debut'] >= now and meteo['heure_debut'] <= now + timedelta(hours=24):
            hour = meteo['heure_debut'].hour
            hourly_data[hour] = meteo.get('irradiance', 0)
    
    # Compléter les manquants avec pattern jour/nuit simple
    for hour in range(24):
        if hour not in hourly_data:
            # Jour (6h-20h) = 400 W/m², Nuit = 0 W/m²
            hourly_data[hour] = 400 if 6 <= hour <= 20 else 0
    
    return hourly_data