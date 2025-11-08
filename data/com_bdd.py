"""
Ce module contient toutes les fonctions utiles pour communiquer avec la base de données MySQL.

Liste des fonctions disponibles :

# Connexion
get_connection

# Clients
add_client
get_client
get_client_ids
count_clients

# Chauffe-eaux
add_chauffe_eau
get_chauffe_eau
get_CE_by_client

# Températures réelles
add_temperature
get_latest_temperature_by_client
get_temperatures_by_chauffe_eau

# Données météo
add_meteo
get_meteo

# Production
add_production
get_production_by_client
add_prevision_production
get_previsions_by_client

# Configuration système
add_system_configuration
get_system_configuration_by_client
add_configuration_prediction
get_configuration_prediction_by_chauffe_eau

# Décisions
add_prediction_temperature
get_prediction_temperature_by_chauffe_eau
add_decision
get_decision_by_CE
"""

import pymysql
from datetime import datetime
from data.bdd_config_loader import load_bdd_config
import json

DB_CONFIG = load_bdd_config()

# ==========================
# ======= CONNEXION ========
# ==========================
def get_connection():
    """Crée et retourne une connexion MySQL."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.MySQLError as e:
        print(" Erreur MySQL :", e)
        return None
    except Exception as e:
        print(" Erreur inattendue :", type(e).__name__, "-", e)
        return None


# ==========================
# ======= CLIENTS ==========
# ==========================
def add_client(nom, email, latitude, longitude, tilt=None, azimuth=None, router_id=None):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    sql = """
        INSERT INTO clients (nom, email, latitude, longitude, tilt, azimuth, router_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, (nom, email, latitude, longitude, tilt, azimuth, router_id))
    conn.commit()
    client_id = cur.lastrowid
    conn.close()
    return client_id


def get_client(client_id):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE client_id = %s", (client_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    columns = [desc[0] for desc in cur.description]
    client_dict = dict(zip(columns, row))
    conn.close()
    return client_dict


def get_client_ids():
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT client_id FROM clients")
    ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids


def count_clients():
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM clients")
    (count,) = cur.fetchone()
    conn.close()
    return count


# ==========================
# ===== CHAUFFE-EAUX =======
# ==========================
def add_chauffe_eau(client_id, capacite_litres, puissance_kw):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chauffe_eaux (client_id, capacite_litres, puissance_kw) VALUES (%s, %s, %s)",
        (client_id, capacite_litres, puissance_kw),
    )
    conn.commit()
    ce_id = cur.lastrowid
    conn.close()
    return ce_id


def get_chauffe_eau(chauffe_eau_id):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT * FROM chauffe_eaux WHERE chauffe_eau_id = %s", (chauffe_eau_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    columns = [desc[0] for desc in cur.description]
    dico = dict(zip(columns, row))
    conn.close()
    return dico


def get_CE_by_client(client_id):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT chauffe_eau_id FROM chauffe_eaux WHERE client_id = %s", (client_id,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print(f"Aucun chauffe-eau trouvé pour client_id={client_id}")
        return None
    if len(rows) > 1:
        print(f" Plusieurs chauffe-eaux pour client_id={client_id}, retourne le premier.")
    return rows[0][0]


# ==========================
# == TEMPÉRATURES RÉELLES ==
# ==========================
def add_temperature(chauffe_eau_id, temperature, timestamp=None):
    conn = get_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
        INSERT INTO temperatures_reelles (chauffe_eau_id, temperature, timestamp_mesure)
        VALUES (%s, %s, %s)
    """
    cur.execute(sql, (chauffe_eau_id, temperature, ts))
    conn.commit()
    mesure_id = cur.lastrowid
    conn.close()
    return mesure_id


def get_latest_temperature_by_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT tr.temperature, tr.timestamp_mesure
        FROM temperatures_reelles tr
        JOIN chauffe_eaux ce ON tr.chauffe_eau_id = ce.chauffe_eau_id
        WHERE ce.client_id = %s
        ORDER BY tr.timestamp_mesure DESC
        LIMIT 1
    """
    cur.execute(sql, (client_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_temperatures_by_chauffe_eau(chauffe_eau_id, start=None, end=None):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM temperatures_reelles WHERE chauffe_eau_id = %s"
    params = [chauffe_eau_id]
    if start:
        sql += " AND timestamp_mesure >= %s"
        params.append(start)
    if end:
        sql += " AND timestamp_mesure <= %s"
        params.append(end)
    sql += " ORDER BY timestamp_mesure ASC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================
# ===== DONNÉES MÉTÉO =====
# ==========================
def add_meteo(client_id, temp_ext, humidity, wind_speed, precipitation, cloud_cover,
              weather_code, heure_debut, heure_fin, source="local"):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO donnees_meteo
        (client_id, temperature_ext, humidity, wind_speed, precipitation, cloud_cover,
         weather_code, heure_debut, heure_fin, source_meteo)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, (client_id, temp_ext, humidity, wind_speed, precipitation,
                      cloud_cover, weather_code, heure_debut, heure_fin, source))
    conn.commit()
    meteo_id = cur.lastrowid
    conn.close()
    return meteo_id


def get_meteo(client_id):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM donnees_meteo WHERE client_id = %s"
    params = [client_id]
   
    sql += " ORDER BY heure_debut ASC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================
# ====== PRODUCTION ========
# ==========================
def add_production(client_id, puissance_kw, heure_production=None):
    conn = get_connection()
    cur = conn.cursor()
    ts = heure_production or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
        INSERT INTO production_reelle (client_id, puissance_produite_kw, heure_production)
        VALUES (%s, %s, %s)
    """
    cur.execute(sql, (client_id, puissance_kw, ts))
    conn.commit()
    prod_id = cur.lastrowid
    conn.close()
    return prod_id


def get_production_by_client(client_id, start=None, end=None):
    conn = get_connection()
    cur = conn.cursor()
    sql = "SELECT * FROM production_reelle WHERE client_id = %s"
    params = [client_id]
    if start:
        sql += " AND heure_production >= %s"
        params.append(start)
    if end:
        sql += " AND heure_production <= %s"
        params.append(end)
    sql += " ORDER BY heure_production ASC"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def add_prevision_production(client_id, puissance_kw, heure_prevision=None):
    conn = get_connection()
    cur = conn.cursor()
    ts = heure_prevision or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = """
        INSERT INTO previsions_production (client_id, puissance_prevue_kw, heure_prevision)
        VALUES (%s, %s, %s)
    """
    cur.execute(sql, (client_id, puissance_kw, ts))
    conn.commit()
    prev_id = cur.lastrowid
    conn.close()
    return prev_id


def get_previsions_by_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM previsions_production WHERE client_id = %s ORDER BY heure_prevision ASC", (client_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================
# == CONFIGURATION SYSTÈME ==
# ==========================
def add_system_configuration(client_id, cold_water_temp, min_comfort_enabled, min_comfort_temp,
                             contract_type, base_tariff, hp_tariff, hc_tariff,
                             comfort_schedule=None, hot_water_draws=None,
                             off_peak_hours=None, custom_tariffs=None):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO system_configuration
        (client_id, cold_water_temperature,
         minimum_comfort_temperature_enabled, minimum_comfort_temperature,
         contract_type, base_tariff, hp_tariff, hc_tariff,
         comfort_schedule, hot_water_draws, off_peak_hours, custom_tariffs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, (client_id, cold_water_temp, int(min_comfort_enabled), min_comfort_temp,
                      contract_type, base_tariff, hp_tariff, hc_tariff,
                      comfort_schedule, hot_water_draws, off_peak_hours, custom_tariffs))
    conn.commit()
    cfg_id = cur.lastrowid
    conn.close()
    return cfg_id


def get_system_configuration_by_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM system_configuration WHERE client_id = %s", (client_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    columns = [desc[0] for desc in cur.description]
    result = dict(zip(columns, row))
    conn.close()
    return result


def add_configuration_prediction(chauffe_eau_id, intervalle_min, horizon_h, seuil_basse, seuil_haute):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO configuration_prediction
        (chauffe_eau_id, intervalle_measure_min, horizon_prediction_heures,
         seuil_alerte_basse, seuil_alerte_haute)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(sql, (chauffe_eau_id, intervalle_min, horizon_h, seuil_basse, seuil_haute))
    conn.commit()
    cfg_id = cur.lastrowid
    conn.close()
    return cfg_id


def get_configuration_prediction_by_chauffe_eau(chauffe_eau_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM configuration_prediction WHERE chauffe_eau_id = %s", (chauffe_eau_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================
# ===== DÉCISIONS ==========
# ==========================
def add_prediction_temperature(chauffe_eau_id, temperature_predite, heure_prevision, confidence, modele_utilise):
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        INSERT INTO decisions_temperature
        (chauffe_eau_id, temperature_predite, heure_prevision, confidence, modele_utilise)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(sql, (chauffe_eau_id, temperature_predite, heure_prevision, confidence, modele_utilise))
    conn.commit()
    decision_id = cur.lastrowid
    conn.close()
    return decision_id


def get_prediction_temperature_by_chauffe_eau(chauffe_eau_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM decisions_temperature WHERE chauffe_eau_id = %s", (chauffe_eau_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def add_decision(chauffe_eau_id, liste, step_min, heure_debut=None, conn=None):
    """
    Ajoute une décision avec métadonnées de timing
    """
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True
    
    if conn is None:
        return None
        
    cur = conn.cursor()
    
    # Heure de début de la séquence de décisions
    if heure_debut is None:
        heure_debut = datetime.now()
    
    # Préparer les données structurées
    decision_data = {
        "start_time": heure_debut.strftime("%Y-%m-%d %H:%M:%S"),
        "step_min": step_min,
        "decisions": liste
    }
    
    sql = "INSERT INTO decision (chauffe_eau_id, statut, heure_decision) VALUES (%s, %s, %s)"
    cur.execute(sql, (chauffe_eau_id, json.dumps(decision_data), heure_debut))
    conn.commit()
    decision_id = cur.lastrowid
    
    if should_close:
        conn.close()
        
    return decision_id

def get_immediate_decision_by_client(client_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT immediate_decision FROM decision WHERE client_id = %s ORDER BY timestamp_creation DESC", (client_id,))
    rows = cur.fetchall()
    
    decisions = []
    for row in rows:
        if row and row[0]:  # Vérifier que la ligne et la valeur existent
            decisions.append(row[0]) 
    
    conn.close()
    return decisions
