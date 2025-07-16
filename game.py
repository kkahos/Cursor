# -*- coding: utf-8 -*-
"""
游戏主类模块
管理游戏的整体逻辑、状态和渲染
"""

import pygame
import random
import sys
from config import *
from game_map import GameMap
from player_tank import PlayerTank
from enemy_tank import EnemyTank, SmartEnemyTank
from bullet import Bullet


class Game:
    """
    游戏主类
    
    负责管理游戏的整体逻辑、状态转换、渲染和用户输入处理
    """
    
    def __init__(self):
        """
        初始化游戏
        
        设置pygame，创建游戏对象和初始状态
        """
        # 初始化pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战 - Tank Battle")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.game_state = "playing"  # playing, game_over, victory, paused
        self.score = 0
        self.level = 1
        
        # 游戏对象
        self.game_map = None
        self.player_tank = None
        self.enemy_tanks = []
        self.bullets = []
        
        # 敌人生成相关
        self.enemies_destroyed = 0
        self.max_enemies_per_level = ENEMY_COUNT
        self.enemy_spawn_timer = 0
        self.enemy_spawn_positions = [
            (SCREEN_WIDTH - 60, 60),
            (SCREEN_WIDTH - 120, 60),
            (SCREEN_WIDTH - 60, 120)
        ]
        
        # 字体
        try:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.SysFont('arial', 36)
            self.small_font = pygame.font.SysFont('arial', 24)
        
        # 初始化游戏
        self.init_game()
    
    def init_game(self):
        """
        初始化游戏状态
        
        创建地图、玩家坦克和初始敌人
        """
        # 创建地图
        self.game_map = GameMap()
        
        # 创建玩家坦克（左下角）
        player_start_x = TILE_SIZE * 2
        player_start_y = SCREEN_HEIGHT - TILE_SIZE * 2
        self.player_tank = PlayerTank(player_start_x, player_start_y)
        
        # 清空游戏对象列表
        self.enemy_tanks = []
        self.bullets = []
        
        # 生成初始敌人
        self.spawn_initial_enemies()
        
        # 重置计数器
        self.enemies_destroyed = 0
        self.enemy_spawn_timer = 0
    
    def spawn_initial_enemies(self):
        """
        生成初始敌人坦克
        """
        for i in range(min(3, self.max_enemies_per_level)):
            if i < len(self.enemy_spawn_positions):
                x, y = self.enemy_spawn_positions[i]
                
                # 随机决定生成普通敌人还是智能敌人
                if random.random() < 0.3:  # 30%概率生成智能敌人
                    enemy = SmartEnemyTank(x, y)
                else:
                    enemy = EnemyTank(x, y)
                
                self.enemy_tanks.append(enemy)
    
    def spawn_enemy(self):
        """
        生成新的敌人坦克
        
        Returns:
            bool: 如果成功生成敌人返回True，否则返回False
        """
        if len(self.enemy_tanks) >= 5:  # 限制同时存在的敌人数量
            return False
        
        # 选择生成位置
        spawn_pos = random.choice(self.enemy_spawn_positions)
        x, y = spawn_pos
        
        # 检查生成位置是否被占用
        spawn_rect = pygame.Rect(x - TANK_SIZE//2, y - TANK_SIZE//2, 
                                TANK_SIZE, TANK_SIZE)
        
        # 检查是否与玩家冲突
        if self.player_tank.alive:
            player_rect = self.player_tank.get_rect()
            if spawn_rect.colliderect(player_rect):
                return False
        
        # 检查是否与其他敌人冲突
        for enemy in self.enemy_tanks:
            if enemy.alive:
                enemy_rect = enemy.get_rect()
                if spawn_rect.colliderect(enemy_rect):
                    return False
        
        # 随机决定敌人类型
        if random.random() < 0.4:  # 40%概率生成智能敌人
            enemy = SmartEnemyTank(x, y)
        else:
            enemy = EnemyTank(x, y)
        
        self.enemy_tanks.append(enemy)
        return True
    
    def handle_events(self):
        """
        处理游戏事件
        
        Returns:
            bool: 如果游戏应该继续运行返回True，否则返回False
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_r and self.game_state in ["game_over", "victory"]:
                    # 重新开始游戏
                    self.restart_game()
                
                elif event.key == pygame.K_p and self.game_state == "playing":
                    # 暂停游戏
                    self.game_state = "paused"
                
                elif event.key == pygame.K_p and self.game_state == "paused":
                    # 恢复游戏
                    self.game_state = "playing"
        
        return True
    
    def update(self):
        """
        更新游戏逻辑
        """
        if self.game_state != "playing":
            return
        
        # 处理玩家输入
        keys = pygame.key.get_pressed()
        if self.player_tank.alive:
            bullet = self.player_tank.handle_input(keys, self.game_map)
            if bullet:
                self.bullets.append(bullet)
        
        # 更新敌人坦克
        for enemy in self.enemy_tanks[:]:  # 使用切片创建副本避免修改时出错
            if enemy.alive:
                bullet = enemy.update(self.game_map, self.player_tank)
                if bullet:
                    self.bullets.append(bullet)
            else:
                self.enemy_tanks.remove(enemy)
                self.enemies_destroyed += 1
                self.score += 100
        
        # 生成新敌人
        current_time = pygame.time.get_ticks()
        if (len(self.enemy_tanks) < 3 and 
            current_time - self.enemy_spawn_timer > ENEMY_SPAWN_DELAY):
            if self.spawn_enemy():
                self.enemy_spawn_timer = current_time
        
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
        
        # 检查碰撞
        self.check_collisions()
        
        # 检查游戏结束条件
        self.check_game_over()
    
    def check_collisions(self):
        """
        检查所有碰撞
        
        包括子弹与坦克、子弹与地图的碰撞
        """
        for bullet in self.bullets[:]:
            if not bullet.active:
                continue
            
            # 子弹与地图碰撞
            bullet_rect = bullet.get_rect()
            if self.game_map.check_collision_with_rect(bullet_rect):
                # 尝试摧毁地形
                if self.game_map.can_destroy_tile(bullet.x, bullet.y):
                    self.game_map.destroy_tile(bullet.x, bullet.y)
                bullet.destroy()
                continue
            
            # 子弹与玩家坦克碰撞
            if (bullet.owner == "enemy" and self.player_tank.alive and 
                self.player_tank.check_collision_with_bullet(bullet)):
                if not self.player_tank.is_invulnerable():
                    self.player_tank.take_damage()
                bullet.destroy()
                continue
            
            # 子弹与敌人坦克碰撞
            if bullet.owner == "player":
                for enemy in self.enemy_tanks[:]:
                    if enemy.alive and enemy.check_collision_with_bullet(bullet):
                        enemy.take_damage()
                        bullet.destroy()
                        break
            
            # 子弹与子弹碰撞
            for other_bullet in self.bullets[:]:
                if (other_bullet != bullet and 
                    other_bullet.active and 
                    other_bullet.owner != bullet.owner):
                    
                    bullet_rect = bullet.get_rect()
                    other_rect = other_bullet.get_rect()
                    
                    if bullet_rect.colliderect(other_rect):
                        bullet.destroy()
                        other_bullet.destroy()
                        break
    
    def check_game_over(self):
        """
        检查游戏结束条件
        """
        # 检查玩家是否死亡
        if not self.player_tank.alive and self.player_tank.lives <= 0:
            self.game_state = "game_over"
            return
        
        # 检查是否所有敌人都被消灭
        if (len(self.enemy_tanks) == 0 and 
            self.enemies_destroyed >= self.max_enemies_per_level):
            self.level += 1
            self.max_enemies_per_level += 1  # 下一关敌人数量增加
            
            if self.level > 5:  # 假设5关后胜利
                self.game_state = "victory"
            else:
                # 进入下一关
                self.init_next_level()
    
    def init_next_level(self):
        """
        初始化下一关
        """
        # 重新生成地图
        self.game_map.generate_map()
        
        # 重置玩家位置（保持生命数）
        self.player_tank.x = TILE_SIZE * 2
        self.player_tank.y = SCREEN_HEIGHT - TILE_SIZE * 2
        self.player_tank.direction = UP
        self.player_tank.alive = True
        
        # 清空子弹
        self.bullets = []
        
        # 清空敌人并生成新敌人
        self.enemy_tanks = []
        self.spawn_initial_enemies()
        
        # 重置计数器
        self.enemies_destroyed = 0
        self.enemy_spawn_timer = pygame.time.get_ticks()
    
    def restart_game(self):
        """
        重新开始游戏
        """
        self.game_state = "playing"
        self.score = 0
        self.level = 1
        self.max_enemies_per_level = ENEMY_COUNT
        self.init_game()
    
    def draw_ui(self):
        """
        绘制用户界面
        """
        # 绘制分数
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 绘制关卡
        level_text = self.font.render(f"关卡: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # 绘制生命数
        if self.player_tank.alive:
            lives_text = self.font.render(f"生命: {self.player_tank.lives}", True, WHITE)
            self.screen.blit(lives_text, (10, 90))
        
        # 绘制敌人数量
        enemy_count = len([e for e in self.enemy_tanks if e.alive])
        enemy_text = self.small_font.render(f"敌人: {enemy_count}", True, WHITE)
        self.screen.blit(enemy_text, (10, 130))
        
        # 绘制控制说明
        if self.game_state == "playing":
            controls = [
                "WASD/方向键: 移动",
                "空格键: 射击",
                "P: 暂停",
                "ESC: 退出"
            ]
            for i, control in enumerate(controls):
                text = self.small_font.render(control, True, LIGHT_GRAY)
                self.screen.blit(text, (SCREEN_WIDTH - 200, 10 + i * 25))
    
    def draw_game_over_screen(self):
        """
        绘制游戏结束屏幕
        """
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 游戏结束文本
        game_over_text = self.font.render("游戏结束!", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # 最终分数
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # 重新开始提示
        restart_text = self.small_font.render("按 R 重新开始，按 ESC 退出", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory_screen(self):
        """
        绘制胜利屏幕
        """
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 胜利文本
        victory_text = self.font.render("恭喜胜利!", True, GREEN)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(victory_text, text_rect)
        
        # 最终分数
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # 重新开始提示
        restart_text = self.small_font.render("按 R 重新开始，按 ESC 退出", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_paused_screen(self):
        """
        绘制暂停屏幕
        """
        # 半透明覆盖层
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        paused_text = self.font.render("游戏暂停", True, YELLOW)
        text_rect = paused_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(paused_text, text_rect)
        
        # 继续提示
        continue_text = self.small_font.render("按 P 继续游戏", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(continue_text, continue_rect)
    
    def draw(self):
        """
        绘制游戏画面
        """
        # 清空屏幕
        self.screen.fill(BLACK)
        
        # 绘制地图
        if self.game_map:
            self.game_map.draw(self.screen)
        
        # 绘制玩家坦克
        if self.player_tank:
            self.player_tank.draw(self.screen)
        
        # 绘制敌人坦克
        for enemy in self.enemy_tanks:
            if enemy.alive:
                enemy.draw(self.screen)
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # 绘制UI
        self.draw_ui()
        
        # 根据游戏状态绘制覆盖屏幕
        if self.game_state == "game_over":
            self.draw_game_over_screen()
        elif self.game_state == "victory":
            self.draw_victory_screen()
        elif self.game_state == "paused":
            self.draw_paused_screen()
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """
        运行游戏主循环
        """
        running = True
        
        while running:
            # 处理事件
            running = self.handle_events()
            
            if running:
                # 更新游戏
                self.update()
                
                # 绘制游戏
                self.draw()
                
                # 控制帧率
                self.clock.tick(FPS)
        
        # 退出
        pygame.quit()
        sys.exit()