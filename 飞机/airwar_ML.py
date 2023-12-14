import pygame
import sys
import random
import math
import copy

# 初始化Pygame
pygame.init()

# 屏幕大小
screen_width = 1000
screen_height = 1000
noneflyzone = 50

# 颜色定义
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 飞机参数
enemy_size = 10
player_size = 10
player_speed = 2
attack_distance = 100
attack_range = 5
attack_damage = 20
maxdegree = 2

# 初始化屏幕
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jailbroken Game")

# 定义飞机类
class Aircraft:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.health = 100
        self.angle = random.randint(-180,180)
        self.locked_enemy = None

    def draw(self):
        rotated_surface = pygame.transform.rotate(self.draw_polygon(), -self.angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rotated_rect.topleft)
    
    def draw_polygon(self):
        surface = pygame.Surface((player_size, player_size), pygame.SRCALPHA)

        # 定义头大尾小的多边形坐标
        polygon_points = [
            (0, player_size / 2),   # 左下
            (player_size / 2, 0),   # 顶点
            (player_size, player_size / 2),  # 右下
            (player_size / 2, player_size)   # 底点
        ]

        pygame.draw.polygon(surface, self.color, polygon_points)
        return surface

    def update(self):
        self.locked_enemy = self.find_target()
        if self.x<noneflyzone or self.x>screen_width-noneflyzone or self.y<noneflyzone or self.y>screen_height-noneflyzone:
            angle_to_enemy = math.atan2(screen_width//2 - self.y, screen_width//2 - self.x)
            targetdegree = math.degrees(angle_to_enemy)
            need = targetdegree-self.angle
            need= (need+720)%360-180
            if(need>maxdegree or need<-maxdegree):
                if(need<=0):
                    self.angle=self.angle+maxdegree
                else:
                    self.angle=self.angle-maxdegree
            else:
                self.angle=self.angle+need
        elif self.locked_enemy:
            angle_to_enemy = math.atan2(self.locked_enemy.y - self.y, self.locked_enemy.x - self.x)
            targetdegree = math.degrees(angle_to_enemy)
            need = targetdegree-self.angle
            need= (need+720)%360-180
            if(need>maxdegree or need<-maxdegree):
                if(need<=0):
                    self.angle=self.angle+maxdegree
                else:
                    self.angle=self.angle-maxdegree
            else:
                self.angle=self.angle+need
            self.attack()
        else:
            self.angle=self.angle + random.randint(-maxdegree,maxdegree)

        # 无论是否有锁定敌人，都更新位置
        radian_angle = math.radians(self.angle)
        self.x += player_speed * math.cos(radian_angle)
        self.y += player_speed * math.sin(radian_angle)

        # 以下代码用于旋转飞机的形状
        rotated_surface = pygame.transform.rotate(self.draw_polygon(), -self.angle)
        rotated_rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, rotated_rect.topleft)

    def attack(self):
        distance_to_enemy = math.sqrt((self.locked_enemy.x - self.x)**2 + (self.locked_enemy.y - self.y)**2)
        angle_to_enemy = math.atan2(self.locked_enemy.y - self.y, self.locked_enemy.x - self.x)
        targetdegree = math.degrees(angle_to_enemy)
        need = targetdegree-self.angle
        need= 180-abs((need+720)%360-180)
        if ((distance_to_enemy < attack_distance)and(need<=attack_range)):
            self.locked_enemy.health -= attack_damage
            if self.locked_enemy.health <= 0:
                enemies.remove(self.locked_enemy)
                self.locked_enemy = None
    
    def find_target(self):
        targets = [enemy for enemy in enemies if enemy.color != self.color]

        if len(targets)==0:
            return None
        # 其次选择前方最近的敌人
        targets.sort(key=lambda enemy: math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2))
        targets.sort(key=lambda enemy: abs(self.angle-math.degrees(math.atan2(enemy.y-self.y,enemy.x-self.x))))

        value_0 = 1000*(360-abs(self.angle-math.degrees(math.atan2(targets[0].y-self.y,targets[0].x-self.x))))
        value_0 = value_0 - 10*math.sqrt((targets[0].x - self.x)**2 + (targets[0].y - self.y)**2)
        if(self.locked_enemy in targets):
            locked_enemy = self.locked_enemy
            value_bef = 1000*abs(self.angle-math.degrees(math.atan2(locked_enemy.y-self.y,locked_enemy.x-self.x)))
            value_bef = value_bef - 10*math.sqrt((locked_enemy.x - self.x)**2 + (locked_enemy.y - self.y)**2)
            value_bef = value_bef + 11451
        else:
            value_bef = 0

        # 优先选择上次锁定的敌人
        if ((self.locked_enemy in targets)and(value_bef>=value_0)):
            return self.locked_enemy

        return targets[0]

# 初始化敌人列表
enemies = []

# 游戏主循环
clock = pygame.time.Clock()
enemy_spawn_timer = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # 点击鼠标左键召唤绿色飞机
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player = Aircraft(mouse_x,mouse_y,GREEN)
            enemies.append(player)
        # 点击鼠标右键召唤红色飞机
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player = Aircraft(mouse_x,mouse_y,RED)
            enemies.append(player)

    

    # 更新敌人飞机
    for enemy in enemies:
        enemy.update()

    # 清空屏幕
    screen.fill(WHITE)

    # 绘制敌人飞机
    for enemy in enemies:
        enemy.draw()

    # 更新显示
    pygame.display.flip()

    # 控制帧率
    clock.tick(60)