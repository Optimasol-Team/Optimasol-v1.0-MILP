import numpy as np

def simulate_classic_water_heater_midi(ctx, maintenance_temp=65.0):
    """
    Simule un chauffe-eau classique avec heures creuses en journée :
    - Chauffe à fond pendant les heures creuses de midi (12h-14h) jusqu'à 65°C
    - Maintient la température à 65°C le reste du temps
    - Utilise l'énergie PV disponible mais ne vend pas le surplus
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
    C = volume_L * 418
    u_values = [0] * N
    T_values = [t0] + [0] * N
    

    pv_used_for_heating = 0
    grid_energy_hp = 0
    grid_energy_hc = 0
    
    for k in range(N):
        hour = (k * step_min / 60) % 24
        
       
        is_midday_off_peak = 12 <= hour < 14
        
        if is_midday_off_peak:
            # Créneaux midi : chauffe tant qu'on n'a pas atteint 65°C
            if T_values[k] < maintenance_temp:
                u_values[k] = 1
            else:
                u_values[k] = 0
        else:
            # Hors créneaux midi : maintient à 65°C avec hystérésis cde 2°
            if T_values[k] < maintenance_temp - 2: 
                u_values[k] = 1
            else:
                u_values[k] = 0
        
        energy_needed_kwh = u_values[k] * (P_nom/1000) * (step_min/60)
        pv_available_kwh = ctx["pv_production"][k] * (step_min/60) if k < len(ctx["pv_production"]) else 0
        pv_used_kwh = min(pv_available_kwh, energy_needed_kwh) if u_values[k] == 1 else 0
        pv_used_for_heating += pv_used_kwh
        grid_energy_kwh = max(0, energy_needed_kwh - pv_used_kwh)
        
        # Répartition HP/HC pour l'énergie réseau
        if grid_energy_kwh > 0:
            if is_midday_off_peak:
                grid_energy_hc += grid_energy_kwh
            else:
                grid_energy_hp += grid_energy_kwh
        
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
    metrics = calculate_classic_metrics_midi(u_values, T_values, ctx, pv_used_for_heating, grid_energy_hp, grid_energy_hc)
    metrics["maintenance_temp"] = maintenance_temp
    return True, u_values, T_values, metrics

def calculate_classic_metrics_midi(u_values, T_values, ctx, pv_used_for_heating, grid_energy_hp, grid_energy_hc):
    """Calcule les métriques pour le système classique avec heures creuses de midi"""
    step_min = int(ctx["step_min"])
    P_nom = float(ctx["water_heater"]["puissance_kw"]) * 1000
    
    total_on_slots = sum(u_values)
    total_on_time = total_on_slots * (step_min / 60)
    total_energy = total_on_slots * (P_nom/1000) * (step_min/60)
    
    # Calcul des coûts
    cost_hp = grid_energy_hp * ctx["tariffs"]["tariffs_eur_per_kwh"]["hp"]
    cost_hc = grid_energy_hc * ctx["tariffs"]["tariffs_eur_per_kwh"]["hc"]
    total_cost = cost_hp + cost_hc
    
    # Autres 
    T_min = min(T_values)
    T_max = max(T_values)
    T_avg = np.mean(T_values)
    
    # Calcul autoconsommation
    pv_energy_total = sum(ctx["pv_production"]) * (step_min/60) if ctx["pv_production"] else 0
    self_consumption_rate = (pv_used_for_heating / total_energy * 100) if total_energy > 0 else 0
    pv_utilization_rate = (pv_used_for_heating / pv_energy_total * 100) if pv_energy_total > 0 else 0
    
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
        "energy_hp_kwh": grid_energy_hp,
        "energy_hc_kwh": grid_energy_hc,
        "cost_hp_eur": cost_hp,
        "cost_hc_eur": cost_hc,
        "temperature_min": T_min,
        "temperature_max": T_max,
        "temperature_avg": T_avg,
        "comfort_violations": comfort_violations,
        "avg_comfort_margin": avg_comfort_margin,
        "pv_used_for_heating_kwh": pv_used_for_heating,
        "grid_energy_used_kwh": grid_energy_hp + grid_energy_hc,
        "self_consumption_rate": self_consumption_rate,
        "pv_utilization_rate": pv_utilization_rate,
        "system_type": "Classique Midi (12h-14h)"
    }