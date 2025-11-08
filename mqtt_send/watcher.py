import time
from datetime import datetime
import threading
from .sender import send_command
from data.com_bdd import get_connection


class DecisionsDBHandler:
    """Surveille les changements dans la table decision de la BDD"""
    
    def __init__(self, check_interval=5):
        self.check_interval = check_interval
        self.last_check = datetime.now()
        self.running = True
    
    def check_database_changes(self):
        """Vérifie les nouvelles décisions dans la base de données"""
        while self.running:
            conn = None
            try:
                conn = get_connection()
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT DISTINCT client_id 
                    FROM decision 
                    WHERE timestamp_creation > %s
                    ORDER BY timestamp_creation DESC
                """, (self.last_check,))
                
                new_clients = cur.fetchall()
                self.last_check = datetime.now()
                
                for (client_id,) in new_clients:
                    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Nouvelle décision détectée pour client {client_id}")
                    try:
                        send_command(str(client_id))
                    except Exception as exc:
                        print(f"[DB Watcher] Erreur d’envoi pour client {client_id}: {exc}")
            
            except Exception as exc:
                print(f"[DB Watcher] Erreur base de données: {exc}")
            
            finally:
                if conn:
                    conn.close()
            
            time.sleep(self.check_interval)
    
    def start(self):
        """Démarrer la surveillance en arrière-plan"""
        thread = threading.Thread(target=self.check_database_changes)
        thread.daemon = True
        thread.start()
    
    def stop(self):
        """Arrêter la surveillance"""
        self.running = False


def run_db_watcher(check_interval: int = 5) -> None:
    """Lancer la surveillance de la BDD"""
    db_handler = DecisionsDBHandler(check_interval=check_interval)
    db_handler.start()

    print(f"[DB Watcher] Surveillance BDD toutes les {check_interval}s (Ctrl-C pour arrêter)")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[DB Watcher] Arrêt demandé, fermeture propre...")
        db_handler.stop()
