import pygame as pg

class Score:
    def __init__(self):
        self.score = 0
        
    def get_score(self):
        return self.score
    
    def set_score(self, condition):
        if condition == "NLVL": # next level
            self.score += 100
        elif condition == "TEST":
            self.score = 100
        elif condition == "GIFT":
            self.score += 20
        elif condition == "EK":
            self.score += 50
    
    def display_score(self, x, y, screen):
        font = pg.font.SysFont(None, 60)
        tx = font.render(f"Score : {self.get_score()}", True, (255, 255, 255))
        # text_rect = tx.get_rect(center=(0, y))
        screen.blit(tx, (0, y*21/22))