# startbreak.py
import pygame
import sys
import breakout as breakout  # importa seu jogo principal

pygame.init()

# Configurações da tela de start
screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Break Out - Start Screen")

# Cores
color = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "blue": (0, 0, 255)
}

# Fonte
font = pygame.font.SysFont(None, 60)

def start_screen():
    running = True
    while running:
        screen.fill(color["black"])
        
        # Texto centralizado
        title_text = font.render("BREAK OUT", True, color["white"])
        start_text = font.render("Press SPACE to Start", True, color["blue"])
        
        title_rect = title_text.get_rect(center=(screen_size[0]//2, screen_size[1]//2 - 50))
        start_rect = start_text.get_rect(center=(screen_size[0]//2, screen_size[1]//2 + 50))
        
        screen.blit(title_text, title_rect)
        screen.blit(start_text, start_rect)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False  # sai da tela de start e inicia o jogo

# Roda a tela de start
start_screen()

# Após sair da tela, inicia o Breakout
breakout  # executa o break.py