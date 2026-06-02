import pygame, sys, time, os
from settings import *
from sprites import BG, Ground, Plane, Obstacle 
from menu import MainMenu
from game_over import GameOver

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('< Velocity Wings > ')
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # Audio Setup
        music_path = self.get_path('..', 'sounds', 'music.wav')
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1)
        
        self.active = False
        self.menu = MainMenu(self.display_surface)
        self.restart_game()

    def get_path(self, *parts): 
        return os.path.join(self.BASE_DIR, *parts)

    def restart_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        
        bg_path = self.get_path('..', 'graphics', 'environment', 'background.png')
        self.scale_factor = WINDOW_HEIGHT / pygame.image.load(bg_path).get_height()
        
        self.bg = BG(self.all_sprites, self.scale_factor)
        self.ground = Ground([self.all_sprites, self.collision_sprites], self.scale_factor)
        self.plane = Plane([self.all_sprites, self.collision_sprites], self.scale_factor)
        
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, 1400)
        
        font_path = self.get_path('..', 'graphics', 'font', 'BD_Cartoon_Shout.otf')
        self.font = pygame.font.Font(font_path, 30)
        self.score = 0

    def run(self):
        last_time = time.time()
        
        while True:
            # 1. Centralized Event Management
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: 
                    pygame.quit()
                    sys.exit()

            # 2. State Controller
            if not self.active:
                if hasattr(self, 'game_over_screen'):
                    if self.game_over_screen.run(events) == 'restart':
                        self.restart_game()
                        self.active = False         # FIXED: Naka-False para bumalik muna sa Main Menu!
                        del self.game_over_screen   # Tatanggalin na ang game over state
                        last_time = time.time()
                else:
                    if self.menu.run(events) == 'start':
                        self.restart_game()
                        self.active = True
                        last_time = time.time()
            else:
                dt = time.time() - last_time
                last_time = time.time()
                
                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.plane.jump()
                    if event.type == self.obstacle_timer:
                        obs = Obstacle([self.all_sprites, self.collision_sprites], self.scale_factor * 1.1)
                        obs.scored = False
                
                self.display_surface.fill('black')
                self.all_sprites.update(dt)
                self.all_sprites.draw(self.display_surface)
                
                # Scoring Handler
                for sprite in self.collision_sprites:
                    if (hasattr(sprite, 'sprite_type') and 
                        sprite.sprite_type == 'obstacle' and 
                        sprite.rect.centerx < self.plane.rect.left and 
                        not getattr(sprite, 'scored', False)):
                        
                        self.score += 1
                        sprite.scored = True
                        self.bg.update_stage_background(self.score)
                
                # Render HUD
                color = 'white' if self.score >= 5 else 'black'
                score_surf = self.font.render(str(self.score), True, color)
                self.display_surface.blit(score_surf, score_surf.get_rect(midtop=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 10)))
                
                # Collision System
                # 1. Check para sa Obstacles (Pixel-Perfect Mask)
                obstacle_collisions = [sprite for sprite in self.collision_sprites if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'obstacle']
                if pygame.sprite.spritecollide(self.plane, obstacle_collisions, False, pygame.sprite.collide_mask):
                    self.active = False
                    self.game_over_screen = GameOver(self.display_surface, self.score)
                
                # 2. Check para sa Ground (Normal Rect Collision)
                ground_collisions = [sprite for sprite in self.collision_sprites if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'ground']
                if pygame.sprite.spritecollide(self.plane, ground_collisions, False):
                    self.active = False
                    self.game_over_screen = GameOver(self.display_surface, self.score)
            
            pygame.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    Game().run()