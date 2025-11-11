import pygame
import sys
import os
import math

pygame.init()

#background
pygame.mixer.init()
pygame.mixer.music.load("./assets/sons/Intro Stage.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

#shot
som_tiro = pygame.mixer.Sound("./assets/sons/tiro.wav") 
som_tiro.set_volume(0.6)


# config
WIDTH, HEIGHT = 700, 560
FPS = 80
SPEED = 5
FRAME_SPEED_IDLE = 0.18
FRAME_SPEED_RUN  = 0.03
FRAME_SPEED_JUMP = 0.10
FRAME_SPEED_SHOOT = 0.08
GRAVITY = 0.7
JUMP_SPEED = 14
GROUND_H = 60
GROUND_Y = HEIGHT - GROUND_H

# megaman scale
SCALE =1.9 #

# MUZZLE (cano)
MUZZLE_INSET_X = 10
MUZZLE_HEIGHT_RATIO = {
    "parado": 0.56,
    "correndo": 0.54,
    "pulando": 0.50,
    "atirando": 0.56,
    "atirando_movimento": 0.54,
    "atirando_pulo": 0.50,
}

# shot
PIZZA_SPEED = 10


#screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MegaMan X")
clock = pygame.time.Clock()

#backgorund
background_path = "assets/background/background1.png"
background = pygame.image.load(background_path).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# sprites and scales
parado = []
for i in range(1, 4):
    img = pygame.image.load(f"assets/parado/parado{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w*SCALE), int(h*SCALE)))
    parado.append(img)

correndo = []
for i in range(1, 12):
    img = pygame.image.load(f"assets/correndo/correndo{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w*SCALE), int(h*SCALE)))
    correndo.append(img)

pulando = []
for i in range(1, 7):
    img = pygame.image.load(f"assets/pulando/pulando{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w*SCALE), int(h*SCALE)))
    pulando.append(img)

atirando = []
for i in range(1, 3):
    img = pygame.image.load(f"assets/atirando/atirando{i}.png").convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w*SCALE), int(h*SCALE)))
    atirando.append(img)


atirando_mov = []
i = 1
while True:
    path = f"assets/atirando_movimento/atirando_m{i}.png"
    if not os.path.isfile(path):
        break
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w*SCALE), int(h*SCALE)))
    atirando_mov.append(img)
    i += 1

# 
atirando_pulo = []
i = 1
while True:
    path = f"assets/atirando_pulo/atirando_p{i}.png"
    if not os.path.isfile(path):
        break
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    img = pygame.transform.scale(img, (int(w*SCALE), int(h*SCALE)))
    atirando_pulo.append(img)
    i += 1

# pizza
pizza_img = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.circle(pizza_img, (255, 200, 100), (10, 10), 10)
pygame.draw.circle(pizza_img, (200, 60, 60), (10, 10), 6)
pygame.draw.circle(pizza_img, (255, 220, 50), (10, 10), 3)

#states
x = WIDTH // 2
y = GROUND_Y
vy = 0
on_ground = True
direita = True
estado = "parado"
atirando_agora = False       
spawn_pizza = False          
frame = 0
timer = 0
pizzas = []                   # {"x":float,"y":float,"angle":float}

def anim_speed_for(state):
    if state in ("correndo", "atirando_movimento"): return FRAME_SPEED_RUN
    if state in ("pulando", "atirando_pulo"): return FRAME_SPEED_JUMP
    if state == "atirando": return FRAME_SPEED_SHOOT
    return FRAME_SPEED_IDLE

prev_estado = None

# === LOOP ===
running = True
while running:
    dt = clock.tick(FPS) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
            atirando_agora = True
            spawn_pizza = True
            frame = 0
            timer = 0
            som_tiro.play()  #  som

        elif event.type == pygame.KEYUP and event.key == pygame.K_j:
            atirando_agora = False

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

    #states
    if atirando_agora:
        if not on_ground and atirando_pulo:
            frames = atirando_pulo
            estado = "atirando_pulo"
        elif movendo and atirando_mov:
            frames = atirando_mov
            estado = "atirando_movimento"
        else:
            frames = atirando
            estado = "atirando"
    else:
        if not on_ground:
            frames = pulando
            estado = "pulando"
        elif movendo:
            frames = correndo
            estado = "correndo"
        else:
            frames = parado
            estado = "parado"

    # reset ao trocar de estado
    if estado != prev_estado:
        frame = 0
        timer = 0
        prev_estado = estado

    #animation
    timer += dt
    if timer > anim_speed_for(estado):
        timer = 0
        if estado in ("pulando", "atirando_pulo"):
            frame = min(frame + 1, len(frames) - 1)
        else:
            frame = (frame + 1) % len(frames)

    #background
    screen.blit(background, (0, 0))

    # sprite
    sprite = frames[min(frame, len(frames)-1)]
    if not direita:
        sprite = pygame.transform.flip(sprite, True, False)
    rect = sprite.get_rect(midbottom=(x, int(y)))

    # pizza position
    if spawn_pizza:
        w, h = sprite.get_size()
        ratio = MUZZLE_HEIGHT_RATIO.get(estado, 0.55)
        muzzle_y = rect.top + int(h * ratio)
        if direita:
            muzzle_x = rect.right - MUZZLE_INSET_X
            angle = 0
        else:
            muzzle_x = rect.left + MUZZLE_INSET_X
            angle = 180
        pizzas.append({"x": float(muzzle_x), "y": float(muzzle_y), "angle": float(angle)})
        spawn_pizza = False

    # pizzas ang
    novas = []
    for p in pizzas:
        rad = math.radians(p["angle"])
        p["x"] += math.cos(rad) * PIZZA_SPEED
        p["y"] -= math.sin(rad) * PIZZA_SPEED
        if -100 < p["x"] < WIDTH + 100 and -200 < p["y"] < HEIGHT + 200:
            novas.append(p)
    pizzas = novas

    #desing
    screen.blit(sprite, rect.topleft)
    pw, ph = pizza_img.get_size()
    for p in pizzas:
        screen.blit(pizza_img, (int(p["x"] - pw // 2), int(p["y"] - ph // 2)))

    pygame.display.flip()

pygame.quit()
sys.exit()
