import config

class EVTOL:
    """
    Représente un drone électrique (eVTOL) autonome.
    Gère son état, sa batterie et ses missions.
    """
    def __init__(self, drone_id: str):
        self.drone_id = drone_id
        
        # États possibles : "EN_VOL", "PRÊT", "EN_RECHARGE", "EN_MAINTENANCE", "AU_REPOS"
        self.status = "EN_VOL" 
        
        self.mission_priority = 0  # 0: Standard, 1: Business, 2: Urgence
        self.current_mission = None 
        
        self.max_battery = config.BATTERY_MAX
        self.current_battery = config.BATTERY_MAX
        
        self.waiting_time = 0

    def go_to_charge(self):
        """ Transition vers l'état de recharge """
        if self.status != "EN_VOL": 
            self.status = "EN_RECHARGE"
            self.waiting_time = 0

    def enter_maintenance(self):
        """ Transition vers le garage (stockage) """
        self.status = "EN_MAINTENANCE"
        self.current_mission = None 
        self.waiting_time = 0

    def set_ready(self):
        """ Transition vers l'état prêt (tarmac) """
        self.status = "PRÊT"
        self.waiting_time = 0

    def assign_mission(self, mission_type: str, priority: int):
        """ Assigne une nouvelle mission et fait décoller le drone """
        if self.status == "EN_MAINTENANCE":
            return 

        self.current_mission = {"type": mission_type, "priority": priority}
        self.status = "EN_VOL"

    def update(self):
        """ Met à jour la batterie et le temps d'attente selon l'état """
        if self.status == "EN_VOL":
            self.current_battery -= config.CONSUMPTION_PER_MIN
            self.waiting_time += 1 
            
        elif self.status == "EN_RECHARGE":
            self.current_battery += config.CHARGE_RATE_PER_MIN
            self.waiting_time = 0 
            
            if self.current_battery >= self.max_battery:
                self.current_battery = self.max_battery
                
        elif self.status in ["EN_MAINTENANCE", "AU_REPOS", "PRÊT"]:
            self.waiting_time += 1 
        
        # Bornage des valeurs de batterie
        if self.current_battery < 0: self.current_battery = 0
        if self.current_battery > self.max_battery: self.current_battery = self.max_battery

    def __str__(self):
        return f"[{self.drone_id}] {self.status} | Bat: {self.current_battery:.1f}%"