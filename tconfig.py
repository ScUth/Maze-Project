import pygame as pg
import datetime as dt
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
    MAZE_PROPERTY = {
        'STARTING_POINT' : (50, 50),
        'ENDING_POINT' : 0,
        'TOP_LEFT' : 0,
        'TOP_RIGHT' : 0,
        'BOTTOM_LEFT' : 0,
        'BOTTOM_RIGHT' : 0
    }
    
    @classmethod
    def get(cls, name, key):
        return getattr(cls, name)[key]
    
    @classmethod
    def set(cls, name, key, value):
        getattr(cls, name)[key] = value
        now = dt.datetime.now()
        print(f"[{now.strftime('%X')}] {key} is now set to : {getattr(cls, name)[key]}")