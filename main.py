from pathlib import Path
import time
import threading
import schedule
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data.com_bdd import get_client_ids
BASE_DIR = Path(__file__).resolve().parent.parent

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


FREQ_SECONDS: int  = config_weather_loader(BASE_DIR / "config")   # frequency for W+P tasks
STEP_MINUTES: int = config_optimizer_loader(BASE_DIR / "config")  # batch window for clients

# ---------------------------------------------------------------------------
#  RUN‑FOREVER SERVICES
# ---------------------------------------------------------------------------

def start_mqtt_services() -> None:
    """Launch MQTT send & receive loops in background daemon threads."""
    # threading.Thread(target=mqtt_receive_main, name="MQTT‑RX", daemon=True).start()   (a voir !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
    threading.Thread(target=mqtt_send_main,   name="MQTT‑TX", daemon=True).start()

# ---------------------------------------------------------------------------
#  JOB DEFINITIONS
# ---------------------------------------------------------------------------

def weather_and_production_job() -> None:
    """Sequentially run weather and production tasks."""
    print(f"[{time.strftime('%H:%M:%S')}] Début tâches météo et production")
    main_weather()
    main_production()
    print(f"[{time.strftime('%H:%M:%S')}] Fin tâches météo et production")

def clients_batch_job() -> None:
    """Spread process_client() calls for every client across STEP_MINUTES minutes."""
    print(f"[{time.strftime('%H:%M:%S')}] Début traitement batch clients")
    
    clients = get_client_ids()
    if not clients:
        print("Aucun client trouvé")
        return

    spacing: float = (STEP_MINUTES * 60) / len(clients)  # seconds between two clients
    print(f"Traitement de {len(clients)} clients avec espacement {spacing:.1f}s")
    
    for idx, client_id in enumerate(clients):
        t = threading.Timer(
            idx * spacing,
            process_client,
            args=(client_id,)  # CORRECTION: supprimer conf_path
        )
        t.daemon = True
        t.start()
        print(f"Client {client_id} programmé dans {idx * spacing:.1f}s")

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
    print("Lancement initial des tâches...")
    weather_and_production_job()
    clients_batch_job()

# ---------------------------------------------------------------------------
#  MAIN LOOP
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point. Starts long‑running services and the scheduler loop."""
    print("Démarrage du système OptimaSol...")
    print(f"Configuration: Météo/Production={FREQ_SECONDS}s, Clients={STEP_MINUTES}min")
    
    start_mqtt_services()
    setup_schedule()

    # Blocking loop – could be swapped for APScheduler if you need persistence.
    try:
        print("Système en cours d'exécution. Ctrl+C pour arrêter.")
        while True:
            schedule.run_pending()
            time.sleep(1)  # small pause to avoid busy‑wait
    except KeyboardInterrupt:
        print("[MAIN] Arrêt demandé – extinction en cours.")

if __name__ == "__main__":
    main()