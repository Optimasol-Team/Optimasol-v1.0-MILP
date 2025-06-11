# logic/optimizer/milp_solver.py

from ortools.linear_solver import pywraplp # type: ignore

# Helpers to be implemented in sibling modules
from .constraints import add_temperature_constraints # type: ignore
from .cost import add_cost_expression # type: ignore
from .heuristics import quick_feasible # type: ignore


def optimise(ctx):
    """
    Build and solve a MILP for the current 24-h window.
    Returns a list[int] of length N containing 0/1 (OFF/ON).
    """
    #  1) Unpack everything we need 
    step_min   = ctx["global_conf"]["time_step_minutes"]
    horizon_h  = ctx["global_conf"]["horizon_hours"]  
    N          = horizon_h * 60 // step_min   #The number of points

    P_nom      = ctx["water_heater"]["power_watts"]
    volume_L   = ctx["water_heater"]["volume_liters"]
    UA         = ctx["water_heater"].get("UA", 9.0)

    comfort_sched   = ctx["water_heater"]["comfort_schedule"]
    min_temp_conf   = ctx["water_heater"]["minimum_comfort_temperature"]
    min_temp_enabled = min_temp_conf.get("enabled", False)
    min_temp_value   = min_temp_conf.get("temperature_celsius", 50)

    pv_series  = ctx["pv_production"]             # list[float] length N
    tariffs    = ctx["tariffs"]                   # HC/HP prices + hours
    t0         = ctx["t0"]                        # current °C

    # ── 2) Create solver & variables ───────────────────────────────
    solver = pywraplp.Solver.CreateSolver("CBC")
    if solver is None:
        raise RuntimeError("CBC solver unavailable. Check the OR-Tools install.")

    # Binary ON/OFF decision variables
    u = [solver.BoolVar(f"u_{k}") for k in range(N)]

    # Continuous temperature variables (0-100 °C bounds)
    T = [solver.NumVar(0.0, 100.0, f"T_{k}") for k in range(N + 1)]

    # ── 3) Add physics & comfort constraints ──────────────────────
    add_temperature_constraints(
        solver, u, T,
        step_min=step_min,
        volume_L=volume_L,
        UA=UA,
        P_nom=P_nom,
        t0=t0,
        comfort_schedule=comfort_sched,
        min_temp_enabled=min_temp_enabled,
        min_temp_value=min_temp_value,
    )

    #  4) Add cost function to the model ─────────────────────
    add_cost_expression(
        solver, u,
        pv_series=pv_series,
        tariffs=tariffs,
        P_nom=P_nom,
        step_min=step_min,
    )

    # ── 5) Solve (with time-limit) ────────────────────────────────
    solver.SetTimeLimit(10000)   # 10 s
    status = solver.Solve()

    # ── 6) If not optimal, fall back to heuristic ─────────────────
    if status != pywraplp.Solver.OPTIMAL:
        return quick_feasible(ctx)    # simple feasible sequence

    # ── 7) Extract binary decisions and return ────────────────────
    best_sequence = [int(var.solution_value()) for var in u]
    return best_sequence
