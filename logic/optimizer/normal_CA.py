import numpy as np

def simulate_classic_water_heater(ctx, maintenance_temp=65.0):
    """
    Simule un chauffe-eau classique avec ballon tampon :
    - Chauffe à fond pendant les heures creuses jusqu'à 65°C
    - Maintient la température à 65°C le reste du temps
    """
    step_min = int(ctx["step_min"])
    horizon_h = int(ctx["horizon_h"])
    N = horizon_h * 60 // step_min
    P_nom = float(ctx["water_heater"]["puissance_kw"]) * 1000
    volume_L = int(ctx["water_heater"]["capacite_litres"])
    t0 = float(ctx["t0"])
    UA = 1.5
    T_ambient = ctx.get("ambient_temperature", 20.0)
    T_cold = ctx.get("cold_water_temperature", 15.0)
    C = volume_L * 4180
    u_values = [0] * N
    T_values = [t0] + [0] * N
    target_maintenance = maintenance_temp
    
    for k in range(N):
        hour = (k * step_min / 60) % 24
        is_off_peak = False
        for off_peak in ctx["tariffs"]["off_peak_hours"]:
            start_h = int(off_peak["start"][:2])
            end_h = int(off_peak["end"][:2])
            if start_h <= hour < end_h or (start_h > end_h and (hour >= start_h or hour < end_h)):
                is_off_peak = True
                break
        
        # LOGIQUE CLASSIQUE :
        # 1. En heure creuse : chauffe à fond jusqu'à 65°C
        # 2. En heure pleine : maintient à 65°C si besoin
        if is_off_peak:
            if T_values[k] < target_maintenance:
                u_values[k] = 1
            else:
                u_values[k] = 0
        else:
            # Heures pleines : maintient à 65°C avec hystérésis
            if T_values[k] < target_maintenance - 2:  # Hystérésis de 2°C
                u_values[k] = 1
            else:
                u_values[k] = 0
        

        heating_energy = (u_values[k] * P_nom * step_min * 60) / C
        heat_loss = (UA * (T_values[k] - T_ambient) * step_min * 60) / C
        
        water_consumed = ctx["water_consumption"][k] if k < len(ctx["water_consumption"]) else 0
        if water_consumed > 0:
            cooling_effect = (water_consumed / volume_L) * (T_values[k] - T_cold)
        else:
            cooling_effect = 0
        
        T_values[k+1] = T_values[k] + heating_energy - heat_loss - cooling_effect
        T_values[k+1] = max(0, min(80, T_values[k+1]))  # Bornes de sécurité
    
    # Calcul des métriques pour le système classique
    metrics = calculate_classic_metrics(u_values, T_values, ctx)
    metrics["maintenance_temp"] = maintenance_temp
    return True, u_values, T_values, metrics

def calculate_classic_metrics(u_values, T_values, ctx):
    """Calcule les métriques pour le système classique"""
    step_min = int(ctx["step_min"])
    P_nom = float(ctx["water_heater"]["puissance_kw"]) * 1000
    
    total_on_slots = sum(u_values)
    total_on_time = total_on_slots * (step_min / 60)
    total_energy = total_on_slots * (P_nom/1000) * (step_min/60)
    
    total_cost = 0
    energy_hp = 0
    energy_hc = 0
    cost_hp = 0
    cost_hc = 0
    
    for k, u_val in enumerate(u_values):
        if u_val == 1:
            hour = (k * step_min / 60) % 24
            energy_slot = (P_nom/1000) * (step_min/60)
            
            # Déterminer tarif
            is_off_peak = False
            for off_peak in ctx["tariffs"]["off_peak_hours"]:
                start_h = int(off_peak["start"][:2])
                end_h = int(off_peak["end"][:2])
                if start_h <= hour < end_h or (start_h > end_h and (hour >= start_h or hour < end_h)):
                    is_off_peak = True
                    break
            
            if is_off_peak:
                energy_hc += energy_slot
                cost_hc += energy_slot * ctx["tariffs"]["tariffs_eur_per_kwh"]["hc"]
            else:
                energy_hp += energy_slot
                cost_hp += energy_slot * ctx["tariffs"]["tariffs_eur_per_kwh"]["hp"]
    
    total_cost = cost_hp + cost_hc
    
    # Autres métriques
    T_min = min(T_values)
    T_max = max(T_values)
    T_avg = np.mean(T_values)
    
    # Pour le système classique, on vérifie le maintien à 65°C
    maintenance_temp = 65.0
    maintenance_violations = sum(1 for T in T_values if T < maintenance_temp - 3)  # -3°C de tolérance
    
    comfort_schedule = ctx.get("comfort_schedule", [50.0] * len(T_values))
    comfort_violations = 0
    comfort_margins = []
    
    for k, T in enumerate(T_values):
        if k < len(comfort_schedule):
            target_temp = comfort_schedule[k]
            comfort_margins.append(T - target_temp)
            if T < target_temp:
                comfort_violations += 1
    
    avg_comfort_margin = np.mean(comfort_margins) if comfort_margins else 0
    
    return {
        "total_energy_kwh": total_energy,
        "total_cost_eur": total_cost,
        "total_on_time_h": total_on_time,
        "energy_hp_kwh": energy_hp,
        "energy_hc_kwh": energy_hc,
        "cost_hp_eur": cost_hp,
        "cost_hc_eur": cost_hc,
        "temperature_min": T_min,
        "temperature_max": T_max,
        "temperature_avg": T_avg,
        "comfort_violations": comfort_violations,
        "maintenance_violations": maintenance_violations,
        "avg_comfort_margin": avg_comfort_margin,
        "system_type": "Classique (65°C constante)"
    }
def calculate_classic_metrics(u_values, T_values, ctx):
    """Calcule les métriques pour le système classique"""
    step_min = int(ctx["step_min"])
    P_nom = float(ctx["water_heater"]["puissance_kw"]) * 1000
    
    total_on_slots = sum(u_values)
    total_on_time = total_on_slots * (step_min / 60)
    total_energy = total_on_slots * (P_nom/1000) * (step_min/60)
    
    # Calcul du coût
    total_cost = 0
    energy_hp = 0
    energy_hc = 0
    cost_hp = 0
    cost_hc = 0
    
    for k, u_val in enumerate(u_values):
        if u_val == 1:
            hour = (k * step_min / 60) % 24
            energy_slot = (P_nom/1000) * (step_min/60)
            
            # Déterminer tarif
            is_off_peak = False
            for off_peak in ctx["tariffs"]["off_peak_hours"]:
                start_h = int(off_peak["start"][:2])
                end_h = int(off_peak["end"][:2])
                if start_h <= hour < end_h or (start_h > end_h and (hour >= start_h or hour < end_h)):
                    is_off_peak = True
                    break
            
            if is_off_peak:
                energy_hc += energy_slot
                cost_hc += energy_slot * ctx["tariffs"]["tariffs_eur_per_kwh"]["hc"]
            else:
                energy_hp += energy_slot
                cost_hp += energy_slot * ctx["tariffs"]["tariffs_eur_per_kwh"]["hp"]
    
    total_cost = cost_hp + cost_hc
    
    # Autres métriques
    T_min = min(T_values)
    T_max = max(T_values)
    T_avg = np.mean(T_values)
    
    comfort_schedule = ctx.get("comfort_schedule", [50.0] * len(T_values))
    comfort_violations = 0
    comfort_margins = []
    
    for k, T in enumerate(T_values):
        if k < len(comfort_schedule):
            target_temp = comfort_schedule[k]
            comfort_margins.append(T - target_temp)
            if T < target_temp:
                comfort_violations += 1
    
    avg_comfort_margin = np.mean(comfort_margins) if comfort_margins else 0
    
    return {
        "total_energy_kwh": total_energy,
        "total_cost_eur": total_cost,
        "total_on_time_h": total_on_time,
        "energy_hp_kwh": energy_hp,
        "energy_hc_kwh": energy_hc,
        "cost_hp_eur": cost_hp,
        "cost_hc_eur": cost_hc,
        "temperature_min": T_min,
        "temperature_max": T_max,
        "temperature_avg": T_avg,
        "comfort_violations": comfort_violations,
        "avg_comfort_margin": avg_comfort_margin,
        "system_type": "Classique"
    }