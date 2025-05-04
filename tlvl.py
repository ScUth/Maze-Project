import pygame as pg
from tscore import Score

class Level:
    def __init__(self):
        self.lvl_num = 0
        self.enemy_speed_mul = 1
        self.maze_size_mul = 1
        self.score = Score()
    
    def increase_difficulty(self):
        pass # well, it's increase the enemy speed
    
    def get_lvl(self):
        return self.lvl_num
    
    def increase_lvl(self):
        self.lvl_num += 1
    
    def display_lvl(self, x, y, screen):
        font = pg.font.SysFont(None, 60)
        tx = font.render(f"Level : {self.lvl_num}", True, (255, 255, 255))
        text_rect = tx.get_rect(center=(x/2, y/12))
        screen.blit(tx, text_rect)