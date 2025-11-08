# irradiance_to_production.py - VERSION CORRIGÉE
import pandas as pd
from pvlib.location import Location
from pvlib.irradiance import get_total_irradiance, erbs

def compute_production(irradiance_dict, client_config):
    """
    Compute electrical power production based on irradiance and panel config.
    """
    # Extraire les paramètres
    location = client_config["location"]
    pv = client_config["pv_system"]

    latitude = location["latitude"]
    longitude = location["longitude"]
    tilt = location["tilt"]
    azimuth = location["azimuth"]

    surface = pv["surface_m2"]
    panel_eff = pv["panel_efficiency"]
    system_eff = pv["system_efficiency"]

    # Préparer les séries temporelles
    times = pd.to_datetime(list(irradiance_dict.keys()))
    ghi = pd.Series(list(irradiance_dict.values()), index=times)

    # CORRECTION: Vérifier que nous avons des données
    if ghi.empty:
        return {}

    # Créer l'objet Location
    site = Location(latitude, longitude)

    try:
        # Obtenir la position solaire
        solpos = site.get_solarposition(times)
        
        # CORRECTION: Gérer les divisions par zéro
        zenith = solpos['zenith'].fillna(90)  # Remplacer NaN par 90°
        
        # Décomposer le GHI en DNI et DHI
        components = erbs(ghi, zenith, times)
        dni = components['dni'].fillna(0)
        dhi = components['dhi'].fillna(0)

        # Calculer l'irradiance sur la surface inclinée (POA)
        irrad = get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            dni=dni,
            ghi=ghi,
            dhi=dhi,
            solar_zenith=solpos['zenith'].fillna(90),
            solar_azimuth=solpos['azimuth'].fillna(180)
        )

        poa_irradiance = irrad['poa_global'].fillna(0)  # W/m²

        # Calculer la puissance produite (W)
        power_output = poa_irradiance * surface * panel_eff * system_eff

        # Convertir en dict {timestamp (str): power (float)}
        production_dict = {
            timestamp.isoformat(): round(float(power), 3)
            for timestamp, power in power_output.items()
        }

        return production_dict

    except Exception as e:
        print(f"[PVLIB Error] {e}")
        # Fallback: calcul simple basé sur GHI seulement
        production_dict = {}
        for timestamp, ghi_value in irradiance_dict.items():
            # Calcul simplifié: GHI * surface * efficacités
            power = ghi_value * surface * panel_eff * system_eff
            production_dict[timestamp] = round(float(power), 3)
        
        return production_dict