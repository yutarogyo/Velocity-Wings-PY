import pygame
import os
import imageio

class GameOver:
    def __init__(self, display_surface, score):
        self.display_surface = display_surface
        self.score = score
        
        # Path setup
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(BASE_DIR, '..', 'graphics', 'font', 'jaja.ttf')
        gif_path = os.path.join(BASE_DIR, '..', 'graphics', 'environment', 'gg.gif')
        
        # Load GIF frames
        self.frames = imageio.mimread(gif_path)
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 100 # Speed ng animation (milliseconds)
        
        # Fonts
        self.font = pygame.font.Font(font_path, 40)
        self.link_font = pygame.font.Font(font_path, 30)

    def run(self, events):
        # 1. Animation Logic (GIF Frame Update)
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_duration:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.last_update = now
            
        # Convert GIF frame to Pygame Surface
        frame_surface = pygame.surfarray.make_surface(self.frames[self.frame_index].swapaxes(0, 1))
        bg_surface = pygame.transform.scale(frame_surface, (self.display_surface.get_width(), self.display_surface.get_height()))
        self.display_surface.blit(bg_surface, (0, 0))
        
        # 2. Text Content
        go_surf = self.font.render('GAME OVER', True, 'White')
        score_surf = self.font.render(f'Score: {self.score}', True, 'Yellow')
        
        # 3. Clickable "TRY AGAIN" Link
        mouse_pos = pygame.mouse.get_pos()
        restart_text = 'TRY AGAIN'
        restart_rect = self.link_font.render(restart_text, True, 'White').get_rect(
            center=(self.display_surface.get_width() / 2, 450)
        )
        
        # Hover Effect
        if restart_rect.collidepoint(mouse_pos):
            restart_surf = self.link_font.render(restart_text, True, 'Cyan')
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            restart_surf = self.link_font.render(restart_text, True, 'White')
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
        # Blit text
        self.display_surface.blit(go_surf, go_surf.get_rect(center=(self.display_surface.get_width() / 2, 200)))
        self.display_surface.blit(score_surf, score_surf.get_rect(center=(self.display_surface.get_width() / 2, 300)))
        self.display_surface.blit(restart_surf, restart_rect)
        
        # 4. Input Handling
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_rect.collidepoint(mouse_pos):
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    return 'restart'
        return None