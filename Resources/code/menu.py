import pygame
import sys
import os
import math
from settings import *
from sprites import BG, Ground
from skin_choices import SkinChoices


class MainMenu:
    def __init__(self, display_surface):
        self.display_surface = display_surface

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        def get_path(*path_parts):
            return os.path.join(BASE_DIR, *path_parts)

        # ---------------- BACKGROUND ----------------
        self.menu_sprites = pygame.sprite.Group()

        bg_path = get_path('..', 'graphics', 'environment', 'background.png')
        bg_height = pygame.image.load(bg_path).get_height()
        self.scale_factor = WINDOW_HEIGHT / bg_height

        self.bg = BG(self.menu_sprites, self.scale_factor)
        self.ground = Ground(self.menu_sprites, self.scale_factor)

        # ---------------- TIMER ----------------
        self.timer = 0

        # ---------------- SKIN ASSETS ----------------
        self.all_skins_assets = {}

        for s_idx in range(4):
            frames = []
            for f_idx in range(3):

                file_name = f'cat{f_idx}.png' if s_idx == 0 else f'skin{s_idx}_{f_idx}.png'
                path = get_path('..', 'graphics', 'plane', file_name)

                if os.path.exists(path):
                    surf = pygame.image.load(path).convert_alpha()
                else:
                    surf = pygame.Surface((40, 30))
                    surf.fill((100, 50 * s_idx, 150))

                scaled = pygame.transform.scale(
                    surf,
                    pygame.math.Vector2(surf.get_size()) * (self.scale_factor / 2.2)
                )
                frames.append(scaled) 

            self.all_skins_assets[s_idx] = frames

        # ---------------- ANIMATION ----------------
        self.cat_index = 0
        self.cat_rect = self.all_skins_assets[0][0].get_rect(
            center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 10)
        )

        # ---------------- TAP IMAGE ----------------
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        tap_path = os.path.join(BASE_DIR, '..', 'graphics', 'plane', 'TAP.png')

        if not os.path.exists(tap_path):
            tap_path = os.path.join(BASE_DIR, '..', 'graphics', 'obstacles', 'Tag.png')

        try:
            self.tap_surf = pygame.image.load(tap_path).convert_alpha()
            self.tap_surf = pygame.transform.scale(self.tap_surf, (100, 70))
        except:
            self.tap_surf = pygame.Surface((80, 35), pygame.SRCALPHA)
            pygame.draw.rect(self.tap_surf, (220, 50, 50), (0, 0, 80, 35), border_radius=6)

        # ---------------- FONTS ----------------
        self.title_font = pygame.font.Font(get_path('..', 'graphics', 'font', 'BD_Cartoon_Shout.otf'), 40)
        self.main_title_font = pygame.font.Font(get_path('..', 'graphics', 'font', 'BD_Cartoon_Shout.otf'), 60)
        self.sub_font = pygame.font.Font(get_path('..', 'graphics', 'font', 'jaja.ttf'), 20)
        self.btn_font = pygame.font.Font(get_path('..', 'graphics', 'font', 'jaja.ttf'), 18)

        # ---------------- STATE ----------------
        self.current_tab = 'main'
        self.skins_manager = SkinChoices()

        self.skins_btn_rect = pygame.Rect(
            (WINDOW_WIDTH / 2) - 75,
            (WINDOW_HEIGHT / 2) + 90,
            150,
            45
        )

    # =========================================================
    def run(self, events):
        dt = 1 / 60
        self.timer += 6 * dt
        mouse_pos = pygame.mouse.get_pos()

        # ---------------- SKIN SELECT TAB ----------------
        if self.current_tab == 'character_select':

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    res = self.skins_manager.update_selection(mouse_pos)

                    if res:
                        if res[0] == "skin_selected":
                            self.skins_manager.selected_skin = res[1]
                            self.current_tab = 'main'

                        elif res == "back_to_menu":
                            self.current_tab = 'main'

            self.skins_manager.draw(
                self.display_surface,
                self.title_font,
                self.btn_font,
                self.all_skins_assets,
                self.timer,
                mouse_pos
            )

            return None

        # ---------------- MAIN MENU ----------------
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.skins_btn_rect.collidepoint(mouse_pos):
                    self.current_tab = 'character_select'
                    return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return ('start', self.skins_manager.selected_skin)

        # ---------------- DRAW BACKGROUND ----------------
        self.display_surface.fill('black')
        self.menu_sprites.update(dt)
        self.menu_sprites.draw(self.display_surface)

        # ---------------- TITLE ----------------
        title_text = '< Velocity Wings >'
        wave_y = (WINDOW_HEIGHT / 5) + math.sin(self.timer * 0.2) * 5

        shadow = self.main_title_font.render(title_text, True, (25, 45, 15))
        main = self.main_title_font.render(title_text, True, (139, 195, 74))

        self.display_surface.blit(shadow, shadow.get_rect(center=(WINDOW_WIDTH/2 + 4, wave_y + 4)))
        self.display_surface.blit(main, main.get_rect(center=(WINDOW_WIDTH/2, wave_y)))

        # ---------------- PLAYER PREVIEW ----------------
        self.cat_index += 9 * dt

        active_frames = self.all_skins_assets[self.skins_manager.selected_skin]

        if self.cat_index >= len(active_frames):
            self.cat_index = 0

        cat_surf = active_frames[int(self.cat_index)]

        cat_wave = (WINDOW_HEIGHT / 2 + 10) + math.sin(self.timer) * 12
        self.cat_rect = cat_surf.get_rect(center=(WINDOW_WIDTH / 2, int(cat_wave)))

        # TAP EFFECT
        pulse = 1.0 + math.sin(self.timer * 1.5) * 0.08

        tap = pygame.transform.scale(
            self.tap_surf,
            (
                int(self.tap_surf.get_width() * pulse),
                int(self.tap_surf.get_height() * pulse)
            )
        )

        self.display_surface.blit(cat_surf, self.cat_rect)

        self.display_surface.blit(
            tap,
            tap.get_rect(right=self.cat_rect.left - 20, centery=self.cat_rect.centery)
        )

        self.display_surface.blit(
            tap,
            tap.get_rect(left=self.cat_rect.right + 20, centery=self.cat_rect.centery)
        )

        # ---------------- SKIN BUTTON ----------------
        btn_color = (139, 195, 74) if self.skins_btn_rect.collidepoint(mouse_pos) else (40, 45, 55)
        txt_color = (0, 0, 0) if self.skins_btn_rect.collidepoint(mouse_pos) else (255, 255, 255)

        pygame.draw.rect(self.display_surface, btn_color, self.skins_btn_rect, border_radius=8)
        pygame.draw.rect(self.display_surface, (255, 255, 255), self.skins_btn_rect, 2, border_radius=8)

        btn = self.btn_font.render("SKIN CHOICES", True, txt_color)
        self.display_surface.blit(btn, btn.get_rect(center=self.skins_btn_rect.center))

        # ---------------- HINT ----------------
        if int(self.timer * 0.5) % 2 == 0:
            hint = self.sub_font.render("PRESS SPACE TO START", True, (255, 255, 255))
            self.display_surface.blit(
                hint,
                hint.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 60))
            )

        return None