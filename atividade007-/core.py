# Imports
import os
import pygame

# Basic config
WIDTH, HEIGHT, FPS = 800, 600, 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (230, 210, 60)
GREEN = (0, 255, 0)
MAGENTA = (255, 0, 255)
SKY_TOP = (140, 200, 255)
SKY_BOTTOM = (100, 170, 255)


# Paths
def _root():
    return os.path.dirname(os.path.abspath(__file__))


def rel(path: str) -> str:
    return os.path.join(_root(), path)


# Pygame init
def init_pygame(enable_sound: bool = True):
    pygame.init()
    mixer_ok = False
    if enable_sound:
        try:
            pygame.mixer.init()
            mixer_ok = True
        except Exception:
            mixer_ok = False

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CORE ENGINE")
    clock = pygame.time.Clock()
    return screen, clock, mixer_ok


# Safe sound load
def safe_sound(path: str, enabled: bool):
    if not enabled:
        return None
    try:
        return pygame.mixer.Sound(rel(path))
    except Exception:
        return None


# Load image with scale
def load_image_scaled(path: str, scale: float) -> pygame.Surface:
    img = pygame.image.load(rel(path)).convert_alpha()
    w, h = img.get_size()
    w2, h2 = max(8, int(w * scale)), max(8, int(h * scale))
    return pygame.transform.smoothscale(img, (w2, h2))


# Vertical gradient
def draw_vertical_gradient(surf: pygame.Surface, top_color, bottom_color):
    w, h = surf.get_size()
    for i in range(h):
        t = i / max(1, h)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        pygame.draw.line(surf, (r, g, b), (0, i), (w, i))


# Screen wrap
def wrap_position(x: float, y: float, w: int = WIDTH, h: int = HEIGHT):
    if x < 0:
        x = w
    elif x > w:
        x = 0
    if y < 0:
        y = h
    elif y > h:
        y = 0
    return x, y


# Cooldown helper
class Cooldown:
    def __init__(self, ms: int):
        self.ms = ms
        self.last = -10**9

    def ready(self) -> bool:
        now = pygame.time.get_ticks()
        if now - self.last >= self.ms:
            self.last = now
            return True
        return False


# Retro font
def _load_retro_font(size: int):
    candidates = [
        "ship/assets/PressStart2P.ttf",
        "tank/assets/PressStart2P.ttf",
    ]
    for path in candidates:
        try:
            return pygame.font.Font(rel(path), size)
        except Exception:
            pass
    return pygame.font.SysFont(None, size)


# Score panel
def draw_score_panel(
    surface: pygame.Surface,
    p1_score: int,
    p2_score: int,
    text_color=BLACK,
    bg_color=SKY_TOP,
    size: int = 44,
    y: int = 50,
):
    font = _load_retro_font(size)
    text = f"{p1_score:02d} x {p2_score:02d}"
    surf = font.render(text, True, text_color, bg_color)
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect)


# Victory screen
def draw_victory_screen(
    surface: pygame.Surface,
    winner_text: str,
    sub_text: str = "Press SPACE to continue",
    bg_color=(0, 0, 0, 160),
    text_color=(255, 220, 60),
    shadow_color=(0, 0, 0),
):
    w, h = surface.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill(bg_color)
    surface.blit(overlay, (0, 0))

    font_big = pygame.font.SysFont("arialblack", 60)
    font_sub = pygame.font.SysFont("arialblack", 28)

    title = font_big.render(winner_text, True, text_color)
    shadow = font_big.render(winner_text, True, shadow_color)
    sub = font_sub.render(sub_text, True, (240, 240, 240))

    surface.blit(
        shadow,
        (w // 2 - title.get_width() // 2 + 3, h // 2 - title.get_height() // 2 - 2),
    )
    surface.blit(
        title,
        (w // 2 - title.get_width() // 2, h // 2 - title.get_height() // 2 - 5),
    )
    surface.blit(sub, (w // 2 - sub.get_width() // 2, h // 2 + 60))


# Round rules
class RoundRules:
    def __init__(self, hits_to_win: int = 3, score_cap: int = 99):
        self.hits_to_win = hits_to_win
        self.score_cap = score_cap


# Round manager
class RoundManager:
    def __init__(self, rules: RoundRules, players_by_id: dict):
        self.rules = rules
        self.players = players_by_id
        self.round_over = False
        self.winner_id = None

    # Register hit
    def on_hit(self, attacker_id: int, target_id: int) -> bool:
        if self.round_over:
            return True

        target = self.players[target_id]
        target.hits = getattr(target, "hits", 0) + 1

        if hasattr(target, "is_spinning"):
            target.is_spinning = True
            if hasattr(target, "spin_progress"):
                target.spin_progress = 0.0

        if target.hits >= self.rules.hits_to_win:
            self.winner_id = attacker_id
            winner = self.players[attacker_id]
            winner.score = min(
                getattr(winner, "score", 0) + 1, self.rules.score_cap
            )
            self.round_over = True
            return True

        return False

    # Update animations
    def update_animations(self):
        for player in self.players.values():
            if hasattr(player, "update_animation"):
                player.update_animation()

    # Reset round
    def reset_round(self, respawn_fn, clear_projectiles_fn=None):
        for player in self.players.values():
            player.hits = 0
            if hasattr(player, "is_spinning"):
                player.is_spinning = False
            if hasattr(player, "spin_progress"):
                player.spin_progress = 0.0

        if clear_projectiles_fn:
            clear_projectiles_fn()

        respawn_fn(self.players)
        self.round_over = False
        self.winner_id = None

    # Winner text
    def winner_text(self, prefix_ship: str = "Player ", prefix_tank: str = "PLAYER "):
        if self.winner_id is None:
            return "", ""
        return f"{prefix_ship}{self.winner_id} wins!", f"{prefix_tank}{self.winner_id} WINS!"
