import pygame as pg
from data_json import Config_json
import math
from tconfig import Config


class Player:
    __config = Config_json("config.json")

    def __init__(self, lvl):
        self.__config._load_json()
        self.x, self.y = Config.get('MAZE_PROPERTY', 'STARTING_POINT')[
            0], Config.get('MAZE_PROPERTY', 'STARTING_POINT')[1]
        self.speed = 2 * (lvl+1)
        self.score = 0
        self.Player_position = None
        self.shoots_num = 0
        self.p_size = self.__config._get_data("MAZE", "box_size") // 5
        self.direction = 0  # radian
        self.bullets = []
        self.shoot_cooldown = 0

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
        keys = pg.key.get_pressed()
        move_x, move_y = 0, 0
        new_direction = self.direction

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            move_x = -1
            new_direction = math.pi
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            move_x = 1
            new_direction = 0
        if keys[pg.K_UP] or keys[pg.K_w]:
            move_y = -1
            new_direction = -math.pi / 2
        if keys[pg.K_DOWN] or keys[pg.K_s]:
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

        # Try full movement first
        new_x = self.x + move_x * self.speed
        new_y = self.y + move_y * self.speed
        
        if not self.check_maze_collision(walls, new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            # Try X movement only
            new_x = self.x + move_x * self.speed
            if not self.check_maze_collision(walls, new_x, self.y):
                self.x = new_x
            # Try Y movement only
            new_y = self.y + move_y * self.speed
            if not self.check_maze_collision(walls, self.x, new_y):
                self.y = new_y

        # Update direction only if movement occurred
        if move_x != 0 or move_y != 0:
            self.direction = new_direction

    def check_maze_collision(self, walls, new_x, new_y):
        radius = self.p_size * 0.9  # Slightly smaller than triangle to feel smooth

        for wall in walls:
            if self.circle_near_wall((new_x, new_y), radius, wall):
                return True
        return False
    
    def circle_near_wall(self, center, radius, wall):
        """Check if a circle (player) is too close to a wall line segment"""
        cx, cy = center
        x1, y1 = wall['start']
        x2, y2 = wall['end']

        line_length = math.hypot(x2 - x1, y2 - y1)
        if line_length == 0:
            return math.hypot(cx - x1, cy - y1) < radius

        # Projection factor
        u = ((cx - x1) * (x2 - x1) + (cy - y1) * (y2 - y1)) / (line_length ** 2)
        u = max(0, min(1, u))
        proj_x = x1 + u * (x2 - x1)
        proj_y = y1 + u * (y2 - y1)

        dist = math.hypot(cx - proj_x, cy - proj_y)
        return dist < radius
    
    def point_near_wall(self, point, walls, threshold=2):
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
        if self.shoot_cooldown <= 0:
            # Create a new bullet at player's position facing current direction
            bullet_x = self.x + self.p_size * math.cos(self.direction)
            bullet_y = self.y + self.p_size * math.sin(self.direction)
            self.bullets.append(Bullet(bullet_x, bullet_y, self.direction))
            self.shoot_cooldown = 10  # 10 frames cooldown (about 0.16 seconds at 60fps)
            self.shoots_num += 1
    
    def update_bullets(self, walls):
        for bullet in self.bullets[:]:  # Iterate over a copy to allow removal
            bullet.update()
            bullet.check_collision(walls)
            if not bullet.active:
                self.bullets.remove(bullet)

        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
    def draw_bullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)

    def get_position(self):
        return (self.x, self.y)

class Bullet:
    def __init__(self, x, y, direction, speed=10, radius=5):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.radius = radius
        self.lifetime = 60  # frames before bullet disappears (1 second at 60fps)
        self.active = True

    def update(self):
        # Move bullet based on direction and speed
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

    def draw(self, screen):
        pg.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

    def check_collision(self, walls):
        # Check if bullet hits any walls
        for wall in walls:
            if self.point_near_wall((self.x, self.y), wall, self.radius):
                self.active = False
                return True
        return False

    def point_near_wall(self, point, wall, threshold):
        """Check if a point is very close to a wall"""
        px, py = point
        x1, y1 = wall['start']
        x2, y2 = wall['end']
        
        # Check distance from point to line segment
        line_length = math.hypot(x2-x1, y2-y1)
        if line_length == 0:  # Skip zero-length walls
            return False
            
        # Calculate projection
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_length**2)
        u = max(0, min(1, u))
        proj_x = x1 + u * (x2 - x1)
        proj_y = y1 + u * (y2 - y1)
        
        # Check distance to projection
        dist = math.hypot(px - proj_x, py - proj_y)
        return dist < threshold