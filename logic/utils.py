#utils.py

import sys
import os

# Ajouter le dossier parent au sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import json
from data.com_bdd import get_previsions_by_client


def load_water_consumption(system_config, step):
    """
    Convertit le champ 'water_consumption' en série de N créneaux (liste de litres)
    step : durée d'un créneau en minutes
    """
    N = 24 * 60 // step
    water_conso = [0] * N  # Valeur par défaut

    if not system_config:
        return water_conso

    water_data = system_config.get('water_consumption')
    if not water_data:
        return water_conso

    # Si JSON stocké en string
    if isinstance(water_data, str):
        try:
            water_data = json.loads(water_data)
        except Exception:
            return water_conso

    # Si dictionnaire avec clé 'distribution'
    if isinstance(water_data, dict) and 'distribution' in water_data:
        distribution = water_data['distribution']
        # Générer la série à partir des heures et litres
        for entry in distribution:
            hour = entry.get('hour', 0)
            liters = entry.get('liters', 0)
            start_idx = int(hour * 60 / step)
            end_idx = int((hour + 1) * 60 / step)
            for i in range(start_idx, min(end_idx, N)):
                water_conso[i] += liters / (end_idx - start_idx)  # répartition uniforme sur le créneau

    # Si c'est déjà une liste de valeurs
    elif isinstance(water_data, list):
        water_conso = distribution_to_series(water_data, step)

    return water_conso


def distribution_to_series(distribution, step_min):
        N = 24 * 60 // step_min
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


def parse_comfort_schedule(system_config, N):
    """Convertit un dict {heure: température} ou une chaîne JSON en liste de N températures"""
    
    minimum_temp = float(system_config.get('minimum_comfort_temperature', 50.0))
    comfort_dict = system_config.get('comfort_schedule', {})
    

    if isinstance(comfort_dict, str):
        try:
            comfort_dict = json.loads(comfort_dict)
        except Exception as e:
            print(f"⚠️ Erreur de parsing JSON comfort_schedule: {e}")
            comfort_dict = {}
    
    comfort_schedule = [minimum_temp] * N
    
    if not comfort_dict:
        return comfort_schedule


    comfort_dict = {int(k): float(v) for k, v in comfort_dict.items() if str(k).isdigit()}

    if N == 24:
        for hour in range(24):
            if hour in comfort_dict:
                comfort_schedule[hour] = comfort_dict[hour]
    else:
        # mapper les créneaux aux heures
        step_min = 60 // (N // 24)
        for i in range(N):
            hour = (i * step_min) // 60
            if hour in comfort_dict:
                comfort_schedule[i] = comfort_dict[hour]
    
    return comfort_schedule

import json
import matplotlib.pyplot as plt
import numpy as np
def verif(data, metrics,T_values, u_values=None,):
    """
    Trace un tableau et un graphique pour comprendre la décision MILP.
    data : dictionnaire complet du client (config + CE + eau + confort)
    metrics : dictionnaire retourné par calculate_detailed_metrics
    u_values : liste des décisions (0/1) du MILP (optionnel si dans metrics)
    """



    # --- Paramètres physiques ---
    step_min = int(data.get("step_min", 15))
    dt_h = step_min / 60
    P_nom = float(data.get("water_heater", {}).get("puissance_kw", 3.0)) * 1000
    volume_L = int(data.get("water_heater", {}).get("capacite_litres", 200))
    UA = 1.5
    T_ambient = 20.0
    T_cold = float(data.get("cold_water_temperature", 15.0))
    client_id = data.get("client_id", "?")

    # --- Récupérer u_values ---
    if u_values is None:
        u_values = metrics.get("u_values", [])
    
    if not u_values:
        print(" Aucune décision u_values fournie !")
        u_values = [0] * 96  # Valeur par défaut

    N = len(u_values)  # Nombre de créneaux réels

    # --- Consommation d'eau (adapter à N) ---
    water_cons_raw = data.get("water_consumption", [])
    if not isinstance(water_cons_raw, list) or len(water_cons_raw) != N:
        # Si water_cons n'a pas la bonne taille, répéter ou interpoler
        if len(water_cons_raw) == 24:  # Si données horaires
            water_cons = np.repeat(water_cons_raw, N // 24).tolist()
        else:
            water_cons = [0.0] * N
    else:
        water_cons = water_cons_raw

    # --- Confort (adapter à N) ---
    comfort_schedule_raw = data.get("comfort_schedule", [])
    if not isinstance(comfort_schedule_raw, list):
        # Si c'est un dict ou string JSON
        if isinstance(comfort_schedule_raw, str):
            try:
                comfort_schedule_raw = json.loads(comfort_schedule_raw)
            except:
                comfort_schedule_raw = {}
        
        if isinstance(comfort_schedule_raw, dict):
            # Convertir dict {heure: temp} en liste de 24
            tmp = [float(data.get("minimum_comfort_temperature", 50.0))] * 24
            for k, v in comfort_schedule_raw.items():
                if str(k).isdigit() and int(k) < 24:
                    tmp[int(k)] = float(v)
            comfort_schedule_raw = tmp
    
    # Adapter à la taille N
    if len(comfort_schedule_raw) == 24 and N != 24:
        comfort_schedule = np.repeat(comfort_schedule_raw, N // 24).tolist()
    elif len(comfort_schedule_raw) != N:
        comfort_schedule = [float(data.get("minimum_comfort_temperature", 50.0))] * N
    else:
        comfort_schedule = comfort_schedule_raw

    # --- Calculs physiques ---
    heating_kw = []
    loss_kw = []
    cooling_kw = []
    comfort_gap = []

    for k in range(N):
        u = u_values[k]
        T = T_values[k]
        wc = water_cons[k]
        target = comfort_schedule[k]
        
        heat = u * P_nom / 1000
        loss = UA * (T - T_ambient) / 1000
        cool = (wc / volume_L) * (T - T_cold) if wc > 0 and volume_L > 0 else 0
        gap = T - target

        heating_kw.append(heat)
        loss_kw.append(loss)
        cooling_kw.append(cool)
        comfort_gap.append(gap)

    # --- Affichage console ---
    print(f"\n{'═'*100}")
    print(f"CLIENT {client_id} - TABLEAU DE BORD MILP (N={N}, step={step_min}min)")
    print(f"{'═'*100}")
    print(f"{'Pas':>4} | {'u':>2} | {'T(°C)':>7} | {'Cible':>7} | {'Écart':>7} | {'Eau(L)':>7} | {'Chauffe(kW)':>11} | {'Perte(kW)':>10} | {'Refroid(kW)':>11}")
    print(f"{'─'*100}")
    
    for k in range(N):
        print(f"{k:>4} | {u_values[k]:>2} | {T_values[k]:>7.2f} | {comfort_schedule[k]:>7.2f} | {comfort_gap[k]:>7.2f} | {water_cons[k]:>7.2f} | {heating_kw[k]:>11.2f} | {loss_kw[k]:>10.2f} | {cooling_kw[k]:>11.2f}")

    # --- Métriques résumées ---
    print(f"\n{'═'*100}")
    print("MÉTRIQUES CLÉS :")
    print(f"  • Violations confort : {sum(1 for g in comfort_gap if g < -0.1)} / {N}")
    print(f"  • Énergie totale : {sum(heating_kw) * dt_h:.2f} kWh")
    print(f"  • Temps de chauffe : {sum(u_values) * dt_h:.2f} h ({sum(u_values)} créneaux)")
    print(f"  • Température moyenne : {np.mean(T_values):.2f}°C (min={min(T_values):.2f}°, max={max(T_values):.2f}°)")
    print(f"{'═'*100}\n")

    # --- Graphique ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
    
    # Axe 1 : Décision et températures
    ax1.step(range(N), u_values, where='post', label="Décision chauffe (u)", color='blue', linewidth=2)
    ax1.plot(T_values[:N], label="Température eau (°C)", color='orange', linewidth=2)
    ax1.plot(comfort_schedule, label="Consigne confort (°C)", linestyle='--', color='green', linewidth=1.5)
    ax1.fill_between(range(N), 
                     comfort_schedule, 
                     [min(T_cold, 50)] * N,  # Zone sous la consigne
                     alpha=0.2, color='red', label='Zone de violation')
    ax1.set_ylabel("Température / Décision")
    ax1.set_title(f"MILP Water Heater Debug - Client {client_id} (Step={step_min}min)")
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 80)

    # Axe 2 : Écarts et consommation
    ax2.bar(range(N), water_cons, label="Consommation eau (L)", color='cyan', alpha=0.6)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(comfort_gap, label="Écart confort (T - cible)", color='red', linewidth=2)
    ax2.set_xlabel("Créneau (step)")
    ax2.set_ylabel("Consommation eau (L)")
    ax2_twin.set_ylabel("Écart (°C)")
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()