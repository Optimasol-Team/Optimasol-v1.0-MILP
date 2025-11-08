"""
mqtt_send/main_send.py : Starts the watcher to monitor all decisions.txt files
"""

from pathlib import Path
from .watcher import run_watcher  
from data.com_bdd import get_client_ids

def send() :
    clients = get_client_ids() # liste des id des clients

    run_watcher(clients)
