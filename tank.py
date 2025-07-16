# -*- coding: utf-8 -*-
"""
坦克基类模块
定义坦克的基本属性和行为
"""

import pygame
import math
from config import *
from bullet import Bullet


class Tank:
    """
    坦克基类
    
    定义所有坦克共有的属性和方法，包括移动、射击、绘制等
    """
    
    def __init__(self, x, y, direction=UP, color=GREEN):
        """
        初始化坦克
        
        Args:
            x (int): 坦克初始x坐标
            y (int): 坦克初始y坐标
            direction (int): 坦克初始朝向
            color (tuple): 坦克颜色(R, G, B)
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.size = TANK_SIZE
        self.speed = TANK_SPEED
        self.alive = True
        
        # 射击相关
        self.last_shot_time = 0
        self.shot_cooldown = 500  # 射击冷却时间（毫秒）
        
        # 移动相关
        self.moving = False
        self.target_x = x
        self.target_y = y
    
    def get_rect(self):
        """
        获取坦克的碰撞矩形
        
        Returns:
            pygame.Rect: 坦克的碰撞矩形
        """
        return pygame.Rect(self.x - self.size // 2, 
                          self.y - self.size // 2,
                          self.size, self.size)
    
    def get_front_position(self):
        """
        获取坦克前方的位置（用于发射子弹）
        
        Returns:
            tuple: (x, y) 坦克前方的坐标
        """
        dx, dy = DIRECTIONS[self.direction]
        front_x = self.x + dx * (self.size // 2 + 5)
        front_y = self.y + dy * (self.size // 2 + 5)
        return front_x, front_y
    
    def can_move(self, new_x, new_y, game_map):
        """
        检查坦克是否可以移动到指定位置
        
        Args:
            new_x (int): 新的x坐标
            new_y (int): 新的y坐标
            game_map (GameMap): 游戏地图对象
            
        Returns:
            bool: 如果可以移动返回True，否则返回False
        """
        # 创建新位置的矩形
        new_rect = pygame.Rect(new_x - self.size // 2, 
                              new_y - self.size // 2,
                              self.size, self.size)
        
        # 检查是否与地图碰撞
        return not game_map.check_collision_with_rect(new_rect)
    
    def move(self, direction, game_map):
        """
        移动坦克
        
        Args:
            direction (int): 移动方向
            game_map (GameMap): 游戏地图对象
            
        Returns:
            bool: 如果成功移动返回True，否则返回False
        """
        if not self.alive:
            return False
        
        # 更新朝向
        self.direction = direction
        
        # 计算新位置
        dx, dy = DIRECTIONS[direction]
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        
        # 检查是否可以移动
        if self.can_move(new_x, new_y, game_map):
            self.x = new_x
            self.y = new_y
            return True
        
        return False
    
    def can_shoot(self):
        """
        检查是否可以射击
        
        Returns:
            bool: 如果可以射击返回True，否则返回False
        """
        current_time = pygame.time.get_ticks()
        return (self.alive and 
                current_time - self.last_shot_time >= self.shot_cooldown)
    
    def shoot(self, owner="unknown"):
        """
        发射子弹
        
        Args:
            owner (str): 子弹所有者标识
            
        Returns:
            Bullet: 创建的子弹对象，如果无法射击则返回None
        """
        if not self.can_shoot():
            return None
        
        # 更新射击时间
        self.last_shot_time = pygame.time.get_ticks()
        
        # 获取子弹发射位置
        bullet_x, bullet_y = self.get_front_position()
        
        # 创建子弹
        bullet = Bullet(bullet_x, bullet_y, self.direction, owner)
        return bullet
    
    def take_damage(self):
        """
        坦克受到伤害
        
        基础实现是直接销毁坦克，子类可以重写此方法实现不同的伤害机制
        """
        self.alive = False
    
    def draw_tank_body(self, screen):
        """
        绘制坦克主体
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        # 绘制坦克主体（矩形）
        tank_rect = self.get_rect()
        pygame.draw.rect(screen, self.color, tank_rect)
        pygame.draw.rect(screen, BLACK, tank_rect, 2)
    
    def draw_tank_cannon(self, screen):
        """
        绘制坦克炮筒
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        # 计算炮筒方向
        dx, dy = DIRECTIONS[self.direction]
        
        # 炮筒起点和终点
        start_x = self.x + dx * 5
        start_y = self.y + dy * 5
        end_x = self.x + dx * (self.size // 2 + 8)
        end_y = self.y + dy * (self.size // 2 + 8)
        
        # 绘制炮筒
        pygame.draw.line(screen, BLACK, 
                        (start_x, start_y), (end_x, end_y), 3)
    
    def draw(self, screen):
        """
        在屏幕上绘制坦克
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        if self.alive:
            self.draw_tank_body(screen)
            self.draw_tank_cannon(screen)
    
    def update(self, game_map):
        """
        更新坦克状态
        
        Args:
            game_map (GameMap): 游戏地图对象
        """
        # 基类的更新方法，子类可以重写
        pass
    
    def check_collision_with_bullet(self, bullet):
        """
        检查坦克是否与子弹碰撞
        
        Args:
            bullet (Bullet): 子弹对象
            
        Returns:
            bool: 如果碰撞返回True，否则返回False
        """
        if not self.alive or not bullet.active:
            return False
        
        tank_rect = self.get_rect()
        return bullet.check_collision_with_rect(tank_rect)
    
    def get_center(self):
        """
        获取坦克中心坐标
        
        Returns:
            tuple: (x, y) 坦克中心坐标
        """
        return (self.x, self.y)