import pygame
import sys
import os

pygame.init()

# === CONFIG ===
WIDTH, HEIGHT = 960, 540
FPS = 60
SPEED = 5
FRAME_SPEED_IDLE = 0.18
FRAME_SPEED_RUN  = 0.03
FRAME_SPEED_JUMP = 0.10
FRAME_SPEED_SHOOT = 0.08
GRAVITY = 0.7
JUMP_SPEED = 14
GROUND_H = 60
GROUND_Y = HEIGHT - GROUND_H

# === TELA ===
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MegaMan X")
clock = pygame.time.Clock()

# === FUNDO ===
background_path = "assets/background/background1.png"
background = pygame.image.load(background_path).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# === SPRITES ===
parado   = [pygame.image.load(f"assets/parado/parado{i}.png").convert_alpha() for i in range(1, 4)]
correndo = [pygame.image.load(f"assets/correndo/correndo{i}.png").convert_alpha() for i in range(1, 12)]
pulando  = [pygame.image.load(f"assets/pulando/pulando{i}.png").convert_alpha() for i in range(1, 7)]
atirando = [pygame.image.load(f"assets/atirando/atirando{i}.png").convert_alpha() for i in range(1, 3)]

# === CRIA PIZZA ===
pizza_img = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.circle(pizza_img, (255, 200, 100), (10, 10), 10)
pygame.draw.circle(pizza_img, (200, 60, 60), (10, 10), 6)
pygame.draw.circle(pizza_img, (255, 220, 50), (10, 10), 3)

# === ESTADOS ===
x = WIDTH // 2
y = GROUND_Y
vy = 0
on_ground = True
direita = True
estado = "parado"
atirando_agora = False
frame = 0
timer = 0
pizzas = []
PIZZA_SPEED = 10

def anim_speed_for(state):
    if state == "correndo": return FRAME_SPEED_RUN
    if state == "pulando":  return FRAME_SPEED_JUMP
    if state == "atirando": return FRAME_SPEED_SHOOT
    return FRAME_SPEED_IDLE

# === LOOP ===
running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_x:
            estado = "atirando"
            atirando_agora = True
            frame = 0
            timer = 0
            offset = 40 if direita else -40
            pizzas.append({"x": x + offset, "y": y - 40, "dir": 1 if direita else -1})

    keys = pygame.key.get_pressed()

    # === MOVIMENTO ===
    movendo = False
    if keys[pygame.K_a]:
        x -= SPEED
        direita = False
        movendo = True
    if keys[pygame.K_d]:
        x += SPEED
        direita = True
        movendo = True

    # === PULO ===
    if keys[pygame.K_w] and on_ground:
        vy = -JUMP_SPEED
        on_ground = False
        estado = "pulando"
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

    # === ESTADOS ===
    if atirando_agora:
        frames = atirando
    elif not on_ground:
        frames = pulando
    elif movendo:
        frames = correndo
    else:
        frames = parado

    if atirando_agora and frame >= len(atirando) - 1:
        atirando_agora = False
        estado = "parado"

    # === ANIMAÇÃO ===
    timer += dt
    if timer > anim_speed_for(estado):
        timer = 0
        frame = (frame + 1) % len(frames)

    # === PIZZAS ===
    for pizza in pizzas:
        pizza["x"] += pizza["dir"] * PIZZA_SPEED
    pizzas = [p for p in pizzas if 0 < p["x"] < WIDTH]

    # === DESENHO ===
    screen.blit(background, (0, 0))  # fundo
    pygame.draw.rect(screen, (25, 25, 25), (0, GROUND_Y, WIDTH, GROUND_H))
    pygame.draw.line(screen, (70, 70, 70), (0, GROUND_Y), (WIDTH, GROUND_Y), 2)

    sprite = frames[min(frame, len(frames)-1)]
    if not direita:
        sprite = pygame.transform.flip(sprite, True, False)

    rect = sprite.get_rect(midbottom=(x, int(y)))
    screen.blit(sprite, rect.topleft)

    for pizza in pizzas:
        screen.blit(pizza_img, (pizza["x"], pizza["y"]))

    pygame.display.flip()

pygame.quit()
sys.exit()
