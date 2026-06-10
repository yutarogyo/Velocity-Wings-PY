import pygame
import math
import os
from settings import *


class SkinChoices:
    def __init__(self):
        self.selected_skin = 0
        self.skin_rects = []
        self.skin_count = 4

        # 2x2 GRID
        card_width = 150
        card_height = 180

        spacing_x = 50
        spacing_y = 40

        start_x = (WINDOW_WIDTH - ((card_width * 2) + spacing_x)) / 2
        start_y = (WINDOW_HEIGHT / 2) - 130

        for row in range(2):
            for col in range(2):
                rect = pygame.Rect(
                    start_x + col * (card_width + spacing_x),
                    start_y + row * (card_height + spacing_y),
                    card_width,
                    card_height
                )
                self.skin_rects.append(rect)

        self.back_rect = pygame.Rect(25, 25, 120, 50)

        self.tab_sprites = pygame.sprite.Group()

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # FRAME PNG
        frame_path = os.path.join(
            BASE_DIR,
            '..',
            'graphics',
            'ui',
            'frame.png'
        )

        self.frame_img = pygame.image.load(frame_path).convert_alpha()

        # BACKGROUND
        bg_path = os.path.join(
            BASE_DIR,
            '..',
            'graphics',
            'environment',
            'background.png'
        )

        bg_height = pygame.image.load(bg_path).get_height()
        self.scale_factor = WINDOW_HEIGHT / bg_height

        from sprites import BG, Ground
        self.bg = BG(self.tab_sprites, self.scale_factor)
        self.ground = Ground(self.tab_sprites, self.scale_factor)

        self.font_path = os.path.join(
            BASE_DIR,
            '..',
            'graphics',
            'font',
            'jaja.ttf'
        )

    # ---------------- SELECTION ----------------
    def update_selection(self, mouse_pos):
        for i, rect in enumerate(self.skin_rects):
            if rect.collidepoint(mouse_pos):
                self.selected_skin = i
                return ("skin_selected", i)

        if self.back_rect.collidepoint(mouse_pos):
            return "back_to_menu"

        return None

    # ---------------- DRAW ----------------
    def draw(self, display_surface, title_font, label_font,
             cat_assets, timer, mouse_pos):

        dt = 1 / 60

        # BACKGROUND
        self.tab_sprites.update(dt)
        self.tab_sprites.draw(display_surface)

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        display_surface.blit(overlay, (0, 0))

        # FONTS
        title_font = pygame.font.Font(self.font_path, 40)
        name_font = pygame.font.Font(self.font_path, 22)
        hint_font = pygame.font.Font(self.font_path, 20)
        back_font = pygame.font.Font(self.font_path, 20)

        # TITLE
        title_shadow = title_font.render("SELECT CHARACTER", True, (0, 0, 0))
        title = title_font.render("SELECT CHARACTER", True, (255, 215, 0))

        display_surface.blit(title_shadow,
            title_shadow.get_rect(center=(WINDOW_WIDTH/2 + 3, WINDOW_HEIGHT/6 + 3))
        )
        display_surface.blit(title,
            title.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/6))
        )

        # BACK BUTTON
        hover_back = self.back_rect.collidepoint(mouse_pos)
        back_color = (255, 80, 80) if hover_back else (180, 50, 50)

        pygame.draw.rect(display_surface, back_color, self.back_rect, border_radius=12)

        back_text = back_font.render("BACK", True, (255, 255, 255))
        display_surface.blit(back_text, back_text.get_rect(center=self.back_rect.center))

        # SKIN NAMES
        names = ["CATHY", "TALON FLAME", "DIANCIE", "RAYQUAZA"]

        # CARDS
        for i, rect in enumerate(self.skin_rects):

            hovered = rect.collidepoint(mouse_pos)
            selected = self.selected_skin == i

            draw_rect = rect.copy()

            if selected:
                draw_rect.y -= 8
            elif hovered:
                draw_rect.y -= 4

            # SHADOW
            shadow_rect = draw_rect.copy()
            shadow_rect.y += 10

            pygame.draw.rect(display_surface, (0, 0, 0), shadow_rect, border_radius=20)

            # CARD BG
            pygame.draw.rect(display_surface, (40, 45, 60), draw_rect, border_radius=20)

            # FRAME
            frame = pygame.transform.scale(
                self.frame_img,
                (draw_rect.width + 16, draw_rect.height + 16)
            )

            frame_rect = frame.get_rect(center=draw_rect.center)
            display_surface.blit(frame, frame_rect)

            # SKIN PREVIEW
            frames = cat_assets[i]
            frame_index = int(timer * 1.5) % len(frames)

            preview = pygame.transform.scale(
                frames[frame_index],
                (int(frames[frame_index].get_width() * 1.0),
                 int(frames[frame_index].get_height() * 1.0))
            )

            preview_rect = preview.get_rect(
                center=(draw_rect.centerx, draw_rect.centery - 15)
            )

            if selected:
                preview_rect.y += int(math.sin(timer * 4) * 4)

            display_surface.blit(preview, preview_rect)

            # NAME (FIXED - ONLY BELOW FRAME)
            text_color = (255, 215, 0) if selected else (255, 255, 255)

            name_shadow = name_font.render(names[i], True, (0, 0, 0))
            name_text = name_font.render(names[i], True, text_color)

            text_pos = (draw_rect.centerx, draw_rect.bottom + 22)

            display_surface.blit(name_shadow,
                name_shadow.get_rect(center=(text_pos[0] + 2, text_pos[1] + 2))
            )
            display_surface.blit(name_text,
                name_text.get_rect(center=text_pos)
            )

        # HINT
        hint = hint_font.render("CLICK A SKIN TO SELECT", True, (220, 220, 220))
        display_surface.blit(hint,
            hint.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT - 40))
        )