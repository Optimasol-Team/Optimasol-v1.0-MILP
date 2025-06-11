# logic/data_preparation.py

"""
Prepares each client's data + global optimiser configuration and
returns a single ctx dictionary ready for the core optimiser.
Entry point: load_client_context(...)
"""

import json
import pathlib
from datetime import datetime, timedelta
from bisect import bisect_left


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────


def _read_optimizer_conf(path: str | pathlib.Path) -> dict:
    """Parse a simple key=value txt file, skip '#' comments."""
    cfg = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            key, val = (tok.strip() for tok in line.split("=", 1))
            cfg[key] = float(val) if val.replace(".", "").isdigit() else val
    return {
        "time_step_minutes": int(cfg.get("step_minutes", cfg.get("step", 15))),
        "horizon_hours": int(
            cfg.get("prediction_horizon_hours",
                    cfg.get("prediction_horizon", 24))
        ),
    }


def _pv_to_series_nearest(
    pv_dict: dict,
    *,
    start: datetime,
    step_minutes: int,
    horizon_hours: int,
) -> list[float]:
    """
    Build a list [kWh0, kWh1, ...] aligned on <start> with <step_minutes>.
    For each slot, choose the PV value whose timestamp is *closest*
    (earlier or later) to the slot centre; never fill 0.0 unless pv_dict
    is empty.
    """
    if not pv_dict:
        n = horizon_hours * 60 // step_minutes
        return [0.0] * n

    # Convert keys to datetime & keep them sorted
    times, values = zip(*sorted(
        ((datetime.fromisoformat(ts), val) for ts, val in pv_dict.items()),
        key=lambda t_v: t_v[0]
    ))

    step = timedelta(minutes=step_minutes)
    half_step = step / 2
    n_steps = horizon_hours * 60 // step_minutes
    series = []

    for i in range(n_steps):
        slot_start = start + i * step
        slot_center = slot_start + half_step

        # position to insert slot_center in 'times'
        idx = bisect_left(times, slot_center)

        # candidate on the left
        cand_left = idx - 1 if idx > 0 else 0
        # candidate on the right
        cand_right = idx if idx < len(times) else len(times) - 1

        # choose whichever is closer to slot_center
        if abs((times[cand_right] - slot_center).total_seconds()) < abs(
            (slot_center - times[cand_left]).total_seconds()
        ):
            series.append(values[cand_right])
        else:
            series.append(values[cand_left])

    return series


# ──────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────


def load_client_context(
    client_dir: str,
    optimiser_conf_path: str | None = None
) -> dict:
    """
    Arguments
    ---------
    client_dir : str
        Path to the client's folder inside Clients/.
    optimiser_conf_path : str | None
        Path to optimise_config.txt (may be None → defaults).

    Returns
    -------
    dict
        ctx ready for the optimiser.
    """
    root = pathlib.Path(client_dir)

    # 1) read static data
    with open(root / "data.json", encoding="utf-8") as f:
        data = json.load(f)

    # 2) PV forecast dict
    with open(root / "production.json", encoding="utf-8") as f:
        pv_dict = json.load(f)

    # 3) current water temperature
    with open(root / "water_state.json", encoding="utf-8") as f:
        water = json.load(f)

    # 4) global (admin) config
    global_conf = (
        _read_optimizer_conf(optimiser_conf_path)
        if optimiser_conf_path else
        {"time_step_minutes": 15, "horizon_hours": 24}
    )

    # 5) produce PV list aligned on 'now'
    now = datetime.now()
    step = global_conf["time_step_minutes"]
    horizon = global_conf["horizon_hours"]
    pv_series = _pv_to_series_nearest(
        pv_dict,
        start=now - timedelta(
            minutes=now.minute % step,
            seconds=now.second,
            microseconds=now.microsecond
        ),
        step_minutes=step,
        horizon_hours=horizon,
    )

    ctx = {
        "water_heater": data["water_heater"],
        "tariffs": data["electricity_contract"],
        "pv_production": pv_series,          # list aligned on the step
        "t0": water["temperature_celsius"],
        "global_conf": global_conf,
    }
    return ctx
