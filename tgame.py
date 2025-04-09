import json
import random as rd
import pygame as pg
from tconfig import Config
from data_json import Config_json
from tmaze import Maze_Gen

class Game:
    __config = Config_json("config.json")

    def __init__(self):
        pg.init()
        pg.display.set_caption("Maze Project")
        img = pg.image.load(r'C:\Users\scien\Documents\cmand\py\proj ref\maze_generator\icon1.png')
        pg.display.set_icon(img)
        self.__config._load_json()
        self.height = self.__config._get_data("WINDOWS", "height")
        self.width = self.__config._get_data("WINDOWS", "width")
        self.__screen = pg.display.set_mode((
            (self.width),
            (self.height)
        )
        )
        self.maze = Maze_Gen()
        self.maze.gen_maze()
        self.__screen.fill(Config.get('COLOR_BLACK'))
        self.running = True
        self.maze_status = False
        
    def __game_reset(self):
        pass
    
    def __event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.maze.set_nearby_origin()
                if event.key == pg.K_i:
                    self.get_data()
    
    def get_data(self):
        print('-'*20)
        print('windows width :', self.width)
        print('windows height :', self.height)
        print('grid width :', Maze_Gen().mapwidth)
        print('grid height :', Maze_Gen().mapheight)
        print('grid columns :', Maze_Gen().columns)
        print('grid rows :', Maze_Gen().rows)
        # print('origin history', Maze_Gen().origin_his)
        print('-'*20)
    
    def game_loop(self):
        while self.running:
            self.__event()
            rect_lis = self.maze.drawGrid()
            for rect in rect_lis:
                pg.draw.circle(self.__screen, Config.get('COLOR_WHITE'), (rect.x, rect.y), 2) # got point from maze -> connected with rect

                # create origin
                origin = self.maze.origin_pos # (x, y, box_size, box_size)

                # make line
                        # if self.maze_status is False and rect < rect_lis[-1]:
                        #     self.maze.gen_maze(rect.x, rect.y, self.__screen)
                        # elif self.maze_status is False and rect == rect_lis[-1]:
                        #     self.maze_status = True
                        # else:
                        #     pass
                        # print(self.maze_status)
                    
                self.maze.draw_maze(rect.x, rect.y, self.__screen, self.maze_status) # test gen maze
                
                # if rect != origin:
                #     pg.draw.line(self.__screen, Config.get('COLOR_WHITE'), (rect.x + 13.5, rect.y + 2), (end_pos_x + 13.5, end_pos_y + 2), 2)
                
                # mark origin
                pg.draw.circle(self.__screen, (255, 0, 0), (origin.x, origin.y), 2)
            pg.display.update()

if __name__ == '__main__':
    g1 = Game()
    g1.game_loop()