import turtle
import platform
import subprocess
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent

speed_multiplier = 1.0


def play_sound(filename: str):
    """Plays a .wav audio file asynchronously on Windows/macOS/Linux."""
    path = str((BASE / filename).resolve())
    system = platform.system()

    # Windows: winsound (native)
    if system == "Windows":
        try:
            import winsound
            winsound.PlaySound(
                path, winsound.SND_FILENAME | winsound.SND_ASYNC
            )
            return
        except Exception:
            pass  # try next methods

    # macOS: afplay (native)
    if system == "Darwin":
        afplay = shutil.which("afplay")
        if afplay:
            subprocess.Popen(
                [afplay, path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return


# Screen setup
screen = turtle.Screen()
screen.title("My Pong")
screen.bgcolor("blue")
screen.setup(width=800, height=600)
screen.tracer(0)

# Initial screen
title = turtle.Turtle()
title.hideturtle()
title.color("white")
title.penup()
title.goto(0, 100)
title.write(
    "My Pong", align="center", font=("Chailce-Noggin", 36, "bold")
)

# Start button
button = turtle.Turtle()
button.shape("square")
button.color("white")
button.shapesize(stretch_wid=2, stretch_len=6)
button.penup()
button.goto(0, -50)

button_text = turtle.Turtle()
button_text.color("white")
button_text.hideturtle()
button_text.penup()
button_text.goto(0, -60)
button_text.write(
    "START", align="center", font=("Chailce-Noggin", 20, "bold")
)


# Game functions
def start_game(x, y):
    if -60 < x < 60 and -70 < y < -30:  # Button area
        title.clear()
        button.hideturtle()
        button_text.clear()
        run_game()


def run_game():
    global score_1, score_2, speed_multiplier
    score_1 = 0
    score_2 = 0
    speed_multiplier = 1.0  # reset ball speed

    # Paddle 1
    paddle_1 = turtle.Turtle()
    paddle_1.speed(0)
    paddle_1.shape("square")
    paddle_1.color("white")
    paddle_1.shapesize(stretch_wid=5, stretch_len=1)
    paddle_1.penup()
    paddle_1.goto(-350, 0)

    # Paddle 2
    paddle_2 = turtle.Turtle()
    paddle_2.speed(0)
    paddle_2.shape("square")
    paddle_2.color("white")
    paddle_2.shapesize(stretch_wid=5, stretch_len=1)
    paddle_2.penup()
    paddle_2.goto(350, 0)

    # Ball
    ball = turtle.Turtle()
    ball.speed(0)
    ball.shape("square")
    ball.color("white")
    ball.penup()
    ball.goto(0, 0)
    ball.dx = 3  # ball speed
    ball.dy = 3  # ball speed

    # HUD
    hud = turtle.Turtle()
    hud.speed(0)
    hud.shape("square")
    hud.color("white")
    hud.penup()
    hud.hideturtle()
    hud.goto(0, 260)
    hud.write(
        f"{score_1} : {score_2}", align="center", font=("Arial", 24, "normal")
    )

    # Paddle movements
    def paddle_1_up():
        y = paddle_1.ycor()
        y = min(250, y + 30)
        paddle_1.sety(y)

    def paddle_1_down():
        y = paddle_1.ycor()
        y = max(-250, y - 30)
        paddle_1.sety(y)

    def paddle_2_up():
        y = paddle_2.ycor()
        y = min(250, y + 30)
        paddle_2.sety(y)

    def paddle_2_down():
        y = paddle_2.ycor()
        y = max(-250, y - 30)
        paddle_2.sety(y)

    # Simultaneous key system
    w_pressed = False
    s_pressed = False
    up_pressed = False
    down_pressed = False

    def update_paddles():
        if w_pressed:
            paddle_1_up()
        if s_pressed:
            paddle_1_down()
        if up_pressed:
            paddle_2_up()
        if down_pressed:
            paddle_2_down()
        screen.ontimer(update_paddles, 20)

    # Press functions
    def press_w():
        nonlocal w_pressed
        w_pressed = True

    def release_w():
        nonlocal w_pressed
        w_pressed = False

    def press_s():
        nonlocal s_pressed
        s_pressed = True

    def release_s():
        nonlocal s_pressed
        s_pressed = False

    def press_up():
        nonlocal up_pressed
        up_pressed = True

    def release_up():
        nonlocal up_pressed
        up_pressed = False

    def press_down():
        nonlocal down_pressed
        down_pressed = True

    def release_down():
        nonlocal down_pressed
        down_pressed = False

    screen.listen()
    screen.onkeypress(press_w, "w")
    screen.onkeyrelease(release_w, "w")
    screen.onkeypress(press_s, "s")
    screen.onkeyrelease(release_s, "s")
    screen.onkeypress(press_up, "Up")
    screen.onkeyrelease(release_up, "Up")
    screen.onkeypress(press_down, "Down")
    screen.onkeyrelease(release_down, "Down")

    update_paddles()

    # Ball movement
    def move_ball():
        global score_1, score_2, speed_multiplier

        # Update ball position multiplied by speed
        ball.setx(ball.xcor() + ball.dx * speed_multiplier)
        ball.sety(ball.ycor() + ball.dy * speed_multiplier)

        # Gradually increase speed
        speed_multiplier += 0.001  # increase 0.1% each update

        # Collision with walls
        if ball.ycor() > 290:
            play_sound("bounce.wav")
            ball.sety(290)
            ball.dy *= -1

        if ball.ycor() < -290:
            play_sound("bounce.wav")
            ball.sety(-290)
            ball.dy *= -1

        max_score = 5

        # Add score for left side
        if ball.xcor() < -390:
            score_2 += 1
            hud.clear()
            hud.write(
                f"{score_1} : {score_2}", align="center",
                font=("Press Start 2P", 24, "normal")
            )
            play_sound("258020__kodack__arcade-bleep-sound.wav")
            ball.goto(0, 0)
            ball.dx *= -1

        if score_2 >= max_score:
            hud.goto(0, 0)
            hud.write(
                'Player 2 wins', align='center',
                font=("Chailce-Noggin", 20, "bold")
            )
            return

        # Add score for right side
        if ball.xcor() > 390:
            score_1 += 1
            hud.clear()
            hud.write(
                f"{score_1} : {score_2}", align="center",
                font=("Press Start 2P", 24, "normal")
            )
            play_sound("258020__kodack__arcade-bleep-sound.wav")
            ball.goto(0, 0)
            ball.dx *= -1

        if score_1 >= max_score:
            hud.goto(0, 0)
            hud.write(
                'Player 1 wins', align='center',
                font=("Chailce-Noggin", 20, "bold")
            )
            return

        # Collision with left paddle
        if ball.distance(paddle_1) < 50 and ball.dx < 0:
            ball.setx(paddle_1.xcor() + 30)
            offset = ball.ycor() - paddle_1.ycor()
            ball.dy = offset / 10  # angular bounce
            ball.dx *= -1
            play_sound("bounce.wav")

        # Collision with right paddle
        if ball.distance(paddle_2) < 50 and ball.dx > 0:
            ball.setx(paddle_2.xcor() - 30)
            offset = ball.ycor() - paddle_2.ycor()
            ball.dy = offset / 10  # angular bounce
            ball.dx *= -1
            play_sound("bounce.wav")

        screen.update()
        screen.ontimer(move_ball, 20)

    # Start ball movement
    move_ball()


# Events
screen.onclick(start_game)
screen.mainloop()
