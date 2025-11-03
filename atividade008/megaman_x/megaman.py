import os
import sys
import pygame
from typing import List, Dict

"""
megaman.py — Protótipo de animação e movimento (sem tiro, pronto para adicionar depois)

Estrutura de pastas:
activity008/
├── megaman.py
└── assets/
    ├── parado/
    ├── andando/
    ├── pulando/
    └── atirando/  (opcional)

Controles:
  ←/→ mover
  Z pular
  ESC sair

Você pode adicionar os sprites de tiro depois; o código foi ajustado para rodar sem eles.
"""

# === CONFIG ===
WIDTH, HEIGHT = 960, 540
FPS = 60
BG_COLOR = (0, 0, 0)
GRAVITY = 0.55
MOVE_SPEED = 5.0
JUMP_SPEED = -12.0
SCALE = 2.0

ANIM_SPEEDS = {
    "parado": 0.12,
    "andando": 0.07,
    "pulando": 0.10,
}

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# === UTILS ===
def load_animation_folder(path: str, placeholder_color=(0, 255, 255)) -> List[pygame.Surface]:
    frames: List[pygame.Surface] = []
    try:
        files = sorted([f for f in os.listdir(path) if f.lower().endswith(".png")])
    except FileNotFoundError:
        files = []

    if not files:
        for i in range(4):
            surf = pygame.Surface((18 + i % 2 * 2, 26 + (i // 2) * 2), pygame.SRCALPHA)
            surf.fill(placeholder_color)
            frames.append(surf)
        return frames

    for f in files:
        img = pygame.image.load(os.path.join(path, f)).convert_alpha()
        if SCALE != 1.0:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * SCALE), int(h * SCALE)))
        frames.append(img)
    return frames

class Animation:
    def __init__(self, frames: List[pygame.Surface], speed: float, loop: bool = True):
        self.frames = frames
        self.speed = speed
        self.loop = loop
        self.index = 0
        self.t = 0.0

    def restart(self):
        self.index = 0
        self.t = 0.0

    def update(self, dt: float):
        if len(self.frames) <= 1:
            return
        self.t += dt
        while self.t >= self.speed:
            self.t -= self.speed
            self.index += 1
            if self.loop:
                self.index %= len(self.frames)
            else:
                self.index = min(self.index, len(self.frames) - 1)

    @property
    def frame(self) -> pygame.Surface:
        return self.frames[self.index]

class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.animations: Dict[str, Animation] = {
            "parado":  Animation(load_animation_folder(os.path.join(ASSETS_DIR, "parado")),  ANIM_SPEEDS["parado"],  loop=True),
            "andando": Animation(load_animation_folder(os.path.join(ASSETS_DIR, "andando")), ANIM_SPEEDS["andando"], loop=True),
            "pulando": Animation(load_animation_folder(os.path.join(ASSETS_DIR, "pulando")), ANIM_SPEEDS["pulando"], loop=False),
        }

        self.state = "parado"
        self.facing_right = True
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.on_ground = False

        self.image = self.animations[self.state].frame
        self.rect = self.image.get_rect(midbottom=(x, y))

    def set_state(self, new_state: str):
        if new_state != self.state:
            self.state = new_state
            self.animations[self.state].restart()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel.x = -MOVE_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel.x = MOVE_SPEED
            self.facing_right = True
        if (keys[pygame.K_z] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel.y = JUMP_SPEED
            self.on_ground = False
            self.set_state("pulando")

    def physics(self):
        self.vel.y += GRAVITY
        self.pos += self.vel

        floor = 420
        if self.pos.y >= floor:
            self.pos.y = floor
            self.vel.y = 0
            if not self.on_ground:
                self.on_ground = True
                if abs(self.vel.x) > 0.1:
                    self.set_state("andando")
                else:
                    self.set_state("parado")

        self.rect.midbottom = (round(self.pos.x), round(self.pos.y))

    def update_state(self):
        if not self.on_ground:
            self.set_state("pulando")
        else:
            if abs(self.vel.x) > 0.1:
                self.set_state("andando")
            else:
                self.set_state("parado")

    def update(self, dt: float):
        self.handle_input()
        self.physics()
        self.update_state()
        self.animations[self.state].update(dt)

        frame = self.animations[self.state].frame
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

def draw_floor(surface: pygame.Surface, y=420):
    pygame.draw.rect(surface, (20, 20, 20), (0, y, surface.get_width(), surface.get_height() - y))
    pygame.draw.line(surface, (80, 80, 80), (0, y), (surface.get_width(), y), 2)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("MegaMan — Animação e Movimento (Sem Tiro)")
    clock = pygame.time.Clock()

    player = Player(200, 420)
    all_sprites = pygame.sprite.Group(player)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        all_sprites.update(dt)

        screen.fill(BG_COLOR)
        draw_floor(screen, 420)
        all_sprites.draw(screen)

        font = pygame.font.SysFont("arial", 18)
        text = font.render("←/→ mover  |  Z pular  |  ESC sair", True, (200, 220, 255))
        screen.blit(text, (18, 18))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
