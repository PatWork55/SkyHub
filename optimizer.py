import random
import config
from evtol import EVTOL
from vertiport import Vertiport

def run_month_simulation(num_pads: int, num_garage: int):
    """
    Simule 28 jours complets (Semaine + Week-end) pour une configuration donnée.
    Retourne : Profit Net, Vols, Refus, Crashs
    """
    # Calcul des coûts fixes mensuels (Capex amorti)
    total_capex = (num_pads * config.COST_PAD_BUILD) + (num_garage * config.COST_GARAGE_BUILD)
    monthly_capex = total_capex / config.AMORTIZATION_MONTHS
    # Ajustement au nombre de jours simulés (28 sur 30)
    sim_fixed_cost = monthly_capex * (config.SIM_DURATION_DAYS / 30)

    hub = Vertiport("ParisHub", num_pads, num_garage, verbose=False)
    drone_counter = 1
    flights = 0
    refusals = 0
    
    # Boucle sur les jours
    for day in range(config.SIM_DURATION_DAYS):
        # Détermination du profil (Semaine vs Week-end)
        day_of_week = day % 7
        is_weekend = (day_of_week >= 5) # 0=Lundi ... 5=Samedi
        current_profile = config.PROFILE_WEEKEND if is_weekend else config.PROFILE_WEEKDAY
        
        # Boucle sur les heures (0-23)
        for hour in range(24):
            traffic_intensity = current_profile[hour]
            
            # Boucle sur les minutes
            for _ in range(60):
                # 1. Gestion des Arrivées
                if random.random() < traffic_intensity:
                    # Création d'un drone temporaire pour évaluation
                    temp_drone = EVTOL(f"D{drone_counter}")
                    temp_drone.current_battery = random.randint(config.BATTERY_START_MIN, config.BATTERY_START_MAX)
                    
                    # Le "Videur" vérifie s'il peut entrer
                    if hub.can_accept_drone(temp_drone):
                        # Attribution priorité (20% d'urgences)
                        if random.random() < 0.2: temp_drone.mission_priority = 2
                        else: temp_drone.mission_priority = 0
                        
                        hub.add_to_approach(temp_drone)
                        drone_counter += 1
                    else:
                        refusals += 1 # Client perdu
                
                # 2. Gestion des Départs
                # La demande suit l'offre avec un facteur (0.9)
                departure_prob = traffic_intensity * 0.9
                if random.random() < departure_prob:
                    if hub.dispatch_mission("Taxi", 0):
                        flights += 1
                
                # 3. Mise à jour physique
                hub.update_simulation()

    # Calcul Bilan Financier
    revenue = flights * config.REVENUE_PER_FLIGHT
    var_cost = flights * config.COST_PER_FLIGHT
    crash_cost = hub.crashes * config.COST_CRASH_PENALTY
    
    net_profit = revenue - var_cost - sim_fixed_cost - crash_cost
    
    return net_profit, flights, refusals, hub.crashes

def main():
    print(f"--- 🛡️ SKYHUB OPTIMIZER (Strict Mode) ---")
    print(f"Durée simu : {config.SIM_DURATION_DAYS} jours | Crash Penalty : {config.COST_CRASH_PENALTY:,.0f} €")
    print("-" * 95)
    print(f"{'CONFIG':<18} | {'PROFIT NET':<12} | {'REFUS':<8} | {'CRASHS':<8} | {'ANALYSE'}")
    print("-" * 95)

    best_config = None
    best_profit = -float('inf')

    # Grid Search depuis le fichier config
    for pads in config.SEARCH_PADS: 
        for garage in config.SEARCH_GARAGE:
            
            profit, flights, refused, crashes = run_month_simulation(pads, garage)
            
            status = ""
            if crashes > 0:
                status = "💀 ÉCHEC SÉCU" 
            elif profit > best_profit:
                best_profit = profit
                best_config = (pads, garage)
                status = "⭐ RECORD"
            elif refused > 6000:
                status = "⚠️ SATURATION"
            
            # Affichage filtré (Positif ou significatif)
            if profit > 0 or status != "":
                print(f"Pads={pads} Garage={garage:<2} | {profit:<10,.0f}€ | {refused:<8} | {crashes:<8} | {status}")

    print("-" * 95)
    if best_config:
        print(f"🏆 INFRASTRUCTURE OPTIMALE RECOMMANDÉE :")
        print(f"👉 {best_config[0]} Chargeurs + {best_config[1]} Places de Garage")
        print(f"   Bénéfice Net : {best_profit:,.0f} €")
    else:
        print("❌ Aucune configuration rentable trouvée.")

if __name__ == "__main__":
    main()