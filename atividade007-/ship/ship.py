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
    BLACK,
    YELLOW,
    GREEN,
    MAGENTA,
    SKY_TOP,
    SKY_BOTTOM,
    init_pygame,
    load_image_scaled,
    safe_sound,
    draw_vertical_gradient,
    wrap_position,
    Cooldown,
    draw_victory_screen,
    draw_score_panel,
    RoundRules,
    RoundManager,
)

# Settings
PLANE_SCALE = 0.3
HITBOX_SCALE = 0.25
SHOW_HITBOX = False
MAX_BULLETS = 5
BULLET_SPEED = 8
BULLET_RANGE = 400
PLAYER_SPEED = 3
ROTATE_SPEED = 3
HITS_TO_WIN = 3
SOUND_ENABLED = True
SHOOT_SOUND = "ship/assets/pew.mp3"
EXPLODE_SOUND = "ship/assets/explode.mp3"
CLOUD_SCALE = 0.4

# Init
screen, clock, mixer_ok = init_pygame(SOUND_ENABLED)
font = pygame.font.SysFont(None, 22)

# Sounds
shoot_sfx = safe_sound(SHOOT_SOUND, mixer_ok)
explode_sfx = safe_sound(EXPLODE_SOUND, mixer_ok)

# Images
plane1_img = load_image_scaled("ship/assets/ship.png", PLANE_SCALE)
plane2_img = load_image_scaled("ship/assets/ship2.png", PLANE_SCALE)

# Cloud
try:
    cloud_img = load_image_scaled("ship/assets/cloud.png", CLOUD_SCALE)
except Exception:
    cloud_img = None


# Bullet class
class Bullet:
    def __init__(
        self,
        x: float,
        y: float,
        dx: float,
        dy: float,
        owner: int,
        max_range: float = BULLET_RANGE,
    ):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.owner = owner
        self.max_range = max_range
        self.travel = 0.0
        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.travel += math.hypot(self.dx, self.dy)
        self.x, self.y = wrap_position(self.x, self.y)
        if self.travel >= self.max_range:
            self.alive = False


# Player class
class Player:
    def __init__(
        self,
        pid: int,
        x: float,
        y: float,
        angle_deg: float,
        image: pygame.Surface,
        keys: tuple[int, int, int],
        hitbox_color: tuple[int, int, int],
    ):
        self.id = pid
        self.x, self.y = x, y
        self.angle = angle_deg
        self.image = image
        self.left, self.right, self.shoot = keys
        self.hitbox_color = hitbox_color
        self.bullets: list[Bullet] = []
        self.hits = 0
        self.score = 0
        self.is_spinning = False
        self.spin_progress = 0.0

        w, h = self.image.get_size()
        hw, hh = max(6, int(w * HITBOX_SCALE)), max(6, int(h * HITBOX_SCALE))
        self.hitbox = pygame.Rect(0, 0, hw, hh)
        self.hitbox.center = (int(self.x), int(self.y))

        self.cd = Cooldown(120)

    # Movement
    def update_movement(self, keys):
        if self.is_spinning:
            return

        if keys[self.left]:
            self.angle = (self.angle + ROTATE_SPEED) % 360
        if keys[self.right]:
            self.angle = (self.angle - ROTATE_SPEED) % 360

        rad = math.radians(self.angle)
        self.x += math.cos(rad) * PLAYER_SPEED
        self.y -= math.sin(rad) * PLAYER_SPEED
        self.x, self.y = wrap_position(self.x, self.y)
        self.hitbox.center = (int(self.x), int(self.y))

    # Animation
    def update_animation(self):
        if self.is_spinning:
            self.spin_progress += 15
            if self.spin_progress >= 360:
                self.is_spinning = False
                self.spin_progress = 0

    # Shoot
    def shoot_bullet(self):
        if not self.cd.ready():
            return None
        if len(self.bullets) >= MAX_BULLETS:
            return None

        rad = math.radians(self.angle)
        dx = math.cos(rad) * BULLET_SPEED
        dy = -math.sin(rad) * BULLET_SPEED
        bullet = Bullet(self.x + dx, self.y + dy, dx, dy, owner=self.id)
        self.bullets.append(bullet)

        if shoot_sfx:
            shoot_sfx.play()
        return bullet

    # Draw
    def draw(self, surf: pygame.Surface):
        img = pygame.transform.rotate(self.image, self.angle + self.spin_progress)
        rect = img.get_rect(center=(self.x, self.y))
        surf.blit(img, rect.topleft)
        if SHOW_HITBOX:
            pygame.draw.rect(surf, self.hitbox_color, self.hitbox, 2)


# Clouds
clouds: list[tuple] = []


def add_cloud_at(x: int, y: int):
    if cloud_img:
        rect = cloud_img.get_rect(center=(x, y))
        clouds.append(("img", cloud_img, rect))
    else:
        w = int(140 * CLOUD_SCALE)
        h = int(80 * CLOUD_SCALE)
        rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        clouds.append(("fallback", rect))


def draw_clouds(surface: pygame.Surface):
    for kind, *rest in clouds:
        if kind == "img":
            img, rect = rest
            surface.blit(img, rect.topleft)
        else:
            (rect,) = rest
            pygame.draw.ellipse(surface, WHITE, rect)
            inner = rect.inflate(-int(rect.w * 0.3), -int(rect.h * 0.25))
            pygame.draw.ellipse(surface, (230, 230, 230), inner)


add_cloud_at(WIDTH // 2 - 100, HEIGHT // 2)
add_cloud_at(WIDTH // 2 + 130, HEIGHT // 2)

# Players
p1 = Player(
    1,
    WIDTH * 0.25,
    HEIGHT / 2 + 20,
    0,
    plane1_img,
    (pygame.K_a, pygame.K_d, pygame.K_LSHIFT),
    GREEN,
)
p2 = Player(
    2,
    WIDTH * 0.75,
    HEIGHT / 2 + 20,
    180,
    plane2_img,
    (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_m),
    MAGENTA,
)

# Round manager
bullets: list[Bullet] = []
players_by_id = {1: p1, 2: p2}
round_mgr = RoundManager(
    RoundRules(hits_to_win=HITS_TO_WIN, score_cap=99), players_by_id
)

# Respawn and clear
def respawn_ship(players: dict[int, Player]):
    p1_local = players[1]
    p2_local = players[2]

    p1_local.x, p1_local.y, p1_local.angle = WIDTH * 0.25, HEIGHT / 2 + 20, 0
    p2_local.x, p2_local.y, p2_local.angle = WIDTH * 0.75, HEIGHT / 2 + 20, 180

    p1_local.bullets.clear()
    p2_local.bullets.clear()

    p1_local.hitbox.center = (int(p1_local.x), int(p1_local.y))
    p2_local.hitbox.center = (int(p2_local.x), int(p2_local.y))


def clear_bullets_ship():
    bullets.clear()


# Events
def handle_events():
    global running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if not round_mgr.round_over:
                if event.key == p1.shoot:
                    new_b = p1.shoot_bullet()
                    if new_b:
                        bullets.append(new_b)
                if event.key == p2.shoot:
                    new_b = p2.shoot_bullet()
                    if new_b:
                        bullets.append(new_b)


# Update
def update(dt: float, keys):
    if round_mgr.round_over:
        round_mgr.update_animations()
        if keys[pygame.K_SPACE]:
            round_mgr.reset_round(respawn_ship, clear_bullets_ship)
        return

    p1.update_movement(keys)
    p2.update_movement(keys)

    for b in bullets[:]:
        b.update()
        if not b.alive:
            bullets.remove(b)
            owner = p1 if b.owner == 1 else p2
            if b in owner.bullets:
                owner.bullets.remove(b)

    for b in bullets[:]:
        target = p2 if b.owner == 1 else p1
        if target.hitbox.collidepoint(int(b.x), int(b.y)) and not target.is_spinning:
            if explode_sfx:
                explode_sfx.play()
            ended = round_mgr.on_hit(
                attacker_id=b.owner,
                target_id=(2 if b.owner == 1 else 1),
            )
            b.alive = False
            bullets.remove(b)
            owner = p1 if b.owner == 1 else p2
            if b in owner.bullets:
                owner.bullets.remove(b)
            if ended:
                break

    p1.update_animation()
    p2.update_animation()


# Draw
def draw():
    draw_vertical_gradient(screen, SKY_TOP, SKY_BOTTOM)
    draw_score_panel(screen, p1.score, p2.score)

    p1.draw(screen)
    p2.draw(screen)

    for b in bullets:
        color = BLACK if b.owner == 1 else YELLOW
        pygame.draw.circle(screen, color, (int(b.x), int(b.y)), 4)

    draw_clouds(screen)

    if round_mgr.round_over:
        ship_text, _ = round_mgr.winner_text(
            prefix_ship="Player ", prefix_tank="PLAYER "
        )
        draw_victory_screen(screen, ship_text, "Press SPACE to continue")

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
