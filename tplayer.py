import pygame as pg
from data_json import Config_json
import math
from tconfig import Config

class Player:
    __config = Config_json("config.json")
    
    def __init__(self):
        self.__config._load_json()
        self.x, self.y = 50, 50
        self.speed = 2
        self.score = 0
        self.Player_position = None
        self.shoots_num = 0
        self.p_size = 8
        self.direction = 0 # radian
    
    def get_vertices(self):
        """Calculate the three vertices of the triangle"""
        point1 = (
            self.x + self.p_size * math.cos(self.direction),
            self.y + self.p_size * math.sin(self.direction)
        )
        point2 = (
            self.x + self.p_size * math.cos(self.direction + 2 * math.pi / 3),
            self.y + self.p_size * math.sin(self.direction + 2 * math.pi / 3)
        )
        point3 = (
            self.x + self.p_size * math.cos(self.direction + 4 * math.pi / 3),
            self.y + self.p_size * math.sin(self.direction + 4 * math.pi / 3)
        )
        return [point1, point2, point3]
    
    def draw(self, screen):
        vertices = self.get_vertices()
        pg.draw.polygon(screen, (255 ,0 ,0), vertices)
    
    def move(self):
        # print(Config.KEY[key])
        keys = pg.key.get_pressed()
        move_x, move_y = 0, 0
        
        if keys[pg.K_LEFT]:
            move_x = -1
            self.direction = math.pi
        if keys[pg.K_RIGHT]:
            move_x = 1
            self.direction = 0
        if keys[pg.K_UP]:
            move_y = -1
            self.direction = -math.pi / 2
        if keys[pg.K_DOWN]:
            move_y = 1
            self.direction = math.pi / 2
            
        if move_x != 0 and move_y != 0:
            move_x *= 0.7071  # 1/sqrt(2)
            move_y *= 0.7071
            if move_x > 0 and move_y < 0:  # Right-up
                self.direction = -math.pi / 4
            elif move_x > 0 and move_y > 0:  # Right-down
                self.direction = math.pi / 4
            elif move_x < 0 and move_y < 0:  # Left-up
                self.direction = -3 * math.pi / 4
            elif move_x < 0 and move_y > 0:  # Left-down
                self.direction = 3 * math.pi / 4
            
        self.x += move_x * self.speed
        self.y += move_y * self.speed
    
    def keep_on_screen(self, screen_width, screen_height):
        """Ensure the triangle stays within screen bounds"""
        self.x = max(self.p_size, min(screen_width - self.p_size, self.x))
        self.y = max(self.p_size, min(screen_height - self.p_size, self.y))
    
    def shoot(self):
        pass
    
    def take_damage(self):
        pass
    
    def collect_gift(self):
        pass
    
    def get_position(self):
        pass