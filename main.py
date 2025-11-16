# main.py
from pathlib import Path
import time
import threading
import schedule
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.com_bdd import get_client_ids
from mqtt_receive.main_receive import receive as mqtt_receive_main
from mqtt_send.main_send import send as mqtt_send_main
from weather.weather_main import main_weather
from logic.decision_engine import process_all_clients

from config_weather_loader import config_weather_loader
from optimizer_config_loader import config_optimizer_loader

BASE_DIR = Path(__file__).resolve().parent.parent

FREQ_SECONDS = config_weather_loader(BASE_DIR / "config")
STEP_MINUTES = config_optimizer_loader(BASE_DIR / "config")

def start_mqtt_services():
    threading.Thread(target=mqtt_receive_main, name="MQTT-RX", daemon=True).start()
    threading.Thread(target=mqtt_send_main, name="MQTT-TX", daemon=True).start()

def weather_job():
    print(f"[{time.strftime('%H:%M:%S')}] Début tâche météo")
    main_weather()
    print(f"[{time.strftime('%H:%M:%S')}] Fin tâche météo")

def optimization_job():
    print(f"[{time.strftime('%H:%M:%S')}] Début optimisation clients")
    process_all_clients()
    print(f"[{time.strftime('%H:%M:%S')}] Fin optimisation clients")

def setup_schedule():
    schedule.every(FREQ_SECONDS).seconds.do(weather_job)
    schedule.every(STEP_MINUTES).minutes.do(optimization_job)
    
    print("Lancement initial des tâches...")
    weather_job()
    optimization_job()

def main():
    print("Démarrage du système OptimaSol...")
    print(f"Configuration: Météo={FREQ_SECONDS}s, Optimisation={STEP_MINUTES}min")
    
    start_mqtt_services()
    setup_schedule()

    try:
        print("Système en cours d'exécution. Ctrl+C pour arrêter.")
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("[MAIN] Arrêt demandé")

if __name__ == "__main__":
    main()