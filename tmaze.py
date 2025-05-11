import random as rd
import pygame as pg
from data_json import Config_json
import math
import random as rd
from tconfig import Config
from collections import defaultdict
import datetime as dt

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
        self.box_size = self.__config._get_data("MAZE", "box_size")
        self.columns = self.mapwidth // self.box_size
        self.rows = math.ceil(self.mapheight/self.box_size)
        self.origin_pos = self.drawGrid()[len(self.drawGrid()) - 1]
        self.origin_his = []
        self.origin_his_pos = []
        self.line = []
        self.main_line = []
        self.corner = []
        self.visited = set() # New: Track visited cells
        self.maze_grid = set()
        # self.shift_time = 600
        self.current_shifts = 0
        self.total = math.ceil(self.mapheight/self.box_size) * math.ceil(self.mapwidth/self.box_size)
        
        # setting
        self.maze_status = False
        self.combine_status = False
        self.image_status = False
        
        # set config
        Config.set('MAZE_PROPERTY', 'BOTTOM_RIGHT', (self.drawGrid()[-1].x, self.drawGrid()[-1].y))
        Config.set('MAZE_PROPERTY', 'TOP_LEFT', (self.drawGrid()[0].x, self.drawGrid()[0].y))
        Config.set('MAZE_PROPERTY', 'TOP_RIGHT', (self.drawGrid()[0].x, self.drawGrid()[-1].y))
        Config.set('MAZE_PROPERTY', 'BOTTOM_LEFT', (self.drawGrid()[-1].x, self.drawGrid()[0].y))
        Config.set('MAZE_PROPERTY', 'STARTING_POINT', (self.drawGrid()[0].x, self.drawGrid()[(self.mapheight // self.box_size)//2].y))
        Config.set('MAZE_PROPERTY', 'ENDING_POINT', (self.drawGrid()[-1].x, self.drawGrid()[(self.mapheight // self.box_size)//2].y))
        
    def drawGrid(self):
        grid_rect = []
        
        offset_x = (self.winwidth - self.mapwidth) // 2
        offset_y = (self.winheight - self.mapheight) // 2
        for x in range(0, self.mapwidth, self.box_size):
            for y in range(0, self.mapheight, self.box_size):
                rect = pg.Rect(offset_x + x, offset_y + y , self.box_size, self.box_size)
                grid_rect.append(rect)
        return grid_rect
    
    def drawGrid_2(self, screen):
        rect_lis = self.drawGrid()
        
        boxd2 = self.box_size // 2
        for rect in rect_lis:
            self.maze_grid.add((rect.x + boxd2, rect.y + boxd2))
            self.maze_grid.add((rect.x + boxd2, rect.y - boxd2))
            self.maze_grid.add((rect.x - boxd2, rect.y - boxd2))
            self.maze_grid.add((rect.x - boxd2, rect.y + boxd2))
        
        # for pgrid in self.maze_grid:
        #     pg.draw.circle(screen, (255, 0, 255), (pgrid[0], pgrid[1]), 2)
            
    def orientation(self, a, b, c):
        # Cross-product to determine orientation
        val = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if val == 0:
            return 0  # Collinear
        return 1 if val > 0 else 2  # Counter-clockwise or clockwise

    def segments_intersect(self, A, B, C, D):
        # Check if segments AB and CD intersect
        o1 = self.orientation(A, B, C)
        o2 = self.orientation(A, B, D)
        o3 = self.orientation(C, D, A)
        o4 = self.orientation(C, D, B)

        # General case: straddling
        if o1 != o2 and o3 != o4:
            return True

        # Special cases (collinear and overlapping)
        if o1 == 0 and self.on_segment(A, C, B):
            return True
        if o2 == 0 and self.on_segment(A, D, B):
            return True
        if o3 == 0 and self.on_segment(C, A, D):
            return True
        if o4 == 0 and self.on_segment(C, B, D):
            return True

        return False

    def on_segment(self, p, q, r):
        # Check if point q lies on segment pr
        if (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and (min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))):
            return True
        return False

    def can_draw_line(self, new_line, existing_lines):
        # Check if new_line intersects with any existing line
        A, B = new_line['start'], new_line['end']
        for line in existing_lines:
            C, D = line['start'], line['end']
            if self.segments_intersect(A, B, C, D):
                return False
        return True
            
    def check_line(self):
        # self.main_line is equal to {'start': (325, 345), 'end': (355, 345)}
        
        for dot in self.maze_grid:
            right_line = {'start': (dot[0], dot[1]), 'end': (dot[0] + self.box_size, dot[1])}
            if self.can_draw_line(right_line, self.line):
                if right_line not in self.main_line and (dot[0] + self.box_size, dot[1]) in self.maze_grid:
                    self.main_line.append(right_line)
            down_line = {'start': (dot[0], dot[1]), 'end': (dot[0], dot[1] + self.box_size)}
            if self.can_draw_line(down_line, self.line):
                if down_line not in self.main_line and (dot[0], dot[1] + self.box_size) in self.maze_grid:
                    self.main_line.append(down_line)
        print(f"[{dt.datetime.now().strftime('%X')}] Line is now computed.")
        
    def get_main_line(self):
        return self.main_line
    
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
            picked_coord = rd.choice(new_coord)
        else:
            picked_coord = rd.choice(ok_coord)

        # print(ok_coord)
        # print(f"original origin was at {self.origin_pos}, origin now at {picked_coord}")
        self.origin_his_pos.append(self.origin_pos)
        self.visited.add((self.origin_pos.x, self.origin_pos.y))
        for rect in rect_lis:
            if rect == picked_coord:
                self.origin_pos = rect
                self.origin_his.append(picked_coord)
    
    def get_Grid(self):
        # useless function
        return self.drawGrid()
    
    def get_status(self):
        return self.image_status
    
    def update_maze(self):
        if len(self.origin_his) >= 1:
            previous_origin = self.origin_his_pos[-1]
            for line in self.line:
                if line["start"] == (previous_origin.x, previous_origin.y):
                    line["end"] = (self.origin_pos.x, self.origin_pos.y)
                    break
            

    def gen_maze(self):
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
    
    def merge_segments(self, segments):

        vertical_lines = defaultdict(list)
        horizontal_lines = defaultdict(list)

        # Classify segments into vertical and horizontal
        for seg in segments:
            x1, y1 = seg['start']
            x2, y2 = seg['end']
            if x1 == x2:
                # Vertical line
                vertical_lines[x1].append(sorted([y1, y2]))
            elif y1 == y2:
                # Horizontal line
                horizontal_lines[y1].append(sorted([x1, x2]))
            else:
                raise ValueError(f"Segment {seg} is not axis-aligned (not purely vertical or horizontal)")

        def merge_intervals(intervals):
            intervals.sort()
            merged = []
            for start, end in intervals:
                if not merged or merged[-1][1] < start:
                    merged.append([start, end])
                else:
                    merged[-1][1] = max(merged[-1][1], end)
            return merged

        merged_segments = []

        # Process vertical lines
        for x, y_intervals in vertical_lines.items():
            merged_y = merge_intervals(y_intervals)
            for y1, y2 in merged_y:
                merged_segments.append({'start': (x, y1), 'end': (x, y2)})

        # Process horizontal lines
        for y, x_intervals in horizontal_lines.items():
            merged_x = merge_intervals(x_intervals)
            for x1, x2 in merged_x:
                merged_segments.append({'start': (x1, y), 'end': (x2, y)})

        self.combine_status = True
        print(f"[{dt.datetime.now().strftime('%X')}] Merging line. Ready for drawing.")
        return merged_segments


    def draw_maze(self, screen):
        # if self.maze_status:
        #     for line in self.main_line:
        #         pg.draw.line(screen, (255, 255, 0), line["start"], line["end"], 1)

        if len(self.visited) < self.total: # +1 until got the self.shift_time then stop shifting
            for _ in range(10):
                self.set_nearby_origin()
                self.current_shifts += 1
                for line in self.line:
                    if line["start"] != (self.origin_pos.x, self.origin_pos.y):
                        pg.draw.line(screen, (255, 255, 255), line["start"], line["end"])
                # if len(self.origin_his) >= 1:
                #     previous_origin = self.origin_his_pos[-1]
                #     pg.draw.circle(screen, (0, 255, 0), (previous_origin.x, previous_origin.y), 2)
                #     for pos in self.origin_his_pos:
                #         pg.draw.circle(screen, (255, 255, 0), (pos.x, pos.y), 2)
                for pgrid in self.maze_grid:
                    pg.draw.circle(screen, (255, 0, 255), (pgrid[0], pgrid[1]), 2)
                break
        else:
            if not self.maze_status:
                self.check_line()
            if not self.combine_status:
                self.main_line = self.merge_segments(self.main_line)
                print(f"[{dt.datetime.now().strftime('%X')}] Drawing complete.")
                self.save_maze_image()
            self.maze_status = True
            
    def save_maze_image(self):
        """Save just the maze portion, sized to fit the maze grid exactly."""
        # Calculate maze boundaries from maze_grid
        all_x = [point[0] for point in self.maze_grid]
        all_y = [point[1] for point in self.maze_grid]
        min_x, max_x = min(all_x) + 2, max(all_x)
        min_y, max_y = min(all_y) + 2, max(all_y)
        
        # Calculate dimensions with 2px padding
        width = max_x - min_x + 4
        height = max_y - min_y + 4
        
        # Create surface with calculated dimensions
        maze_surface = pg.Surface((width, height))
        maze_surface.fill((0, 0, 0))  # Black background
        
        # Draw all lines adjusted to the surface coordinates
        for line in self.main_line:
            # Adjust coordinates relative to maze boundaries
            adj_start = (line["start"][0] - min_x + 2, line["start"][1] - min_y + 2)
            adj_end = (line["end"][0] - min_x + 2, line["end"][1] - min_y + 2)
            pg.draw.line(maze_surface, (255, 255, 255), adj_start, adj_end, 1)
        
        # Save with timestamp
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"maze.png"
        pg.image.save(maze_surface, filename)
        self.image_status = True
        print(f"[{dt.datetime.now().strftime('%X')}] Maze saved as {filename} (Dimensions: {width}x{height})")
        
    def clear_maze(self):
        self.origin_his = []
        self.origin_his_pos = []
        self.line = []
        self.main_line = []
        self.corner = []
        self.visited = set() # New: Track visited cells
        self.maze_grid = set()
        self.maze_status = False
        self.combine_status = False
        self.image_status = False