from pathlib import Path
import time
import threading
import schedule

# ---------------------------------------------------------------------------
#  ALWAYS‑ON MQTT SERVICES
# ---------------------------------------------------------------------------
# These two services must run for the entire lifetime of the application.
# They handle MQTT ingress (router_data) and egress (decisions) respectively.
from mqtt_receive.main_receive import receive as mqtt_receive_main    # listener – never returns
from mqtt_send.main_send       import send    as mqtt_send_main       # sender   – never returns

# ---------------------------------------------------------------------------
#  SCHEDULABLE TASKS
# ---------------------------------------------------------------------------
# They are imported as functions and will be triggered on a timetable:
from weather.weather_main            import main_weather          # weather forecasting task
from weather_processing.main_production import main_production    # production optimisation task
from logic.client_processor          import process_client        # per‑client processing

# ---------------------------------------------------------------------------
#  CONFIG LOADERS
# ---------------------------------------------------------------------------
# We keep main.py clean; parsing is delegated to dedicated helpers.
from config_weather_loader   import config_weather_loader    # returns seconds (int)
from optimizer_config_loader import config_optimizer_loader  # returns step_minutes (int)

# ---------------------------------------------------------------------------
#  PATHS & CONFIG VALUES
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).parent                        # folder that contains this file
CLIENTS_ROOT: Path = BASE_DIR / "clients"                   # one sub‑directory per client

FREQ_SECONDS: int  = config_weather_loader(BASE_DIR / "config")   # frequency for W+P tasks
STEP_MINUTES: int = config_optimizer_loader(BASE_DIR / "config")  # batch window for clients

# ---------------------------------------------------------------------------
#  RUN‑FOREVER SERVICES
# ---------------------------------------------------------------------------

def start_mqtt_services() -> None:
    """Launch MQTT send & receive loops in background daemon threads."""
    #threading.Thread(target=mqtt_receive_main, name="MQTT‑RX", daemon=True).start()   (a voir !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
    threading.Thread(target=mqtt_send_main,   name="MQTT‑TX", daemon=True).start()

# ---------------------------------------------------------------------------
#  JOB DEFINITIONS
# ---------------------------------------------------------------------------

def weather_and_production_job() -> None:
    """Sequentially run weather and production tasks."""
    main_weather()
    main_production()


def list_client_dirs() -> list[Path]:
    """Return every sub‑directory inside CLIENTS_ROOT that represents a client."""
    if not CLIENTS_ROOT.is_dir():
        return []
    return [p for p in CLIENTS_ROOT.iterdir() if p.is_dir() and not p.name.startswith('.')]


def clients_batch_job() -> None:
    """Spread process_client() calls for every client across STEP_MINUTES minutes.

    Each client directory is scheduled with a delay so that the whole batch
    is evenly distributed inside the STEP_MINUTES window.
    """
    clients = list_client_dirs()
    if not clients:
        return

    spacing: float = (STEP_MINUTES * 60) / len(clients)  # seconds between two clients
    conf_path = BASE_DIR / "config" / "optimize_config.txt"
    for idx, cli_dir in enumerate(clients):
        t = threading.Timer(
            idx * spacing,
            process_client,
            args=(cli_dir,conf_path)
        )
        t.daemon = True
        t.start()

# ---------------------------------------------------------------------------
#  SCHEDULER SETUP
# ---------------------------------------------------------------------------

def setup_schedule() -> None:
    """Register recurring jobs with the *schedule* library."""
    # Weather + production every FREQ_SECONDS
    schedule.every(FREQ_SECONDS).seconds.do(weather_and_production_job)

    # Clients batch every STEP_MINUTES minutes
    schedule.every(STEP_MINUTES).minutes.do(clients_batch_job)

    # Optionally trigger immediately at startup
    weather_and_production_job()
    clients_batch_job()

# ---------------------------------------------------------------------------
#  MAIN LOOP
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point. Starts long‑running services and the scheduler loop."""
    start_mqtt_services()
    setup_schedule()

    # Blocking loop – could be swapped for APScheduler if you need persistence.
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # small pause to avoid busy‑wait
    except KeyboardInterrupt:
        print("[MAIN] Shutdown requested – exiting gracefully.")


if __name__ == "__main__":
    main()
