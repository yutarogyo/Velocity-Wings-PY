import pygame
import sys
import os
from settings import *
from sprites import Plane, Obstacle, BG, Ground
from menu import MainMenu
from game_over import GameOver
from random import randint

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_path(*path_parts):
    return os.path.join(BASE_DIR, *path_parts)


class Game:
    def __init__(self):
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Velocity Wings')
        self.clock = pygame.time.Clock()

        # STATES
        self.active = False
        self.game_over = False
        self.is_night = False

        # SCORE
        self.score = 0
        self.scored_pairs = set()

        # PIPE SYSTEM
        self.pair_counter = 0

        # SPAWN TIMER
        self.spawn_interval = 1400
        self.obstacle_timer = pygame.USEREVENT + 1
        pygame.time.set_timer(self.obstacle_timer, self.spawn_interval)

        # GROUPS
        self.all_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

        # BACKGROUND
        self.bg_day_surf = pygame.image.load(
            get_path('..', 'graphics', 'environment', 'background.png')
        ).convert()

        self.bg_night_surf = pygame.image.load(
            get_path('..', 'graphics', 'environment', 'background_special.png')
        ).convert()

        self.scale_factor = WINDOW_HEIGHT / self.bg_day_surf.get_height()

        self.bg = BG(self.all_sprites, self.scale_factor)
        self.ground = Ground([self.all_sprites], self.scale_factor)

        self.player = None

        # FONT
        self.font = pygame.font.Font(
            get_path('..', 'graphics', 'font', 'jaja.ttf'),
            30
        )

        # MENU
        self.menu = MainMenu(self.display_surface)
        self.game_over_screen = None

        self.selected_skin = 0

        # =========================
        # LOGO + GLOW (ADDED ONLY)
        # =========================
        self.logo = pygame.image.load(
            get_path('..', 'graphics', 'ui', 'logo.png')
        ).convert_alpha()

        self.logo = pygame.transform.smoothscale(self.logo, (140, 140))
        self.logo_rect = self.logo.get_rect(topright=(WINDOW_WIDTH - 20, 20))

        self.logo_glow = pygame.transform.smoothscale(self.logo, (170, 170))
        self.logo_glow_rect = self.logo_glow.get_rect(center=self.logo_rect.center)

    # =========================
    # RESET GAME
    # =========================
    def restart_game(self):
        self.all_sprites.empty()
        self.obstacle_sprites.empty()

        self.score = 0
        self.scored_pairs.clear()

        self.active = True
        self.game_over = False
        self.is_night = False

        self.bg = BG(self.all_sprites, self.scale_factor)
        self.ground = Ground([self.all_sprites], self.scale_factor)

        self.player = Plane(
            self.all_sprites,
            self.scale_factor,
            self.selected_skin
        )

        self.pair_counter = 0

    def go_to_menu(self):
        self.all_sprites.empty()
        self.obstacle_sprites.empty()

        self.active = False
        self.game_over = False
        self.is_night = False

        self.bg = BG(self.all_sprites, self.scale_factor)
        self.ground = Ground([self.all_sprites], self.scale_factor)

    def trigger_game_over(self):
        self.active = False
        self.game_over = True
        self.game_over_screen = GameOver(self.display_surface, self.score)

        with open("score.txt", "a") as f:
            f.write(str(self.score) + "\n")

    def collisions(self):
        if pygame.sprite.spritecollide(
            self.player,
            self.obstacle_sprites,
            False,
            pygame.sprite.collide_mask
        ):
            self.trigger_game_over()

        if pygame.sprite.collide_mask(self.player, self.ground):
            self.trigger_game_over()

        if self.player.rect.top <= 0:
            self.trigger_game_over()

    def check_score(self):
        for obs in self.obstacle_sprites:
            if obs.type == "bottom" and obs.pair_id not in self.scored_pairs:

                if self.player.rect.centerx > obs.rect.centerx:
                    self.score += 1
                    self.scored_pairs.add(obs.pair_id)

                    if self.score >= 5 and not self.is_night:
                        self.is_night = True

                        new_bg = pygame.transform.scale(
                            self.bg_night_surf,
                            pygame.math.Vector2(
                                self.bg_night_surf.get_size()
                            ) * self.scale_factor
                        )

                        self.bg.image = new_bg

    def cleanup(self):
        for obs in list(self.obstacle_sprites):
            if obs.rect.right < -200:
                obs.kill()

    def display_score(self):
        if self.active:
            color = (255, 255, 255) if self.is_night else (0, 0, 0)

            score_surf = self.font.render(str(self.score), True, color)
            score_rect = score_surf.get_rect(
                midtop=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 10)
            )

            self.display_surface.blit(score_surf, score_rect)

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.active:

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.player.jump()

                    if event.type == self.obstacle_timer:

                        self.pair_counter += 1
                        pair_id = self.pair_counter

                        center_y = randint(
                            int(WINDOW_HEIGHT * 0.25),
                            int(WINDOW_HEIGHT * 0.75)
                        )

                        spawn_x = WINDOW_WIDTH + 100
                        gap = 150

                        Obstacle(
                            [self.all_sprites, self.obstacle_sprites],
                            self.scale_factor,
                            'top',
                            center_y - gap // 2,
                            pair_id,
                            spawn_x
                        )

                        Obstacle(
                            [self.all_sprites, self.obstacle_sprites],
                            self.scale_factor,
                            'bottom',
                            center_y + gap // 2,
                            pair_id,
                            spawn_x
                        )

            # UPDATE
            for sprite in self.all_sprites:
                sprite.update(dt)

            self.cleanup()

            # DRAW
            self.display_surface.fill("black")
            self.all_sprites.draw(self.display_surface)

            # =========================
            # FLOATING + GLOW LOGO
            # =========================
            offset_y = pygame.math.sin(pygame.time.get_ticks() * 0.003) * 8
            offset = pygame.math.Vector2(0, offset_y)

            glow = self.logo_glow.copy()
            glow.set_alpha(90)

            glow_rect = self.logo_glow_rect.copy()
            glow_rect.center += offset

            logo_rect = self.logo_rect.copy()
            logo_rect.center += offset

            self.display_surface.blit(glow, glow_rect)
            self.display_surface.blit(self.logo, logo_rect)

            if self.active:
                self.collisions()
                self.check_score()
                self.display_score()

            elif self.game_over:
                if self.game_over_screen:
                    result = self.game_over_screen.run(events)
                    if result == "restart":
                        self.go_to_menu()

            else:
                menu_result = self.menu.run(events)
                if menu_result and menu_result[0] == "start":
                    self.selected_skin = menu_result[1]
                    self.restart_game()

            pygame.display.update()


if __name__ == "__main__":
    Game().run()