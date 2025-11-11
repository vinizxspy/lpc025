import os
import re
import sys
import math
import pygame

pygame.init()

# === CONFIG ===
WIDTH, HEIGHT = 960, 540
FPS = 60
SPEED = 5
FRAME_SPEED_IDLE = 0.18
FRAME_SPEED_RUN = 0.08
FRAME_SPEED_JUMP = 0.10
FRAME_SPEED_SHOOT = 0.08
GRAVITY = 0.7
JUMP_SPEED = 14
GROUND_Y = HEIGHT - 130  # “chão” visual do cenário

# === MUZZLE (cano da arma) ===
MUZZLE_INSET_X = 12
MUZZLE_HEIGHT_RATIO = {
    "parado": 0.56,
    "correndo": 0.54,
    "pulando": 0.50,
    "atirando": 0.56,
    "atirando_movimento": 0.54,
    "atirando_pulo": 0.50,
}

# === PROJÉTIL (ANGULAR) ===
PIZZA_SPEED = 10       # velocidade do projétil
TILT_UP_DEG = 12       # inclinação para cima quando no ar (opcional)

# === TELA ===
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MegaMan X")
clock = pygame.time.Clock()

# === FUNDO (tile com escala inteira; evita buracos e rastros) ===
bg_path = "assets/background/background1.png"
bg_raw = pygame.image.load(bg_path).convert()
bg_w, bg_h = bg_raw.get_size()
tile_scale = max(1, int(min(WIDTH // bg_w, HEIGHT // bg_h)))  # fator inteiro p/ pixel-art
bg_tile = pygame.transform.scale(bg_raw, (bg_w * tile_scale, bg_h * tile_scale))
tile_w, tile_h = bg_tile.get_size()

def draw_background(surface):
    for ty in range(0, HEIGHT, tile_h):
        for tx in range(0, WIDTH, tile_w):
            surface.blit(bg_tile, (tx, ty))

# === UTILS DE CARREGAMENTO ===
_num_re = re.compile(r"(\d+)")

def _natural_key(name: str):
    return [int(s) if s.isdigit() else s.lower() for s in _num_re.split(name)]

def load_series_exact(folder: str, prefix: str, scale: float = 2.5):
    frames = []
    i = 1
    while True:
        path = os.path.join("assets", folder, f"{prefix}{i}.png")
        if not os.path.isfile(path):
            break
        img = pygame.image.load(path).convert_alpha()
        if scale != 1.0:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        frames.append(img)
        i += 1
    if not frames:
        print(f"[AVISO] Nenhum frame em assets/{folder}/ com prefixo {prefix}")
        frames.append(pygame.Surface((1, 1), pygame.SRCALPHA))
    return frames

def load_series_flex(folder: str, prefixes: list[str], scale: float = 2.5):
    """
    Carrega frames aceitando múltiplos prefixos (ordem natural).
    Ex.: folder='atirando_pulo', prefixes=['atirando_pulo','atirando_p','shoot_jump']
    """
    base = os.path.join("assets", folder)
    if not os.path.isdir(base):
        print(f"[AVISO] Pasta ausente: {base}")
        return [pygame.Surface((1, 1), pygame.SRCALPHA)]

    all_files = [f for f in os.listdir(base) if f.lower().endswith(".png")]
    if not all_files:
        print(f"[AVISO] Sem PNGs em {base}")
        return [pygame.Surface((1, 1), pygame.SRCALPHA)]

    pref_low = [p.lower() for p in prefixes]
    wanted = [f for f in all_files if any(f.lower().startswith(p) for p in pref_low)]

    if not wanted:
        wanted = all_files
        print(f"[AVISO] Prefixos {prefixes} não encontrados em {base}, usando todos PNGs.")

    wanted.sort(key=_natural_key)

    frames = []
    for fname in wanted:
        path = os.path.join(base, fname)
        img = pygame.image.load(path).convert_alpha()
        if scale != 1.0:
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * scale), int(h * scale)))
        frames.append(img)

    if not frames:
        frames = [pygame.Surface((1, 1), pygame.SRCALPHA)]
    return frames

# === SPRITES ===
parado   = load_series_exact("parado",   "parado",   scale=2.5)  # 3
correndo = load_series_exact("correndo", "correndo", scale=2.5)  # 11
pulando  = load_series_exact("pulando",  "pulando",  scale=2.5)  # 6

# Tiro parado (geralmente 2)
atirando = load_series_exact("atirando", "atirando", scale=2.5)

# Atirando correndo (aceita atirando_mX e alternativos)
atirando_movimento = load_series_flex(
    "atirando_movimento",
    prefixes=["atirando_movimento", "atirando_m", "shoot_run", "running_shoot"],
    scale=2.5,
)

# Atirando pulando (aceita atirando_pX e alternativos)
atirando_pulo = load_series_flex(
    "atirando_pulo",
    prefixes=["atirando_pulo", "atirando_p", "shoot_jump", "jump_shoot"],
    scale=2.5,
)

# === IMAGEM DA PIZZA (projétil) ===
pizza_img = pygame.Surface((24, 24), pygame.SRCALPHA)
pygame.draw.circle(pizza_img, (255, 200, 100), (12, 12), 12)
pygame.draw.circle(pizza_img, (200, 60, 60), (12, 12), 8)
pygame.draw.circle(pizza_img, (255, 220, 50), (12, 12), 4)

# === ESTADO ===
x = WIDTH // 2
y = GROUND_Y
vy = 0
on_ground = True
direita = True
frame = 0
timer = 0
pizzas = []             # agora: {"x":..,"y":..,"angle":..}
shooting_cycle = False  # ciclo curto quando J é pressionado
spawn_pizza = False     # cria pizza na boca da arma neste frame

state_name = "parado"
prev_state_name = None

def anim_speed_for(name: str) -> float:
    if name in ("correndo", "atirando_movimento"):
        return FRAME_SPEED_RUN
    if name in ("pulando", "atirando_pulo"):
        return FRAME_SPEED_JUMP
    if name in ("atirando",):
        return FRAME_SPEED_SHOOT
    return FRAME_SPEED_IDLE

# === LOOP ===
running = True
while running:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # Disparo: quando APERTA J, inicia ciclo e agenda pizza para nascer no cano
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
            shooting_cycle = True
            frame = 0
            timer = 0
            spawn_pizza = True  # criaremos após calcular sprite/rect do estado atual

        # Ao SOLTAR J, encerra tiro imediatamente (volta ao estado base)
        elif event.type == pygame.KEYUP and event.key == pygame.K_j:
            shooting_cycle = False

    keys = pygame.key.get_pressed()

    # === FLAGS DE ENTRADA ===
    shooting_held = keys[pygame.K_j]        # mantém animação de tiro enquanto J estiver pressionado
    left_pressed  = keys[pygame.K_a]
    right_pressed = keys[pygame.K_d]
    jump_pressed  = keys[pygame.K_w]

    # === MOVIMENTO LATERAL ===
    movendo = False
    if left_pressed:
        x -= SPEED
        direita = False
        movendo = True
    if right_pressed:
        x += SPEED
        direita = True
        movendo = True

    # === PULO ===
    if jump_pressed and on_ground:
        vy = -JUMP_SPEED
        on_ground = False
        frame = 0
        timer = 0

    # === GRAVIDADE ===
    if not on_ground:
        vy += GRAVITY
        y += vy
        if y >= GROUND_Y:
            y = GROUND_Y
            vy = 0
            on_ground = True

    # ===== LIMITES DE TELA (DESCOMENTE PARA ATIVAR) =====
    # MARGEM_X = 24
    # TOPO_MAX = 60
    # x = max(MARGEM_X, min(WIDTH - MARGEM_X, x))
    # y = min(GROUND_Y, y)
    # y = max(TOPO_MAX, y)

    # === ESCOLHA DE ESTADO/FRAMES ===
    active_shoot = shooting_held or shooting_cycle

    if active_shoot:
        if not on_ground and len(atirando_pulo) > 0:
            frames = atirando_pulo
            state_name = "atirando_pulo"
        elif movendo and len(atirando_movimento) > 0:
            frames = atirando_movimento
            state_name = "atirando_movimento"
        elif len(atirando) > 0:
            frames = atirando
            state_name = "atirando"
        else:
            if not on_ground:
                frames = pulando
                state_name = "pulando"
            elif movendo:
                frames = correndo
                state_name = "correndo"
            else:
                frames = parado
                state_name = "parado"
    else:
        if not on_ground:
            frames = pulando
            state_name = "pulando"
        elif movendo:
            frames = correndo
            state_name = "correndo"
        else:
            frames = parado
            state_name = "parado"

    # Reset seguro ao mudar de estado (evita índice fora do range)
    if state_name != prev_state_name:
        frame = 0
        timer = 0
        prev_state_name = state_name

    # === ANIMAÇÃO ===
    timer += dt
    speed = anim_speed_for(state_name)
    if timer > speed:
        timer = 0
        if state_name in ("pulando", "atirando_pulo"):
            frame = min(frame + 1, len(frames) - 1)  # pulo pode travar no último
        else:
            frame = (frame + 1) % len(frames)

    # === DESENHO DO FUNDO ===
    draw_background(screen)

    # Sprite atual
    safe_index = min(frame, len(frames) - 1)
    sprite = frames[safe_index]
    if not direita:
        sprite = pygame.transform.flip(sprite, True, False)
    rect = sprite.get_rect(midbottom=(x, int(y)))

    # === CRIA A PIZZA NA BOCA DA ARMA (no frame do KEYDOWN J) ===
    if spawn_pizza:
        w, h = sprite.get_size()
        ratio = MUZZLE_HEIGHT_RATIO.get(state_name, 0.55)
        muzzle_y = rect.top + int(h * ratio)
        if direita:
            muzzle_x = rect.right - MUZZLE_INSET_X
            base_angle = 0
        else:
            muzzle_x = rect.left + MUZZLE_INSET_X
            base_angle = 180

        # pequeno tilt para cima quando no ar (opcional)
        if not on_ground:
            base_angle += -TILT_UP_DEG if (base_angle == 0) else TILT_UP_DEG

        # guarda em ângulo (graus)
        pizzas.append({"x": float(muzzle_x), "y": float(muzzle_y), "angle": float(base_angle)})
        spawn_pizza = False

    # === ATUALIZA PIZZAS (movimento por ângulo) ===
    new_pizzas = []
    for p in pizzas:
        rad = math.radians(p["angle"])
        p["x"] += math.cos(rad) * PIZZA_SPEED
        p["y"] -= math.sin(rad) * PIZZA_SPEED  # Y cresce pra baixo, por isso menos sin
        if -100 < p["x"] < WIDTH + 100 and -200 < p["y"] < HEIGHT + 200:
            new_pizzas.append(p)
    pizzas = new_pizzas

    # === DESENHA PERSONAGEM ===
    screen.blit(sprite, rect.topleft)

    # === DESENHA PIZZAS (centraliza o sprite da pizza) ===
    pw, ph = pizza_img.get_size()
    for p in pizzas:
        screen.blit(pizza_img, (int(p["x"] - pw // 2), int(p["y"] - ph // 2)))

    pygame.display.flip()

pygame.quit()
sys.exit()
