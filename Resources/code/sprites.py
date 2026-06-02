import pygame, os
from settings import *
from random import choice, randint

# Helper function para makuha ang tamang file path kahit anong OS gamit
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
def get_path(*path_parts): return os.path.join(BASE_DIR, *path_parts)

# CLASS PARA SA BACKGROUND: Humahawak sa pag-scroll at pag-change ng background (Day/Night)
class BG(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'bg'
        self.scale_factor = scale_factor
        self.load_new_background(get_path('..', 'graphics', 'environment', 'background.png'))

    # Kinakarga at inaayos ang sukat ng image para mag-fit sa screen
    def load_new_background(self, path):
        bg_image = pygame.image.load(path).convert()
        full_height = bg_image.get_height() * self.scale_factor
        full_width = bg_image.get_width() * self.scale_factor
        self.image = pygame.Surface((full_width * 2, full_height))
        self.image.blit(pygame.transform.scale(bg_image, (full_width, full_height)), (0, 0))
        self.image.blit(pygame.transform.scale(bg_image, (full_width, full_height)), (full_width, 0))
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    # Dito nagpapalit ng image kapag umabot na sa specific score (Stage Management)
    def update_stage_background(self, score):
        if score == 5:
            night_path = get_path('..', 'graphics', 'environment', 'background_special.png')
            if os.path.exists(night_path): self.load_new_background(night_path)

    # Ine-execute ang horizontal scrolling movement ng background
    def update(self, dt):
        self.pos.x -= 300 * dt
        if self.rect.centerx <= 0: self.pos.x = 0
        self.rect.x = round(self.pos.x)

# CLASS PARA SA GROUND: Nagbibigay ng floor element na gumagalaw rin
class Ground(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'ground' # FIXED: Tinanggal ang panggulong self.sprite_type = 'plane'
        surf = pygame.image.load(get_path('..', 'graphics', 'environment', 'ground.png')).convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)
        self.rect = self.image.get_rect(bottomleft=(0, WINDOW_HEIGHT))
        self.pos = pygame.math.Vector2(self.rect.topleft)

    def update(self, dt):
        self.pos.x -= 360 * dt
        if self.rect.centerx <= 0: self.pos.x = 0
        self.rect.x = round(self.pos.x)

# CLASS PARA SA PLAYER (Pusa): Humahawak sa gravity, movement, at animation
class Plane(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'plane' # FIXED: Idinagdag ang nawawalang property para sa main.py
        self.import_frames(scale_factor)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midleft=(WINDOW_WIDTH / 20, WINDOW_HEIGHT / 2))
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.gravity, self.direction = 600, 0 # Physics variables
        self.mask = pygame.mask.from_surface(self.image) # Para sa pixel-perfect collision
        self.jump_sound = pygame.mixer.Sound(get_path('..', 'sounds', 'jump.wav'))

    # Pagkarga ng lahat ng frames para sa animation ng pusa
    def import_frames(self, scale_factor):
        self.frames = []
        for i in range(3):
            surf = pygame.image.load(get_path('..', 'graphics', 'plane', f'cat{i}.png')).convert_alpha()
            self.frames.append(pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * (scale_factor / 2.5)))

    # Reset position kapag namatay o restart ng game
    def reset_position(self):
        self.pos = pygame.math.Vector2(WINDOW_WIDTH / 20, WINDOW_HEIGHT / 2)
        self.direction = 0

    # Logic para sa talon (pabaliktad na direction value)
    def jump(self):
        self.jump_sound.play()
        self.direction = -400

    # Pag-update ng posisyon (gravity) at rotation base sa velocity
    def update(self, dt):
        self.direction += self.gravity * dt
        self.pos.y += self.direction * dt
        self.rect.y = round(self.pos.y)
        self.frame_index += 10 * dt
        if self.frame_index >= len(self.frames): self.frame_index = 0
        self.image = pygame.transform.rotozoom(self.frames[int(self.frame_index)], -self.direction * 0.06, 1)
        self.mask = pygame.mask.from_surface(self.image)

# CLASS PARA SA MGA BALAKID: Random spawning at movement
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, groups, scale_factor):
        super().__init__(groups)
        self.sprite_type = 'obstacle'
        surf = pygame.image.load(get_path('..', 'graphics', 'obstacles', f'{choice((0, 1))}.png')).convert_alpha()
        self.image = pygame.transform.scale(surf, pygame.math.Vector2(surf.get_size()) * scale_factor)
        x = WINDOW_WIDTH + randint(40, 100)
        
        # Randomize kung sa taas (bitin) o baba (ground) lalabas ang obstacle
        if choice(('up', 'down')) == 'up':
            self.rect = self.image.get_rect(midbottom=(x, WINDOW_HEIGHT + randint(10, 50)))
        else:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midtop=(x, randint(-50, -10)))
        
        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.mask = pygame.mask.from_surface(self.image)
        
    # Pag-move ng obstacles pabalik sa kaliwa; 'kill()' kapag wala na sa screen para makatipid sa memory
    def update(self, dt):
        self.pos.x -= 400 * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right <= -100: self.kill()