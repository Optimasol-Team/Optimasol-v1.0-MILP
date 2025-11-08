from datetime import datetime, timedelta, time
import pulp

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

def add_cost_expression(prob, u_vars, *, pv_series, tariffs, P_nom, step_min, price_sell=None, optimization_start=None):
    N = len(u_vars)
    dt_h = step_min / 60
    heat_coeff = (P_nom/1000) * dt_h
    price_sell = price_sell or tariffs["tariffs_eur_per_kwh"].get("sell", 0.10)

    if optimization_start is None:
        optimization_start = datetime.now()
    
    now_aligned = optimization_start.replace(second=0, microsecond=0)
    now_aligned -= timedelta(minutes=now_aligned.minute % step_min)
    now_aligned = datetime.now().replace(second=0, microsecond=0)
    now_aligned -= timedelta(minutes=now_aligned.minute % step_min)
    
    buy_vars = []
    sell_vars = []
    cost_terms = []
    
    for k, u_k in enumerate(u_vars):
        heat_kWh = heat_coeff * u_k
        pv_kWh = pv_series[k] * dt_h
        
        buy_k = pulp.LpVariable(f"buy_{k}", lowBound=0)
        sell_k = pulp.LpVariable(f"sell_{k}", lowBound=0)
        
 
        # L'énergie achetée + PV = énergie chauffage + énergie vendue
        prob += buy_k + pv_kWh == heat_kWh + sell_k

        # On ne peut pas vendre plus que le PV disponible
  
        prob += sell_k <= pv_kWh
        
        slot_center = now_aligned + timedelta(minutes=step_min * (k + 0.5))
        price_buy = _price_for_slot(slot_center, tariffs)
        
        cost_terms.append(price_buy * buy_k - price_sell * sell_k)
    
    prob += pulp.lpSum(cost_terms)
    return {
        'buy_vars': buy_vars,
        'sell_vars': sell_vars,
        'cost_terms': cost_terms
    }