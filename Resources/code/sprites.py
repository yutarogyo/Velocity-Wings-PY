import pygame
import os
from settings import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_path(*path_parts):
    return os.path.join(BASE_DIR, *path_parts)


# =========================
# PLAYER
# =========================
class Plane(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor, skin_index=0):
        super().__init__(groups)

        self.skin_index = skin_index
        self.import_frames(scale_factor)

        self.frame_index = 0
        self.image = self.frames[self.frame_index]

        self.rect = self.image.get_rect(
            midleft=(WINDOW_WIDTH / 20, WINDOW_HEIGHT / 2)
        )

        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.gravity = 650
        self.direction = 0

        self.mask = pygame.mask.from_surface(self.image)

    def import_frames(self, scale_factor):
        self.frames = []

        for i in range(3):
            if self.skin_index == 0:
                file_name = f'cat{i}.png'
            else:
                file_name = f'skin{self.skin_index}_{i}.png'

            path = get_path('..', 'graphics', 'plane', file_name)

            if os.path.exists(path):
                surf = pygame.image.load(path).convert_alpha()
            else:
                surf = pygame.Surface((40, 30), pygame.SRCALPHA)
                surf.fill((120, 120, 200))

            size = pygame.math.Vector2(surf.get_size()) * (scale_factor / 2.5)
            size = (int(size.x), int(size.y))

            surf = pygame.transform.smoothscale(surf, size)
            self.frames.append(surf)

    def apply_gravity(self, dt):
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = int(self.pos.y)

    def jump(self):
        self.direction = -310

    def animate(self, dt):
        self.frame_index += 10 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    def rotate(self):
        self.image = pygame.transform.rotozoom(
            self.image,
            -self.direction * 0.06,
            1
        )
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.apply_gravity(dt)
        self.animate(dt)
        self.rotate()


# =========================
# OBSTACLE (FULL FIXED FLAPPY SYSTEM)
# =========================
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor, obstacle_type, center_y, pair_id, spawn_x):
        super().__init__(groups)

        self.pair_id = pair_id
        self.type = obstacle_type

        path = get_path('..', 'graphics', 'obstacles', '0.png')
        surf = pygame.image.load(path).convert_alpha()

        # FIXED SCALE (stable, no dot bug)
        scale = scale_factor * 2.8
        size = surf.get_size()
        new_size = (int(size[0] * scale), int(size[1] * scale))

        self.image = pygame.transform.smoothscale(surf, new_size)
        self.image = self.image.convert_alpha()

        gap = 150

        # TRUE FLAPPY BIRD ALIGNMENT
        if obstacle_type == 'top':
            self.rect = self.image.get_rect(midbottom=(spawn_x, center_y - gap // 2))
        else:
            self.rect = self.image.get_rect(midtop=(spawn_x, center_y + gap // 2))

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos.x -= 220 * dt
        self.rect.x = int(self.pos.x)

        if self.rect.right < -200:
            self.kill()


# =========================
# BACKGROUND
# =========================
class BG(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor, image_surf=None):
        super().__init__(groups)

        if image_surf is None:
            image_surf = pygame.image.load(
                get_path('..', 'graphics', 'environment', 'background.png')
            ).convert()

        size = pygame.math.Vector2(image_surf.get_size()) * scale_factor
        size = (int(size.x), int(size.y))

        self.image = pygame.transform.smoothscale(image_surf, size)
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        self.pos.x -= 30 * dt

        if self.rect.centerx <= 0:
            self.pos.x = 0

        self.rect.x = int(self.pos.x)


# =========================
# GROUND
# =========================
class Ground(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)

        surf = pygame.image.load(
            get_path('..', 'graphics', 'environment', 'ground.png')
        ).convert_alpha()

        size = pygame.math.Vector2(surf.get_size()) * scale_factor
        size = (int(size.x), int(size.y))

        self.image = pygame.transform.smoothscale(surf, size)
        self.rect = self.image.get_rect(bottomleft=(0, WINDOW_HEIGHT))

        self.pos = pygame.math.Vector2(self.rect.topleft)

        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.pos.x -= 200 * dt

        if self.rect.centerx <= 0:
            self.pos.x = 0

        self.rect.x = int(self.pos.x)