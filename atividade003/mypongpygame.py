# Jucimar Jr
# 2024

import pygame
import math

pygame.init()

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

SCORE_MAX = 2

SIZE = (1280, 720)
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("MyPong - PyGame Edition - 2024-09-02")

# Score text
score_font = pygame.font.Font('assets/PressStart2P.ttf', 44)
score_text = score_font.render('00 x 00', True, COLOR_WHITE, COLOR_BLACK)
score_text_rect = score_text.get_rect()
score_text_rect.center = (680, 50)

# Victory text
victory_font = pygame.font.Font('assets/PressStart2P.ttf', 100)
victory_text = victory_font.render('VICTORY', True, COLOR_WHITE, COLOR_BLACK)
victory_text_rect = victory_text.get_rect()
victory_text_rect.center = (640, 360)

# Sound effects
bounce_sound_effect = pygame.mixer.Sound('assets/bounce.wav')
scoring_sound_effect = pygame.mixer.Sound(
    'assets/258020__kodack__arcade-bleep-sound.wav'
)

# Player 1
player_1 = pygame.image.load("assets/player.png")
player_1_y = 300
player_1_move_up = False
player_1_move_down = False

# Player 2 - robot
player_2 = pygame.image.load("assets/player.png")
player_2_y = 300
player_2_speed = 5

# Ball
ball = pygame.image.load("assets/ball.png")
ball_x = 640
ball_y = 360
ball_dx = 5
ball_dy = 5

# NEW VELOCITY VARIABLES
BALL_SPEED_DEFAULT = 5
BALL_SPEED_MAX = 15
BALL_SPEED_INCREASE = 0.25  # Increases by 0.25 with each hit

# Score
score_1 = 0
score_2 = 0

# Game loop
game_loop = True
game_clock = pygame.time.Clock()

while game_loop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_loop = False

        # Keystroke events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player_1_move_up = True
            if event.key == pygame.K_DOWN:
                player_1_move_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                player_1_move_up = False
            if event.key == pygame.K_DOWN:
                player_1_move_down = False

    # Checking the victory condition
    if score_1 < SCORE_MAX and score_2 < SCORE_MAX:
        # Clear screen
        screen.fill(COLOR_BLACK)

        # Ball collision with the wall (FIXED)
        if ball_y > 700:
            ball_y = 700  # Forces the ball back onto the screen
            ball_dy *= -1
            bounce_sound_effect.play()
        elif ball_y <= 0:
            ball_y = 0  # Forces the ball back onto the screen
            ball_dy *= -1
            bounce_sound_effect.play()

        # Ball collision with player 1's paddle (FIXED)
        # Added 'ball_dx < 0' to prevent bugs
        if ball_x < 100 and ball_dx < 0:
            if player_1_y < ball_y + 25 and player_1_y + 150 > ball_y:
                # Reverses the horizontal direction
                ball_dx *= -1
                bounce_sound_effect.play()

                # Calculates the center of the paddle
                # and the center of the ball
                paddle_center = player_1_y + 75
                ball_center = ball_y + 12.5

                # Calculates the distance from the center of
                # the paddle to the center of the ball
                impact_diff = paddle_center - ball_center

                # Adjusts the vertical speed based on the difference.
                # The divisor (e.g., 10) controls the "intensity" of the angle.
                ball_dy = -impact_diff / 10
            # INCREASES THE BALL'S SPEED
            if abs(ball_dx) < BALL_SPEED_MAX:
                ball_dx += math.copysign(BALL_SPEED_INCREASE, ball_dx)

        # Ball collision with player 2's paddle (FIXED)
        # Added 'ball_dx > 0' to prevent bugs
        if ball_x > 1160 and ball_dx > 0:
            if player_2_y < ball_y + 25 and player_2_y + 150 > ball_y:
                # Reverses the horizontal direction
                ball_dx *= -1
                bounce_sound_effect.play()

                paddle_center = player_2_y + 75
                ball_center = ball_y + 12.5
                impact_diff = paddle_center - ball_center
                ball_dy = -impact_diff / 10

                # INCREASES THE BALL'S SPEED
                if abs(ball_dx) < BALL_SPEED_MAX:
                    ball_dx += math.copysign(BALL_SPEED_INCREASE, ball_dx)

        # Scoring points
        if ball_x < -50:
            ball_x = 640
            ball_y = 360
            # Reverses direction and RESETS the speed
            ball_dy *= -1
            ball_dx = math.copysign(BALL_SPEED_DEFAULT, -1)
            # Serves to the right
            score_2 += 1
            scoring_sound_effect.play()
        elif ball_x > 1320:
            ball_x = 640
            ball_y = 360
            # Reverses direction and RESETS the speed
            ball_dy *= -1
            ball_dx = math.copysign(BALL_SPEED_DEFAULT, 1)
            # Serves to the left
            score_1 += 1
            scoring_sound_effect.play()

        # Ball movement
        ball_x += ball_dx
        ball_y += ball_dy

        # Player 1 up movement
        if player_1_move_up:
            player_1_y -= 5

        # Player 1 down movement
        if player_1_move_down:
            player_1_y += 5

        # Player 1 collides with upper wall
        if player_1_y <= 0:
            player_1_y = 0

        # Player 1 collides with lower wall
        elif player_1_y >= 570:
            player_1_y = 570

        # Player 2 "Artificial Intelligence" (WITH JITTER CORRECTION)
        paddle_center = player_2_y + 75

        # Moves the paddle smoothly, but only if
        # the distance is greater than its speed
        # This creates a "dead zone" to prevent jitter.
        if paddle_center < ball_y - player_2_speed:
            player_2_y += player_2_speed
        elif paddle_center > ball_y + player_2_speed:
            player_2_y -= player_2_speed

        # Player 2 collides with upper wall
        if player_2_y <= 0:
            player_2_y = 0

        # Player 2 collides with lower wall
        elif player_2_y >= 570:
            player_2_y = 570

        # Update score HUD
        score_text = score_font.render(
            f"{score_1:02d} x {score_2:02d}", True, COLOR_WHITE, COLOR_BLACK
        )

        # Drawing objects
        screen.blit(ball, (ball_x, ball_y))
        screen.blit(player_1, (50, player_1_y))
        screen.blit(player_2, (1180, player_2_y))
        screen.blit(score_text, score_text_rect)
    else:
        # Drawing victory
        screen.fill(COLOR_BLACK)
        screen.blit(score_text, score_text_rect)
        screen.blit(victory_text, victory_text_rect)

    # Update screen
    pygame.display.flip()
    game_clock.tick(60)

pygame.quit()
