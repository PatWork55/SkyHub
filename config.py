"""
CONFIGURATION GLOBALE - SKYHUB PROJECT (Mode Pendulaire)
Profils distincts pour les arrivées (Matin) et les départs (Soir).
"""
import math
import statistics

# --- 1. PARAMÈTRES DU DRONE (EVTOL) ---
BATTERY_MAX = 100.0             
BATTERY_START_MIN = 15     # Batterie min à l'arrivée (%)     
BATTERY_START_MAX = 45     # Batterie max à l'arrivée (%)       
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

# --- 5. PROFILS DE TRAFIC (ARRIVÉES vs DÉPARTS) ---

# ARRIVÉES (Semaine) : Gros pic le matin (07h-09h), calme le soir
PROFILE_ARRIVAL_WEEKDAY = [
    0.05, 0.05, 0.05, 0.10, 0.20, 0.50,  # 00-05h
    0.95, 0.95, 0.80, 0.60, 0.40, 0.30,  # 06-11h (RUSH MATIN)
    0.30, 0.30, 0.30, 0.30, 0.40, 0.40,  # 12-17h
    0.40, 0.30, 0.20, 0.10, 0.05, 0.05   # 18-23h
]

# DÉPARTS (Semaine) : Calme le matin, Gros pic le soir (17h-19h)
PROFILE_DEPARTURE_WEEKDAY = [
    0.05, 0.05, 0.05, 0.05, 0.10, 0.20,  # 00-05h
    0.30, 0.40, 0.30, 0.30, 0.30, 0.40,  # 06-11h
    0.40, 0.50, 0.60, 0.80, 0.95, 0.95,  # 12-17h (RUSH SOIR)
    0.90, 0.70, 0.50, 0.20, 0.10, 0.05   # 18-23h
]

# Week-end (Plus équilibré)
PROFILE_WEEKEND_FLAT = [0.2] * 24 

# =============================================================================
#  CALCUL AUTOMATIQUE DE L'ESPACE DE RECHERCHE
# =============================================================================

def calculate_search_space():
    """
    Dimensionne l'infra en se basant sur le pire cas d'ARRIVÉE (car c'est ça qui bouche les pads).
    """
    # On dimensionne les pads sur le pic d'arrivée
    avg_prob = statistics.mean(PROFILE_ARRIVAL_WEEKDAY)
    max_prob = max(PROFILE_ARRIVAL_WEEKDAY)
    
    pad_capacity = 1.0 / AVG_CYCLE_TIME
    pads_for_avg = avg_prob / pad_capacity  
    
    min_pads_search = math.floor(pads_for_avg * 0.8) 
    max_pads_search = math.ceil(pads_for_avg * 1.5) 
    
    if min_pads_search < 1: min_pads_search = 1
    
    # Le garage est crucial ici car on stocke les drones du matin jusqu'au soir
    min_garage_search = min_pads_search * 3  # On augmente le ratio garage
    max_garage_search = min_pads_search * 15
    
    pads_range = range(min_pads_search, max_pads_search + 1)
    garage_range = range(min_garage_search, max_garage_search + 1, 5)
    
    return pads_range, garage_range

SEARCH_PADS, SEARCH_GARAGE = calculate_search_space()

if __name__ == "__main__":
    print(f"--- CONFIG AUTO-DÉTECTÉE (ASYMÉTRIQUE) ---")
    print(f"Pic Arrivée: {max(PROFILE_ARRIVAL_WEEKDAY):.2f} | Pic Départ: {max(PROFILE_DEPARTURE_WEEKDAY):.2f}")
    print(f"Recherche Pads:   {list(SEARCH_PADS)}")
    print(f"Recherche Garage: {list(SEARCH_GARAGE)}")