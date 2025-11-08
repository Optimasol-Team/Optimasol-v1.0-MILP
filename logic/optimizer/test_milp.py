import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import pulp
from milp_solver import milp_analysis
from normal_CA import simulate_classic_water_heater
from normal_CA_PV import simulate_classic_water_heater_midi

def create_scenario_famille_typique():
    """SCÉNARIO 1: Famille de 4 personnes - journée type avec pics de consommation"""
    water_heater = {"puissance_kw": 2.5, "capacite_litres": 250}
    
    tariffs = {
        "contract_type": "HPHC",
        "tariffs_eur_per_kwh": {"hp": 0.25, "hc": 0.18, "sell": 0.10},
        "off_peak_hours": [{"start": "12:00", "end": "15:00"}]
    }
    
    N = 24 * 4  # 24h avec pas de 15min
    pv_series = []
    for i in range(N):
        hour = (i * 0.25) % 24
        # Production PV typique d'une journée ensoleillée
        base_production = 3.0 * np.exp(-0.5 * ((hour - 13) / 3)**2)
        production = max(0, base_production + np.random.normal(0, 0.2))
        pv_series.append(production)
    
    # Profil de consommation réaliste pour une famille
    consumption_profile = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 7 <= hour <= 9:    # Douches du matin
            consumption = 2.0 * np.exp(-0.5 * ((hour - 8) / 0.4)**2)
        elif 12 <= hour <= 14: # Vaisselle déjeuner
            consumption = 0.8 * np.exp(-0.5 * ((hour - 13) / 0.3)**2)
        elif 19 <= hour <= 21: # Douches du soir + vaisselle
            consumption = 1.5 * np.exp(-0.5 * ((hour - 20) / 0.5)**2)
        else:
            consumption = 0.0
        consumption_profile.append(consumption * 8)  # Conversion en litres
    
    # Consignes adaptées aux besoins familiaux
    comfort_schedule = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 6 <= hour <= 10:   # Réveil - besoin de température élevée
            target_temp = 60.0
        elif 17 <= hour <= 22: # Soirée - confort important
            target_temp = 58.0
        elif 11 <= hour <= 16: # Journée - température modérée
            target_temp = 52.0
        else:                  # Nuit - économie d'énergie
            target_temp = 50.0
        comfort_schedule.append(target_temp)
    
    return {
        "step_min": 15, "horizon_h": 24, "water_heater": water_heater, "t0": 55.0,
        "pv_production": pv_series, "water_consumption": consumption_profile,
        "comfort_schedule": comfort_schedule, "tariffs": tariffs,
        "minimum_comfort_temperature_enabled": True, "minimum_comfort_temperature": 45.0,
        "ambient_temperature": 18.0, "cold_water_temperature": 12.0
    }

def create_scenario_personne_seule():
    """SCÉNARIO 2: Personne seule - faible consommation mais besoin de flexibilité"""
    water_heater = {"puissance_kw": 1.5, "capacite_litres": 150}
    
    tariffs = {
        "contract_type": "HPHC", 
        "tariffs_eur_per_kwh": {"hp": 0.23, "hc": 0.16, "sell": 0.08},
        "off_peak_hours": [{"start": "22:00", "end": "06:00"}]
    }
    
    N = 24 * 4
    pv_series = []
    for i in range(N):
        hour = (i * 0.25) % 24
        # Production PV modérée (appartement)
        base_production = 1.5 * np.exp(-0.5 * ((hour - 13) / 3.5)**2)
        production = max(0, base_production + np.random.normal(0, 0.15))
        pv_series.append(production)
    
    # Consommation réduite - personne seule
    consumption_profile = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 8 <= hour <= 9:    # Douche matin
            consumption = 1.2 * np.exp(-0.5 * ((hour - 8.5) / 0.3)**2)
        elif 20 <= hour <= 21: # Douche soir
            consumption = 1.0 * np.exp(-0.5 * ((hour - 20.5) / 0.3)**2)
        else:
            consumption = 0.0
        consumption_profile.append(consumption * 6)
    
    # Consignes adaptées - pas besoin de températures très élevées
    comfort_schedule = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 7 <= hour <= 10:   # Périodes d'utilisation
            target_temp = 55.0
        elif 19 <= hour <= 22:
            target_temp = 55.0
        else:                  # Hors utilisation
            target_temp = 48.0
        comfort_schedule.append(target_temp)
    
    return {
        "step_min": 15, "horizon_h": 24, "water_heater": water_heater, "t0": 50.0,
        "pv_production": pv_series, "water_consumption": consumption_profile,
        "comfort_schedule": comfort_schedule, "tariffs": tariffs,
        "minimum_comfort_temperature_enabled": True, "minimum_comfort_temperature": 48.0,
        "ambient_temperature": 20.0, "cold_water_temperature": 15.0
    }

def create_scenario_maison_retraite():
    """SCÉNARIO 3: Maison de retraite - consommation étalée sur la journée"""
    water_heater = {"puissance_kw": 4.0, "capacite_litres": 400}
    
    tariffs = {
        "contract_type": "HPHC",
        "tariffs_eur_per_kwh": {"hp": 0.28, "hc": 0.20, "sell": 0.12},
        "off_peak_hours": [{"start": "22:00", "end": "06:00"}]
    }
    
    N = 24 * 4
    pv_series = []
    for i in range(N):
        hour = (i * 0.25) % 24
        # Forte production PV (toiture importante)
        base_production = 5.0 * np.exp(-0.5 * ((hour - 13) / 2.5)**2)
        production = max(0, base_production + np.random.normal(0, 0.3))
        pv_series.append(production)
    
    # Consommation étalée sur la journée
    consumption_profile = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 6 <= hour <= 10:   # Toilettes et douches matin
            consumption = 1.5 * np.exp(-0.5 * ((hour - 8) / 0.8)**2)
        elif 12 <= hour <= 14: # Vaisselle déjeuner
            consumption = 1.0 * np.exp(-0.5 * ((hour - 13) / 0.4)**2)
        elif 17 <= hour <= 20: # Toilettes et douches soir
            consumption = 1.8 * np.exp(-0.5 * ((hour - 18.5) / 0.7)**2)
        else:
            consumption = 0.3  # Consommation résiduelle constante
        consumption_profile.append(consumption * 10)
    
    # Température constante élevée pour confort des personnes âgées
    comfort_schedule = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 6 <= hour <= 22:   # Journée - confort important
            target_temp = 62.0
        else:                  # Nuit - légère réduction
            target_temp = 58.0
        comfort_schedule.append(target_temp)
    
    return {
        "step_min": 15, "horizon_h": 24, "water_heater": water_heater, "t0": 60.0,
        "pv_production": pv_series, "water_consumption": consumption_profile,
        "comfort_schedule": comfort_schedule, "tariffs": tariffs,
        "minimum_comfort_temperature_enabled": True, "minimum_comfort_temperature": 58.0,
        "ambient_temperature": 22.0, "cold_water_temperature": 12.0
    }

def create_scenario_bureau():
    """SCÉNARIO 4: Bureaux - consommation concentrée sur les pauses"""
    water_heater = {"puissance_kw": 3.0, "capacite_litres": 200}
    
    tariffs = {
        "contract_type": "HPHC",
        "tariffs_eur_per_kwh": {"hp": 0.30, "hc": 0.22, "sell": 0.15},
        "off_peak_hours": [{"start": "12:00", "end": "15:00"}]
    }
    
    N = 24 * 4
    pv_series = []
    for i in range(N):
        hour = (i * 0.25) % 24
        # Production PV importante (bâtiment commercial)
        base_production = 4.0 * np.exp(-0.5 * ((hour - 13) / 2.8)**2)
        production = max(0, base_production + np.random.normal(0, 0.25))
        pv_series.append(production)
    
    # Consommation uniquement pendant les heures de bureau
    consumption_profile = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 9 <= hour <= 10:   # Pause café matin
            consumption = 2.0 * np.exp(-0.5 * ((hour - 9.5) / 0.2)**2)
        elif 12 <= hour <= 14: # Pause déjeuner
            consumption = 2.5 * np.exp(-0.5 * ((hour - 13) / 0.5)**2)
        elif 15 <= hour <= 16: # Pause café après-midi
            consumption = 1.5 * np.exp(-0.5 * ((hour - 15.5) / 0.3)**2)
        else:
            consumption = 0.0
        consumption_profile.append(consumption * 5)
    
    # Consignes adaptées aux heures d'ouverture
    comfort_schedule = []
    for i in range(N):
        hour = (i * 0.25) % 24
        if 8 <= hour <= 18:   # Heures de bureau
            target_temp = 55.0
        else:                  # Soirée et nuit
            target_temp = 45.0
        comfort_schedule.append(target_temp)
    
    return {
        "step_min": 15, "horizon_h": 24, "water_heater": water_heater, "t0": 50.0,
        "pv_production": pv_series, "water_consumption": consumption_profile,
        "comfort_schedule": comfort_schedule, "tariffs": tariffs,
        "minimum_comfort_temperature_enabled": True, "minimum_comfort_temperature": 45.0,
        "ambient_temperature": 21.0, "cold_water_temperature": 15.0
    }

def create_comprehensive_plots(u_values, T_values, metrics, ctx, scenario_name):
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(f'OPTIMISATION CHAUFFE-EAU - {scenario_name}', fontsize=16, fontweight='bold')
    
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    times = [start_time + timedelta(minutes=i * ctx["step_min"]) for i in range(len(u_values))]
    
    # 1. Température et consignes
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(times, T_values[:-1], 'b-', linewidth=2, label='Température ballon')
    
    comfort_schedule = ctx.get("comfort_schedule", [])
    if comfort_schedule:
        for i in range(len(comfort_schedule)):
            if i == 0 or comfort_schedule[i] != comfort_schedule[i-1]:
                ax1.plot(times[i], comfort_schedule[i], 'ro', markersize=6, label='Consigne' if i == 0 else "")
    
    min_comfort = ctx.get("minimum_comfort_temperature", 50.0)
    ax1.axhline(y=min_comfort, color='r', linestyle='--', label='Min confort', alpha=0.7)
    ax1.set_ylabel('Température (°C)')
    ax1.set_title('Évolution de la Température')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # 2. Commande chauffage et production PV
    ax2 = plt.subplot(3, 2, 2)
    ax2.step(times, u_values, 'r-', where='post', linewidth=2, label='Chauffage ON/OFF')
    ax2_twin = ax2.twinx()
    ax2_twin.plot(times, ctx["pv_production"], 'g-', linewidth=2, label='Production PV', alpha=0.7)
    ax2_twin.set_ylabel('Production PV (kW)', color='green')
    ax2_twin.tick_params(axis='y', labelcolor='green')
    ax2.set_ylabel('État Chauffage')
    ax2.set_title('Commande et Production PV')
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # 3. Consommation d'eau chaude
    ax3 = plt.subplot(3, 2, 3)
    water_consumption = ctx.get("water_consumption", [0] * len(u_values))
    ax3.bar(times, water_consumption, width=0.01, alpha=0.7, color='orange', label='Consommation eau')
    ax3.set_ylabel('Consommation (L/15min)')
    ax3.set_title('Profil de Consommation d\'Eau')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # 4. Répartition énergétique
    ax4 = plt.subplot(3, 2, 4)
    energy_types = ['Réseau HP', 'Réseau HC', 'PV Autoconsommé']
    energy_values = [metrics["energy_hp_kwh"], metrics["energy_hc_kwh"], metrics["pv_used_for_heating_kwh"]]
    colors = ['red', 'blue', 'green']
    bars = ax4.bar(energy_types, energy_values, color=colors, alpha=0.7)
    ax4.set_ylabel('Énergie (kWh)')
    ax4.set_title('Origine de l\'Énergie Consommée')
    for bar, value in zip(bars, energy_values):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{value:.2f}', ha='center', va='bottom')

    # 5. Analyse des coûts
    ax5 = plt.subplot(3, 2, 5)
    cost_types = ['Coût Total', 'Coût HP', 'Coût HC']
    cost_values = [metrics["total_cost_eur"], metrics["cost_hp_eur"], metrics["cost_hc_eur"]]
    cost_colors = ['purple', 'red', 'blue']
    bars = ax5.bar(cost_types, cost_values, color=cost_colors, alpha=0.7)
    ax5.set_ylabel('Coût (€)')
    ax5.set_title('Répartition des Coûts')
    for bar, value in zip(bars, cost_values):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001, f'{value:.3f}€', ha='center', va='bottom')
    
    # 6. Résumé performances
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    
    # Calcul indicateurs clés
    economy_vs_hp_only = (metrics['energy_hc_kwh'] * 
                         (ctx["tariffs"]["tariffs_eur_per_kwh"]["hp"] - 
                          ctx["tariffs"]["tariffs_eur_per_kwh"]["hc"]))
    
    summary_text = (
        f"SYNTHÈSE - {scenario_name}\n\n"
        f"🎯 PERFORMANCES ÉNERGÉTIQUES:\n"
        f"• Coût total: {metrics['total_cost_eur']:.3f} €\n"
        f"• Économies vs HP seule: {economy_vs_hp_only:.3f} €\n"
        f"• Autoconsommation PV: {metrics['self_consumption_rate']:.1f}%\n"
        f"• PV utilisée: {metrics['pv_utilization_rate']:.1f}%\n\n"
        f"🔥 CONSOMMATIONS:\n"
        f"• Énergie totale: {metrics['total_energy_kwh']:.2f} kWh\n"
        f"• Dont HC: {metrics['energy_hc_kwh']:.2f} kWh\n"
        f"• Temps chauffe: {metrics['total_on_time_h']:.1f} h\n\n"
        f"🌡️ CONFORT:\n"
        f"• Temp. moyenne: {metrics['temperature_avg']:.1f}°C\n"
        f"• Marge confort: {metrics['avg_comfort_margin']:.1f}°C\n"
        f"• Violations: {metrics['comfort_violations']}"
    )
    
    ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=10,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3),
             fontfamily='monospace')
    
    plt.tight_layout()
    return fig

def run_demonstration():
    """Lance une démonstration complète avec les 4 scénarios réalistes"""
    scenarios = {
        "🏠 FAMILLE TYPIQUE": create_scenario_famille_typique,
        "👤 PERSONNE SEULE": create_scenario_personne_seule, 
        "👵 MAISON RETRAITE": create_scenario_maison_retraite,
        "🏢 BUREAUX": create_scenario_bureau
    }
    
    results = {}
    
    print("🔧 DÉMONSTRATION OPTIMISATION CHAUFFE-EAU INTELLIGENT")
    print("=" * 60)
    print("Cette démo illustre comment l'optimisation adapte la stratégie de")
    print("chauffage en fonction du profil d'usage et de la production PV.")
    print("=" * 60)
    
    for name, scenario_func in scenarios.items():
        print(f"\n{'='*60}")
        print(f"🎯 {name}")
        print(f"{'='*60}")
        
        ctx = scenario_func()
        success, u_values, T_values, metrics = milp_analysis(ctx)
        
        if success:
            results[name] = {'ctx': ctx, 'u_values': u_values, 'T_values': T_values, 'metrics': metrics}
            
            print(f"📊 Génération du rapport détaillé...")
            fig = create_comprehensive_plots(u_values, T_values, metrics, ctx, name)
            filename = f'optimisation_{name.replace(" ", "_").lower()}.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            # Affichage synthétique
            print(f"✅ OPTIMISATION RÉUSSIE:")
            print(f"   • Coût journalier: {metrics['total_cost_eur']:.3f}€")
            print(f"   • Énergie consommée: {metrics['total_energy_kwh']:.2f} kWh")
            print(f"   • Autoconsommation PV: {metrics['self_consumption_rate']:.1f}%")
            print(f"   • Confort: {metrics['comfort_violations']} violations")
            
        else:
            print(f"❌ Échec de l'optimisation pour ce scénario")
    
    return results

def create_comparison_chart(results):
    """Crée un graphique comparatif des performances entre scénarios"""
    if not results or len(results) < 2:
        return
    
    print(f"\n{'='*60}")
    print("📈 COMPARAISON DES PERFORMANCES PAR SCÉNARIO")
    print(f"{'='*60}")
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('COMPARAISON DES STRATÉGIES D\'OPTIMISATION PAR PROFIL D\'USAGE', 
                 fontsize=16, fontweight='bold')
    
    names = list(results.keys())
    
    # 1. Coûts totaux
    costs = [results[name]['metrics']['total_cost_eur'] for name in names]
    bars1 = ax1.bar(names, costs, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax1.set_title('Coût Journalier Total', fontweight='bold')
    ax1.set_ylabel('Coût (€)')
    for bar, cost in zip(bars1, costs):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{cost:.3f}€', ha='center', va='bottom', fontweight='bold')
    
    # 2. Énergie consommée
    energy = [results[name]['metrics']['total_energy_kwh'] for name in names]
    bars2 = ax2.bar(names, energy, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax2.set_title('Énergie Totale Consommée', fontweight='bold')
    ax2.set_ylabel('Énergie (kWh)')
    for bar, energ in zip(bars2, energy):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{energ:.1f}kWh', ha='center', va='bottom', fontweight='bold')
    
    # 3. Taux d'autoconsommation
    auto_cons = [results[name]['metrics']['self_consumption_rate'] for name in names]
    bars3 = ax3.bar(names, auto_cons, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax3.set_title('Taux d\'Autoconsommation PV', fontweight='bold')
    ax3.set_ylabel('Taux (%)')
    for bar, rate in zip(bars3, auto_cons):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 4. Répartition énergie HC/HP
    hc_ratios = []
    for name in names:
        total_energy = results[name]['metrics']['total_energy_kwh']
        hc_energy = results[name]['metrics']['energy_hc_kwh']
        hc_ratios.append((hc_energy / total_energy * 100) if total_energy > 0 else 0)
    
    bars4 = ax4.bar(names, hc_ratios, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax4.set_title('Pourcentage d\'Énergie en Heures Creuses', fontweight='bold')
    ax4.set_ylabel('Part HC (%)')
    for bar, ratio in zip(bars4, hc_ratios):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{ratio:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('comparaison_strategies_optimisation.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_comparison_plot(scenario_data, scenario_name):
    """Crée un graphique comparant 3 scénarios avec abscisses lisibles"""
    ctx = scenario_data['ctx']
    opti = scenario_data['optimized']
    classic = scenario_data['classic']
    classic_pv = scenario_data.get('classic_pv', classic)

    # --- FIGURE GÉNÉRALE ---
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(f'COMPARAISON DES 3 STRATÉGIES - {scenario_name}',
                 fontsize=18, fontweight='bold', color='#2c3e50', y=0.98)
    
    gs = plt.GridSpec(3, 3, figure=fig, height_ratios=[2, 1.5, 1.5], hspace=0.4, wspace=0.3)

    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    times = [start_time + timedelta(minutes=i * ctx["step_min"]) for i in range(len(opti['u']))]

    # Fonction pour formatter les heures de façon lisible
    def format_time_axis(ax):
        """Formate l'axe des temps pour être lisible"""
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))  # Toutes les 4 heures
        ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))  # Marques mineures toutes les heures
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
        ax.tick_params(axis='x', rotation=0, labelsize=8)
        ax.tick_params(axis='x', which='minor', length=3)

    # --- LIGNE 1 : ÉVOLUTION DES TEMPÉRATURES ---
    
    # 1.1 Classique seul
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(times, classic['T'][:-1], color='#e74c3c', linewidth=2, label='Classique')
    ax1.plot(times[::4], ctx["comfort_schedule"][::4], 'k--o', markersize=1, linewidth=1, label='Consigne')
    ax1.set_title('Classique seul', fontsize=12, fontweight='bold', color='#2c3e50')
    ax1.set_ylabel('Température (°C)', fontsize=10)
    ax1.legend(frameon=False, fontsize=8)
    ax1.grid(True, alpha=0.25)
    format_time_axis(ax1)

    # 1.2 Classique + PV
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(times, classic_pv['T'][:-1], color='#f39c12', linewidth=2, label='Classique+PV')
    ax2.plot(times[::4], ctx["comfort_schedule"][::4], 'k--o', markersize=1, linewidth=1, label='Consigne')
    ax2.set_title('Classique + PV', fontsize=12, fontweight='bold', color='#2c3e50')
    ax2.set_ylabel('Température (°C)', fontsize=10)
    ax2.legend(frameon=False, fontsize=8)
    ax2.grid(True, alpha=0.25)
    format_time_axis(ax2)

    # 1.3 Optimisé
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(times, opti['T'][:-1], color='#3498db', linewidth=2, label='Optimisé')
    ax3.plot(times[::4], ctx["comfort_schedule"][::4], 'k--o', markersize=1, linewidth=1, label='Consigne')
    ax3.set_title('Optimisé', fontsize=12, fontweight='bold', color='#2c3e50')
    ax3.set_ylabel('Température (°C)', fontsize=10)
    ax3.legend(frameon=False, fontsize=8)
    ax3.grid(True, alpha=0.25)
    format_time_axis(ax3)

    # --- LIGNE 2 : COMMANDES DE CHAUFFAGE + PV ---
    
    # 2.1 Classique seul + PV
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.step(times, classic['u'], color='#e74c3c', where='post', linewidth=1.5, label='Chauffage')
    ax4.set_title('Classique seul + PV', fontsize=11, fontweight='bold')
    ax4.set_ylabel('État chauffage', fontsize=9)
    ax4.set_ylim(-0.1, 1.2)
    ax4.grid(True, alpha=0.3)
    format_time_axis(ax4)
    
    ax4_pv = ax4.twinx()
    ax4_pv.plot(times, ctx["pv_production"], color='#27ae60', linewidth=1, alpha=0.7, label='PV')
    ax4_pv.set_ylabel('PV (kW)', color='#27ae60', fontsize=8)
    ax4_pv.tick_params(axis='y', labelcolor='#27ae60', labelsize=7)
    # Pas de formatage d'heure sur l'axe secondaire

    # 2.2 Classique + PV
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.step(times, classic_pv['u'], color='#f39c12', where='post', linewidth=1.5, label='Chauffage')
    ax5.set_title('Classique + PV', fontsize=11, fontweight='bold')
    ax5.set_ylabel('État chauffage', fontsize=9)
    ax5.set_ylim(-0.1, 1.2)
    ax5.grid(True, alpha=0.3)
    format_time_axis(ax5)
    
    ax5_pv = ax5.twinx()
    ax5_pv.plot(times, ctx["pv_production"], color='#27ae60', linewidth=1, alpha=0.7, label='PV')
    ax5_pv.set_ylabel('PV (kW)', color='#27ae60', fontsize=8)
    ax5_pv.tick_params(axis='y', labelcolor='#27ae60', labelsize=7)

    # 2.3 Optimisé + PV
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.step(times, opti['u'], color='#3498db', where='post', linewidth=1.5, label='Chauffage')
    ax6.set_title('Optimisé + PV', fontsize=11, fontweight='bold')
    ax6.set_ylabel('État chauffage', fontsize=9)
    ax6.set_ylim(-0.1, 1.2)
    ax6.grid(True, alpha=0.3)
    format_time_axis(ax6)
    
    ax6_pv = ax6.twinx()
    ax6_pv.plot(times, ctx["pv_production"], color='#27ae60', linewidth=1, alpha=0.7, label='PV')
    ax6_pv.set_ylabel('PV (kW)', color='#27ae60', fontsize=8)
    ax6_pv.tick_params(axis='y', labelcolor='#27ae60', labelsize=7)

    # --- LIGNE 3 : COMPARAISONS SYNTHÈSE ---
    
    # 3.1 Répartition énergie
    ax7 = fig.add_subplot(gs[2, 0])
    energy_types = ['HP', 'HC', 'PV']
    
    classic_energy = [classic['metrics']['energy_hp_kwh'], classic['metrics']['energy_hc_kwh'],
                      classic['metrics'].get('pv_used_for_heating_kwh', 0)]
    classic_pv_energy = [classic_pv['metrics']['energy_hp_kwh'], classic_pv['metrics']['energy_hc_kwh'],
                         classic_pv['metrics'].get('pv_used_for_heating_kwh', 0)]
    opti_energy = [opti['metrics']['energy_hp_kwh'], opti['metrics']['energy_hc_kwh'],
                   opti['metrics'].get('pv_used_for_heating_kwh', 0)]

    x = np.arange(len(energy_types))
    width = 0.25
    
    bars1 = ax7.bar(x - width, classic_energy, width, label='Classique', color='#e74c3c', alpha=0.8)
    bars2 = ax7.bar(x, classic_pv_energy, width, label='Classique+PV', color='#f39c12', alpha=0.8)
    bars3 = ax7.bar(x + width, opti_energy, width, label='Optimisé', color='#3498db', alpha=0.8)
    
    ax7.set_title('Répartition Énergie (kWh)', fontsize=11, fontweight='bold')
    ax7.set_ylabel('Énergie (kWh)', fontsize=9)
    ax7.set_xticks(x)
    ax7.set_xticklabels(energy_types, fontsize=9)
    ax7.legend(frameon=False, fontsize=8)
    ax7.grid(axis='y', alpha=0.3)

    # Ajout des valeurs sur les barres
    for bars, values in [(bars1, classic_energy), (bars2, classic_pv_energy), (bars3, opti_energy)]:
        for bar, value in zip(bars, values):
            if value > 0.05:  # Éviter d'afficher les très petites valeurs
                ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=8)

    # 3.2 Répartition coûts
    ax8 = fig.add_subplot(gs[2, 1])
    cost_types = ['Total', 'HP', 'HC']
    
    classic_costs = [classic['metrics']['total_cost_eur'], classic['metrics']['cost_hp_eur'], classic['metrics']['cost_hc_eur']]
    classic_pv_costs = [classic_pv['metrics']['total_cost_eur'], classic_pv['metrics']['cost_hp_eur'], classic_pv['metrics']['cost_hc_eur']]
    opti_costs = [opti['metrics']['total_cost_eur'], opti['metrics']['cost_hp_eur'], opti['metrics']['cost_hc_eur']]

    x_cost = np.arange(len(cost_types))
    
    bars4 = ax8.bar(x_cost - width, classic_costs, width, label='Classique', color='#e74c3c', alpha=0.8)
    bars5 = ax8.bar(x_cost, classic_pv_costs, width, label='Classique+PV', color='#f39c12', alpha=0.8)
    bars6 = ax8.bar(x_cost + width, opti_costs, width, label='Optimisé', color='#3498db', alpha=0.8)
    
    ax8.set_title('Répartition Coûts (€)', fontsize=11, fontweight='bold')
    ax8.set_ylabel('Coût (€)', fontsize=9)
    ax8.set_xticks(x_cost)
    ax8.set_xticklabels(cost_types, fontsize=9)
    ax8.legend(frameon=False, fontsize=8)
    ax8.grid(axis='y', alpha=0.3)

    for bars, values in [(bars4, classic_costs), (bars5, classic_pv_costs), (bars6, opti_costs)]:
        for bar, value in zip(bars, values):
            if value > 0.001:  # Éviter d'afficher 0.000
                ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                        f'{value:.3f}€', ha='center', va='bottom', fontsize=8)

    # 3.3 Tableau synthèse
    ax9 = fig.add_subplot(gs[2, 2])
    ax9.axis('off')

    # Calculs des indicateurs
    puissance = ctx["water_heater"]["puissance_kw"]
    capacite = ctx["water_heater"]["capacite_litres"]
    
    # Économies
    economy_vs_classic_pv = classic_pv['metrics']['total_cost_eur'] - opti['metrics']['total_cost_eur']
    economy_vs_classic = classic['metrics']['total_cost_eur'] - opti['metrics']['total_cost_eur']
    
    economy_percent_pv = (economy_vs_classic_pv / classic_pv['metrics']['total_cost_eur']) * 100 if classic_pv['metrics']['total_cost_eur'] > 0 else 0
    economy_percent_classic = (economy_vs_classic / classic['metrics']['total_cost_eur']) * 100 if classic['metrics']['total_cost_eur'] > 0 else 0

    # Autoconsommation
    auto_cons_classic = classic['metrics'].get('self_consumption_rate', 0)
    auto_cons_classic_pv = classic_pv['metrics'].get('self_consumption_rate', 0)
    auto_cons_opti = opti['metrics'].get('self_consumption_rate', 0)

    # Énergie totale
    energy_classic = classic['metrics']['total_energy_kwh']
    energy_classic_pv = classic_pv['metrics']['total_energy_kwh']
    energy_opti = opti['metrics']['total_energy_kwh']

    HC = ctx["tariffs"]["off_peak_hours"]

    summary_text = (
        f"SYNTHÈSE DES PERFORMANCES\n\n"
        f"COÛT JOURNALIER\n"
        f"Classique: {classic['metrics']['total_cost_eur']:.3f}€\n"
        f"Classique+PV: {classic_pv['metrics']['total_cost_eur']:.3f}€\n"
        f"Optimisé: {opti['metrics']['total_cost_eur']:.3f}€\n"
        f"→ Éco. vs classique: {economy_percent_classic:.1f}%\n"
        f"→ Éco. vs classique+PV: {economy_percent_pv:.1f}%\n\n"
        f"ÉNERGIE TOTALE\n"
        f"Classique: {energy_classic:.1f} kWh\n"
        f"Classique+PV: {energy_classic_pv:.1f} kWh\n"
        f"Optimisé: {energy_opti:.1f} kWh\n\n"
        f"AUTOCONSOMMATION\n"
        f"Classique: {auto_cons_classic:.1f}%\n"
        f"Classique+PV: {auto_cons_classic_pv:.1f}%\n"
        f"Optimisé: {auto_cons_opti:.1f}%\n\n"
        f"PUISSANCE: {puissance} kW - {capacite}L\n"
        f" HC : {HC}"
    )

    ax9.text(0.05, 0.95, summary_text, transform=ax9.transAxes, fontsize=9,
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#f8f9fa', 
             edgecolor='#dee2e6', alpha=0.8), fontfamily='DejaVu Sans Mono', linespacing=1.4)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(f'comparaison_3_strategies_{scenario_name.lower()}.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"✅ Graphique 3 stratégies sauvegardé : comparaison_3_strategies_{scenario_name.lower()}.png")

def run_comparison_optimized_vs_classic():
    scenarios = {"FAMILLE": create_scenario_famille_typique,
                 "BUREAU" : create_scenario_bureau,
                 "SEUL" : create_scenario_personne_seule,
                 "MAISON DE RETRAITE" : create_scenario_maison_retraite
                 }
    comparison_results = {}
    
    for name, scenario_func in scenarios.items():
        ctx = scenario_func()
        success_opti, u_opti, T_opti, metrics_opti = milp_analysis(ctx)
        success_classic, u_classic, T_classic, metrics_classic = simulate_classic_water_heater(ctx)
        success_classic_pv, u_classic_pv, T_classic_pv, metrics_classic_pv = simulate_classic_water_heater_midi(ctx)
        
        if success_opti and success_classic and success_classic_pv:
            comparison_results[name] = {
                'ctx': ctx,
                'optimized': {'u': u_opti, 'T': T_opti, 'metrics': metrics_opti},
                'classic': {'u': u_classic, 'T': T_classic, 'metrics': metrics_classic},
                'classic_pv': {'u': u_classic_pv,'T':T_classic_pv,'metrics': metrics_classic_pv}
            }
            create_comparison_plot(comparison_results[name], name)           
        else:
            print("❌ Échec de l'analyse")
    
    return comparison_results

    """Compare l'optimisation MILP vs système classique avec maintien à 65°C"""
    scenarios = {
        "FAMILLE": create_scenario_famille_typique,
        "PERSONNE_SEULE": create_scenario_personne_seule,
    }
    
    comparison_results = {}
    
    print("🔍 COMPARAISON OPTIMISÉ vs CLASSIQUE (65°C constante)")
    print("=" * 60)
    
    for name, scenario_func in scenarios.items():
        print(f"\n🎯 Scénario: {name}")
        print("-" * 40)
        
        ctx = scenario_func()
        
        # Exécuter l'optimisation MILP
        success_opti, u_opti, T_opti, metrics_opti = milp_analysis(ctx)
        
        # Exécuter le système classique (maintien à 65°C)
        success_classic, u_classic, T_classic, metrics_classic = simulate_classic_water_heater(ctx, maintenance_temp=65.0)
        
        if success_opti and success_classic:
            comparison_results[name] = {
                'ctx': ctx,
                'optimized': {'u': u_opti, 'T': T_opti, 'metrics': metrics_opti},
                'classic': {'u': u_classic, 'T': T_classic, 'metrics': metrics_classic}
            }
            
            # Calculs des différences
            cost_saving = metrics_classic['total_cost_eur'] - metrics_opti['total_cost_eur']
            saving_percent = (cost_saving / metrics_classic['total_cost_eur']) * 100 if metrics_classic['total_cost_eur'] > 0 else 0
            
            energy_saving = metrics_classic['total_energy_kwh'] - metrics_opti['total_energy_kwh']
            energy_percent = (energy_saving / metrics_classic['total_energy_kwh']) * 100 if metrics_classic['total_energy_kwh'] > 0 else 0
            
            auto_cons_opti = metrics_opti.get('self_consumption_rate', 0)
            auto_cons_classic = metrics_classic.get('self_consumption_rate', 0)
            auto_cons_diff = auto_cons_opti - auto_cons_classic
            
            print(f"💰 COÛTS:")
            print(f"   • Optimisé: {metrics_opti['total_cost_eur']:.3f}€")
            print(f"   • Classique: {metrics_classic['total_cost_eur']:.3f}€")
            print(f"   → Économie: {cost_saving:.3f}€ ({saving_percent:.1f}%)")
            
            print(f"⚡ ÉNERGIE:")
            print(f"   • Optimisé: {metrics_opti['total_energy_kwh']:.2f} kWh")
            print(f"   • Classique: {metrics_classic['total_energy_kwh']:.2f} kWh")
            print(f"   → Économie: {energy_saving:.2f} kWh ({energy_percent:.1f}%)")
            
            print(f"🌞 AUTOCONSOMMATION:")
            print(f"   • Optimisé: {auto_cons_opti:.1f}%")
            print(f"   • Classique: {auto_cons_classic:.1f}%")
            print(f"   → Différence: {auto_cons_diff:+.1f}%")
            
            print(f"🌡️  TEMPÉRATURE MOYENNE:")
            print(f"   • Optimisé: {metrics_opti['temperature_avg']:.1f}°C")
            print(f"   • Classique: {metrics_classic['temperature_avg']:.1f}°C")
            print(f"   → Différence: {metrics_opti['temperature_avg'] - metrics_classic['temperature_avg']:+.1f}°C")
            
            print(f"✅ CONFORT:")
            print(f"   • Optimisé: {metrics_opti['comfort_violations']} violations")
            print(f"   • Classique: {metrics_classic['comfort_violations']} violations")
            
            # Générer le graphique comparatif
            create_comparison_plot(comparison_results[name], name)
            
        else:
            print("❌ Échec de l'analyse")
    
    return comparison_results



if __name__ == "__main__":
    results = run_comparison_optimized_vs_classic()
    
