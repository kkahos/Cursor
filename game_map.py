# -*- coding: utf-8 -*-
"""
游戏地图模块
处理地图的生成、渲染和碰撞检测
"""

import pygame
import random
from config import *


class GameMap:
    """
    游戏地图类
    
    负责地图的生成、渲染、碰撞检测和地形管理
    """
    
    def __init__(self):
        """
        初始化地图
        
        创建地图数据结构并生成随机地图
        """
        self.width = MAP_WIDTH
        self.height = MAP_HEIGHT
        self.tile_size = TILE_SIZE
        
        # 初始化地图数据，0表示空地
        self.map_data = [[EMPTY for _ in range(self.width)] 
                        for _ in range(self.height)]
        
        # 生成地图
        self.generate_map()
    
    def generate_map(self):
        """
        生成游戏地图
        
        随机生成砖墙、钢墙、水域等地形元素
        确保玩家出生点和敌人出生点周围有足够的空间
        """
        # 清空地图
        for y in range(self.height):
            for x in range(self.width):
                self.map_data[y][x] = EMPTY
        
        # 在地图边缘放置钢墙
        for x in range(self.width):
            self.map_data[0][x] = STEEL_WALL  # 顶部
            self.map_data[self.height - 1][x] = STEEL_WALL  # 底部
        
        for y in range(self.height):
            self.map_data[y][0] = STEEL_WALL  # 左侧
            self.map_data[y][self.width - 1] = STEEL_WALL  # 右侧
        
        # 随机生成内部地形
        for y in range(2, self.height - 2):
            for x in range(2, self.width - 2):
                # 跳过玩家出生区域（左下角）
                if y >= self.height - 4 and x <= 3:
                    continue
                
                # 跳过敌人出生区域（右上角）
                if y <= 3 and x >= self.width - 4:
                    continue
                
                rand = random.random()
                if rand < 0.3:  # 30%概率生成砖墙
                    self.map_data[y][x] = BRICK_WALL
                elif rand < 0.35:  # 5%概率生成钢墙
                    self.map_data[y][x] = STEEL_WALL
                elif rand < 0.4:  # 5%概率生成水域
                    self.map_data[y][x] = WATER
        
        # 在中央区域创建一些策略性障碍
        center_x, center_y = self.width // 2, self.height // 2
        
        # 创建十字形障碍
        for i in range(-2, 3):
            if 1 < center_x + i < self.width - 1:
                self.map_data[center_y][center_x + i] = BRICK_WALL
            if 1 < center_y + i < self.height - 1:
                self.map_data[center_y + i][center_x] = BRICK_WALL
    
    def get_tile_at_position(self, x, y):
        """
        获取指定像素位置的地图块类型
        
        Args:
            x (int): 像素x坐标
            y (int): 像素y坐标
            
        Returns:
            int: 地图块类型常量
        """
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        
        if (0 <= tile_x < self.width and 0 <= tile_y < self.height):
            return self.map_data[tile_y][tile_x]
        return STEEL_WALL  # 超出边界视为钢墙
    
    def is_passable(self, x, y):
        """
        检查指定像素位置是否可通行
        
        Args:
            x (int): 像素x坐标
            y (int): 像素y坐标
            
        Returns:
            bool: 如果可通行返回True，否则返回False
        """
        tile_type = self.get_tile_at_position(x, y)
        return tile_type in [EMPTY, GRASS]
    
    def can_destroy_tile(self, x, y):
        """
        检查指定位置的地形是否可以被摧毁
        
        Args:
            x (int): 像素x坐标
            y (int): 像素y坐标
            
        Returns:
            bool: 如果可以摧毁返回True，否则返回False
        """
        tile_type = self.get_tile_at_position(x, y)
        return tile_type == BRICK_WALL
    
    def destroy_tile(self, x, y):
        """
        摧毁指定位置的地形
        
        Args:
            x (int): 像素x坐标
            y (int): 像素y坐标
            
        Returns:
            bool: 如果成功摧毁返回True，否则返回False
        """
        tile_x = x // self.tile_size
        tile_y = y // self.tile_size
        
        if (0 <= tile_x < self.width and 0 <= tile_y < self.height and
            self.map_data[tile_y][tile_x] == BRICK_WALL):
            self.map_data[tile_y][tile_x] = EMPTY
            return True
        return False
    
    def check_collision_with_rect(self, rect):
        """
        检查矩形与地图障碍物的碰撞
        
        Args:
            rect (pygame.Rect): 要检查碰撞的矩形
            
        Returns:
            bool: 如果发生碰撞返回True，否则返回False
        """
        # 检查矩形四个角落的地形
        corners = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1)
        ]
        
        for x, y in corners:
            if not self.is_passable(x, y):
                return True
        
        return False
    
    def get_tile_rect(self, tile_x, tile_y):
        """
        获取指定地图块的像素矩形
        
        Args:
            tile_x (int): 地图块x坐标
            tile_y (int): 地图块y坐标
            
        Returns:
            pygame.Rect: 地图块的像素矩形
        """
        return pygame.Rect(tile_x * self.tile_size, 
                          tile_y * self.tile_size,
                          self.tile_size, 
                          self.tile_size)
    
    def draw(self, screen):
        """
        在屏幕上绘制地图
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        for y in range(self.height):
            for x in range(self.width):
                tile_type = self.map_data[y][x]
                rect = self.get_tile_rect(x, y)
                
                if tile_type == BRICK_WALL:
                    pygame.draw.rect(screen, BROWN, rect)
                    pygame.draw.rect(screen, DARK_GRAY, rect, 1)
                elif tile_type == STEEL_WALL:
                    pygame.draw.rect(screen, GRAY, rect)
                    pygame.draw.rect(screen, WHITE, rect, 2)
                elif tile_type == WATER:
                    pygame.draw.rect(screen, BLUE, rect)
                elif tile_type == GRASS:
                    pygame.draw.rect(screen, DARK_GREEN, rect)