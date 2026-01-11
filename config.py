"""
CONFIGURATION GLOBALE - SKYHUB PROJECT (Mode Dynamique)
Les plages de recherche sont calculées automatiquement selon le trafic.
"""
import math
import statistics

# --- 1. PARAMÈTRES DU DRONE (EVTOL) ---
BATTERY_MAX = 100.0             
BATTERY_START_MIN = 15          
BATTERY_START_MAX = 45          
CONSUMPTION_PER_MIN = 2.5       
CHARGE_RATE_PER_MIN = 5.0       

# --- 2. SÉCURITÉ & CONTRÔLE AÉRIEN ---
SAFETY_BUFFER_MIN = 5.0         
AVG_CYCLE_TIME = 15.0           # Temps estimé pour 1 rotation (Charge + Manœuvre)

# --- 3. PARAMÈTRES ÉCONOMIQUES ---
COST_PAD_BUILD = 100000.0       
COST_GARAGE_BUILD = 15000.0     
AMORTIZATION_MONTHS = 60        

REVENUE_PER_FLIGHT = 50.0       
COST_PER_FLIGHT = 15.0          
COST_CRASH_PENALTY = 500000.0   

# --- 4. PARAMÈTRES DE SIMULATION ---
SIM_DURATION_DAYS = 28          

# --- 5. PROFILS DE TRAFIC ---
PROFILE_WEEKDAY = [
    0.05, 0.05, 0.05, 0.10, 0.20, 0.40, 
    0.80, 0.95, 0.90, 0.70, 0.50, 0.40, 
    0.40, 0.40, 0.45, 0.50, 0.60, 0.80, 
    0.95, 0.90, 0.70, 0.50, 0.30, 0.10  
]

PROFILE_WEEKEND = [
    0.10, 0.10, 0.10, 0.05, 0.05, 0.10, 
    0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 
    0.70, 0.70, 0.70, 0.70, 0.70, 0.60, 
    0.50, 0.40, 0.40, 0.30, 0.20, 0.10  
]

# =============================================================================
#  CALCUL AUTOMATIQUE DE L'ESPACE DE RECHERCHE (AUTO-SCALING)
# =============================================================================

def calculate_search_space():
    """
    Analyse les profils de trafic et déduit les bornes min/max logiques
    pour éviter de chercher au hasard.
    """
    # 1. Analyse du Trafic
    # On prend le pire cas (Semaine) pour dimensionner
    avg_prob = statistics.mean(PROFILE_WEEKDAY) # Moyenne (ex: 0.45)
    max_prob = max(PROFILE_WEEKDAY)             # Pic (ex: 0.95)
    
    # 2. Calcul du Flux (Drones par minute)
    # Flux Moyen = 0.45 drone/min
    # Flux Pic = 0.95 drone/min
    
    # 3. Capacité d'un seul Pad (Drones par minute)
    # Si un cycle dure 15 min, un pad traite 1/15 = 0.066 drone/min
    pad_capacity = 1.0 / AVG_CYCLE_TIME
    
    # 4. Estimation des Pads Nécessaires
    # Théorie : Combien de pads pour absorber le flux MOYEN sans garage ?
    pads_for_avg = avg_prob / pad_capacity  # ex: 0.45 / 0.066 = 6.75
    
    # Théorie : Combien de pads pour absorber le flux PIC sans garage ?
    pads_for_peak = max_prob / pad_capacity # ex: 0.95 / 0.066 = 14.25
    
    # DÉCISION INTELLIGENTE :
    # On ne construit jamais pour le Pic absolu (trop cher), on compte sur le garage.
    # On cherche donc entre "Moyenne - un peu" et "Pic atténué".
    
    min_pads_search = math.floor(pads_for_avg * 0.8) # On tente d'être très agressif (sous-dimensionné)
    max_pads_search = math.ceil(pads_for_avg * 1.5)  # On ne va pas jusqu'au pic absolu (trop cher)
    
    # Sécurité : Au moins 1 pad
    if min_pads_search < 1: min_pads_search = 1
    
    # 5. Estimation du Garage Nécessaire
    # Le garage sert de tampon. Plus le trafic est instable, plus il faut de garage.
    # On estime large : de 2x à 10x le nombre de pads min.
    min_garage_search = min_pads_search * 2
    max_garage_search = min_pads_search * 12
    
    # --- GÉNÉRATION DES PLAGES ---
    pads_range = range(min_pads_search, max_pads_search + 1)
    # Pour le garage, on fait des pas de 5 pour aller vite
    garage_range = range(min_garage_search, max_garage_search + 1, 5)
    
    return pads_range, garage_range

# Exécution du calcul automatique au chargement du fichier
SEARCH_PADS, SEARCH_GARAGE = calculate_search_space()

# Optionnel : Affichage pour debug (sera visible au lancement)
print(f"--- CONFIG AUTO-DÉTECTÉE ---")
print(f"Flux Moyen: {statistics.mean(PROFILE_WEEKDAY):.2f}/min | Flux Pic: {max(PROFILE_WEEKDAY):.2f}/min")
print(f"Recherche Pads:   {list(SEARCH_PADS)}")
print(f"Recherche Garage: {list(SEARCH_GARAGE)}")
print("-" * 30)