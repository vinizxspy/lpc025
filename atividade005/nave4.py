import pygame
import math

pygame.init()
pygame.mixer.init()

white = (255, 255, 255)
black = (0, 0, 0)
screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Asteroids")
clock = pygame.time.Clock()


# Sprite Class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # base image
        self.original_image = pygame.image.load("./nave.jpeg").convert_alpha()
        self.original_image = pygame.transform.scale_by(self.original_image, 0.1)

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        # rotation attributes
        self.angle = 0  # 0° pointing upward
        self.rotation_speed = 3  # rotation speed

    def update(self):
        keys = pygame.key.get_pressed()

        # Ship rotation
        if keys[pygame.K_LEFT]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT]:
            self.angle -= self.rotation_speed

        # Update rotated image without distortion
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Move forward (based on the image’s "front" = top)
        if keys[pygame.K_UP]:
            rad = math.radians(self.angle - 270)  # subtract 90° to align the top as the front
            self.rect.x += math.cos(rad) * 5
            self.rect.y -= math.sin(rad) * 5  # inverted for pygame coordinates


# Sprite group creation
all_sprites = pygame.sprite.Group()
player = Player(400, 400)
all_sprites.add(player)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(black)
    all_sprites.update()
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()