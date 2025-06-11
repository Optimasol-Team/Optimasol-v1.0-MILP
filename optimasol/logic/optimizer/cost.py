# logic/optimizer/cost.py
# ------------------------------------------------------------------
# Linear cost expression: buy_k ≥ 0, sell_k ≥ 0
# buy_k - sell_k = heat_kWh - PV_kWh
# Objective = Σ (buy_k·price_buy  -  sell_k·price_sell)
# ------------------------------------------------------------------

from datetime import datetime, timedelta, time
from ortools.linear_solver import pywraplp  # type: ignore


def _price_for_slot(slot_center: datetime, tariffs: dict) -> float:
    """
    Return €/kWh for the slot center depending on HC/HP windows.
    Fallback: use 'base' if contract is not HPHC.
    """
    base = tariffs["tariffs_eur_per_kwh"].get("base",
                                              tariffs["tariffs_eur_per_kwh"]["hp"])
    if tariffs.get("contract_type") != "HPHC":
        return base

    hp = tariffs["tariffs_eur_per_kwh"]["hp"]
    hc = tariffs["tariffs_eur_per_kwh"]["hc"]

    # only one off-peak window assumed
    w = tariffs["off_peak_hours"][0]
    start = time.fromisoformat(w["start"])
    end   = time.fromisoformat(w["end"])

    in_hc = start <= slot_center.time() or slot_center.time() < end
    return hc if in_hc else hp


def add_cost_expression(
    solver,
    u_vars,
    *,
    pv_series,
    tariffs,
    P_nom: float,
    step_min: int,
    price_sell: float | None = None,
):
    """Add objective function to solver."""
    N = len(u_vars)
    dt_h = step_min / 60
    heat_coeff = (P_nom / 1000) * dt_h  # kWh when u_k == 1

    # default selling price: same as feed-in tariff in data.json
    price_sell = price_sell or tariffs["tariffs_eur_per_kwh"].get("sell", 0.10)

    now_aligned = datetime.now().replace(second=0, microsecond=0)
    now_aligned -= timedelta(minutes=now_aligned.minute % step_min)

    total_cost = solver.NumVar(0, solver.infinity(), "total_cost")

    expr = []
    for k, u_k in enumerate(u_vars):
        heat_kWh = heat_coeff * u_k
        pv_kWh = pv_series[k]

        # Buy & sell non-negative variables
        buy_k  = solver.NumVar(0, solver.infinity(), f"buy_{k}")
        sell_k = solver.NumVar(0, solver.infinity(), f"sell_{k}")

        # buy_k - sell_k = heat_kWh - pv_kWh
        solver.Add(buy_k - sell_k == heat_kWh - pv_kWh)

        slot_center = now_aligned + timedelta(minutes=step_min * (k + 0.5))
        price_buy = _price_for_slot(slot_center, tariffs)

        expr.append(price_buy * buy_k - price_sell * sell_k)

    solver.Add(total_cost == solver.Sum(expr))
    solver.Minimize(total_cost)
