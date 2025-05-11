import pygame as pg
import random as rd
from tconfig import Config
from data_json import Config_json

class Gift:
    __config = Config_json("config.json")
    
    def __init__(self, rectlis):
        self.__config._load_json()
        self.box_size = self.__config._get_data("MAZE", "box_size")
        self.rectlis = rectlis
        self.collected = False
        self.x, self.y = 0, 0
        self.spawn()
        self.radius = self.box_size // 3
        # For image loading (you'll need to replace 'gift.png' with your actual image)
        try:
            self.image = pg.image.load('clipart763940.png')
            self.image = pg.transform.scale(self.image, (self.radius*2, self.radius*2))
            self.use_image = True
        except:
            self.use_image = False
    
    def spawn(self):
        """Spawn the gift at a random position in the maze grid"""
        if self.rectlis:
            self.x, self.y = rd.choice(self.rectlis).x, rd.choice(self.rectlis).y
            self.collected = False
    
    def draw(self, screen):
        """Draw the gift on the screen"""
        if not self.collected:
            if self.use_image:
                screen.blit(self.image, (self.x - self.radius, self.y - self.radius))
            else:
                # Fallback drawing if image fails to load
                pg.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), self.radius)
    
    def check_collision(self, player_pos, bullets):
        """Check if player or bullets collide with the gift"""
        if self.collected:
            return False
            
        px, py = player_pos
        # Check player collision (distance-based)
        if ((px - self.x)**2 + (py - self.y)**2) <= (self.radius * 2)**2:
            self.collected = True
            return True
        
        # Check bullet collisions
        for bullet in bullets:
            if ((bullet.x - self.x)**2 + (bullet.y - self.y)**2) <= (self.radius + bullet.radius)**2:
                bullet.active = False  # Bullet disappears
                self.collected = True
                return True
                
        return False