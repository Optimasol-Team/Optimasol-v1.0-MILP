# logic/optimizer/heuristics.py
# ------------------------------------------------------------------
# Very naive fallback: keep the heater ON until the first comfort
# point is satisfied, then OFF. Always feasible, rarely optimal.
# ------------------------------------------------------------------

def quick_feasible(ctx) -> list[int]:
    """Return a simple feasible 0/1 sequence if MILP fails."""
    N = ctx["global_conf"]["horizon_hours"] * 60 // ctx["global_conf"]["time_step_minutes"]
    # switch ON for the first hour, then OFF
    on_slots = 60 // ctx["global_conf"]["time_step_minutes"]
    seq = [1] * on_slots + [0] * (N - on_slots)
    return seq
