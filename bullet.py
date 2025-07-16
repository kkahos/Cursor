# -*- coding: utf-8 -*-
"""
子弹类模块
处理子弹的创建、移动、碰撞检测等功能
"""

import pygame
from config import *


class Bullet:
    """
    子弹类
    
    负责子弹的移动、碰撞检测和绘制
    """
    
    def __init__(self, x, y, direction, owner):
        """
        初始化子弹
        
        Args:
            x (int): 子弹初始x坐标
            y (int): 子弹初始y坐标
            direction (int): 子弹移动方向
            owner (str): 子弹所有者，"player" 或 "enemy"
        """
        self.x = x
        self.y = y
        self.direction = direction
        self.owner = owner
        self.speed = BULLET_SPEED
        self.size = BULLET_SIZE
        self.active = True
        
        # 根据方向设置移动向量
        self.dx, self.dy = DIRECTIONS[direction]
        self.dx *= self.speed
        self.dy *= self.speed
    
    def update(self):
        """
        更新子弹位置
        
        每帧调用一次，更新子弹的位置
        如果子弹移出屏幕边界，则将其标记为非活跃状态
        """
        if not self.active:
            return
            
        # 更新位置
        self.x += self.dx
        self.y += self.dy
        
        # 检查是否超出屏幕边界
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT):
            self.active = False
    
    def get_rect(self):
        """
        获取子弹的碰撞矩形
        
        Returns:
            pygame.Rect: 子弹的碰撞矩形
        """
        return pygame.Rect(self.x - self.size // 2, 
                          self.y - self.size // 2, 
                          self.size, self.size)
    
    def draw(self, screen):
        """
        在屏幕上绘制子弹
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        if self.active:
            pygame.draw.circle(screen, BULLET_COLOR, 
                             (int(self.x), int(self.y)), 
                             self.size // 2)
    
    def check_collision_with_rect(self, rect):
        """
        检查子弹是否与指定矩形碰撞
        
        Args:
            rect (pygame.Rect): 要检查碰撞的矩形
            
        Returns:
            bool: 如果碰撞返回True，否则返回False
        """
        if not self.active:
            return False
            
        bullet_rect = self.get_rect()
        if bullet_rect.colliderect(rect):
            self.active = False
            return True
        return False
    
    def destroy(self):
        """
        销毁子弹
        
        将子弹标记为非活跃状态
        """
        self.active = False