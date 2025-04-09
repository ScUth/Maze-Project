import pygame as pg
class Config:
    COLOR = {
        'COLOR_BLACK' : (0, 0, 0),
        'COLOR_WHITE' : (255, 255, 255)
    }
    KEY = {
        pg.K_r : "R"
    }
    
    @classmethod
    def get(cls, key):
        return cls.COLOR[key]