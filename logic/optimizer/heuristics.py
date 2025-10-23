# logic/optimizer/heuristics.py
# ------------------------------------------------------------------
# Very naive fallback: keep the heater ON until the first comfort
# point is satisfied, then OFF. Always feasible, rarely optimal.
# ------------------------------------------------------------------

def quick_feasible(ctx) -> list[int]:
    """Return a simple feasible 0/1 sequence if MILP fails."""
    N = ctx["horizon_h"] * 60 // ctx["step_min"] 
    on_slots = 60 // ctx["step_min"]  
    seq = [1] * on_slots + [0] * (N - on_slots)
    return seq
