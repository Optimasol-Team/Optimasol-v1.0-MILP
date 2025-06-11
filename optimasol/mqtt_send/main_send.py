"""
mqtt_send/main_send.py : Starts the watcher to monitor all decisions.txt files
"""

from pathlib import Path
from .watcher import run_watcher  

def send() :
    # Base directory = 1 niveau au-dessus du dossier courant
    base_dir = Path(__file__).resolve().parent.parent
    clients_dir = base_dir / "clients"

    run_watcher(clients_dir)
