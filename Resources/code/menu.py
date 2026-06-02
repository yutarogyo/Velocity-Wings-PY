import pygame
import sys
import os
import math
from settings import *
from sprites import BG, Ground  

class MainMenu:
    def __init__(self, display_surface):
        self.display_surface = display_surface
        
        # Path management
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        def get_path(*path_parts):
            return os.path.join(BASE_DIR, *path_parts)

        # Background management (Moving background)
        self.menu_sprites = pygame.sprite.Group()
        bg_path = get_path('..', 'graphics', 'environment', 'background.png')
        bg_height = pygame.image.load(bg_path).get_height()
        scale_factor = WINDOW_HEIGHT / bg_height

        self.bg = BG(self.menu_sprites, scale_factor)
        self.ground = Ground(self.menu_sprites, scale_factor)

        # Animation state
        self.timer = 0
        self.cat_frames = []
        for i in range(3):
            cat_path = get_path('..', 'graphics', 'plane', f'cat{i}.png')
            surf = pygame.image.load(cat_path).convert_alpha()
            scaled_surf = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * (scale_factor / 2.0))
            self.cat_frames.append(scaled_surf)
        
        self.cat_index = 0
        self.cat_surf = self.cat_frames[self.cat_index]
        self.cat_rect = self.cat_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 30))

        # TAP Button graphic
        tap_path = get_path('..', 'graphics', 'plane', 'TAP.png')
        if not os.path.exists(tap_path):
            tap_path = get_path('..', 'graphics', 'obstacles', 'Tag.png')
            
        try:
            self.tap_surf = pygame.image.load(tap_path).convert_alpha()
            self.tap_surf = pygame.transform.scale(self.tap_surf, (100, 70))
        except:
            self.tap_surf = pygame.Surface((80, 35), pygame.SRCALPHA)
            pygame.draw.rect(self.tap_surf, (220, 50, 50), (0, 0, 80, 35), border_radius=6)

        # --- DUAL FONT LOADING ---
        self.title_font = pygame.font.Font(get_path('..', 'graphics', 'font', 'BD_Cartoon_Shout.otf'), 60)
        self.sub_font = pygame.font.Font(get_path('..', 'graphics', 'font', 'jaja.ttf'), 20)

    def run(self, events): # FIXED: Tinatanggap na ang events mula sa main.py
        # Gagamit tayo ng fixed delta time para sa menu animation (approx 60 FPS)
        dt = 1 / 60 
        self.timer += 6 * dt

        # Input Handling gamit ang ipinasang events galing sa main.py
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                return 'start' # Mag-re-return ng 'start' para magsimula ang laro

        # Rendering & Logic
        self.display_surface.fill('black')
        self.menu_sprites.update(dt)
        self.menu_sprites.draw(self.display_surface)

        # --- TITLE DESIGN ---
        title_text = '< Velocity Wings >'
        wave_y = (WINDOW_HEIGHT / 5) + math.sin(self.timer * 0.2) * 5
        
        shadow_surf = self.title_font.render(title_text, True, (25, 45, 15))
        main_surf = self.title_font.render(title_text, True, (139, 195, 74))
        
        self.display_surface.blit(shadow_surf, shadow_surf.get_rect(center = (WINDOW_WIDTH / 2 + 4, wave_y + 4)))
        self.display_surface.blit(main_surf, main_surf.get_rect(center = (WINDOW_WIDTH / 2, wave_y)))

        # Cat Animation
        self.cat_index += 9 * dt
        if self.cat_index >= len(self.cat_frames): self.cat_index = 0
        self.cat_surf = self.cat_frames[int(self.cat_index)]
        cat_wave = (WINDOW_HEIGHT / 2 + 20) + math.sin(self.timer) * 12
        self.cat_rect.centery = int(cat_wave)

        # Floating / Pulsing Effects
        pulse = 1.0 + math.sin(self.timer * 1.5) * 0.08
        current_tap = pygame.transform.scale(self.tap_surf, (int(self.tap_surf.get_width() * pulse), int(self.tap_surf.get_height() * pulse)))
        
        self.display_surface.blit(self.cat_surf, self.cat_rect)
        self.display_surface.blit(current_tap, current_tap.get_rect(right = self.cat_rect.left - 20, centery = self.cat_rect.centery))
        self.display_surface.blit(current_tap, current_tap.get_rect(left = self.cat_rect.right + 20, centery = self.cat_rect.centery))

        # Flashing Instruction Text
        if int(self.timer * 0.5) % 2 == 0:
            sub_surf = self.sub_font.render('PRESS SPACE TO JUMP', True, (255, 255, 255))
            self.display_surface.blit(sub_surf, sub_surf.get_rect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80)))

        return None