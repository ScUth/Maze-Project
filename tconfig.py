import pygame as pg
class Config:
    COLOR = {
        'COLOR_BLACK' : (0, 0, 0),
        'COLOR_WHITE' : (255, 255, 255)
    }
    KEY = {
        pg.K_UP: "UP",
        pg.K_DOWN: "DOWN",
        pg.K_LEFT: "LEFT",
        pg.K_RIGHT: "RIGHT"
    }
    
    @classmethod
    def get(cls, key):
        return cls.COLOR[key]