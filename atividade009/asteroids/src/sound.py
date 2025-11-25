import pygame as pg
import config as C


class SoundManager:
    def __init__(self):
        pg.mixer.init()
        self.load_sounds()

    def load_sounds(self):
        try:
            self.player_shoot = pg.mixer.Sound(C.SND_PLAYER_SHOOT)
        except:
            self.player_shoot = None

        try:
            self.ufo_shoot = pg.mixer.Sound(C.SND_UFO_SHOOT)
        except:
            self.ufo_shoot = None

        try:
            self.explosion = pg.mixer.Sound(C.SND_EXPLOSION)
        except:
            self.explosion = None

        # Ajusta volume global
        for snd in (self.player_shoot, self.ufo_shoot, self.explosion):
            if snd:
                snd.set_volume(C.MASTER_VOLUME)

    def play_player_shoot(self):
        if self.player_shoot:
            self.player_shoot.play()

    def play_ufo_shoot(self):
        if self.ufo_shoot:
            self.ufo_shoot.play()

    def play_explosion(self):
        if self.explosion:
            self.explosion.play()
