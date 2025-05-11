import csv
import random as rd
import pygame as pg
import time
from tconfig import Config
from data_json import Config_json
from tmaze import Maze_Gen
from tplayer import Player, Bullet
from tlvl import Level
from tscore import Score
from tgift import Gift
from tenemy import Enemy
import tkinter as tk
from tdata import Data

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
        self.num_gift = 0
        self.num_bullets = 0
        self.num_enemies_killed = 0
        self.previous_play = time.time()
        
        # other classes
        self.maze = Maze_Gen()
        self.lvl = Level()
        self.player = Player(self.lvl.get_lvl())
        self.score = Score()
        self.gift = Gift(self.maze.drawGrid())

        # get        
        self.enemies = [Enemy(i, self.maze.get_main_line(), self.lvl.get_lvl()) for i in range(4)]
        
        self.maze.gen_maze()
        self.__screen.fill(Config.get('COLOR', 'COLOR_BLACK'))
        self.running = True
        self.clock = pg.time.Clock()
        self.img = None
        self.player_started = False
        self.font = pg.font.SysFont(None, 36)
        self.small_font = pg.font.SysFont(None, 24)
        self.start_time = time.time()
        self.r_start_time = time.time()
        self.game_over = False
        
        # collect data
        self.movement_csv = r"data_csv\Movement.csv"
        self.level_csv = r"data_csv\Level.csv"
        self.gift_csv = r"data_csv\Gift.csv"
        self.enemies_csv = r"data_csv\Enemy.csv"
        self.bullet_csv = r"data_csv\Bullet fired.csv"
        self.time_csv = r"data_csv\Time.csv"
        self.score_csv = r"data_csv\Score.csv"
        self.whole_time_csv = r"data_csv\Time_End.csv"
        
    def __game_reset(self):
        self.maze.clear_maze()
        self.maze.gen_maze()
        self.player = Player(Level().get_lvl())
        self.lvl = Level()
        self.score = Score()
        self.gift = Gift(self.maze.drawGrid())
        self.enemies = [Enemy(i, self.maze.get_main_line(), self.lvl.get_lvl()) for i in range(4)]
        self.player_started = False
    
    def __event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.write_csv([[self.lvl.get_lvl()]], self.level_csv)
                self.write_csv([[self.num_gift]], self.gift_csv)
                self.write_csv([[self.score.get_score()]], self.score_csv)
                self.write_csv([[self.num_bullets]], self.bullet_csv)
                self.write_csv([[self.num_enemies_killed]], self.enemies_csv)
                self.write_csv([[time.time() - self.previous_play]], self.time_csv)
                self.write_csv([[time.time() - self.r_start_time]], self.whole_time_csv)
                self.running = False
            elif event.type == pg.KEYDOWN:
                # if event.key == pg.K_r:
                #     self.maze.set_nearby_origin()
                if event.key == pg.K_i:
                    self.get_data()
                if event.key == pg.K_l:
                    self.lvl.increase_lvl()
                if event.key == pg.K_p:
                    self.maze.drawGrid_2(self.__screen)
                if event.key == pg.K_SPACE:
                    self.player.shoot()
                    self.num_bullets += 1
                if event.key in Config.KEY:
                    self.write_csv([[Config.KEY[event.key]]], self.movement_csv)
                if event.key == pg.K_u:
                    root = tk.Tk()
                    root.title("Data Analysis")
                    root.geometry("900x600")
                    data = Data(root)
                    root.mainloop()
    
    def get_data(self):
        print('-'*20)
        print('windows width :', self.width)
        print('windows height :', self.height)
        print('grid width :', Maze_Gen().mapwidth)
        print('grid height :', Maze_Gen().mapheight)
        print('grid columns :', Maze_Gen().columns)
        print('grid rows :', Maze_Gen().rows)
        # print('origin history', Maze_Gen().visited)
        print('mazeGrid : ', self.maze.maze_grid)
        # print('original origin position', self.maze.origin_pos)
        print("Line", self.maze.line)
        # print("drawable line : ", len(self.maze.get_main_line()))
        print("drawable line : ", self.maze.get_main_line())
        print('-'*20)
        
    def write_csv(self, data, file):
        with open(file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    
    def show_game_over(self):
        # Calculate play time
        play_time = time.time() - self.r_start_time
        minutes = int(play_time // 60)
        seconds = int(play_time % 60)
        
        # Create a semi-transparent overlay
        overlay = pg.Surface((self.width, self.height), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Black with 200/255 opacity
        self.__screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(center=(self.width//2, self.height//2 - 50))
        self.__screen.blit(game_over_text, text_rect)
        
        # Level reached
        level_text = self.small_font.render(f"Level Reached: {self.lvl.get_lvl()}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(self.width//2, self.height//2))
        self.__screen.blit(level_text, level_rect)
        
        # Time played
        time_text = self.small_font.render(f"Time Played: {minutes}m {seconds}s", True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(self.width//2, self.height//2 + 40))
        self.__screen.blit(time_text, time_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to restart or Q to quit", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.width//2, self.height//2 + 100))
        self.__screen.blit(restart_text, restart_rect)
        
        #show stat
        
        pg.display.update()
    
    def game_loop(self):
        while self.running:
            self.__event()
            rect_lis = self.maze.drawGrid()
            self.__screen.fill(Config.get('COLOR', 'COLOR_BLACK'))
            if self.maze.get_status() is True:
                self.img = pg.image.load(r"maze.png")
                self.__screen.blit(self.img, (min(self.maze.maze_grid)[0],min(self.maze.maze_grid)[1]))

            transparent_surface = pg.Surface(
                (self.__config._get_data("MAZE", "box_size"), 
                self.__config._get_data("MAZE", "box_size")), 
                pg.SRCALPHA  # Enable per-pixel alpha
            )
            transparent_surface.fill((150, 0, 150, 128))  # RGBA (128 = 50% opacity)
            # Blit the transparent surface at the ending position
            ending_pos_x = Config.get("MAZE_PROPERTY", "ENDING_POINT")[0] - (self.__config._get_data("MAZE", "box_size") // 2)
            ending_pos_y = Config.get("MAZE_PROPERTY", "ENDING_POINT")[1] - (self.__config._get_data("MAZE", "box_size") // 2)
            starting_pos_x = Config.get("MAZE_PROPERTY", "STARTING_POINT")[0] - (self.__config._get_data("MAZE", "box_size") // 2)
            starting_pos_y = Config.get("MAZE_PROPERTY", "STARTING_POINT")[1] - (self.__config._get_data("MAZE", "box_size") // 2)
            self.__screen.blit(transparent_surface, (ending_pos_x, ending_pos_y))
            
            ending_rect = pg.Rect(ending_pos_x, ending_pos_y, self.__config._get_data("MAZE", "box_size"), self.__config._get_data("MAZE", "box_size"))
            starting_rect = pg.Rect(starting_pos_x, starting_pos_y, self.__config._get_data("MAZE", "box_size"), self.__config._get_data("MAZE", "box_size"))
            # pg.draw.rect(self.__screen, (150, 0, 150), ending_rect)
            # print([i.speed for i in self.enemies])
            for rect in rect_lis:
                # pg.draw.circle(self.__screen, Config.get('COLOR', 'COLOR_WHITE'), (rect.x, rect.y), 2) # got point from maze -> connected with rect
                # create origin
                # origin = self.maze.origin_pos # (x, y, box_size, box_size)
                    
                self.maze.draw_maze(self.__screen) # test gen maze
                self.maze.update_maze()
                
                # mark origin
                # pg.draw.circle(self.__screen, (255, 0, 0), (origin.x, origin.y), 2)
                
                # check if maze is solvable then stop generating.
            self.player.move(self.maze.get_main_line())
            self.player.update_bullets(self.maze.get_main_line())
            self.player.draw(self.__screen)
            self.player.draw_bullets(self.__screen)
            # Check gift collection
            
            if self.gift.check_collision(self.player.get_position(), self.player.bullets):
                self.score.set_score("GIFT")  # Assuming you have a score increment for gifts
                self.num_gift += 1
                print(self.num_gift)
            if self.maze.maze_status:
                self.gift.draw(self.__screen)
            # print(len(self.maze.main_line))
            # self.player.keep_on_screen(self.width, self.height)
            # check if player reaching the ending point
            player_position = self.player.get_position()
            if not starting_rect.collidepoint(player_position):
                self.player_started = True
            if ending_rect.collidepoint(player_position):
                self.lvl.increase_lvl()
                self.score.set_score("NLVL")
                self.maze.clear_maze()
                self.maze.gen_maze()
                self.player.x, self.player.y = Config.get('MAZE_PROPERTY', 'STARTING_POINT')
                self.player.bullets = []
                self.gift = Gift(self.maze.drawGrid())
                self.enemies = [Enemy(i, self.maze.get_main_line(), self.lvl.get_lvl()) for i in range(4)]
                self.write_csv([[self.num_gift]], self.gift_csv)
                self.write_csv([[self.num_bullets]], self.bullet_csv)
                self.num_bullets = 0
                self.write_csv([[self.num_enemies_killed]], self.enemies_csv)
                self.num_enemies_killed = 0
                self.write_csv([[time.time() - self.previous_play]], self.time_csv)
                print(time.time() - self.previous_play)
                self.previous_play = time.time()

            self.lvl.display_lvl(self.width, self.height, self.__screen)
            self.score.display_score(self.width, self.height, self.__screen)
            self.maze.drawGrid_2(self.__screen)

            # Update enemies
            player_size = self.player.p_size
            for enemy in self.enemies:
                if self.player_started:
                    enemy.update(player_position, self.player.bullets)
                enemy.draw(self.__screen)
                
                if enemy.shot:
                    self.score.set_score('EK')
                    self.num_enemies_killed += 1
                    enemy.shot = False
                    
                # Check if enemy collides with player
                if enemy.check_player_collision(player_position, player_size):
                    print("Game Over! You were caught by an enemy!")
                    self.game_over = True
                    self.show_game_over()
                    waiting = True
                    while waiting:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                waiting = False
                                self.write_csv([[self.lvl.get_lvl()]], self.level_csv)
                                self.write_csv([[self.num_gift]], self.gift_csv)
                                self.write_csv([[self.score.get_score()]], self.score_csv)
                                self.write_csv([[self.num_bullets]], self.bullet_csv)
                                self.write_csv([[self.num_enemies_killed]], self.enemies_csv)
                                self.write_csv([[time.time() - self.previous_play]], self.time_csv)
                                self.write_csv([[time.time() - self.r_start_time]], self.whole_time_csv)
                                self.running = False
                            elif event.type == pg.KEYDOWN:
                                if event.key == pg.K_r:
                                    self.__game_reset()
                                    waiting = False
                                    self.game_over = False
                                    self.write_csv([[self.lvl.get_lvl()]], self.level_csv)
                                    self.write_csv([[self.num_gift]], self.gift_csv)
                                    self.num_gift = 0
                                    self.write_csv([[self.score.get_score()]], self.score_csv)
                                    self.write_csv([[self.num_bullets]], self.bullet_csv)
                                    self.num_bullets = 0
                                    self.write_csv([[self.num_enemies_killed]], self.enemies_csv)
                                    self.num_enemies_killed = 0
                                    self.write_csv([[time.time() - self.previous_play]], self.time_csv)
                                    self.write_csv([[time.time() - self.r_start_time]], self.whole_time_csv)
                                    self.r_start_time = time.time()
                                    self.previous_play = time.time()
                                    self.start_time = time.time()
                                elif event.key == pg.K_q:
                                    waiting = False
                                    self.write_csv([[self.lvl.get_lvl()]], self.level_csv)
                                    self.write_csv([[self.num_gift]], self.gift_csv)
                                    self.write_csv([[self.score.get_score()]], self.score_csv)
                                    self.write_csv([[self.num_bullets]], self.bullet_csv)
                                    self.write_csv([[self.num_enemies_killed]], self.enemies_csv)
                                    self.write_csv([[time.time() - self.previous_play]], self.time_csv)
                                    self.write_csv([[time.time() - self.r_start_time]], self.whole_time_csv)
                                    self.running = False
                                elif event.key == pg.K_u:
                                    root = tk.Tk()
                                    root.title("Data Analysis (pause)")
                                    root.geometry("900x600")
                                    data = Data(root)
                                    root.mainloop()
            
            pg.display.update()
            self.clock.tick(60)
            

if __name__ == '__main__':
    g1 = Game()
    g1.game_loop()