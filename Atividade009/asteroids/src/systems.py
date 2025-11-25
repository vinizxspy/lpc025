import math 
from random import uniform

import pygame as pg

import config as C
from sprites import Asteroid, Ship, UFO, Bullet  #
from utils import Vec, rand_edge_pos, rand_unit_vec
from sound import SoundManager  #


class World:

    def __init__(self):
        self.ship = Ship(Vec(C.WIDTH / 2, C.HEIGHT / 2))
        self.bullets = pg.sprite.Group()
        self.ufo_bullets = pg.sprite.Group()  # 
        self.asteroids = pg.sprite.Group()
        self.ufos = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group(self.ship)
        self.score = 0
        self.lives = C.START_LIVES
        self.wave = 0
        self.wave_cool = C.WAVE_DELAY
        self.safe = C.SAFE_SPAWN_TIME
        self.ufo_timer = C.UFO_SPAWN_EVERY
        self.sound = SoundManager()  # 

    def start_wave(self):
        self.wave += 1
        count = 3 + self.wave
        for _ in range(count):
            pos = rand_edge_pos()
            while (pos - self.ship.pos).length() < 150:
                pos = rand_edge_pos()
            ang = uniform(0, math.tau)
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX)
            vel = Vec(math.cos(ang), math.sin(ang)) * speed
            self.spawn_asteroid(pos, vel, "L")

    def spawn_asteroid(self, pos: Vec, vel: Vec, size: str):
        a = Asteroid(pos, vel, size)
        self.asteroids.add(a)
        self.all_sprites.add(a)

    def spawn_ufo(self):
        small = uniform(0, 1) < 0.5
        y = uniform(0, C.HEIGHT)
        x_left = uniform(0, 1) < 0.5
        x = 0 if x_left else C.WIDTH
        ufo = UFO(Vec(x, y), small)
        
        if small:
            pass   
        else: #  
            if x_left:  
                ufo.dir = Vec(1, 0)
            else: 
                ufo.dir = Vec(-1, 0) 
        ufo.shoot_cool = 0.0  
        self.ufos.add(ufo)
        self.all_sprites.add(ufo)

    def try_fire(self):
        if len(self.bullets) >= C.MAX_BULLETS:
            return
        b = self.ship.fire()
        if b:
            self.bullets.add(b)
            self.all_sprites.add(b)
            self.sound.play_player_shoot()  

    def hyperspace(self):
        self.ship.hyperspace()
        self.score = max(0, self.score - C.HYPERSPACE_COST)

    def update(self, dt: float, keys):
        #Atualização dos Inputs e Sprites
        self.all_sprites.update(dt)
        self.ship.control(keys, dt)

        #Perseguição dinâmica da nave pequena de recalculação
        for ufo in self.ufos:
            if ufo.small:
                #Vetor do ufo para o player
                to_ship = (self.ship.pos - ufo.pos)

                if to_ship.length() > 0:
                    target_dir = to_ship.normalize()
                    ufo.dir = ufo.dir.lerp(target_dir, 0.06)
                ufo.speed = 55


        # Timers
        if self.safe > 0:
            self.safe -= dt
            self.ship.invuln = 0.5
        self.ufo_timer -= dt
        if self.ufo_timer <= 0:
            self.spawn_ufo()
            self.ufo_timer = C.UFO_SPAWN_EVERY

        self.update_ufo_shots(dt)#
        self.handle_collisions()

        if not self.asteroids and self.wave_cool <= 0:
            self.start_wave()
            self.wave_cool = C.WAVE_DELAY
        elif not self.asteroids:
            self.wave_cool -= dt

    def update_ufo_shots(self, dt: float):  # 
        for ufo in self.ufos:  
            ufo.shoot_cool = getattr(ufo, "shoot_cool", 0.0) - dt
            if ufo.shoot_cool <= 0:
                if (self.ship.pos - ufo.pos).length() > 0:
                    dirv = (self.ship.pos - ufo.pos).normalize()
                else:  
                    dirv = Vec(0,-1) #Caso esteja exatamente na posição do UFO
                vel = dirv * C.SHIP_BULLET_SPEED
                b = Bullet(ufo.pos, vel) 
                self.ufo_bullets.add(b) 
                self.all_sprites.add(b)
                self.sound.play_ufo_shoot() 
                ufo.shoot_cool = 1.5 

    def handle_collisions(self):
        hits = pg.sprite.groupcollide(
            self.asteroids,
            self.bullets or self.ufo_bullets,
            False,
            True,
            collided=lambda a, b: (a.pos - b.pos).length() < a.r,
        )
        for ast, _ in hits.items():
            self.split_asteroid(ast)

        if self.ship.invuln <= 0 and self.safe <= 0:
            for ast in self.asteroids:
                if (ast.pos - self.ship.pos).length() < (ast.r + self.ship.r):
                    self.ship_die()
                    break
            for ufo in self.ufos:
                if (ufo.pos - self.ship.pos).length() < (ufo.r + self.ship.r):
                    self.ship_die()
                    break
            
            for b in list(self.ufo_bullets): 
                if (b.pos - self.ship.pos).length() < (b.r + self.ship.r):
                    b.kill()
                    self.ship_die()
                    break

        for ufo in list(self.ufos):
            for b in list(self.bullets):
                if (ufo.pos - b.pos).length() < (ufo.r + b.r):
                    score = (C.UFO_SMALL["score"] if ufo.small
                             else C.UFO_BIG["score"])
                    self.score += score
                    ufo.kill()
                    b.kill()
                    self.sound.play_explosion() 

        #break for asteroids
        for ufo in list(self.ufos): 
            for ast in list(self.asteroids):
                if (ufo.pos - ast.pos).length() < (ufo.r + ast.r): 
                    score = (C.UFO_SMALL["score"] if ufo.small else C.UFO_BIG["score"]) 
                    self.score += score
                    self.split_asteroid(ast) 
                    ufo.kill()  
                    break

    def split_asteroid(self, ast: Asteroid):
        self.score += C.AST_SIZES[ast.size]["score"]
        self.sound.play_explosion()  
        split = C.AST_SIZES[ast.size]["split"]
        pos = Vec(ast.pos)
        ast.kill()
        for s in split:
            dirv = rand_unit_vec()
            speed = uniform(C.AST_VEL_MIN, C.AST_VEL_MAX) * 1.2
            self.spawn_asteroid(pos, dirv * speed, s)

    def ship_die(self):
        self.sound.play_explosion() 
        self.lives -= 1
        self.ship.pos.xy = (C.WIDTH / 2, C.HEIGHT / 2)
        self.ship.vel.xy = (0, 0)
        self.ship.angle = -90
        self.ship.invuln = C.SAFE_SPAWN_TIME
        self.safe = C.SAFE_SPAWN_TIME
        if self.lives < 0:
            # Reset total
            self.__init__()

    def draw(self, surf: pg.Surface, font: pg.font.Font):
        for spr in self.all_sprites:
            spr.draw(surf)

        pg.draw.line(surf, (60, 60, 60), (0, 50), (C.WIDTH, 50), width=1)
        txt = f"SCORE {self.score:06d}   LIVES {self.lives}   WAVE {self.wave}"
        label = font.render(txt, True, C.WHITE)
        surf.blit(label, (10, 10))
