# irradiance_to_production.py

"""
Irradiance to Production Calculator

This module calculates real solar panel power output (in watts)
from global horizontal irradiance (GHI) data using panel and
site characteristics via pvlib.

"""

import pandas as pd
from pvlib.location import Location
from pvlib.irradiance import get_total_irradiance
from pvlib.irradiance import erbs, get_total_irradiance
def compute_production(irradiance_dict, client_config):
    """
    Compute electrical power production based on irradiance and panel config.

    Parameters:
        irradiance_dict (dict): {timestamp (ISO str): irradiance (W/m²)}
        client_config (dict): {
            "location": { "latitude", "longitude", "tilt", "azimuth" },
            "pv_system": { "surface_m2", "panel_efficiency", "system_efficiency" }
        }

    Returns:
        dict: {timestamp (ISO str): power_produced (float in watts)}
    """
    # Extract parameters
    location = client_config["location"]
    pv = client_config["pv_system"]

    latitude = location["latitude"]
    longitude = location["longitude"]
    tilt = location["tilt"]
    azimuth = location["azimuth"]

    surface = pv["surface_m2"]
    panel_eff = pv["panel_efficiency"]
    system_eff = pv["system_efficiency"]

    # Prepare time and irradiance as pandas Series
    times = pd.to_datetime(list(irradiance_dict.keys()))
    ghi = pd.Series(list(irradiance_dict.values()), index=times)

    # Create pvlib Location object
    site = Location(latitude, longitude)

    # Get solar position
    solpos = site.get_solarposition(times)
    components = erbs(ghi, solpos['zenith'], times)
    dni = components['dni']
    dhi = components['dhi']
    # Compute irradiance on the tilted panel surface (POA)
    irrad = get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        dni=dni,
        ghi=ghi,
        dhi=dhi,
        solar_zenith=solpos['zenith'],
        solar_azimuth=solpos['azimuth']
    )

    poa_irradiance = irrad['poa_global'] # W/m²

    # Compute power produced (W)
    power_output = poa_irradiance * surface * panel_eff * system_eff

    # Convert to {timestamp (str): power (float)} dict
    production_dict = {
        timestamp.isoformat(timespec='minutes'): round(power, 3)
        for timestamp, power in power_output.items()
    }

    return production_dict
