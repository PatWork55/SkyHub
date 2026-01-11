import math
import config
from evtol import EVTOL

class Vertiport:
    """
    Gère l'infrastructure (Pads, Garage, Ciel) et le contrôle aérien.
    """
    def __init__(self, name: str, num_charging_pads: int, num_parking_spots: int, verbose: bool = True):
        self.name = name
        self.num_charging_pads = num_charging_pads
        self.num_parking_spots = num_parking_spots
        self.verbose = verbose
        
        self.crashes = 0 
        
        # Initialisation des zones de stockage
        self.charging_pads = [None] * num_charging_pads 
        self.parking_spots = [None] * num_parking_spots
        self.approach_queue = []

    def log(self, message: str):
        """ Wrapper pour print, activé seulement si verbose=True """
        if self.verbose:
            print(message)

    def can_accept_drone(self, incoming_drone: EVTOL) -> bool:
        """
        CONTRÔLEUR AÉRIEN PRÉDICTIF (STRICT)
        Décide si un drone peut entrer dans l'espace aérien du Vertiport.
        Retourne True si accepté, False si refusé (risque de crash ou saturation).
        """
        # 1. Vérification Physique (Capacité de stockage)
        # On compte tous les drones présents (Ciel + Pads + Garage)
        occupants_total = len(self.approach_queue) + \
                          len([d for d in self.charging_pads if d]) + \
                          len([d for d in self.parking_spots if d])
        
        capacity_total = self.num_charging_pads + self.num_parking_spots
        
        # Règle : On garde toujours 1 place tampon pour éviter le blocage (deadlock)
        if occupants_total >= (capacity_total - 1):
            return False 

        # 2. Vérification Temporelle (Autonomie vs Attente estimée)
        flight_time_remaining = incoming_drone.current_battery / config.CONSUMPTION_PER_MIN
        
        # Estimation du débit du Vertiport
        # Hypothèse : Temps moyen de rotation sur un pad = 15 min
        avg_cycle_time = 15.0 
        throughput_per_min = self.num_charging_pads / avg_cycle_time
        
        # Temps d'attente estimé dans la file
        queue_size = len(self.approach_queue)
        estimated_wait_time = queue_size / throughput_per_min if throughput_per_min > 0 else 999
        
        # Règle : Le temps d'attente doit être inférieur à l'autonomie moins la marge de sécurité
        if estimated_wait_time > (flight_time_remaining - config.SAFETY_BUFFER_MIN):
            return False 

        return True 

    def add_to_approach(self, evtol: EVTOL):
        """ Ajoute un drone validé dans la file d'attente """
        type_str = "URGENCE" if evtol.mission_priority == 2 else "PASSAGERS" if evtol.mission_priority == 1 else "VIDE"
        self.log(f"📡 RADAR: {evtol.drone_id} ({type_str}) demande l'atterrissage.")
        evtol.status = "EN_VOL"
        self.approach_queue.append(evtol)

    def find_free_index(self, location_list: list) -> int:
        """ Trouve le premier index vide dans une liste """
        for i in range(len(location_list)):
            if location_list[i] is None:
                return i
        return -1

    def optimize_fleet_position(self):
        """ Algorithme de 'Valet' : Déplace les drones entre Garage et Pads """
        
        # A. Garage -> Pad (Libérer une place de garage pour ceux qui atterrissent)
        free_garage_idx = self.find_free_index(self.parking_spots)
        if free_garage_idx != -1:
            is_traffic_jam = len(self.approach_queue) > 0
            battery_threshold = 60.0 if is_traffic_jam else 99.0
            
            best_candidate = None
            best_pad_idx = -1
            max_battery = -1

            # On cherche le drone le plus chargé sur les pads pour le garer
            for i, drone in enumerate(self.charging_pads):
                if drone and drone.current_battery >= battery_threshold:
                    if drone.current_battery > max_battery:
                        max_battery = drone.current_battery
                        best_candidate = drone
                        best_pad_idx = i
            
            if best_candidate:
                self.parking_spots[free_garage_idx] = best_candidate
                self.charging_pads[best_pad_idx] = None 
                best_candidate.status = "AU_REPOS"
                self.log(f"♻️ DÉLESTAGE : {best_candidate.drone_id} déplacé vers Garage.")
                return 

        # B. Pad -> Garage (Recharger les drones vides du garage)
        free_pad_idx = self.find_free_index(self.charging_pads)
        if free_pad_idx != -1:
            candidate_to_charge = None
            garage_idx = -1
            min_battery = 101 
            
            for i, drone in enumerate(self.parking_spots):
                if drone and drone.current_battery < 100:
                    if drone.current_battery < min_battery:
                        min_battery = drone.current_battery
                        candidate_to_charge = drone
                        garage_idx = i
            
            if candidate_to_charge:
                self.charging_pads[free_pad_idx] = candidate_to_charge
                self.parking_spots[garage_idx] = None
                candidate_to_charge.go_to_charge()
                self.log(f"🔌 RECHARGE : {candidate_to_charge.drone_id} sort du garage.")

    def run_landing_logic(self):
        """ Gère l'atterrissage prioritaire """
        if not self.approach_queue:
            return

        # Tri : Priorité > Batterie Faible
        self.approach_queue.sort(key=lambda d: (-d.mission_priority, d.current_battery))
        landing_drone = self.approach_queue[0] 

        # 1. Essai Pad
        pad_index = self.find_free_index(self.charging_pads)
        if pad_index != -1:
            self.approach_queue.pop(0) 
            self.charging_pads[pad_index] = landing_drone
            landing_drone.status = "EN_RECHARGE"
            self.log(f"⬇️ ATTERRISSAGE (Charge) : {landing_drone.drone_id}")
            return

        # 2. Essai Garage (Si urgence ou passagers)
        garage_index = self.find_free_index(self.parking_spots)
        if garage_index != -1 and (landing_drone.mission_priority > 0 or landing_drone.current_battery < 15):
            self.approach_queue.pop(0) 
            self.parking_spots[garage_index] = landing_drone
            landing_drone.status = "AU_REPOS"
            self.log(f"⬇️ ATTERRISSAGE (Sécurité) : {landing_drone.drone_id}")
            return

    def dispatch_mission(self, mission_type: str, priority: int) -> bool:
        """ Trouve le meilleur drone disponible pour une mission """
        self.log(f"🔔 COMMANDE : Recherche drone pour '{mission_type}' (Prio: {priority})")
        
        best_drone = None
        origin_list = None
        origin_index = -1
        
        # Seuil minimum de batterie pour partir
        min_bat_req = 30 if priority == 2 else 50

        # Recherche dans les deux zones
        for current_list in [self.charging_pads, self.parking_spots]:
            for i, d in enumerate(current_list):
                if d and d.current_battery >= min_bat_req:
                    if best_drone is None or d.current_battery > best_drone.current_battery:
                        best_drone = d
                        origin_list = current_list
                        origin_index = i
        
        if best_drone:
            self.log(f"🛫 DÉCOLLAGE : {best_drone.drone_id}")
            best_drone.assign_mission(mission_type, priority)
            origin_list[origin_index] = None 
            return True
        else:
            self.log(f"❌ ÉCHEC : Flotte indisponible.")
            return False

    def update_simulation(self):
        """ Mise à jour d'un tick de simulation """
        # Mise à jour des entités
        for d in self.approach_queue: d.update()
        for d in self.charging_pads: 
            if d: d.update()
        for d in self.parking_spots:
            if d: 
                if d.status != "AU_REPOS": d.status = "AU_REPOS"
                d.update()

        # Vérification des Crashs (Audit)
        crashed = [d for d in self.approach_queue if d.current_battery <= 0]
        for d in crashed:
            self.log(f"🔥 CRASH AÉRIEN : {d.drone_id} s'est écrasé !")
            self.crashes += 1 
            self.approach_queue.remove(d)

        # Logique de gestion
        self.optimize_fleet_position()
        self.run_landing_logic()