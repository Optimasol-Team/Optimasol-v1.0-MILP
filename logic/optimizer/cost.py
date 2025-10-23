from datetime import datetime, timedelta, time
from ortools.linear_solver import pywraplp

def _price_for_slot(slot_center, tariffs):
    base = tariffs["tariffs_eur_per_kwh"].get("base", tariffs["tariffs_eur_per_kwh"]["hp"])
    if tariffs.get("contract_type") != "HPHC":
        return base
    hp = tariffs["tariffs_eur_per_kwh"]["hp"]
    hc = tariffs["tariffs_eur_per_kwh"]["hc"]
    w = tariffs["off_peak_hours"][0]
    start = time.fromisoformat(w["start"])
    end = time.fromisoformat(w["end"])
    in_hc = start <= slot_center.time() or slot_center.time() < end
    return hc if in_hc else hp

def add_cost_expression(solver, u_vars, *, pv_series, tariffs, P_nom, step_min, price_sell=None):
    N = len(u_vars)
    dt_h = step_min / 60
    heat_coeff = (P_nom / 1000) * dt_h
    price_sell = price_sell or tariffs["tariffs_eur_per_kwh"].get("sell", 0.10)
    now_aligned = datetime.now().replace(second=0, microsecond=0)
    now_aligned -= timedelta(minutes=now_aligned.minute % step_min)
    total_cost = solver.NumVar(0, solver.infinity(), "total_cost")
    expr = []
    for k, u_k in enumerate(u_vars):
        heat_kWh = heat_coeff * u_k
        pv_kWh = pv_series[k]
        buy_k = solver.NumVar(0, solver.infinity(), f"buy_{k}")
        sell_k = solver.NumVar(0, solver.infinity(), f"sell_{k}")
        solver.Add(buy_k - sell_k == heat_kWh - pv_kWh)
        slot_center = now_aligned + timedelta(minutes=step_min * (k + 0.5))
        price_buy = _price_for_slot(slot_center, tariffs)
        expr.append(price_buy * buy_k - price_sell * sell_k)
    solver.Add(total_cost == solver.Sum(expr))
    solver.Minimize(total_cost)