import pygame
import math

pygame.init()
pygame.mixer.init()

# Cores e configuração de tela
white = (255, 255, 255)
black = (0, 0, 0)
screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()


# Classe da Nave (Player)
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Imagem base da nave
        self.original_image = pygame.image.load("./nave.jpeg").convert_alpha()
        self.original_image = pygame.transform.scale_by(self.original_image, 0.1)

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        # Atributos de rotação
        self.angle = 0  # 0° significa "frente para cima"
        self.rotation_speed = 3  # velocidade de rotação

        # Atributos de movimento
        self.vel_x = 0
        self.vel_y = 0
        self.acceleration = 0.3
        self.friction = 0.98  # desaceleração natural (atrito)

    def update(self):
        keys = pygame.key.get_pressed()

        # Rotação da nave
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed

        # Movimento para frente (seta ↑)
        if keys[pygame.K_UP]:
            rad = math.radians(self.angle - 270)  # "topo" da imagem é a frente
            self.vel_x += math.cos(rad) * self.acceleration
            self.vel_y -= math.sin(rad) * self.acceleration

        # seta ↓
        # Reduz gradualmente a velocidade da nave
        if keys[pygame.K_DOWN]:
            self.vel_x *= 0.9  # quanto menor o valor, mais forte o freio
            self.vel_y *= 0.9

        # Aplicar atrito natural (mesmo sem apertar nada)
        self.vel_x *= self.friction
        self.vel_y *= self.friction

        # Atualiza posição com base na velocidade
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Atualiza a imagem rotacionada da nave
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


# Grupo de sprites
all_sprites = pygame.sprite.Group()
player = Player(400, 400)
all_sprites.add(player)

# Loop principal do jogo
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Atualiza tela
    screen.fill(black)
    all_sprites.update()
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
