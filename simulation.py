import json
import random
import pygame 
import config
from vertiport import Vertiport
from visualizer import VertiportVisualizer
from evtol import EVTOL

def run_demo():
    # 1. CHARGEMENT INFRASTRUCTURE
    try:
        with open("best_params.json", "r") as f:
            data = json.load(f)
            PADS = data['num_pads']
            GARAGE = data['num_garage']
            print(f"📂 Infra chargée : {PADS} Pads | {GARAGE} Garage")
    except FileNotFoundError:
        PADS, GARAGE = 6, 20
        print("⚠️ Pas de fichier config, valeurs par défaut.")

    # 2. INITIALISATION
    hub = Vertiport("SkyHub Pendulaire", PADS, GARAGE)
    viz = VertiportVisualizer()
    drone_cnt = 1
    
    clock = pygame.time.Clock()
    FPS = 20 

    print(f"--- DÉMARRAGE SIMULATION (Profil Asymétrique) ---")
    
    for minute in range(1440):
        clock.tick(FPS)
        if pygame.event.peek(pygame.QUIT): break

        # 1. TEMPS ET PROFILS
        current_hour = (minute // 60) % 24
        
        # On pioche dans les listes séparées
        prob_arrival = config.PROFILE_ARRIVAL_WEEKDAY[current_hour]
        prob_departure = config.PROFILE_DEPARTURE_WEEKDAY[current_hour]
        
        # ---------------------------------
        # GESTION DES ARRIVÉES
        if random.random() < prob_arrival:
            d = EVTOL(f"D{drone_cnt:03d}")
            d.current_battery = random.randint(config.BATTERY_START_MIN, config.BATTERY_START_MAX)
            
            if hub.can_accept_drone(d):
                hub.add_to_approach(d)
                drone_cnt += 1

        # ---------------------------------
        # GESTION DES DÉPARTS (Indépendante des arrivées !)
        if random.random() < prob_departure:
            hub.dispatch_mission("Taxi", 0)

        # ---------------------------------
        hub.update_simulation()
        viz.draw(hub, minute)

if __name__ == "__main__":
    run_demo()