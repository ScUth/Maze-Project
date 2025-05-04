import json
import random as rd
import pygame as pg
from tconfig import Config
from data_json import Config_json
from tmaze import Maze_Gen
from tplayer import Player
from tlvl import Level
from tscore import Score

class Game:
    __config = Config_json("config.json")

    def __init__(self):
        pg.init()
        pg.display.set_caption("Maze Project")
        img = pg.image.load(r'icon1.png')
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
        self.player = Player()
        self.lvl = Level()
        self.score = Score()
        self.maze.gen_maze()
        self.__screen.fill(Config.get('COLOR', 'COLOR_BLACK'))
        self.running = True
        self.clock = pg.time.Clock()
        
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
                if event.key == pg.K_q:
                    self.lvl.increase_lvl()
                if event.key == pg.K_p:
                    self.maze.drawGrid_2(self.__screen)
                # if event.key == pg.K_y:
                #     self.score.set_score("NLVL")
    
    def get_data(self):
        print('-'*20)
        print('windows width :', self.width)
        print('windows height :', self.height)
        print('grid width :', Maze_Gen().mapwidth)
        print('grid height :', Maze_Gen().mapheight)
        print('grid columns :', Maze_Gen().columns)
        print('grid rows :', Maze_Gen().rows)
        # print('origin history', Maze_Gen().visited)
        # print('mazeGrid : ', self.maze.maze_grid)
        # print('original origin position', self.maze.origin_pos)
        print("Line", self.maze.line)
        # print("drawable line : ", len(self.maze.get_main_line()))
        print("drawable line : ", self.maze.get_main_line())
        print('-'*20)
    
    def game_loop(self):
        while self.running:
            self.__event()
            rect_lis = self.maze.drawGrid()
            self.__screen.fill(Config.get('COLOR', 'COLOR_BLACK'))
            
            ending_rect = pg.Rect(Config.get("MAZE_PROPERTY", "ENDING_POINT")[0]-(self.__config._get_data("MAZE", "box_size")//2), Config.get("MAZE_PROPERTY", "ENDING_POINT")[1], self.__config._get_data("MAZE", "box_size"), self.__config._get_data("MAZE", "box_size"))
            pg.draw.rect(self.__screen, (150, 0, 150), ending_rect)
            
            for rect in rect_lis:
                # pg.draw.circle(self.__screen, Config.get('COLOR_WHITE'), (rect.x, rect.y), 2) # got point from maze -> connected with rect
                # create origin
                # origin = self.maze.origin_pos # (x, y, box_size, box_size)
                    
                self.maze.draw_maze(rect.x, rect.y, self.__screen) # test gen maze
                self.maze.update_maze()
                
                # mark origin
                # pg.draw.circle(self.__screen, (255, 0, 0), (origin.x, origin.y), 2)
                
                # check if maze is solvable then stop generating.

            self.player.move(self.maze.get_main_line())
            self.player.draw(self.__screen)
            # print(len(self.maze.main_line))
            # self.player.keep_on_screen(self.width, self.height)
            
            # check if player reaching the ending point
            player_position = self.player.get_position()
            if ending_rect.collidepoint(player_position):
                self.lvl.increase_lvl()
                self.score.set_score("NLVL")
                self.maze.clear_maze()
                self.maze.gen_maze()
                self.player.x, self.player.y = Config.get('MAZE_PROPERTY', 'STARTING_POINT')

            self.lvl.display_lvl(self.width, self.height, self.__screen)
            self.score.display_score(self.width, self.height, self.__screen)
            self.maze.drawGrid_2(self.__screen)
            pg.display.update()
            self.clock.tick(60)
            

if __name__ == '__main__':
    g1 = Game()
    g1.game_loop()