import random as rd
import pygame as pg
from data_json import Config_json
import math
import random as rd
from tconfig import Config

class Maze_Gen:
    __config = Config_json("config.json")
    
    def __init__(self):
        # entire windows
        self.__config._load_json()
        self.winheight = self.__config._get_data("WINDOWS", "height")
        self.winwidth = self.__config._get_data("WINDOWS", "width")
        self.mapwidth = self.__config._get_data("MAZE", 'width')
        self.mapheight = self.__config._get_data("MAZE", 'height')
        
        # maze config
        self.size = (10, 10)
        self.box_size = 30
        self.columns = self.mapwidth // self.box_size
        self.rows = math.ceil(self.mapheight /   self.box_size)
        self.origin_pos = self.drawGrid()[len(self.drawGrid()) - 1]
        self.origin_his = []
        self.origin_his_pos = []
        self.line = []
        self.corner = []
        
    def drawGrid(self):
        grid_rect = []
        
        offset_x = (self.winwidth - self.mapwidth) // 2
        offset_y = (self.winheight - self.mapheight) // 2
        for x in range(0, self.mapwidth, self.box_size):
            for y in range(0, self.mapheight, self.box_size):
                rect = pg.Rect(offset_x + x, offset_y + y , self.box_size, self.box_size)
                grid_rect.append(rect)
        return grid_rect
    
    def set_nearby_origin(self):
        max_orihis = 7
        recent = set(self.origin_his[-max_orihis:])
        rect_lis = self.drawGrid()
        a_ori = self.origin_pos.y + self.box_size
        b_ori = self.origin_pos.y - self.box_size
        l_ori = self.origin_pos.x - self.box_size
        r_ori = self.origin_pos.x + self.box_size
        
        new_coord = [
            (self.origin_pos.x, a_ori, self.box_size, self.box_size),
            (self.origin_pos.x, b_ori, self.box_size, self.box_size),
            (l_ori, self.origin_pos.y, self.box_size, self.box_size),
            (r_ori, self.origin_pos.y, self.box_size, self.box_size)
        ]
        
        # ok_coord = filter(lambda x: x in rect_lis and x not in recent, new_coord)
        ok_coord = [coord for coord in new_coord if coord in rect_lis and coord not in recent]
        
        if not ok_coord:
            return

        picked_coord = rd.choice(ok_coord)
        print(f"original origin was at {self.origin_pos}, origin now at {picked_coord}")
        self.origin_his_pos.append(self.origin_pos)
        # print(self.origin_his)
        for i in rect_lis:
            if i == picked_coord:
                self.origin_pos = i
                self.origin_his.append(picked_coord)
        # print(f"confirmed origin : {self.origin_pos}, set : {recent}")
    
    def get_Grid(self):
        # useless function
        return self.drawGrid()
    
    def update_maze(self, start_pos, new_end):
        for line in self.line:
            if line["start"] == start_pos:
                line["end"] = new_end
                break

    def gen_maze(self): # ori_ = origin
        rect_lis = self.drawGrid()
        self.line.clear()
        
        for rect in rect_lis:
            if rect.x < rect_lis[-1].x:
                start = (rect.x, rect.y)  # center of the dot
                end = (rect.x + self.box_size, rect.y)  # move right
            else:
                start = (rect.x, rect.y)  # center of the dot
                end = (rect.x, rect.y + self.box_size)  # move right
            self.line.append({"start": start, "end": end})

    def draw_maze(self, x, y, screen, status):
        # gen maze from default template
        rect_lis = self.drawGrid()
            # if status is False and x < rect_lis[-1].x:
            #     self.gen_maze(x, y, screen)
            # elif status is False and x == rect_lis[-1].x:
            #     status = True
        screen.fill(Config.get('COLOR_BLACK'))
        # self.gen_maze()
        for line in self.line:
            if line["start"] != (self.origin_pos.x, self.origin_pos.y):
                pg.draw.line(screen, (255, 255, 255), line["start"], line["end"])
        # rules
        if len(self.origin_his) >= 1:
            previous_origin = self.origin_his_pos[-1]
            pg.draw.circle(screen, (0, 255, 0), (previous_origin.x, previous_origin.y), 2)
            self.update_maze((previous_origin.x, previous_origin.y), (self.origin_pos.x, self.origin_pos.y))
            
# do next = figure it out how to avoid corner and make it playable