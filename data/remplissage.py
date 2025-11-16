from com_bdd import (
    get_connection, add_client, add_chauffe_eau, add_temperature, 
    add_meteo, add_production, add_prevision_production, 
    add_system_configuration, add_configuration_prediction,
    add_prediction_temperature, add_decision, get_client_ids
)
from datetime import datetime, timedelta
import random
import json

def clear_all_data():
    """Supprime tous les clients et leurs données associées"""
    conn = get_connection()
    if conn is None:
        print("❌ Impossible de se connecter à la base de données")
        return False
    
    try:
        cur = conn.cursor()
        
        print("🗑️  Suppression de toutes les données...")
        
        # Désactiver les contraintes de clé étrangère
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Supprimer toutes les données dans l'ordre inverse des dépendances
        tables = [
            'decision', 'decisions_temperature', 'configuration_prediction',
            'temperatures_reelles', 'previsions_production', 'production_reelle',
            'donnees_meteo', 'system_configuration', 'chauffe_eaux', 'clients'
        ]
        
        for table in tables:
            cur.execute(f"DELETE FROM {table}")
            print(f"✅ Données supprimées de {table}")
        
        # Réactiver les contraintes
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
        print("✅ Toutes les données ont été supprimées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def populate_all_tables():
    """Peuple toutes les tables pour tous les clients avec notre format"""
    
    # Étape 0: Supprimer toutes les données existantes
    if not clear_all_data():
        return
    
    print("🚀 Démarrage du peuplement complet de la base de données...")
    
    # Étape 1: Créer les clients
    clients_data = [
        # (nom, email, latitude, longitude, tilt, azimuth, router_id)
        ("Martin Dubois", "martin.dubois@email.com", 48.8566, 2.3522, 30, 180, "ROUTER001","123"),
        ("Sophie Laurent", "sophie.laurent@email.com", 45.7640, 4.8357, 25, 170, "ROUTER002","eaea"),
        ("Pierre Moreau", "pierre.moreau@email.com", 43.2965, 5.3698, 35, 160, "ROUTER003",'hello'),
        ("Marie Garnier", "marie.garnier@email.com", 47.2184, -1.5536, 28, 175, "ROUTER004"'hiiiii'),
        ("Jean Petit", "jean.petit@email.com", 43.6047, 1.4442, 32, 165, "ROUTER005",'idn'),
        ("Catherine Roux", "catherine.roux@email.com", 44.8378, -0.5792, 27, 180, "ROUTER006",'vector'),
        ("Michel Bernard", "michel.bernard@email.com", 47.3220, 5.0415, 29, 170, "ROUTER007"'plus'),
        ("Isabelle Leroy", "isabelle.leroy@email.com", 50.6292, 3.0573, 31, 175, "ROUTER008",'dinspi'),
        ("Philippe Gauthier", "philippe.gauthier@email.com", 49.4432, 1.0990, 26, 160, "ROUTER009"'1965'),
        ("Nathalie Fournier", "nathalie.fournier@email.com", 46.6034, 1.8883, 33, 165, "ROUTER010",'paris')
    ]
    
    client_ids = []
    print("\n👥 Création des clients...")
    for client in clients_data:
        client_id = add_client(*client)
        if client_id:
            client_ids.append(client_id)
            print(f"✅ Client ajouté: {client[0]} (ID: {client_id})")
    
    print(f"\n🎯 {len(client_ids)} clients créés avec succès")
    
    # Étape 2: Peuplement de toutes les tables pour chaque client
    for client_id in client_ids:
        print(f"\n{'='*50}")
        print(f"📦 Peuplement des données pour le client ID: {client_id}")
        print(f"{'='*50}")
        
        # 2.1 Chauffe-eaux (1 par client pour simplifier)
        print("🔥 Ajout des chauffe-eaux...")
        ce_id = add_chauffe_eau(
            client_id=client_id,
            capacite_litres=random.choice([200, 250, 300]),
            puissance_kw=random.choice([2.0, 2.5, 3.0])
        )
        print(f"  ✅ Chauffe-eau {ce_id} ajouté")
        
        # 2.2 Configuration système - ADAPTÉ À NOTRE FORMAT
        print("⚙️  Ajout de la configuration système...")
        
        # Format de comfort_schedule adapté à parse_comfort_schedule
        comfort_schedule_dict = {
            6: 60,  # 6h-7h à 60°C
            7: 60,
            8: 60,
            18: 55, # 18h-21h à 55°C
            19: 55,
            20: 55,
            21: 55
        }
        
        # Format de water_consumption adapté à load_water_consumption
        water_consumption_data = {
            'distribution': [
                {'hour': 7, 'liters': 50},   # Douche matin
                {'hour': 19, 'liters': 80},  # Bain soir
                {'hour': 21, 'liters': 30}   # Vaisselle
            ]
        }
        
    # Dans remplissage.py, modifiez l'appel :
        system_config_id = add_system_configuration(
            client_id=client_id,
            cold_water_temp=round(random.uniform(8.0, 15.0), 1),
            min_comfort_enabled=random.choice([True, False]),
            min_comfort_temp=round(random.uniform(45.0, 55.0), 1),
            contract_type=random.choice(["base", "heures_creuses"]),
            base_tariff=round(random.uniform(0.15, 0.25), 3),
            hp_tariff=round(random.uniform(0.18, 0.28), 3),
            hc_tariff=round(random.uniform(0.12, 0.18), 3),
            comfort_schedule=json.dumps(comfort_schedule_dict),
            water_consumption=json.dumps(water_consumption_data),  # <-- changer hot_water_draws → water_consumption
            off_peak_hours=json.dumps({"start": "22:00", "end": "06:00"}),
            sell_tariffs=json.dumps({"sell_tariff": 0.10})  
        )
        print(f"  ✅ Configuration système {system_config_id} ajoutée")
        
        # 2.3 Configuration prédiction
        print("🔮 Ajout des configurations de prédiction...")
        config_pred_id = add_configuration_prediction(
            chauffe_eau_id=ce_id,
            intervalle_min=15,  # Step_min fixe à 15 pour notre code
            horizon_h=24,
            seuil_basse=45.0,
            seuil_haute=65.0
        )
        print(f"  ✅ Configuration prédiction {config_pred_id} pour CE {ce_id}")
        
        # 2.4 Température initiale
        print("🌡️  Ajout de la température initiale...")
        temp_id = add_temperature(
            chauffe_eau_id=ce_id,
            temperature=round(random.uniform(50.0, 65.0), 1),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        print(f"  ✅ Température initiale {temp_id} ajoutée")
        
        # 2.5 Prévisions de production (pour les 24 prochaines heures)
        print("📊 Ajout des prévisions de production...")
        now = datetime.now()
        N = 96  # 24h * 4 (step_min=15) = 96 points
        
        for i in range(N):
            heure_prevision = now + timedelta(minutes=15 * i)
            
            # Production réaliste : maximum à midi
            hour = heure_prevision.hour
            base_production = random.uniform(0.5, 3.5)
            hour_factor = 1 - abs(12 - hour) / 12  # Maximum à midi
            production = max(0, base_production * hour_factor)
            
            prev_id = add_prevision_production(
                client_id=client_id,
                puissance_kw=round(production, 2),
                heure_prevision=heure_prevision.strftime("%Y-%m-%d %H:%M:%S")
            )
        print(f"  ✅ Prévisions production ajoutées ({N} points)")
        
        print(f"✅ Client {client_id} complètement peuplé !")
    
    print(f"\n{'='*60}")
    print("🎉 PEUPLEMENT TERMINÉ AVEC SUCCÈS !")
    print(f"{'='*60}")
    print(f"📊 Récapitulatif :")
    print(f"   • {len(client_ids)} clients créés")
    print(f"   • 1 chauffe-eau par client")
    print(f"   • Configuration système adaptée à notre code")
    print(f"   • Step_min fixé à 15 minutes")
    print(f"   • Prévisions production sur 24h (96 points)")
    print(f"{'='*60}")

# Exécution du script
if __name__ == "__main__":
    populate_all_tables()