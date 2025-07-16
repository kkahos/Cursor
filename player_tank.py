# -*- coding: utf-8 -*-
"""
玩家坦克模块
继承自Tank基类，实现玩家特有的功能
"""

import pygame
from tank import Tank
from config import *


class PlayerTank(Tank):
    """
    玩家坦克类
    
    继承自Tank基类，增加生命值系统和玩家特有的功能
    """
    
    def __init__(self, x, y, lives=PLAYER_LIVES):
        """
        初始化玩家坦克
        
        Args:
            x (int): 坦克初始x坐标
            y (int): 坦克初始y坐标
            lives (int): 玩家生命数量
        """
        super().__init__(x, y, UP, PLAYER_TANK_COLOR)
        self.lives = lives
        self.max_lives = lives
        self.invulnerable_time = 0  # 无敌时间
        self.invulnerable_duration = 2000  # 无敌持续时间（毫秒）
        self.respawn_x = x  # 重生点x坐标
        self.respawn_y = y  # 重生点y坐标
        
        # 玩家坦克射击冷却时间更短
        self.shot_cooldown = 300
    
    def handle_input(self, keys, game_map):
        """
        处理玩家输入
        
        Args:
            keys (dict): 当前按下的键盘按键状态
            game_map (GameMap): 游戏地图对象
            
        Returns:
            Bullet: 如果发射了子弹则返回子弹对象，否则返回None
        """
        if not self.alive:
            return None
        
        bullet = None
        moved = False
        
        # 处理移动输入
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            moved = self.move(UP, game_map)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            moved = self.move(DOWN, game_map)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            moved = self.move(LEFT, game_map)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            moved = self.move(RIGHT, game_map)
        
        # 处理射击输入
        if keys[pygame.K_SPACE]:
            bullet = self.shoot("player")
        
        return bullet
    
    def take_damage(self):
        """
        玩家坦克受到伤害
        
        如果处于无敌状态则不受伤害
        如果还有生命则重生，否则游戏结束
        """
        # 检查是否处于无敌状态
        current_time = pygame.time.get_ticks()
        if current_time < self.invulnerable_time:
            return
        
        # 减少生命
        self.lives -= 1
        
        if self.lives > 0:
            # 还有生命，重生
            self.respawn()
        else:
            # 生命耗尽
            self.alive = False
    
    def respawn(self):
        """
        重生玩家坦克
        
        将坦克移动到重生点并给予短暂的无敌时间
        """
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.direction = UP
        self.alive = True
        
        # 设置无敌时间
        self.invulnerable_time = pygame.time.get_ticks() + self.invulnerable_duration
    
    def is_invulnerable(self):
        """
        检查是否处于无敌状态
        
        Returns:
            bool: 如果处于无敌状态返回True，否则返回False
        """
        current_time = pygame.time.get_ticks()
        return current_time < self.invulnerable_time
    
    def draw(self, screen):
        """
        绘制玩家坦克
        
        如果处于无敌状态，坦克会闪烁显示
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        if not self.alive:
            return
        
        # 如果处于无敌状态，实现闪烁效果
        if self.is_invulnerable():
            # 每200毫秒切换一次显示状态
            current_time = pygame.time.get_ticks()
            if (current_time // 200) % 2 == 0:
                super().draw(screen)
        else:
            super().draw(screen)
    
    def draw_tank_body(self, screen):
        """
        绘制玩家坦克主体
        
        为玩家坦克添加特殊的视觉效果
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        # 绘制坦克主体
        tank_rect = self.get_rect()
        pygame.draw.rect(screen, self.color, tank_rect)
        pygame.draw.rect(screen, BLACK, tank_rect, 2)
        
        # 在坦克中心绘制一个小圆点作为标识
        center_x, center_y = self.get_center()
        pygame.draw.circle(screen, WHITE, (int(center_x), int(center_y)), 3)
    
    def update(self, game_map):
        """
        更新玩家坦克状态
        
        Args:
            game_map (GameMap): 游戏地图对象
        """
        # 调用父类的更新方法
        super().update(game_map)
        
        # 这里可以添加玩家坦克特有的更新逻辑
        pass
    
    def get_lives_remaining(self):
        """
        获取剩余生命数
        
        Returns:
            int: 剩余生命数
        """
        return self.lives
    
    def add_life(self):
        """
        增加一条生命
        
        通常用于获得奖励道具时
        """
        if self.lives < self.max_lives * 2:  # 限制最大生命数
            self.lives += 1
    
    def reset(self):
        """
        重置玩家坦克到初始状态
        
        用于开始新游戏时
        """
        self.x = self.respawn_x
        self.y = self.respawn_y
        self.direction = UP
        self.alive = True
        self.lives = self.max_lives
        self.invulnerable_time = 0
        self.last_shot_time = 0