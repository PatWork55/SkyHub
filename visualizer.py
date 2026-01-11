import pygame
import sys
from vertiport import Vertiport
import config

# --- COULEURS ---
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)
GREEN = (50, 200, 50)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
ORANGE = (255, 165, 0)

class VertiportVisualizer:
    def __init__(self, width=1200, height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("SkyHub Control Center")
        self.font = pygame.font.SysFont("Arial", 16)
        self.title_font = pygame.font.SysFont("Arial", 22, bold=True)

    def draw_drone(self, x, y, w, h, drone):
        if drone is None:
            pygame.draw.rect(self.screen, GRAY, (x, y, w, h), 1)
            return

        # Couleur selon priorité
        color = WHITE
        if drone.mission_priority == 2: color = RED      
        elif drone.mission_priority == 1: color = BLUE   
        
        pygame.draw.rect(self.screen, color, (x, y, w, h), border_radius=5)
        
        # ID et Batterie
        id_text = self.font.render(drone.drone_id, True, BLACK)
        self.screen.blit(id_text, (x + 5, y + 5))
        
        # Jauge batterie
        bar_width = w - 10
        fill_width = int(bar_width * (drone.current_battery / 100.0))
        bat_color = GREEN if drone.current_battery > 50 else ORANGE if drone.current_battery > 20 else RED
        
        pygame.draw.rect(self.screen, BLACK, (x + 5, y + h - 15, bar_width, 8))
        pygame.draw.rect(self.screen, bat_color, (x + 5, y + h - 15, fill_width, 8))

    def draw(self, vertiport: Vertiport, time_step: int):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill(BLACK)
        title = self.title_font.render(f"{vertiport.name} - STEP {time_step}", True, WHITE)
        self.screen.blit(title, (20, 20))

        # Ciel
        y_offset = 100
        for i, drone in enumerate(vertiport.approach_queue):
            self.draw_drone(20, y_offset + i * 60, 260, 50, drone)

        # Pads
        x_offset = 320
        y_offset = 100
        for i, drone in enumerate(vertiport.charging_pads):
            self.draw_drone(x_offset, y_offset, 160, 80, drone)
            y_offset += 90

        # Garage
        x_offset = 600
        y_offset = 100
        for i, drone in enumerate(vertiport.parking_spots):
            self.draw_drone(x_offset + (i%5)*150, y_offset + (i//5)*70, 140, 60, drone)

        pygame.display.flip()