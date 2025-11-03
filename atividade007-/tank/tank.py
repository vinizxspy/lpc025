# Imports
import math
import os
import sys

import pygame

# Import from core
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import (
    WIDTH,
    HEIGHT,
    FPS,
    WHITE,
    GREEN,
    YELLOW,
    init_pygame,
    load_image_scaled,
    safe_sound,
    draw_victory_screen,
    draw_score_panel,
    RoundRules,
    RoundManager,
)

# Settings
TANK_SCALE = 0.15
HITBOX_RATIO = 0.55
ROT_SPEED = 3
MOVE_SPEED = 4
BULLET_SPEED = 10
SHOOT_CD_MS = 500
HITS_TO_WIN = 3
WIN_SCORE_CAP = 99

# Init
screen, clock, mixer_ok = init_pygame(True)

# Sounds
shoot_sfx = safe_sound("tank/assets/bullet.wav", mixer_ok)
hit_sfx   = safe_sound("tank/assets/hit.wav", mixer_ok)
start_sfx = safe_sound("tank/assets/clash-royale-start-up-sound.mp3", mixer_ok) 

# Images
tank_img = load_image_scaled("tank/assets/tank1.png", TANK_SCALE)


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, angle_deg: float, owner_id: int):
        super().__init__()
        self.image = pygame.Surface((6, 6))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle_deg
        self.owner_id = owner_id

    def update(self, walls, tanks_by_id, round_mgr: RoundManager):
        rad = math.radians(self.angle - 270)
        self.rect.x += math.cos(rad) * BULLET_SPEED
        self.rect.y -= math.sin(rad) * BULLET_SPEED

        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.kill()
                return

        target_id = 2 if self.owner_id == 1 else 1
        target = tanks_by_id[target_id]
        if target.is_spinning:
            return

        if self.rect.colliderect(target.hitbox):
            if hit_sfx:
                hit_sfx.play()
            round_mgr.on_hit(attacker_id=self.owner_id, target_id=target_id)
            self.kill()
            return


# Tank class
class Tank(pygame.sprite.Sprite):
    def __init__(self, pid: int, x: int, y: int, controls: dict):
        super().__init__()
        self.id = pid
        self.original = tank_img
        self.image = tank_img.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = pygame.Rect(
            0, 0, int(self.rect.w * HITBOX_RATIO), int(self.rect.h * HITBOX_RATIO)
        )
        self.hitbox.center = self.rect.center

        self.angle = 0
        self.controls = controls
        self.hits = 0
        self.score = 0
        self.is_spinning = False
        self.spin_progress = 0.0
        self._last_shot = -10**9

    def can_shoot(self) -> bool:
        now = pygame.time.get_ticks()
        if now - self._last_shot >= SHOOT_CD_MS:
            self._last_shot = now
            return True
        return False

    def shoot(self, bullets_group: pygame.sprite.Group):
        if not self.can_shoot():
            return
        rad = math.radians(self.angle - 270)
        bx = self.hitbox.centerx + math.cos(rad) * (self.rect.w // 2)
        by = self.hitbox.centery - math.sin(rad) * (self.rect.h // 2)
        bullets_group.add(Bullet(bx, by, self.angle, self.id))
        if shoot_sfx:
            shoot_sfx.play()

    def update(self, keys, walls):
        if self.is_spinning:
            return

        if keys[self.controls["left"]]:
            self.angle += ROT_SPEED
        if keys[self.controls["right"]]:
            self.angle -= ROT_SPEED

        mx = my = 0
        if keys[self.controls["forward"]]:
            rad = math.radians(self.angle - 270)
            mx += math.cos(rad) * MOVE_SPEED
            my -= math.sin(rad) * MOVE_SPEED

        new_hit = self.hitbox.move(mx, my)
        if not any(new_hit.colliderect(w.rect) for w in walls):
            self.hitbox = new_hit

        self.image = pygame.transform.rotate(self.original, self.angle)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update_animation(self):
        if self.is_spinning:
            self.spin_progress += 18
            self.image = pygame.transform.rotate(
                self.original, self.angle + self.spin_progress
            )
            self.rect = self.image.get_rect(center=self.hitbox.center)
            if self.spin_progress >= 360:
                self.is_spinning = False
                self.spin_progress = 0.0

    def draw_hitbox(self, surf: pygame.Surface):
        pygame.draw.rect(surf, GREEN, self.hitbox, 1)


# Wall class
class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, w: int, h: int):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((230, 210, 60))
        self.rect = self.image.get_rect(topleft=(x, y))


# Walls
def build_walls():
    walls = pygame.sprite.Group()
    b = 30
    data = [
        (0, 0, WIDTH, b),
        (0, HEIGHT - b, WIDTH, b),
        (0, 0, b, HEIGHT),
        (WIDTH - b, 0, b, HEIGHT),
        (WIDTH // 2 - 160, HEIGHT // 2 - 80, 60, 160),
        (WIDTH // 2 + 100, HEIGHT // 2 - 80, 60, 160),
    ]
    for item in data:
        walls.add(Wall(*item))
    return walls


# Controls
controls1 = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "forward": pygame.K_UP,
    "shoot": pygame.K_SPACE,
}
controls2 = {
    "left": pygame.K_a,
    "right": pygame.K_d,
    "forward": pygame.K_w,
    "shoot": pygame.K_KP_ENTER,
}

# Objects
walls = build_walls()
bullets = pygame.sprite.Group()
players = pygame.sprite.Group()

p1 = Tank(1, 150, HEIGHT // 2, controls1)
p2 = Tank(2, WIDTH - 150, HEIGHT // 2, controls2)
players.add(p1, p2)

# Round manager
tanks_by_id = {1: p1, 2: p2}
round_mgr = RoundManager(
    RoundRules(hits_to_win=HITS_TO_WIN, score_cap=WIN_SCORE_CAP),
    tanks_by_id,
)

# Play start sound at game start
if start_sfx:
    start_sfx.play()


# Respawn and clear
def respawn_tank(players: dict[int, Tank]):
    p1_local = players[1]
    p2_local = players[2]

    p1_local.angle = 0
    p2_local.angle = 0

    p1_local.hitbox.center = (150, HEIGHT // 2)
    p2_local.hitbox.center = (WIDTH - 150, HEIGHT // 2)

    p1_local.image = pygame.transform.rotate(p1_local.original, p1_local.angle)
    p2_local.image = pygame.transform.rotate(p2_local.original, p2_local.angle)

    p1_local.rect = p1_local.image.get_rect(center=p1_local.hitbox.center)
    p2_local.rect = p2_local.image.get_rect(center=p2_local.hitbox.center)


def clear_bullets_tank():
    bullets.empty()


# Events
def handle_events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


# Update
def update(dt: float, keys):
    if round_mgr.round_over:
        round_mgr.update_animations()
        if keys[pygame.K_SPACE]:
            round_mgr.reset_round(respawn_tank, clear_bullets_tank)
            if start_sfx:   # play start SFX each new round
                start_sfx.play()
        return

    if keys[controls1["shoot"]]:
        p1.shoot(bullets)
    if keys[controls2["shoot"]]:
        p2.shoot(bullets)

    p1.update(keys, walls)
    p2.update(keys, walls)
    bullets.update(walls, tanks_by_id, round_mgr)

    p1.update_animation()
    p2.update_animation()


# Draw
def draw():
    screen.fill((180, 60, 40))
    walls.draw(screen)
    players.draw(screen)
    bullets.draw(screen)

    draw_score_panel(screen, p1.score, p2.score)

    if round_mgr.round_over:
        _, tank_text = round_mgr.winner_text(
            prefix_ship="Player ", prefix_tank="PLAYER "
        )
        draw_victory_screen(screen, tank_text, "Press SPACE to continue")

    pygame.display.flip()


# Main loop
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    handle_events()
    pressed = pygame.key.get_pressed()
    update(dt, pressed)
    draw()

pygame.quit()
sys.exit()
