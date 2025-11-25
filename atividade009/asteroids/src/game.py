import random
import sys
from dataclasses import dataclass

import pygame as pg

import config as C
from systems import World
from utils import text


@dataclass
class Scene:
    name: str


class Game:
    def __init__(self):
        pg.init()
        if C.RANDOM_SEED is not None:
            random.seed(C.RANDOM_SEED)
        self.screen = pg.display.set_mode((C.WIDTH, C.HEIGHT))
        pg.display.set_caption("Asteroides")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 20)
        self.big = pg.font.SysFont("consolas", 48)
        self.scene = Scene("menu")
        self.world = World()

    def run(self):
        while True:
            dt = self.clock.tick(C.FPS) / 1000.0
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    sys.exit(0)
                if e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit(0)
                if self.scene.name == "play":
                    if e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                        self.world.try_fire()
                    if e.type == pg.KEYDOWN and e.key == pg.K_LSHIFT:
                        self.world.hyperspace()
                elif self.scene.name == "menu":
                    if e.type == pg.KEYDOWN:
                        self.scene = Scene("play")

            keys = pg.key.get_pressed()
            self.screen.fill(C.BLACK)

            if self.scene.name == "menu":
                self.draw_menu()
            elif self.scene.name == "play":
                self.world.update(dt, keys)
                self.world.draw(self.screen, self.font)

            pg.display.flip()

    def draw_menu(self):
        text(self.screen, self.big, "ASTEROIDS",
             C.WIDTH // 2 - 150, 180)
        text(self.screen, self.font,
             "Setas: virar/acelerar  Espaço: tiro  Shift: hiper",
             160, 300)
        text(self.screen, self.font,
             "Pressione qualquer tecla...", 260, 360)
