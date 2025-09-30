# breakout - one block per paddle hit, blocks solid after break

# First test comment of the break code
import math
import pygame
from pathlib import Path

pygame.init()
pygame.mixer.init()

# SCREEN SETUP
screen_size = (800, 800)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Break Out")

# PLAYER AND BALL SETUP
ball_size = 15
ball = pygame.Rect(400, 500, ball_size, ball_size)

player_size = 100
player = pygame.Rect(400, 750, player_size, 15)

blocks_per_line = 14
lines_of_blocks = 8

# COLLORS
colors = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "blue": (0, 0, 255),
    "orange": (249, 79, 0),
    "red": (255, 0, 0),
}

# Map each color to a score value
points_per_color = {
    colors["white"]: 0,
    colors["yellow"]: 1,
    colors["green"]: 3,
    colors["orange"]: 5,
    colors["red"]: 7
}

# GAME VARIABLES
end_game = False
lives = 3
score = 0
speed_level_1 = 2.0
speed_level_2 = 3.5
speed_level_3 = 4.5
speed_level_4 = 5.5

# Flags to control if the speed has already been changed
hit_green = False
hit_orange = False
hit_red = False


# Initial diagonal normalized ball direction
ball_move = [speed_level_1 / (2**0.5), speed_level_1 / (2**0.5)]
can_break_block = True  # Allow breaking 1 block after paddle hit


# BLOCKS
def create_blocks(blocks_per_line, lines_of_blocks):
    """Create blocks on the screen with defined spacing."""
    width_size, height_size = screen_size
    block_distance = int(width_size * 0.008)  # reduce space between blocks
    block_width = width_size / blocks_per_line - block_distance
    block_height = int(height_size * 0.015)  # thinner height
    line_distance = block_height + int(height_size * 0.01)

    blocks = []
    offset_top = int(height_size * 0.1)
    for j in range(lines_of_blocks):
        for i in range(blocks_per_line):
            block = pygame.Rect(
                i * (block_width + block_distance),
                offset_top + j * line_distance,
                block_width,
                block_height
            )
            blocks.append(block)
    return blocks


# Colors per line
line_colors = [
    colors["red"], colors["red"], colors["orange"], colors["orange"],
    colors["green"], colors["green"], colors["yellow"], colors["yellow"]
]

# Create blocks and colors
blocks = create_blocks(blocks_per_line, lines_of_blocks)
block_colors = []
for line in range(lines_of_blocks):
    for _ in range(blocks_per_line):
        block_colors.append(line_colors[line])

# SOUNDS SETUP
BASE = Path(__file__).resolve().parent  # script folder

# Game sounds
sound_blocks = pygame.mixer.Sound(str(BASE / "assets/breaksound.wav"))
sound_collision = pygame.mixer.Sound(str(BASE / "assets/bounce.wav"))
sound_loss = pygame.mixer.Sound(str(BASE / "assets/wrong-buzzer-6268.mp3"))


# DRAWING FUNCTIONS
def draw_start_screen():
    """Draw ball and player on the start screen."""
    screen.fill(colors["black"])
    pygame.draw.rect(screen, colors["blue"], player)
    pygame.draw.rect(screen, colors["white"], ball)


def draw_blocks(blocks):
    """Draw blocks on the screen with specific colors."""
    for idx, block in enumerate(blocks):
        pygame.draw.rect(screen, block_colors[idx], block)


def draw_end_screen(message):
    """Draw end game screen with a message."""
    screen.fill(colors["black"])
    font = pygame.font.SysFont(None, 80)
    text = font.render(message, True, colors["white"])
    center_coords = (screen_size[0] // 2, screen_size[1] // 2)
    text_rect = text.get_rect(center=center_coords)
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)


def update_player_movement():
    """Update player position based on keys."""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT] and (player.x + player_size) < screen_size[0]:
        player.x += 5
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= 5


# BALL MOVEMENT
def move_ball(ball, lives):
    """Move the ball and update lives if necessary."""
    global ball_move
    movement = ball_move
    ball.x += movement[0]
    ball.y += movement[1]

    # Wall collisions
    if ball.x <= 0:
        ball.x = 0
        movement[0] = -movement[0]
        sound_collision.play()
    if ball.x + ball_size >= screen_size[0]:
        ball.x = screen_size[0] - ball_size
        movement[0] = -movement[0]
        sound_collision.play()
    if ball.y < 0:
        ball.y = 0
        movement[1] = -movement[1]
        sound_collision.play()

    # Lives system
    if ball.y + ball_size >= screen_size[1]:
        sound_loss.play()
        lives -= 1
        if lives > 0:
            ball.x = screen_size[0] // 2
            ball.y = screen_size[1] // 2

            # Keep speed according to previous hits
            current_speed = speed_level_1
            if hit_green:
                current_speed = speed_level_2
            if hit_orange:
                current_speed = speed_level_3
            if hit_red:
                current_speed = speed_level_4

            movement[0] = current_speed / math.sqrt(2)
            movement[1] = -current_speed / math.sqrt(2)
            return movement, lives
        else:
            return None, lives  # out of lives
    return movement, lives


# BALL COLLISION
def ball_collision_player(ball, player):
    """Check ball collision with player and adjust speed."""
    global hit_green, hit_orange, hit_red, can_break_block
    if ball.colliderect(player) and ball_move[1] > 0:
        sound_collision.play()
        ball.bottom = player.top
        ball_move[1] = -ball_move[1]
        offset = ball.centerx - player.centerx
        new_speed_x = max(-6, min(6, offset / 10))
        ball_move[0] = new_speed_x

        # Adjust target speed according to levels
        target_speed = speed_level_1
        if hit_green:
            target_speed = speed_level_2
        if hit_orange:
            target_speed = speed_level_3
        if hit_red:
            target_speed = speed_level_4

        current_speed = math.sqrt(ball_move[0]**2 + ball_move[1]**2)
        if current_speed > 0:
            factor = target_speed / current_speed
            ball_move[0] *= factor
            ball_move[1] *= factor

        # Reset permission to break one block per paddle hit
        can_break_block = True


# MAIN LOOP
while not end_game:
    result = move_ball(ball, lives)
    draw_start_screen()
    draw_blocks(blocks)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_game = True

    update_player_movement()
    if result[0] is None:
        draw_end_screen("GAME OVER")
        break
    else:
        ball_move, lives = result

    ball_collision_player(ball, player)

    # BLOCK COLLISION
    collided_blocks = [
        idx
        for idx, block in enumerate(blocks)
        if ball.colliderect(block)
    ]
    for idx in collided_blocks:
        block = blocks[idx]

        # Only break one block per paddle hit
        if can_break_block:
            can_break_block = False  # Already broke one block
            # Points gained and speed update
            block_color = block_colors[idx]
            target_speed = 0
            if block_color == colors["red"] and not hit_red:
                hit_red = True
                hit_orange = True
                hit_green = True
                target_speed = speed_level_4
            elif block_color == colors["orange"] and not hit_orange:
                hit_orange = True
                hit_green = True
                target_speed = speed_level_3
            elif block_color == colors["green"] and not hit_green:
                hit_green = True
                target_speed = speed_level_2

            if target_speed > 0:
                speed_current = math.sqrt(ball_move[0]**2 + ball_move[1]**2)
                if speed_current > 0:
                    factor = target_speed / speed_current
                    ball_move[0] *= factor
                    ball_move[1] *= factor

            score += points_per_color.get(block_color, 1)
            sound_blocks.play()

            # Remove broken block
            blocks.pop(idx)
            block_colors.pop(idx)

        # Treat remaining blocks as solid
        overlap_x = min(ball.right - block.left, block.right - ball.left)
        overlap_y = min(ball.bottom - block.top, block.bottom - ball.top)
        if overlap_x < overlap_y:
            if ball.centerx < block.centerx:
                ball.right = block.left
            else:
                ball.left = block.right
            ball_move[0] = -ball_move[0]
        else:
            if ball.centery < block.centery:
                ball.bottom = block.top
            else:
                ball.top = block.bottom
            ball_move[1] = -ball_move[1]

    # Win condition
    if len(blocks) == 0:
        draw_end_screen("YOU WIN!")
        break

    # HUD
    font_size = int(screen_size[1] * 0.05)
    font = pygame.font.SysFont(None, font_size)
    y_pos_top = 10

    # Formatted score
    formatted_score = f"{score:03d}"
    score_text = font.render(formatted_score, True, colors["white"])
    x_pos_score = screen_size[0] // 2 + 100
    screen.blit(score_text, (x_pos_score, y_pos_top))

    # Remaining lives
    lives_text = font.render(f"{lives}", True, colors["white"])
    screen.blit(lives_text, (30, y_pos_top))

    # Central divider
    player_label = font.render("||", True, colors["white"])
    screen.blit(player_label, (screen_size[0] // 2 - 100, y_pos_top))

    pygame.time.wait(5)
    pygame.display.flip()

pygame.quit()