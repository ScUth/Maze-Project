import pygame as pg

class Player:
    def __init__(self):
        self.x, self.y = 0, 0
        self.speed = 0
        self.score = 0
        self.Player_position = None
        self.shoots_num = 0
    
    def draw(self, screen):
        pg.draw.polygon(screen, (255 ,0 ,0), [[50, 50], [50, 55], [53, 53]])
    
    def move(self):
        pass
    
    def shoot(self):
        pass
    
    def take_damage(self):
        pass
    
    def collect_gift(self):
        pass
    
    def get_position(self):
        pass