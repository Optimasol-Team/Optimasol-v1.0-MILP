import pulp, numpy as np
from cost import add_cost_expression

def milp_analysis(ctx):
    step_min = int(ctx["step_min"])
    horizon_h = int(ctx["horizon_h"])
    N = horizon_h * 60 // step_min
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
    comfort_schedule = ctx.get("comfort_schedule", [ctx.get("minimum_comfort_temperature", 50.0)] * N)

    for k in range(N):
        heating_energy = (u[k] * P_nom * step_min * 60) / C
        heat_loss = (UA * (T[k] - T_ambient) * step_min * 60) / C
        wc = ctx["water_consumption"][k] if k < len(ctx["water_consumption"]) else 0
        cooling_effect = (wc / volume_L) * (T[k] - T_cold) if wc > 0 else 0
        prob += T[k + 1] == T[k] + heating_energy - heat_loss - cooling_effect

        if ctx.get("minimum_comfort_temperature_enabled", False):
            min_temp = comfort_schedule[k] if k < len(comfort_schedule) else ctx.get("minimum_comfort_temperature", 50.0)
            prob += T[k + 1] >= min_temp

    add_cost_expression(
        prob, u,
        pv_series=ctx["pv_production"],
        tariffs=ctx["tariffs"],
        P_nom=P_nom,
        step_min=step_min
    )

    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=30))

    if prob.status == pulp.LpStatusOptimal:
        u_values = [int(pulp.value(var)) for var in u]
        T_values = [float(pulp.value(var)) for var in T]
        metrics = calculate_detailed_metrics(u_values, T_values, ctx, prob)
        return True, u_values, T_values, metrics
    else:
        print(f"❌ Échec: {pulp.LpStatus[prob.status]}")
        return False, None, None, None


def calculate_detailed_metrics(u_values, T_values, ctx, prob):
    step_min = int(ctx["step_min"])
    P_nom = float(ctx["water_heater"]["puissance_kw"]) * 1000

    total_on_slots = sum(u_values)
    total_on_time = total_on_slots * (step_min / 60)
    total_energy = total_on_slots * (P_nom / 1000) * (step_min / 60)
    total_cost = 0
    energy_hp = energy_hc = cost_hp = cost_hc = 0
    pv_used_for_heating = grid_energy_used = 0
    dt_h = step_min / 60

    for k, u_val in enumerate(u_values):
        if u_val == 1:
            energy_needed = (P_nom / 1000) * dt_h
            pv_available = ctx["pv_production"][k] * dt_h
            pv_used = min(pv_available, energy_needed)
            pv_used_for_heating += pv_used
            grid_used = max(0, energy_needed - pv_used)
            grid_energy_used += grid_used

            from cost import _price_for_slot
            from datetime import datetime, timedelta

            now = datetime.now().replace(second=0, microsecond=0)
            now -= timedelta(minutes=now.minute % step_min)
            slot_center = now + timedelta(minutes=step_min * (k + 0.5))
            price = _price_for_slot(slot_center, ctx["tariffs"])

            hc_price = ctx["tariffs"]["tariffs_eur_per_kwh"].get("hc", 0.18)
            if abs(price - hc_price) < 0.01:
                energy_hc += grid_used
                cost_hc += grid_used * price
            else:
                energy_hp += grid_used
                cost_hp += grid_used * price

    total_cost = cost_hp + cost_hc
    pv_series = ctx["pv_production"]
    pv_energy_total = sum(pv_series) * dt_h
    self_consumption_rate = (pv_used_for_heating / total_energy * 100) if total_energy > 0 else 0
    pv_utilization_rate = (pv_used_for_heating / pv_energy_total * 100) if pv_energy_total > 0 else 0
    pv_energy_total = sum(pv_series) * (step_min / 60) * (P_nom / 1000)
    pv_used_for_heating = 0

    for k in range(len(u_values)):
        if u_values[k] == 1 and pv_series[k] > 0:
            pv_used = min(pv_series[k] * (step_min / 60), (P_nom / 1000) * (step_min / 60))
            pv_used_for_heating += pv_used

    self_consumption_rate = (pv_used_for_heating / total_energy * 100) if total_energy > 0 else 0
    pv_utilization_rate = (pv_used_for_heating / pv_energy_total * 100) if pv_energy_total > 0 else 0

    energy_hp = energy_hc = 0
    for k, u_val in enumerate(u_values):
        if u_val == 1:
            from cost import _price_for_slot
            from datetime import datetime, timedelta

            now = datetime.now().replace(second=0, microsecond=0)
            now -= timedelta(minutes=now.minute % step_min)
            slot_center = now + timedelta(minutes=step_min * (k + 0.5))
            price = _price_for_slot(slot_center, ctx["tariffs"])

            energy_slot = (P_nom / 1000) * (step_min / 60)
            hc_price = ctx["tariffs"]["tariffs_eur_per_kwh"].get("hc", 0.18)
            if abs(price - hc_price) < 0.01:
                energy_hc += energy_slot
            else:
                energy_hp += energy_slot

    cost_hp = energy_hp * ctx["tariffs"]["tariffs_eur_per_kwh"]["hp"]
    cost_hc = energy_hc * ctx["tariffs"]["tariffs_eur_per_kwh"]["hc"]
    T_min = min(T_values)
    T_max = max(T_values)
    T_avg = np.mean(T_values)
    comfort_schedule = ctx.get("comfort_schedule", [ctx.get("minimum_comfort_temperature", 50.0)] * len(T_values))
    comfort_violations = 0
    comfort_margins = []

    for k, T in enumerate(T_values):
        if k < len(comfort_schedule):
            target = comfort_schedule[k]
            comfort_margins.append(T - target)
            if T < target:
                comfort_violations += 1

    avg_margin = np.mean(comfort_margins) if comfort_margins else 0

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
        "pv_energy_total_kwh": pv_energy_total,
        "pv_used_for_heating_kwh": pv_used_for_heating,
        "self_consumption_rate": self_consumption_rate,
        "pv_utilization_rate": pv_utilization_rate,
        "comfort_violations": comfort_violations,
        "avg_comfort_margin": avg_margin,
    }
