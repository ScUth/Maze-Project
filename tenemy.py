import pygame as pg
import math
from tconfig import Config
from data_json import Config_json
import random
import heapq
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor
from tscore import Score
import time
import datetime as dt

class Enemy:
    __config = Config_json("config.json")
    
    __CORNER_POSITIONS = [
        'TOP_LEFT',
        'TOP_RIGHT',
        'BOTTOM_LEFT',
        'BOTTOM_RIGHT'
    ]
    
    _pathfinding_executor = ThreadPoolExecutor(max_workers=4)
    
    def __init__(self, corner_index, maze_walls, lvl):
        self.__config._load_json()
        self.corner_index = corner_index
        self.corner_name = self.__CORNER_POSITIONS[corner_index]
        self.x, self.y = Config.get('MAZE_PROPERTY', self.corner_name)
        self.width = self.__config._get_data('MAZE', 'box_size') // 2
        self.height = self.__config._get_data('MAZE', 'box_size') // 2
        self.speed = 0.5 * (lvl + 1)
        self.current_speed = self.speed
        self.maze_walls = maze_walls  # This is your self.line from Maze_Gen
        self.path = []
        self.respawn_timer = 0
        self.is_active = True
        self.color = (
            random.randint(100, 255),
            random.randint(100, 255),
            random.randint(100, 255)
        )
        self.path_update_interval = 50  # frames between path updates
        self.path_update_counter = random.randint(0, self.path_update_interval)  # Stagger updates
        self.last_player_pos = None
        self.simple_path = deque()  # For immediate movement while calculating
        self.calculating_path = False
        self.grid_size = self.__config._get_data('MAZE', 'box_size')
        self.score = Score()
        self.shot = False
        self.last_path_update_time = 0  # Track last update time
        self.path_update_cooldown = 4800
        
        # Precompute wall collisions
        self.wall_rects = self._precompute_wall_rects()
        self.last_player_pos = None

    def _precompute_wall_rects(self):
        """Precompute wall rectangles for faster collision checking"""
        wall_rects = []
        for wall in self.maze_walls:
            if wall['start'][0] == wall['end'][0]:  # Vertical wall
                rect = pg.Rect(
                    wall['start'][0] - 2,
                    min(wall['start'][1], wall['end'][1]),
                    4,
                    abs(wall['end'][1] - wall['start'][1])
                )
            else:  # Horizontal wall
                rect = pg.Rect(
                    min(wall['start'][0], wall['end'][0]),
                    wall['start'][1] - 2,
                    abs(wall['end'][0] - wall['start'][0]),
                    4
                )
            wall_rects.append(rect)
        return wall_rects

    def get_position(self):
        return (self.x, self.y)

    def draw(self, screen):
        if not self.is_active:
            return
            
        enemy_rect = pg.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        pg.draw.rect(screen, self.color, enemy_rect)

    def move_towards_player(self, player_pos):
        if not self.is_active:
            return
            
        if self.calculating_path:
            self._move_simple_towards(player_pos)
            return
            
        self.path_update_counter -= 1
        current_time = time.time()
        player_moved = (
        self.last_player_pos is None or
        self.distance(player_pos, self.last_player_pos) > self.grid_size * 2
        )
        
        cooldown_expired = (current_time - self.last_path_update_time) >= self.path_update_cooldown
        path_invalid = not self.path  # No path left
        
        if cooldown_expired or player_moved or path_invalid:
            # print(dt.datetime.now().strftime('%X'))
            self._update_path_async(player_pos)
            self.last_path_update_time = current_time  # Reset cooldown
        else:
            self._follow_path()

    def _update_path_async(self, player_pos):
        if self.calculating_path:  # Avoid overlapping calculations
            return

        self.calculating_path = True
        self.last_player_pos = player_pos

        current_node = (round(self.x / self.grid_size), round(self.y / self.grid_size))
        target_node = (round(player_pos[0] / self.grid_size), round(player_pos[1] / self.grid_size))

        # Submit to thread pool (if using one)
        threading.Thread(
            target=self._calculate_path_threaded,
            args=(current_node, target_node),
            daemon=True
        ).start()
    
    def _calculate_path_threaded(self, start_node, end_node): # a-staR
        # Same calculation as _calculate_path_in_background
        open_set = []
        heapq.heappush(open_set, (0, start_node))
        came_from = {}
        g_score = {start_node: 0}
        f_score = {start_node: self.heuristic(start_node, end_node)}
        closed_set = set()
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == end_node:
                path = self._reconstruct_path(came_from, current)
                self.path = path
                self.calculating_path = False
                return
                
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue
                    
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] =  self.heuristic(neighbor, end_node)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        if came_from:
            current = min(closed_set, key=lambda x: self.heuristic(x, end_node))
            path = self._reconstruct_path(came_from, current)
            self.path = path
        self.calculating_path = False

    def _calculate_path_in_background(self, start_node, end_node):
        MAX_ITERATIONS_PER_FRAME = 100 # limited iteration
        
        for _ in range(MAX_ITERATIONS_PER_FRAME):
            if not open_set:
                break
            open_set = []
            heapq.heappush(open_set, (0, start_node))
            came_from = {}
            g_score = {start_node: 0}
            f_score = {start_node: self.heuristic(start_node, end_node)}
            closed_set = set()
            
            for _ in range(50):  # Limited iterations per frame
                if not open_set:
                    break
                    
                current = heapq.heappop(open_set)[1]
                
                if current == end_node:
                    path = self._reconstruct_path(came_from, current)
                    self.path = path
                    self.calculating_path = False
                    return
                    
                closed_set.add(current)
                
                for neighbor in self.get_neighbors(current):
                    if neighbor in closed_set:
                        continue
                        
                    tentative_g_score = g_score[current] + 1
                    
                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, end_node)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
            
            if came_from:
                current = min(closed_set, key=lambda x: self.heuristic(x, end_node))
                path = self._reconstruct_path(came_from, current)
                self.path = path
            self.calculating_path = False

    def _reconstruct_path(self, came_from, current):
        total_path = []
        while current in came_from:
            total_path.append((current[0] * self.grid_size, current[1] * self.grid_size))
            current = came_from[current]
        return list(reversed(total_path))

    def _follow_path(self):
        if not self.path:
            return
            
        target_x, target_y = self.path[0]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 5:
            self.path.pop(0)
        else:
            if distance > 0:
                dx = dx / distance * self.current_speed
                dy = dy / distance * self.current_speed
            self.x += dx
            self.y += dy

    def _move_simple_towards(self, target_pos):
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx = dx / distance * self.current_speed
            dy = dy / distance * self.current_speed
            
        new_x = self.x + dx
        new_y = self.y + dy
        
        temp_rect = pg.Rect(
            new_x - self.width//2,
            new_y - self.height//2,
            self.width,
            self.height
        )
        
        collision = False
        for wall_rect in self.wall_rects:
            if temp_rect.colliderect(wall_rect):
                collision = True
                break
                
        if not collision:
            self.x = new_x
            self.y = new_y
        else:
            temp_rect.x = self.x + dx - self.width//2
            temp_rect.y = self.y - self.height//2
            if not any(temp_rect.colliderect(wall) for wall in self.wall_rects):
                self.x += dx
            else:
                temp_rect.x = self.x - self.width//2
                temp_rect.y = self.y + dy - self.height//2
                if not any(temp_rect.colliderect(wall) for wall in self.wall_rects):
                    self.y += dy

    def get_neighbors(self, node):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []
        
        for dx, dy in directions:
            neighbor = (node[0] + dx, node[1] + dy)
            x1, y1 = node[0] * self.grid_size, node[1] * self.grid_size
            x2, y2 = neighbor[0] * self.grid_size, neighbor[1] * self.grid_size
            
            if not self.intersects_wall((x1, y1), (x2, y2)):
                neighbors.append(neighbor)
        return neighbors

    def intersects_wall(self, point1, point2):
        for wall in self.maze_walls:
            if self.segments_intersect(point1, point2, wall['start'], wall['end']):
                return True
        return False

    def segments_intersect(self, A, B, C, D):
        def ccw(A, B, C):
            return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def distance(self, pos1, pos2):
        return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)

    def check_hit_by_bullet(self, bullets):
        if not self.is_active:
            return False
            
        enemy_rect = pg.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        
        for bullet in bullets:
            bullet_rect = pg.Rect(
                bullet.x - bullet.radius,
                bullet.y - bullet.radius,
                bullet.radius * 2,
                bullet.radius * 2
            )
            
            if enemy_rect.colliderect(bullet_rect):
                bullets.remove(bullet)
                self.shot = True
                self.respawn()
                return True
        return False

    def check_player_collision(self, player_pos, player_size):
        if not self.is_active:
            return False
            
        enemy_rect = pg.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        
        player_rect = pg.Rect(
            player_pos[0] - player_size // 2,
            player_pos[1] - player_size // 2,
            player_size,
            player_size
        )
        
        return enemy_rect.colliderect(player_rect)

    def respawn(self):
        self.is_active = False
        self.respawn_timer = 600 # ms
        self.current_speed *= 2
        self.path = []
        self.x, self.y = Config.get('MAZE_PROPERTY', self.corner_name)

    def update(self, player_pos, bullets):
        if not self.is_active:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.is_active = True
                self.current_speed = self.speed * 2  # Ensure speed is doubled on respawn
        else:
            self.move_towards_player(player_pos)
            self.check_hit_by_bullet(bullets)