# Tela
WIDTH = 960
HEIGHT = 720
FPS = 60

# Jogo
START_LIVES = 3
SAFE_SPAWN_TIME = 2.0  # s de invulnerabilidade ao renascer
WAVE_DELAY = 2.0       # s entre ondas

# Nave
SHIP_RADIUS = 15
SHIP_TURN_SPEED = 220.0  # deg/s
SHIP_THRUST = 220.0      # px/s^2
SHIP_FRICTION = 0.995
SHIP_FIRE_RATE = 0.2     # s entre tiros
SHIP_BULLET_SPEED = 420.0
HYPERSPACE_COST = 250    # pontos negativos

# Asteroides
AST_VEL_MIN = 30.0
AST_VEL_MAX = 90.0
AST_SIZES = {
    "L": {"r": 46, "score": 20, "split": ["M", "M"]},
    "M": {"r": 24, "score": 50, "split": ["S", "S"]},
    "S": {"r": 12, "score": 100, "split": []},
}

# Tiro
BULLET_RADIUS = 2
BULLET_TTL = 1.0
MAX_BULLETS = 4

# UFO
UFO_SPAWN_EVERY = 15.0
UFO_SPEED = 80.0
UFO_BIG = {"r": 18, "score": 200, "aim": 0.2}
UFO_SMALL = {"r": 12, "score": 1000, "aim": 0.6}

# Áudio (efeitos sonoros)
MASTER_VOLUME = 0.5  
SND_PLAYER_SHOOT = "assets/sounds/player_shoot.mp3" 
SND_UFO_SHOOT = "assets/sounds/ufo_shoot.mp3"  
SND_EXPLOSION = "assets/sounds/explosion.mp3" 

# Cores (R, G, B)
WHITE = (240, 240, 240)
GRAY = (120, 120, 120)
BLACK = (0, 0, 0)

# Aleatoriedade
RANDOM_SEED = None  # ou defina um int para reprodutibilidade
