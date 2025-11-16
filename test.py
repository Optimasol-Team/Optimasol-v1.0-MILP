# test.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_complet():
    print("TEST COMPLET SYSTEME")
    
    print("1. Test base de données...")
    from data.com_bdd import get_connection, get_client_ids
    conn = get_connection()
    if conn:
        clients = get_client_ids()
        print(f"BDD OK - {len(clients)} clients")
        conn.close()
    else:
        print("BDD ERROR")
        return

    """nt("2. Test météo...")
    from weather.weather_main import main_weather
    main_weather()"""

    print("3. Test optimiseur...")
    from logic.client_processor import process_all_clients
    from data.com_bdd import get_client_ids
    clients = get_client_ids()
    process_all_clients(clients[::3])

    print("4. Verification données...")
    from data.com_bdd import get_previsions_by_client, get_decision_by_CE, get_CE_by_client
    
    for client_id in get_client_ids()[:3]:
        previsions = get_previsions_by_client(client_id)
        ce_id = get_CE_by_client(client_id)
        decisions = get_decision_by_CE(ce_id) if ce_id else []
        print(f"Client {client_id}: {previsions} previsions, {decisions}\n")

    print("TEST TERMINE")

if __name__ == "__main__":
    test_complet()