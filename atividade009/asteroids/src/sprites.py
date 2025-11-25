import math
from random import uniform

import pygame as pg

import config as C
from utils import Vec, angle_to_vec, draw_circle, draw_poly, wrap_pos


class Bullet(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.ttl = C.BULLET_TTL
        self.r = C.BULLET_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.ttl -= dt
        if self.ttl <= 0:
            self.kill()
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        draw_circle(surf, self.pos, self.r)


class Asteroid(pg.sprite.Sprite):
    def __init__(self, pos: Vec, vel: Vec, size: str):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(vel)
        self.size = size  # 'L' | 'M' | 'S'
        self.r = C.AST_SIZES[size]["r"]
        self.poly = self._make_poly()
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def _make_poly(self):
        steps = 12 if self.size == "L" else 10 if self.size == "M" else 8
        pts = []
        for i in range(steps):
            ang = i * (360 / steps)
            jitter = uniform(0.75, 1.2)
            r = self.r * jitter
            v = Vec(math.cos(math.radians(ang)),
                    math.sin(math.radians(ang)))
            pts.append(v * r)
        return pts

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        pts = [(self.pos + p) for p in self.poly]
        pg.draw.polygon(surf, C.WHITE, pts, width=1)


class Ship(pg.sprite.Sprite):
    def __init__(self, pos: Vec):
        super().__init__()
        self.pos = Vec(pos)
        self.vel = Vec(0, 0)
        self.angle = -90.0
        self.cool = 0.0
        self.invuln = 0.0
        self.alive = True
        self.r = C.SHIP_RADIUS
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)

    def control(self, keys: pg.key.ScancodeWrapper, dt: float):
        if keys[pg.K_LEFT]:
            self.angle -= C.SHIP_TURN_SPEED * dt
        if keys[pg.K_RIGHT]:
            self.angle += C.SHIP_TURN_SPEED * dt
        if keys[pg.K_UP]:
            self.vel += angle_to_vec(self.angle) * C.SHIP_THRUST * dt
        self.vel *= C.SHIP_FRICTION

    def fire(self) -> Bullet | None:
        if self.cool > 0:
            return None
        dirv = angle_to_vec(self.angle)
        pos = self.pos + dirv * (self.r + 6)
        vel = self.vel + dirv * C.SHIP_BULLET_SPEED
        self.cool = C.SHIP_FIRE_RATE
        return Bullet(pos, vel)

    def hyperspace(self):
        self.pos = Vec(uniform(0, C.WIDTH), uniform(0, C.HEIGHT))
        self.vel.xy = (0, 0)
        self.invuln = 1.0

    def update(self, dt: float):
        if self.cool > 0:
            self.cool -= dt
        if self.invuln > 0:
            self.invuln -= dt
        self.pos += self.vel * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        dirv = angle_to_vec(self.angle)
        left = angle_to_vec(self.angle + 140)
        right = angle_to_vec(self.angle - 140)
        p1 = self.pos + dirv * self.r
        p2 = self.pos + left * self.r * 0.9
        p3 = self.pos + right * self.r * 0.9
        draw_poly(surf, [p1, p2, p3])
        if self.invuln > 0 and int(self.invuln * 10) % 2 == 0:
            draw_circle(surf, self.pos, self.r + 6)


class UFO(pg.sprite.Sprite):
    def __init__(self, pos: Vec, small: bool):
        super().__init__()
        self.pos = Vec(pos)
        self.small = small
        self.r = C.UFO_SMALL["r"] if small else C.UFO_BIG["r"]
        self.speed = C.UFO_SPEED
        self.rect = pg.Rect(0, 0, self.r * 2, self.r * 2)
        self.dir = Vec(1, 0) if uniform(0, 1) < 0.5 else Vec(-1, 0)

    def update(self, dt: float):
        self.pos += self.dir * self.speed * dt
        self.pos = wrap_pos(self.pos)
        self.rect.center = self.pos

    def draw(self, surf: pg.Surface):
        w, h = self.r * 2, self.r
        rect = pg.Rect(0, 0, w, h)
        rect.center = self.pos
        pg.draw.ellipse(surf, C.WHITE, rect, width=1)
        cup = pg.Rect(0, 0, w * 0.5, h * 0.7)
        cup.center = (self.pos.x, self.pos.y - h * 0.3)
        pg.draw.ellipse(surf, C.WHITE, cup, width=1)
