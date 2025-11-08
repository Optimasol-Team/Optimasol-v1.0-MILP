"""
decision_executor.py - Exécute les décisions au bon moment
"""

from data.com_bdd import get_connection
from datetime import datetime, timedelta
import json
import time

def get_current_decision(chauffe_eau_id):
    """Récupère la décision actuelle à exécuter"""
    conn = get_connection()
    if not conn:
        return None
        
    cur = conn.cursor()
    
    # Récup la dernière décision
    cur.execute("""
        SELECT statut, heure_decision 
        FROM decision 
        WHERE chauffe_eau_id = %s 
        ORDER BY heure_decision DESC 
        LIMIT 1
    """, (chauffe_eau_id,))
    
    row = cur.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return None
    
    try:
        decision_data = json.loads(row[0])
        start_time = datetime.strptime(decision_data["start_time"], "%Y-%m-%d %H:%M:%S")
        step_min = decision_data["step_min"]
        decisions = decision_data["decisions"]
        
        # Calculer l'index actuel
        now = datetime.now()
        elapsed_minutes = (now - start_time).total_seconds() / 60
        current_index = int(elapsed_minutes // step_min)
        
        if 0 <= current_index < len(decisions):
            return decisions[current_index]
        else:
            return None  # Hors de l'horizon
            
    except Exception as e:
        print(f"Erreur parsing décision: {e}")
        return None

def format_command(decision_value):
    """Convertit 0/1 en commande SETMODE"""
    if decision_value == 0:
        return "SETMODE 10"  # OFF
    else:           
        return "SETMODE 12"  # ON