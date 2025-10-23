import pulp

def optimise(ctx):
    step_min = int(ctx["step_min"])
    horizon_h = int(ctx["horizon_h"])
    N = horizon_h * 60 // step_min

    water_heater = ctx["water_heater"]
    P_nom = float(water_heater["puissance_kw"]) * 1000
    volume_L = int(water_heater["capacite_litres"])
    UA = 9.0

    min_temp_enabled = ctx.get("minimum_comfort_temperature_enabled", False)
    min_temp_value = float(ctx.get("minimum_comfort_temperature", 50.0))
    comfort_sched = ctx.get("comfort_schedule", [])
    
    pv_series = [float(p) for p in ctx["pv_production"]]
    tariffs = ctx["tariffs"]
    t0 = float(ctx["t0"])

    # Créer le problème avec PuLP
    prob = pulp.LpProblem("WaterHeaterOptimization", pulp.LpMinimize)
    
    # Variables
    u = [pulp.LpVariable(f"u_{k}", cat='Binary') for k in range(N)]
    T = [pulp.LpVariable(f"T_{k}", lowBound=0, upBound=100) for k in range(N + 1)]
    
    # Contraintes de température (simplifiées)
    prob += T[0] == t0  # Température initiale
    
    # Coût (simplifié)
    cost_expr = 0
    for k in range(N):
        # Coût basé sur la consommation et production PV
        cost_expr += u[k] * tariffs["tariffs_eur_per_kwh"]["base"] * (P_nom/1000) * (step_min/60)
    
    prob += cost_expr
    
    # Résoudre
    prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=10))
    
    if prob.status == pulp.LpStatusOptimal:
        return [int(pulp.value(var)) for var in u]
    else:
        # Fallback
        on_slots = 60 // step_min
        return [1] * on_slots + [0] * (N - on_slots)