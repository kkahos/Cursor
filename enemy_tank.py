# -*- coding: utf-8 -*-
"""
敌人坦克模块
继承自Tank基类，实现AI控制的敌人坦克
"""

import pygame
import random
import math
from tank import Tank
from config import *


class EnemyTank(Tank):
    """
    敌人坦克类
    
    继承自Tank基类，实现AI控制的自动行为
    """
    
    def __init__(self, x, y):
        """
        初始化敌人坦克
        
        Args:
            x (int): 坦克初始x坐标
            y (int): 坦克初始y坐标
        """
        super().__init__(x, y, DOWN, ENEMY_TANK_COLOR)
        
        # AI相关属性
        self.ai_timer = 0
        self.ai_decision_interval = 60  # AI决策间隔（帧数）
        self.current_action = "move"  # 当前动作：move, shoot, idle
        self.target_direction = DOWN
        self.stuck_counter = 0  # 卡住计数器
        self.max_stuck_time = 30  # 最大卡住时间
        
        # 移动相关
        self.last_position = (x, y)
        self.direction_change_timer = 0
        self.preferred_directions = [DOWN, LEFT, RIGHT, UP]  # 优先方向
        
        # 射击相关
        self.shot_cooldown = 800  # 敌人坦克射击冷却时间较长
        self.shoot_probability = 0.3  # 每次决策时的射击概率
        
        # 寻路相关
        self.player_last_seen_pos = None
        self.search_mode = False
    
    def get_distance_to_player(self, player_tank):
        """
        计算与玩家坦克的距离
        
        Args:
            player_tank (PlayerTank): 玩家坦克对象
            
        Returns:
            float: 与玩家的距离
        """
        if not player_tank.alive:
            return float('inf')
        
        dx = self.x - player_tank.x
        dy = self.y - player_tank.y
        return math.sqrt(dx * dx + dy * dy)
    
    def can_see_player(self, player_tank, game_map):
        """
        检查是否能看到玩家坦克（直线路径上没有障碍物）
        
        Args:
            player_tank (PlayerTank): 玩家坦克对象
            game_map (GameMap): 游戏地图对象
            
        Returns:
            bool: 如果能看到玩家返回True，否则返回False
        """
        if not player_tank.alive:
            return False
        
        # 简化的视线检查：检查是否在同一行或同一列，且路径无障碍
        dx = player_tank.x - self.x
        dy = player_tank.y - self.y
        
        # 检查是否在同一行或同一列
        if abs(dx) < 10:  # 同一列
            step_y = 1 if dy > 0 else -1
            for y in range(int(self.y), int(player_tank.y), step_y * 20):
                if not game_map.is_passable(self.x, y):
                    return False
            return True
        elif abs(dy) < 10:  # 同一行
            step_x = 1 if dx > 0 else -1
            for x in range(int(self.x), int(player_tank.x), step_x * 20):
                if not game_map.is_passable(x, self.y):
                    return False
            return True
        
        return False
    
    def get_direction_to_player(self, player_tank):
        """
        获取朝向玩家的方向
        
        Args:
            player_tank (PlayerTank): 玩家坦克对象
            
        Returns:
            int: 朝向玩家的方向
        """
        if not player_tank.alive:
            return self.direction
        
        dx = player_tank.x - self.x
        dy = player_tank.y - self.y
        
        # 选择主要移动方向
        if abs(dx) > abs(dy):
            return RIGHT if dx > 0 else LEFT
        else:
            return DOWN if dy > 0 else UP
    
    def choose_random_direction(self):
        """
        选择一个随机方向
        
        Returns:
            int: 随机方向
        """
        return random.choice([UP, DOWN, LEFT, RIGHT])
    
    def is_stuck(self):
        """
        检查坦克是否卡住
        
        Returns:
            bool: 如果卡住返回True，否则返回False
        """
        # 检查位置是否有变化
        current_pos = (self.x, self.y)
        if current_pos == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.last_position = current_pos
        
        return self.stuck_counter > self.max_stuck_time
    
    def make_ai_decision(self, player_tank, game_map):
        """
        AI决策过程
        
        Args:
            player_tank (PlayerTank): 玩家坦克对象
            game_map (GameMap): 游戏地图对象
            
        Returns:
            tuple: (action, direction) 决策结果
        """
        if not player_tank.alive:
            # 玩家死亡，随机移动
            return "move", self.choose_random_direction()
        
        distance_to_player = self.get_distance_to_player(player_tank)
        can_see = self.can_see_player(player_tank, game_map)
        
        # 如果能看到玩家且在射击范围内
        if can_see and distance_to_player < 200:
            # 朝向玩家
            target_dir = self.get_direction_to_player(player_tank)
            
            # 决定是否射击
            if (self.direction == target_dir and 
                random.random() < self.shoot_probability):
                return "shoot", target_dir
            else:
                return "turn", target_dir
        
        # 如果看不到玩家，向玩家方向移动
        elif distance_to_player < 300:
            target_dir = self.get_direction_to_player(player_tank)
            return "move", target_dir
        
        # 距离太远，随机移动
        else:
            return "move", self.choose_random_direction()
    
    def update(self, game_map, player_tank=None):
        """
        更新敌人坦克状态
        
        Args:
            game_map (GameMap): 游戏地图对象
            player_tank (PlayerTank): 玩家坦克对象
        """
        if not self.alive:
            return None
        
        self.ai_timer += 1
        bullet = None
        
        # 检查是否卡住
        if self.is_stuck():
            # 如果卡住了，随机选择新方向
            self.target_direction = self.choose_random_direction()
            self.stuck_counter = 0
        
        # AI决策
        if self.ai_timer >= self.ai_decision_interval:
            if player_tank:
                action, direction = self.make_ai_decision(player_tank, game_map)
                self.current_action = action
                self.target_direction = direction
            else:
                # 没有玩家目标，随机行动
                self.current_action = "move"
                self.target_direction = self.choose_random_direction()
            
            self.ai_timer = 0
        
        # 执行当前动作
        if self.current_action == "move":
            success = self.move(self.target_direction, game_map)
            if not success:
                # 移动失败，尝试其他方向
                self.target_direction = self.choose_random_direction()
        
        elif self.current_action == "turn":
            self.direction = self.target_direction
            self.current_action = "move"  # 转向后继续移动
        
        elif self.current_action == "shoot":
            self.direction = self.target_direction
            bullet = self.shoot("enemy")
            self.current_action = "move"  # 射击后继续移动
        
        return bullet
    
    def draw_tank_body(self, screen):
        """
        绘制敌人坦克主体
        
        为敌人坦克添加特殊的视觉标识
        
        Args:
            screen (pygame.Surface): 游戏屏幕对象
        """
        # 绘制坦克主体
        tank_rect = self.get_rect()
        pygame.draw.rect(screen, self.color, tank_rect)
        pygame.draw.rect(screen, BLACK, tank_rect, 2)
        
        # 在坦克上绘制一个小三角形作为敌人标识
        center_x, center_y = self.get_center()
        triangle_points = [
            (center_x, center_y - 5),
            (center_x - 4, center_y + 3),
            (center_x + 4, center_y + 3)
        ]
        pygame.draw.polygon(screen, BLACK, triangle_points)
    
    def take_damage(self):
        """
        敌人坦克受到伤害
        
        敌人坦克一击即毁
        """
        self.alive = False
    
    def reset_ai(self):
        """
        重置AI状态
        
        用于重新开始游戏或重置敌人行为
        """
        self.ai_timer = 0
        self.current_action = "move"
        self.target_direction = DOWN
        self.stuck_counter = 0
        self.last_position = (self.x, self.y)
        self.direction_change_timer = 0


class SmartEnemyTank(EnemyTank):
    """
    智能敌人坦克类
    
    比普通敌人坦克更聪明的AI行为
    """
    
    def __init__(self, x, y):
        """
        初始化智能敌人坦克
        
        Args:
            x (int): 坦克初始x坐标
            y (int): 坦克初始y坐标
        """
        super().__init__(x, y)
        self.ai_decision_interval = 30  # 更频繁的决策
        self.shoot_probability = 0.5  # 更高的射击概率
        self.shot_cooldown = 600  # 更短的射击冷却时间
        
        # 使用不同的颜色表示智能敌人
        self.color = (255, 100, 100)  # 浅红色
    
    def make_ai_decision(self, player_tank, game_map):
        """
        智能AI决策
        
        Args:
            player_tank (PlayerTank): 玩家坦克对象
            game_map (GameMap): 游戏地图对象
            
        Returns:
            tuple: (action, direction) 决策结果
        """
        if not player_tank.alive:
            return "move", self.choose_random_direction()
        
        distance_to_player = self.get_distance_to_player(player_tank)
        can_see = self.can_see_player(player_tank, game_map)
        
        # 智能敌人会预测玩家移动
        predicted_player_x = player_tank.x
        predicted_player_y = player_tank.y
        
        # 如果能看到玩家
        if can_see and distance_to_player < 250:
            target_dir = self.get_direction_to_player(player_tank)
            
            # 更高概率射击
            if (self.direction == target_dir and 
                random.random() < self.shoot_probability):
                return "shoot", target_dir
            else:
                return "turn", target_dir
        
        # 积极追击玩家
        elif distance_to_player < 400:
            target_dir = self.get_direction_to_player(player_tank)
            return "move", target_dir
        
        # 巡逻模式
        else:
            return "move", self.choose_random_direction()