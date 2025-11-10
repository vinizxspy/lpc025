import sys
import pygame

# Initialize pygame
pygame.init()

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mega Man")
clock = pygame.time.Clock()

# Tunables / gameplay
TARGET_SIZE = (48, 48)          # sprite scale (pixel art)
VEL_X = 3.0                     # horizontal speed (px/frame)

# Animation speeds (~1.0 per 60 FPS tick)
ANIM_IDLE = 0.04
ANIM_WALK = 0.20
ANIM_WALK_SHOOT = 0.25

# Jump physics
GRAVITY = 0.55
JUMP_VELOCITY = -11.0

# Your base sprite art looks LEFT. Set False to flip once to face RIGHT.
BASE_FACES_RIGHT = False

# Shooting
KEY_SHOOT = pygame.K_j
BULLET_SPEED = 9
BULLET_W, BULLET_H = 10, 3
SHOOT_COOLDOWN_MS = 180

# Muzzle offsets (fine-tune for your art)
MUZZLE_OFFSET_RIGHT = (12, -14)
MUZZLE_OFFSET_LEFT = (-12, -14)

# Invisible ground segment (valid while x <= GROUND_END_X)
GROUND_Y = 460
GROUND_END_X = 640
SHOW_GROUND_LINE = False  # debug helper

# Colors
COLOR_CYAN = (0, 255, 255)
COLOR_DEBUG_GREEN = (0, 220, 0)


# Helpers
def scale_nn(img: pygame.Surface) -> pygame.Surface:
    """Nearest-neighbor scale (preserves pixel art)."""
    return pygame.transform.scale(img, TARGET_SIZE)

def load_image(path: str, *, alpha=True) -> pygame.Surface:
    """Load an image or fail gracefully with a clear error."""
    try:
        surf = pygame.image.load(path)
        return surf.convert_alpha() if alpha else surf.convert()
    except Exception as e:
        print(f"Failed to load image '{path}': {e}")
        pygame.quit()
        raise SystemExit


# PLACE YOUR IMAGES HERE (all under sprites/)
BG_PATH = "sp/fundo.png"
IDLE_1_PATH = "sp/olho.png"
IDLE_2_PATH = "sp/fecha.png"
WALK_1_PATH = "sp/andar1.png"
WALK_2_PATH = "sp/andar2.png"
WALK_3_PATH = "sp/andar3.png"
JUMP_1_PATH = "sp/pulo-.png"
SHOOT_IDLE_PATH = "sp/para_ati.png"
SW_1_PATH = "sp/ati1.png"
SW_2_PATH = "sp/ati2.png"
SW_3_PATH = "sp/ati3.png"

# Load background once and scale to screen
bg = load_image(BG_PATH, alpha=False)
bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))


# Sprites
class Bullet(pygame.sprite.Sprite):
    """Simple horizontal projectile."""

    def __init__(self, x: int, y: int, dir_right: bool) -> None:
        super().__init__()
        self.image = pygame.Surface((BULLET_W, BULLET_H), pygame.SRCALPHA)
        self.image.fill(COLOR_CYAN)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = BULLET_SPEED if dir_right else -BULLET_SPEED

    def update(self) -> None:
        self.rect.x += self.vx
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()


class Player(pygame.sprite.Sprite):
    """Player with facing, walk/jump, and shooting animations."""

    def __init__(self, x: int, ground_y: int) -> None:
        super().__init__()

        # Load all frames
        idle_1 = scale_nn(load_image(IDLE_1_PATH))
        idle_2 = scale_nn(load_image(IDLE_2_PATH))

        walk_1 = scale_nn(load_image(WALK_1_PATH))
        walk_2 = scale_nn(load_image(WALK_2_PATH))
        walk_3 = scale_nn(load_image(WALK_3_PATH))

        jump_1 = scale_nn(load_image(JUMP_1_PATH))

        shoot_idle = scale_nn(load_image(SHOOT_IDLE_PATH))

        sw_1 = scale_nn(load_image(SW_1_PATH))
        sw_2 = scale_nn(load_image(SW_2_PATH))
        sw_3 = scale_nn(load_image(SW_3_PATH))

        # If base art faces LEFT, flip once so our "right" sets are actually right
        if not BASE_FACES_RIGHT:
            flip = lambda im: pygame.transform.flip(im, True, False)
            idle_1, idle_2 = flip(idle_1), flip(idle_2)
            walk_1, walk_2, walk_3 = flip(walk_1), flip(walk_2), flip(walk_3)
            jump_1 = flip(jump_1)
            shoot_idle = flip(shoot_idle)
            sw_1, sw_2, sw_3 = flip(sw_1), flip(sw_2), flip(sw_3)

        # Right-facing lists
        self.idle_right = [idle_1, idle_2]
        self.walk_right = [walk_1, walk_2, walk_3]
        self.jump_right = [jump_1]                 # 1 frame
        self.shoot_idle_right = [shoot_idle]       # 1 frame
        self.shoot_walk_right = [sw_1, sw_2, sw_3]

        # Left-facing lists (mirrored)
        mirror = lambda frames: [pygame.transform.flip(f, True, False) for f in frames]
        self.idle_left = mirror(self.idle_right)
        self.walk_left = mirror(self.walk_right)
        self.jump_left = mirror(self.jump_right)
        self.shoot_idle_left = mirror(self.shoot_idle_right)
        self.shoot_walk_left = mirror(self.shoot_walk_right)

        # State
        self.facing = "right"              # "right" | "left"
        self.state = "idle"                # "idle" | "walk" | "jump"
        self.shooting = False
        self.frame_index = 0.0

        # Physics
        self.vel_y = 0.0
        self.ground_y = ground_y

        # Shooting
        self.last_shot_ms = 0

        # Current frame
        self.frames = self.idle_right
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, ground_y)

    # Ground helpers
    def ground_active_here(self) -> bool:
        """True if there is ground under current X (x <= GROUND_END_X)."""
        return self.rect.centerx <= GROUND_END_X

    def on_ground(self) -> bool:
        """True if standing on the invisible ground segment."""
        return self.ground_active_here() and (self.rect.bottom >= self.ground_y)

    # Input/state
    def start_jump(self) -> None:
        """Begin a jump only if on ground."""
        if self.on_ground():
            self.vel_y = JUMP_VELOCITY
            self.state = "jump"
            self.frame_index = 0.0
            self._choose_frames(moving=False)

    def set_inputs(self, dir_x: int, shooting_hold: bool) -> None:
        """Update facing, movement state, and shooting flag."""
        self.shooting = shooting_hold

        if dir_x < 0:
            self.facing = "left"
        elif dir_x > 0:
            self.facing = "right"

        moving = dir_x != 0
        if self.state != "jump":
            self.state = "walk" if moving else "idle"

        self._choose_frames(moving)

    def request_shoot(self, now_ms: int, bullets_group: pygame.sprite.Group) -> None:
        """Spawn a bullet if cooldown is ready."""
        if (now_ms - self.last_shot_ms) >= SHOOT_COOLDOWN_MS:
            mx, my = self._muzzle_pos()
            bullets_group.add(Bullet(mx, my, self.facing == "right"))
            self.last_shot_ms = now_ms

    # Animation chooser
    def _choose_frames(self, moving: bool) -> None:
        """
        Select frames by state + shooting + facing.
        Rule: jump + shoot uses 'shoot idle' frame.
        """
        left = (self.facing == "left")

        if self.state == "jump":
            if self.shooting:
                self.frames = self.shoot_idle_left if left else self.shoot_idle_right
            else:
                self.frames = self.jump_left if left else self.jump_right
            return

        if self.state == "walk":
            if self.shooting:
                self.frames = self.shoot_walk_left if left else self.shoot_walk_right
            else:
                self.frames = self.walk_left if left else self.walk_right
            return

        # idle
        if self.shooting:
            self.frames = self.shoot_idle_left if left else self.shoot_idle_right
        else:
            self.frames = self.idle_left if left else self.idle_right

    # Update tick
    def update(self, dt: float, dir_x: int) -> None:
        """Integrate physics and advance animation."""
        # Horizontal
        self.rect.x += int(dir_x * VEL_X)

        # Vertical
        self.vel_y += GRAVITY * dt
        self.rect.y += int(self.vel_y * dt)

        # Ground collision (only where ground is active)
        if self.ground_active_here() and self.rect.bottom >= self.ground_y:
            self.rect.bottom = self.ground_y
            if self.vel_y > 0:
                self.vel_y = 0.0
            if self.state == "jump":
                self.state = "idle"
                self._choose_frames(moving=(dir_x != 0))

        # Keep inside screen horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Animation step
        if self.state == "jump":
            self.frame_index = 0.0  # single-frame jump (or jump+shoot)
        else:
            if self.state == "walk" and self.shooting:
                speed = ANIM_WALK_SHOOT
            elif self.state == "walk":
                speed = ANIM_WALK
            else:
                speed = ANIM_IDLE

            if len(self.frames) > 1:
                self.frame_index += speed * dt
                if self.frame_index >= len(self.frames):
                    self.frame_index = 0.0
            else:
                self.frame_index = 0.0

        self.image = self.frames[int(self.frame_index)]

    # Internal
    def _muzzle_pos(self) -> tuple[int, int]:
        if self.facing == "right":
            dx, dy = MUZZLE_OFFSET_RIGHT
        else:
            dx, dy = MUZZLE_OFFSET_LEFT
        return self.rect.centerx + dx, self.rect.centery + dy


# Main loop (like your example)
running = True

# Create entities
player = Player(x=SCREEN_WIDTH // 2, ground_y=GROUND_Y)
players = pygame.sprite.Group(player)
bullets = pygame.sprite.Group()

want_jump = False
want_shoot = False

while running:
    dt = clock.tick(60) / 16.6667  # normalized dt (~1.0 at 60 FPS)
    now_ms = pygame.time.get_ticks()

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                want_jump = True
            if event.key == KEY_SHOOT:
                want_shoot = True

    # Input state
    keys = pygame.key.get_pressed()
    dir_x = (-1 if keys[pygame.K_a] else 0) + (1 if keys[pygame.K_d] else 0)
    shooting_hold = keys[KEY_SHOOT]

    # Apply inputs
    player.set_inputs(dir_x, shooting_hold)

    if want_jump:
        player.start_jump()
        want_jump = False

    if want_shoot:
        player.request_shoot(now_ms, bullets)
        want_shoot = False

    # Updates
    player.update(dt, dir_x)
    bullets.update()

    # Draw
    screen.blit(bg, (0, 0))

    if SHOW_GROUND_LINE:
        pygame.draw.line(
            screen,
            COLOR_DEBUG_GREEN,
            (0, GROUND_Y - 1),
            (GROUND_END_X, GROUND_Y - 1),
            2,
        )

    players.draw(screen)
    bullets.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()

