import pygame as pg
from data_json import Config_json
import math
from tconfig import Config


class Player:
    __config = Config_json("config.json")

    def __init__(self):
        self.__config._load_json()
        self.x, self.y = Config.get('MAZE_PROPERTY', 'STARTING_POINT')[
            0], Config.get('MAZE_PROPERTY', 'STARTING_POINT')[1]
        self.speed = 5
        self.score = 0
        self.Player_position = None
        self.shoots_num = 0
        self.p_size = self.__config._get_data("MAZE", "box_size") // 5
        self.direction = 0  # radian

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
        pg.draw.polygon(screen, (255, 0, 0), vertices)

    def move(self, walls):
        # print(Config.KEY[key])
        keys = pg.key.get_pressed()
        move_x, move_y = 0, 0
        new_direction = self.direction

        if keys[pg.K_LEFT]:
            move_x = -1
            self.direction = math.pi
        if keys[pg.K_RIGHT]:
            move_x = 1
            self.direction = 0
        if keys[pg.K_UP]:
            move_y = -1
            new_direction = -math.pi / 2
        if keys[pg.K_DOWN]:
            move_y = 1
            new_direction = math.pi / 2

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071  # 1/sqrt(2)
            move_y *= 0.7071
            if move_x > 0 and move_y < 0:  # Right-up
                new_direction = -math.pi / 4
            elif move_x > 0 and move_y > 0:  # Right-down
                new_direction = math.pi / 4
            elif move_x < 0 and move_y < 0:  # Left-up
                new_direction = -3 * math.pi / 4
            elif move_x < 0 and move_y > 0:  # Left-down
                new_direction = 3 * math.pi / 4

        # self.x += move_x * self.speed
        # self.y += move_y * self.speed
        new_x = self.x + move_x * self.speed
        new_y = self.y + move_y * self.speed
    
        # Try X movement first
        if move_x != 0:
            new_x = self.x + move_x * self.speed
            if not self.check_maze_collision(walls, new_x, self.y):
                self.x = new_x
            else:
                # Try sliding by checking just Y movement
                if move_y != 0:
                    new_y = self.y + move_y * self.speed
                    if not self.check_maze_collision(walls, self.x, new_y):
                        self.y = new_y
        
        # Then try Y movement
        if move_y != 0:
            new_y = self.y + move_y * self.speed
            if not self.check_maze_collision(walls, self.x, new_y):
                self.y = new_y
            else:
                # Try sliding by checking just X movement
                if move_x != 0:
                    new_x = self.x + move_x * self.speed
                    if not self.check_maze_collision(walls, new_x, self.y):
                        self.x = new_x
    
        # Update direction only if movement occurred
            if move_x != 0 or move_y != 0:
                self.direction = new_direction

    def check_maze_collision(self, walls, new_x, new_y):
        # check that next position player moving to have any walls?
        tmp_vertices = self.get_vertices_pos(new_x, new_y, self.direction)

        player_edges = [
            (tmp_vertices[0], tmp_vertices[1]),
            (tmp_vertices[1], tmp_vertices[2]),
            (tmp_vertices[2], tmp_vertices[0])
        ]
        
        # Check each player edge against each wall
        for edge_start, edge_end in player_edges:
            for wall in walls:
                if self.segments_intersect(edge_start, edge_end, wall['start'], wall['end']):
                    # print("amogus")###################################################################
                    return True
        
        # Additional check: see if any player vertex is inside a wall (for corner cases)
        for vertex in tmp_vertices:
            if self.point_near_wall(vertex, walls):
                return True
                
        return False
    
    def point_near_wall(self, point, walls, threshold=3):
        """Check if a point is very close to any wall"""
        px, py = point
        for wall in walls:
            x1, y1 = wall['start']
            x2, y2 = wall['end']
            
            # Check distance from point to line segment
            line_length = math.hypot(x2-x1, y2-y1)
            if line_length == 0:  # Skip zero-length walls
                continue
                
            # Calculate projection
            u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_length**2)
            u = max(0, min(1, u))
            proj_x = x1 + u * (x2 - x1)
            proj_y = y1 + u * (y2 - y1)
            
            # Check distance to projection
            dist = math.hypot(px - proj_x, py - proj_y)
            if dist < threshold:
                return True
        return False

    def get_vertices_pos(self, x, y, direction):
        return [
            (x + self.p_size * math.cos(direction),
             y + self.p_size * math.sin(direction)),
            (x + self.p_size * math.cos(direction + 2 * math.pi / 3),
             y + self.p_size * math.sin(direction + 2 * math.pi / 3)),
            (x + self.p_size * math.cos(direction + 4 * math.pi / 3),
             y + self.p_size * math.sin(direction + 4 * math.pi / 3))
        ]

    def segments_intersect(self, A, B, C, D):
        """Check if line segments AB and CD intersect"""
        def ccw(A, B, C):
            return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

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
        return (self.x, self.y)
