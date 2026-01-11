import pygame
import sys
import config  # Nécessaire pour afficher le % de trafic du profil
from vertiport import Vertiport

# --- PALETTE DE COULEURS (Style Control Center) ---
COLOR_BG = (15, 20, 30)         # Bleu nuit profond (Fond)
COLOR_GRID = (30, 40, 50)       # Lignes de grille discrètes
COLOR_TEXT = (200, 200, 200)    # Blanc cassé (Texte principal)
COLOR_ACCENT = (0, 255, 200)    # Cyan (Bordures et Titres)

# Couleurs des Drones
COLOR_DRONE_BODY = (240, 240, 240)
COLOR_PRIORITY_HIGH = (255, 50, 50)   # Rouge (Priorité Urgente)
COLOR_PRIORITY_STD = (50, 150, 255)   # Bleu (Standard)
COLOR_BATTERY_LOW = (255, 100, 0)     # Orange
COLOR_BATTERY_OK = (50, 200, 50)      # Vert

class VertiportVisualizer:
    def __init__(self, width=1600, height=950):
        pygame.init()
        # On augmente la taille de la fenêtre pour tout faire rentrer
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("SkyHub Control Center v2.0")
        
        # Polices d'écriture (Monospace pour bien aligner les chiffres)
        self.font_title = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_label = pygame.font.SysFont("Consolas", 18)
        self.font_small = pygame.font.SysFont("Consolas", 12)

    def draw_grid(self):
        """Dessine une grille technique en arrière-plan"""
        w, h = self.screen.get_size()
        for x in range(0, w, 40):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, h))
        for y in range(0, h, 40):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (w, y))

    def draw_drone_icon(self, center_x, center_y, drone):
        """Dessine un drone stylisé (Cercle + Hélices)"""
        if drone is None:
            return

        # 1. Couleur du Halo selon la priorité
        glow_color = COLOR_PRIORITY_HIGH if drone.mission_priority == 2 else COLOR_PRIORITY_STD
        
        # 2. Hélices (Forme en X)
        size = 15
        pygame.draw.line(self.screen, glow_color, (center_x-size, center_y-size), (center_x+size, center_y+size), 3)
        pygame.draw.line(self.screen, glow_color, (center_x-size, center_y+size), (center_x+size, center_y-size), 3)
        
        # 3. Corps du drone (Cercle)
        pygame.draw.circle(self.screen, COLOR_DRONE_BODY, (center_x, center_y), 10)
        
        # 4. Barre de batterie (Sous le drone)
        bat_pct = drone.current_battery / 100.0
        bat_color = COLOR_BATTERY_OK if drone.current_battery > 30 else COLOR_BATTERY_LOW
        
        # Fond noir de la jauge
        pygame.draw.rect(self.screen, (0,0,0), (center_x-15, center_y+18, 30, 5))
        # Niveau de batterie
        pygame.draw.rect(self.screen, bat_color, (center_x-15, center_y+18, 30 * bat_pct, 5))

        # 5. ID du Drone
        text = self.font_small.render(drone.drone_id, True, COLOR_TEXT)
        self.screen.blit(text, (center_x - text.get_width()//2, center_y - 25))

    def draw_section(self, title, x, y, w, h, items, layout="grid"):
        """Dessine un conteneur (File d'attente, Pads ou Garage)"""
        # Bordure Cadre
        pygame.draw.rect(self.screen, COLOR_ACCENT, (x, y, w, h), 1, border_radius=8)
        
        # Titre avec fond
        pygame.draw.rect(self.screen, (20, 30, 40), (x+10, y-12, 220, 24))
        count = len([i for i in items if i]) # Compte les slots occupés
        total = len(items)
        title_surf = self.font_label.render(f"{title} ({count}/{total})", True, COLOR_ACCENT)
        self.screen.blit(title_surf, (x+20, y-10))

        # Dessin des emplacements
        padding = 10
        
        if layout == "vertical": # Pour la file d'attente (Queue)
            slot_h = 60
            for i, drone in enumerate(items):
                slot_y = y + 40 + i * slot_h
                # Si la file est trop longue pour l'écran, on arrête d'afficher
                if slot_y + 50 > y + h: break 
                
                # Cadre du slot
                pygame.draw.rect(self.screen, COLOR_GRID, (x+padding, slot_y, w-2*padding, 50), 1, border_radius=4)
                if drone:
                    self.draw_drone_icon(x + w//2, slot_y + 25, drone)
        
        elif layout == "grid": # Pour Pads et Garage
            # Calcul automatique des colonnes
            # MODIFICATION ICI : On passe à 10 colonnes pour le Garage pour qu'il soit plus large que haut
            cols = 10 if title == "PARKING / GARAGE" else 6
            
            slot_w = (w - (cols+1)*padding) // cols
            slot_h = 60
            
            for i, drone in enumerate(items):
                r = i // cols
                c = i % cols
                slot_x = x + padding + c*(slot_w + padding)
                slot_y = y + 40 + r*(slot_h + padding)
                
                # Si ça dépasse du cadre, on arrête
                if slot_y + slot_h > y + h: break

                # Slot vide (fond gris foncé)
                pygame.draw.rect(self.screen, (25, 30, 40), (slot_x, slot_y, slot_w, slot_h), border_radius=4)
                pygame.draw.rect(self.screen, COLOR_GRID, (slot_x, slot_y, slot_w, slot_h), 1, border_radius=4)
                
                # Numéro du slot (P1, G1...)
                prefix = "P" if title == "CHARGING PADS" else "G"
                label = self.font_small.render(f"{prefix}{i+1}", True, (60, 70, 80))
                self.screen.blit(label, (slot_x+5, slot_y+5))

                if drone:
                    self.draw_drone_icon(slot_x + slot_w//2, slot_y + slot_h//2, drone)

    def draw(self, vertiport: Vertiport, time_step: int):
        # Gestion des événements (Pour ne pas que la fenêtre plante)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 1. Arrière-plan
        self.screen.fill(COLOR_BG)
        self.draw_grid()

        # 2. Calcul du temps (Conversion Minute -> Heure:Minute)
        hour = (time_step // 60) % 24
        minute = time_step % 60
        time_str = f"{hour:02d}:{minute:02d}"

        # 3. Récupération des profils de trafic (si disponible dans config)
        try:
            pct_arr = config.PROFILE_ARRIVAL_WEEKDAY[hour] * 100
            pct_dep = config.PROFILE_DEPARTURE_WEEKDAY[hour] * 100
            traffic_text = f"IN: {pct_arr:.0f}% | OUT: {pct_dep:.0f}%"
        except:
            traffic_text = "TRAFFIC: N/A"

        # 4. En-tête (Header)
        header_text = f"SKYHUB OPTIMIZER | TIME: {time_str} | {traffic_text}"
        self.screen.blit(self.font_title.render(header_text, True, COLOR_TEXT), (20, 20))

        # 5. Dessin des Sections (LAYOUT REVU)
        
        # --- GAUCHE : File d'attente (Airspace) ---
        # x=20, Largeur=250, Hauteur=850 (Toute la hauteur dispo)
        self.draw_section("APPROACH QUEUE", 20, 80, 250, 850, vertiport.approach_queue, layout="vertical")
        
        # --- CENTRE HAUT : Pads de charge ---
        # x=290, Largeur=900, Hauteur=300
        self.draw_section("CHARGING PADS", 290, 80, 900, 300, vertiport.charging_pads, layout="grid")
        
        # --- CENTRE BAS : Garage (Beaucoup plus large) ---
        # x=290, y=400, Largeur=900, Hauteur=530
        self.draw_section("PARKING / GARAGE", 290, 400, 900, 530, vertiport.parking_spots, layout="grid")
        
        # --- DROITE : Statistiques en temps réel ---
        # x=1210, Largeur=370
        pygame.draw.rect(self.screen, COLOR_GRID, (1210, 80, 370, 300), 1)
        stat_title = self.font_label.render("LIVE STATISTICS", True, COLOR_ACCENT)
        self.screen.blit(stat_title, (1220, 90))
        
        # Données dynamiques
        waiting = len(vertiport.approach_queue)
        charging = sum(1 for d in vertiport.charging_pads if d)
        parked = sum(1 for d in vertiport.parking_spots if d)
        
        stats = [
            f"Drones in Airspace : {waiting}",
            f"Active Charging    : {charging} / {vertiport.num_charging_pads}",
            f"Garage Occupancy   : {parked} / {vertiport.num_parking_spots}",
            f"Total Fleet        : {waiting + charging + parked}",
            f"Simulation Speed   : 20 min/sec" 
        ]
        
        for i, line in enumerate(stats):
            s = self.font_label.render(f"> {line}", True, COLOR_TEXT)
            self.screen.blit(s, (1220, 130 + i*30))

        pygame.display.flip()