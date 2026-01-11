import random
import json
import config
from evtol import EVTOL
from vertiport import Vertiport

def run_month_simulation(num_pads: int, num_garage: int):
    # Calcul des coûts fixes
    total_capex = (num_pads * config.COST_PAD_BUILD) + (num_garage * config.COST_GARAGE_BUILD)
    monthly_capex = total_capex / config.AMORTIZATION_MONTHS
    sim_fixed_cost = monthly_capex * (config.SIM_DURATION_DAYS / 30)

    hub = Vertiport("ParisHub", num_pads, num_garage, verbose=False)
    drone_counter = 1
    flights = 0
    refusals = 0
    
    for day in range(config.SIM_DURATION_DAYS):
        day_of_week = day % 7
        is_weekend = (day_of_week >= 5)
        
        # SÉLECTION DU BON PROFIL
        if is_weekend:
            prof_arr = config.PROFILE_WEEKEND_FLAT
            prof_dep = config.PROFILE_WEEKEND_FLAT
        else:
            prof_arr = config.PROFILE_ARRIVAL_WEEKDAY
            prof_dep = config.PROFILE_DEPARTURE_WEEKDAY
        
        for hour in range(24):
            prob_arrival = prof_arr[hour]
            prob_departure = prof_dep[hour]
            
            for _ in range(60):
                # 1. GESTION DES ARRIVÉES (Selon profil Arrivée)
                if random.random() < prob_arrival:
                    temp_drone = EVTOL(f"D{drone_counter}")
                    temp_drone.current_battery = random.randint(config.BATTERY_START_MIN, config.BATTERY_START_MAX)
                    
                    if hub.can_accept_drone(temp_drone):
                        if random.random() < 0.2: temp_drone.mission_priority = 2
                        else: temp_drone.mission_priority = 0
                        
                        hub.add_to_approach(temp_drone)
                        drone_counter += 1
                    else:
                        refusals += 1
                
                # 2. GESTION DES DÉPARTS (Selon profil Départ - INDÉPENDANT)
                if random.random() < prob_departure:
                    if hub.dispatch_mission("Taxi", 0):
                        flights += 1
                
                # 3. MISE À JOUR
                hub.update_simulation()

    # Bilan
    revenue = flights * config.REVENUE_PER_FLIGHT
    var_cost = flights * config.COST_PER_FLIGHT
    crash_cost = hub.crashes * config.COST_CRASH_PENALTY
    net_profit = revenue - var_cost - sim_fixed_cost - crash_cost
    
    return net_profit, flights, refusals, hub.crashes

def main():
    print(f"--- 🛡️ SKYHUB OPTIMIZER (Mode Pendulaire) ---")
    print(f"Simulation sur {config.SIM_DURATION_DAYS} jours avec profils asymétriques.")
    print("-" * 95)
    print(f"{'CONFIG':<18} | {'PROFIT NET':<12} | {'REFUS':<8} | {'CRASHS':<8} | {'ANALYSE'}")
    print("-" * 95)

    best_config = None
    best_profit = -float('inf')

    for pads in config.SEARCH_PADS: 
        for garage in config.SEARCH_GARAGE:
            profit, flights, refused, crashes = run_month_simulation(pads, garage)
            
            status = ""
            if crashes > 0: status = "💀 ÉCHEC SÉCU" 
            elif profit > best_profit:
                best_profit = profit
                best_config = (pads, garage)
                status = "⭐ RECORD"
            elif refused > 6000: status = "⚠️ SATURATION"
            
            if profit > 0 or status != "":
                print(f"Pads={pads} Garage={garage:<2} | {profit:<10,.0f}€ | {refused:<8} | {crashes:<8} | {status}")

    print("-" * 95)
    if best_config:
        print(f"🏆 INFRASTRUCTURE OPTIMALE : {best_config[0]} Pads + {best_config[1]} Garage")
        
        # SAUVEGARDE
        solution_data = {"num_pads": best_config[0], "num_garage": best_config[1]}
        with open("best_params.json", "w") as f:
            json.dump(solution_data, f)
        print("💾 Sauvegardé dans best_params.json")
    else:
        print("❌ Aucune configuration rentable.")

if __name__ == "__main__":
    main()