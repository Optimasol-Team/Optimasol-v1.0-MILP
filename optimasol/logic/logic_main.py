import numpy as np
import matplotlib.pyplot as plt
import random as rd
from math import sqrt
import itertools
import time
from scipy.signal import savgol_filter
import matplotlib.ticker as ticker

start_time = time.time()
class parameter_client:
    def __init__(self, Tamb, P, volume, k, max_temp, liste_point, pente_n, horaire, douche,n, t0):
        self.Tamb = Tamb
        self.P = P
        self.volume = volume
        self.k = k
        self.max = max_temp
        self.points = liste_point
        self.pente_positive = P / 4.18 / volume
        self.pente_negative = pente_n
        self.douche = douche
        self.horaire = horaire
        self.n = n
        self.t0 = t0



def temperature(liste, t0, hyperpara):
    positions = [t0]
    for i in range(len(liste)):
        if liste[i]:
            positions.append(positions[-1] + hyperpara.pente_positive)
        else:
            positions.append(positions[-1] + hyperpara.pente_negative)
        for elt in hyperpara.horaire :
            if elt >= i*24/hyperpara.n and elt <= (i+1)*24/hyperpara.n  :
                positions[-1] -= hyperpara.douche
    return positions

def intervalle (liste_points,hyperpara):
    # va te sortir une liste avec dedans le i tel que i<liste_point[j]*n/24<i+1
    pas = 24/hyperpara.n
    liste = [0]
    for elt in liste_points:
        for i in range(hyperpara.n):
            heure = i*pas
            if elt < heure :
                liste.append(i-1)
                break
    liste.append(hyperpara.n-1)
    return liste


def choix(temp, hyperpara):
    contrainte = hyperpara.points # liste_de_point = {7: 65, 19: 65}
    interv = intervalle(contrainte,hyperpara)
    liste = []
    for point in contrainte.key():
        for i in range(len(temp)):
            if point >= i*24/hyperpara.n and point < (i+1)*24/hyperpara.n:
                if temp[i]< contrainte[point]:
                    break
                else : liste.append(temp)
    return liste











def integrale(liste,n):
    som = 0
    for elt in liste :
        som+= elt*24/n
    return som

def fitness (liste,tarifs,hyperpara):
    pas = 24/len(liste  )
    for elt in liste :
        if x==1 :
            x=1



def choix_possibilité(combinaisons,hyperpara):
    contrainte = hyperpara.points # liste_de_point = {7: 65, 19: 65}
    contrainte_values = [0]+list(contrainte.values())+[0]
    t0 = hyperpara.t0
    interv = intervalle(contrainte,hyperpara)
    positions = [] # population
    conbi = []
    for elmt in combinaisons :
        elt = list(elmt)
        position = [t0] # individu

        for j in range(len(interv)-1):
                for k in range(interv[j],interv[j+1]): # on parcours par intervalle
                    if elt[k]==1:
                        position.append(position[-1] + hyperpara.pente_positive)
                    else:
                        position.append(position[-1] + hyperpara.pente_negative)
                    for horaire in hyperpara.horaire : # on le changera plus tard en utilisant la fonction intervale
                        if horaire >= k*24/hyperpara.n and horaire < (k+1)*24/hyperpara.n :
                            position[-1] -= hyperpara.douche
                    if position[-1]< contrainte_values[j]:
                        rejete = elt #et vérifie à chaque fois si ca respecte la contrainte sinon rien ne sert de continuer
                        break
        if elt != rejete:
            conbi.append(elt)
            positions.append(position)

    return conbi, positions



def calculer_cout(combination,hyperpara,production_pv, tarifs, puissance_chauffage, prix_vente_pv=0.05):
    cout_total = 0.0
    revenu_vente_pv = 0.0
    nombre_intervalles = len(combination)
    duree_ival = 24 / nombre_intervalles

    for i in range(nombre_intervalles):
        etat_chauffage = combination[i]
        instant_heure = i* 24/ hyperpara.n
        prix_kwh = trouver_prix_kwh(instant_heure, tarifs)

        # Energie consommée par le chauffage pendant l'intervalle (en kWh)
        energie_chauffage_kwh = etat_chauffage * puissance_chauffage * duree_ival / 1000

        # Production photovoltaïque pendant l'intervalle (en kWh)
        index_pv = int(i * len(production_pv) / nombre_intervalles)
        production_watt = production_pv[min(index_pv, len(production_pv) - 1)]
        production_pv_kwh = production_watt * duree_ival / 1000

        # Calcul de la consommation réseau et du surplus PV
        consommation_reseau_kwh = max(0, energie_chauffage_kwh - production_pv_kwh)
        surplus_pv_kwh = max(0, production_pv_kwh - energie_chauffage_kwh)

        # Mise à jour du coût total et du revenu de vente PV
        cout_total += consommation_reseau_kwh * prix_kwh
        revenu_vente_pv += surplus_pv_kwh * prix_vente_pv

    return cout_total - revenu_vente_pv


def heure_str_to_float(horaire):
    heures_str, minutes_str = horaire.split(":")
    return int(heures_str) + int(minutes_str) / 60

def trouver_prix(instant, tarifs, duree):
    def dans_intervalle(h, debut, fin):
        if debut <= fin:
            return debut <= h < fin
        else:
            return h >= debut or h < fin # si de 22h à 3 h par ex

    for periode in tarifs:
        debut = heure_str_to_float(periode["debut"])
        fin = heure_str_to_float(periode["fin"])
        if dans_intervalle(instant, debut, fin):
            return periode["prix"]
    return 0.0 # Ou None, ou lever une exception

#============================== Essaie ===========================================================================

tarifs = [
    {"type": "creuse", "debut": "22:00", "fin": "06:00", "prix": 0.12},
    {"type": "pleine", "debut": "06:00", "fin": "22:00", "prix": 0.15},
    # ... d'autres périodes potentielles
]

n = 18 # toute les 1h30 à voir pour changer en fonction du temps que me le programme
t0 = 50
liste_de_point = {7: 65, 19: 65}
para_c = parameter_client(20, 2500, 200, 0.5, 80, liste_de_point, -0.2, [7, 20], 7,n,60)

Production = np.array([
    0.0, 0.01, 0.04, 0.10, 0.22, 0.40, 0.60, 0.75,
    0.75, 0.60, 0.40, 0.22, 0.10, 0.04, 0.01, 0.0
]) * 1000  # en Watts

# ma production dit avoir le même nombre de points
combinaisons = [comb for comb in itertools.product([0, 1], repeat=n-1)]
#température = [temperature(combi) for combi in combinaisons]
#tri_pas_optimal = [choix(temp, para_c) for temp in température]
trie = choix_possibilité(combinaisons,para_c)
print("avant trie, nb de combinaison :",len(combinaisons))
print('après trie, nb de combinaison:',len(trie[0]))

#combinaisons = [[list(comb), temperature(comb, t0, para_c)] for comb in itertools.product([0, 1], repeat=n-1)]
#example_combination = [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0]
#courbe = temperature(example_combination, t0, para_c)

example_combination = trie[0][0]


courbe = trie[1][0]

end_time = time.time()
executive_time = end_time-start_time
print("temps d'exectution :", executive_time, "s")

X = [i * 1.5 for i in range(len(courbe))]
fig, axs = plt.subplots(2, 2, figsize=(10, 6)) # Augmentation de la largeur de la figure

print()

# 1
axs[0, 0].plot(X, courbe, '.', markersize=8, label='Points de température') # Affichage des points
axs[0, 0].plot(X, courbe, '-', linewidth=2, label='Évolution de la température') # Affichage de la courbe lissée
axs[0, 0].set_xlabel('Temps (heure)')
axs[0, 0].set_ylabel('Température (°C)')
axs[0, 0].set_title('Évolution de la température dans le cumulus ')
axs[0, 0].legend()
axs[0, 0].grid(True)
axs[0, 0].tick_params(axis='x')
axs[0, 0].locator_params(axis='x', nbins=8)
axs[0, 0].tick_params(axis='y')
axs[0, 0].xaxis.set_major_formatter(ticker.ScalarFormatter()) # Force l'utilisation du formateur scalaire par défaut
axs[0, 0].set_ylim(min(courbe) - 5, max(courbe) + 5) # Ajustement des limites de l'axe Y pour inclure y=0 (si nécessaire)

#2
Production_cumulus = np.array([
    0.0, 0.01, 0.04, 0.10, 0.22, 0.40, 0.60, 0.75,
    0.75, 0.60, 0.40, 0.22, 0.10, 0.04, 0.01, 0.0
]) * 1000  # en Watts
temps_pv = np.linspace(0, 24, len(Production_cumulus))
production_pv = np.zeros_like(temps_pv)
peak_production = 2000
midday_hour = 12


# Simulation simple d'une courbe en cloche (sinusoïdale positive)
production_pv = peak_production * np.sin(np.pi * (temps_pv - 6) / 12)
production_pv[production_pv < 0] = 0 # La production ne peut pas être négative

axs[0, 1].plot(temps_pv, production_pv, color='orange', label='Production Photovoltaïque')
axs[0, 1].set_xlabel('Temps (heure)')
axs[0, 1].set_ylabel('Production (W)')
axs[0, 1].set_title('Simulation de Production Photovoltaïque')
axs[0, 1].legend()
axs[0, 1].grid(True)
axs[0, 1].tick_params(axis='x', rotation=45)
axs[0, 1].xaxis.set_major_formatter(ticker.ScalarFormatter())
axs[0, 1].tick_params(axis='y')


# 3
axs[1, 0].step(X[:len(example_combination)], example_combination, where='post', label='État') # Utilisation du bon index et ajustement de la longueur de X
axs[1, 0].set_xlabel('Temps (heure)')
axs[1, 0].set_ylabel('État (0: Éteint, 1: Allumé)')
axs[1, 0].set_title('État du cumulus ')
axs[1, 0].set_yticks([0, 1])
axs[1, 0].set_yticklabels(['Éteint', 'Allumé'])
axs[1, 0].grid(True, which='major', axis='y', linestyle='--')
axs[1, 0].legend()



plt.tight_layout()
plt.show()

