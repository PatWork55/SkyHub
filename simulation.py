import time
import random
import config
from evtol import EVTOL
from vertiport import Vertiport
from visualizer import VertiportVisualizer

def run_demo():
    # CONFIGURATION GAGNANTE
    PADS = 7
    GARAGE = 20
    
    hub = Vertiport("SkyHub Paris (Demo)", PADS, GARAGE, verbose=True)
    viz = VertiportVisualizer()
    drone_cnt = 1
    
    print(f"--- DÉMARRAGE DÉMO ({PADS} Pads / {GARAGE} Garage) ---")
    
    # On simule un "Rush Hour" (Matin)
    for minute in range(600):
        # Ralentir pour voir l'animation
        # time.sleep(0.1) 
        
        # Trafic intense (0.9)
        if random.random() < 0.9:
            d = EVTOL(f"D{drone_cnt:03d}")
            d.current_battery = random.randint(15, 45)
            
            if hub.can_accept_drone(d):
                hub.add_to_approach(d)
                drone_cnt += 1
            else:
                print(f"⛔ REFUS ACCÈS : Vertiport saturé")

        if random.random() < 0.8:
            hub.dispatch_mission("Taxi", 0)

        hub.update_simulation()
        viz.draw(hub, minute)

if __name__ == "__main__":
    run_demo()