#milp_solver.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pulp, numpy as np
from .cost import add_cost_expression, price_for_slot
from datetime import datetime, timedelta

def milp_analysis(ctx):
    step_min = int(ctx["step_min"])

    N = 24 * 60 // step_min
    optimization_start = ctx.get("optimization_start_time", datetime.now())
    start_aligned = optimization_start.replace(second=0, microsecond=0)
    start_aligned -= timedelta(minutes=start_aligned.minute % step_min)

    P_nom = float(ctx["water_heater"]["puissance_kw"]) * 1000
    volume_L = int(ctx["water_heater"]["capacite_litres"])
    t0 = float(ctx["t0"])
    prob = pulp.LpProblem("WaterHeater_Cost_Optimization", pulp.LpMinimize)
    u = [pulp.LpVariable(f"u_{k}", cat='Binary') for k in range(N)]
    T = [pulp.LpVariable(f"T_{k}", lowBound=0, upBound=80) for k in range(N + 1)]
    UA = 1.5
    T_ambient = ctx.get("ambient_temperature", 20.0)
    T_cold = ctx.get("cold_water_temperature", 15.0)
    C = volume_L * 4180
    prob += T[0] == t0
    

    comfort_schedule = generate_comfort_schedule_for_horizon(ctx, start_aligned, N, step_min)

    for k in range(N):
        heating_energy = (u[k] * P_nom * step_min * 60) / C
        heat_loss = (UA * (T[k] - T_ambient) * step_min * 60) / C
        wc = ctx["water_consumption"][k] if k < len(ctx["water_consumption"]) else 0
        cooling_effect = (wc / volume_L) * (T[k] - T_cold) if wc > 0 else 0
        prob += T[k + 1] == T[k] + heating_energy - heat_loss - cooling_effect

        min_temp = comfort_schedule[k] if k < len(comfort_schedule) else ctx.get("minimum_comfort_temperature", 50.0)
        prob += T[k + 1] >= min_temp

    add_cost_expression(
        prob, u,
        pv_series=ctx["pv_production"],
        tariffs=ctx["tariffs"],
        P_nom=P_nom,
        step_min=step_min,
        optimization_start=start_aligned  
    )
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=30))

    if prob.status == pulp.LpStatusOptimal:
        u_values = [int(pulp.value(var)) for var in u]
        T_values = [float(pulp.value(var)) for var in T]
        metrics = calculate_detailed_metrics(u_values, T_values, ctx, start_aligned, prob) 
        return True, u_values, T_values, metrics
    else:
        print(f"❌ Échec: {pulp.LpStatus[prob.status]}")
        return False, None, None, None
def generate_comfort_schedule_for_horizon(ctx, start_time, N, step_min):
    raw_schedule = ctx.get("comfort_schedule", [])
    if not raw_schedule:
        return [ctx.get("minimum_comfort_temperature", 50.0)] * N
    
    raw_len = len(raw_schedule)
    start_index = (start_time.hour * 60 + start_time.minute) // step_min
    start_index = start_index % raw_len
    
    # Répéter le schedule pour couvrir N créneaux
    shifted = raw_schedule[start_index:] + raw_schedule[:start_index]
    full_schedule = (shifted * (N // len(shifted) + 1))[:N]
    
    return full_schedule

def calculate_detailed_metrics(u_values, T_values, ctx, start_aligned, prob=None):
    """Calcule les métriques détaillées en cohérence avec le modèle MILP"""
    N = len(u_values)
    step_min = int(ctx["step_min"])
    P_nom = float(ctx["water_heater"]["puissance_kw"]) * 1000
    dt_h = step_min / 60

    
    total_on_slots = sum(u_values)
    total_on_time = total_on_slots * dt_h
    total_energy = total_on_slots * (P_nom / 1000) * dt_h
    
  
    energy_hp = energy_hc = cost_hp = cost_hc = 0
    pv_used_for_heating = 0
    grid_energy_used = 0

   
    if prob is not None and prob.status == pulp.LpStatusOptimal:
        try:
            buy_vars = [prob.variablesDict().get(f"buy_{k}") for k in range(len(u_values))]
            sell_vars = [prob.variablesDict().get(f"sell_{k}") for k in range(len(u_values))]
            
            for k, u_val in enumerate(u_values):
                if u_val == 1 and buy_vars[k] is not None and sell_vars[k] is not None:
                    buy_val = pulp.value(buy_vars[k])
                    sell_val = pulp.value(sell_vars[k])
                    
                   
                    pv_used = ctx["pv_production"][k] * dt_h - sell_val if k < len(ctx["pv_production"]) else 0
                    grid_used = buy_val
                    
                    pv_used_for_heating += pv_used
                    grid_energy_used += grid_used

                   
                    slot_center = start_aligned + timedelta(minutes=step_min * (k + 0.5))

                    price = price_for_slot(slot_center, ctx["tariffs"])

                    hc_price = ctx["tariffs"]["tariffs_eur_per_kwh"].get("hc", 0.18)
                    if abs(price - hc_price) < 0.01:
                        energy_hc += grid_used
                        cost_hc += grid_used * price
                    else:
                        energy_hp += grid_used
                        cost_hp += grid_used * price
                        
        except (KeyError, AttributeError):
            # Fallback si problème avec les variables MILP
            prob = None

    # Fallback : calcul approximatif (pour démo ou erreur MILP)
    if prob is None:
        for k, u_val in enumerate(u_values):
            if u_val == 1:
                energy_needed = (P_nom / 1000) * dt_h
                pv_available = ctx["pv_production"][k] * dt_h if k < len(ctx["pv_production"]) else 0
                
                pv_used = min(pv_available, energy_needed)
                grid_used = energy_needed
                
                pv_used_for_heating += pv_used
                grid_energy_used += grid_used

               
                slot_center = start_aligned + timedelta(minutes=step_min * (k + 0.5))
                price = price_for_slot(slot_center, ctx["tariffs"])
                
                hc_price = ctx["tariffs"]["tariffs_eur_per_kwh"].get("hc", 0.18)
                if abs(price - hc_price) < 0.01:
                    energy_hc += grid_used
                    cost_hc += grid_used * price
                else:
                    energy_hp += grid_used
                    cost_hp += grid_used * price

    total_cost = cost_hp + cost_hc

   
    pv_energy_total = sum(ctx["pv_production"][:len(u_values)]) * dt_h if ctx["pv_production"] else 0
    self_consumption_rate = (pv_used_for_heating / total_energy * 100) if total_energy > 0 else 0
    pv_utilization_rate = (pv_used_for_heating / pv_energy_total * 100) if pv_energy_total > 0 else 0

  
    T_min = min(T_values)
    T_max = max(T_values)
    T_avg = np.mean(T_values)


    comfort_schedule = generate_comfort_schedule_for_horizon(ctx, start_aligned, len(T_values)-1, step_min)
    
    comfort_violations = 0
    comfort_margins = []

    for k, T in enumerate(T_values):
        if k < len(comfort_schedule):
            target = comfort_schedule[k]
            comfort_margins.append(T - target)
            if T < target:
                comfort_violations += 1

    avg_margin = np.mean(comfort_margins) if comfort_margins else 0
    comfort_schedule = generate_comfort_schedule_for_horizon(ctx, start_aligned, N, step_min)
    return {
        "confort_schedule": comfort_schedule,
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
        "pv_energy_total_kwh": pv_energy_total,
        "pv_used_for_heating_kwh": pv_used_for_heating,
        "grid_energy_used_kwh": grid_energy_used,
        "self_consumption_rate": self_consumption_rate,
        "pv_utilization_rate": pv_utilization_rate,
        "comfort_violations": comfort_violations,
        "avg_comfort_margin": avg_margin,
    }