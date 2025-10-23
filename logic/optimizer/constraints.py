# logic/optimizer/constraints.py
# ------------------------------------------------------------------
# Build all temperature-related constraints (physics + comfort).
# ------------------------------------------------------------------

from datetime import time


def _time_to_index(hh_mm: str, step_min: int) -> int:
    """Convert 'HH:MM' to slot index k."""
    h, m = map(int, hh_mm.split(":"))
    return (h * 60 + m) // step_min


def add_temperature_constraints(
    solver,
    u_vars,
    T_vars,
    *,
    step_min: int,
    volume_L: float,
    UA: float,
    P_nom: float,
    t0: float,
    comfort_schedule: list,
    min_temp_enabled: bool,
    min_temp_value: float,
    rho: float = 1000,           # kg/m³
    Cp: float = 4180,            # J/(kg·°C)
    Tamb: float = 20.0,          # °C  (assumed indoor)
):
    """Add physics + comfort constraints to CBC/OR-tools solver."""

    N = len(u_vars)
    dt_h = step_min / 60         # hours
    C_kWh = rho * (volume_L / 1000) * Cp / 3_600_000  # (kWh per °C)
    loss_coeff = (UA * dt_h) / C_kWh                  # dimensionless
    heat_coeff = (P_nom / 1000) * dt_h / C_kWh        # kWh → °C

    # Initial temperature
    solver.Add(T_vars[0] == t0)

    # Dynamics:  T_{k+1} = (1-loss)·T_k + heat_coeff·u_k + loss·Tamb
    for k in range(N):
        solver.Add(
            T_vars[k + 1]
            == (1 - loss_coeff) * T_vars[k]
            + heat_coeff * u_vars[k]
            + loss_coeff * Tamb
        )

    # Point targets (06:30 → 70 °C etc.)
    for item in comfort_schedule:
        idx = _time_to_index(item["time"], step_min)
        # if idx falls outside window (rare), ignore
        if 0 <= idx <= N:
            solver.Add(T_vars[idx] >= item["target_temperature_celsius"])

    # Permanent minimum temperature
    if min_temp_enabled:
        for Tk in T_vars:
            solver.Add(Tk >= min_temp_value)
