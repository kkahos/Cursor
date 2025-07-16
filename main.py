#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坦克大战游戏主程序
Tank Battle Game Main Entry Point

运行此文件开始游戏：python main.py
"""

import os
import sys

# 确保能够导入游戏模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    import pygame
except ImportError:
    print("错误: 未找到pygame库。请先安装pygame:")
    print("pip install pygame")
    sys.exit(1)

from game import Game


def main():
    """
    主函数
    
    初始化并启动坦克大战游戏
    """
    try:
        print("=" * 50)
        print("      欢迎来到坦克大战游戏!")
        print("        Tank Battle Game")
        print("=" * 50)
        print()
        print("游戏控制:")
        print("  WASD 或 方向键 - 移动坦克")
        print("  空格键 - 发射子弹")
        print("  P - 暂停/继续游戏")
        print("  R - 游戏结束后重新开始")
        print("  ESC - 退出游戏")
        print()
        print("游戏目标:")
        print("  消灭所有敌人坦克通过关卡")
        print("  保护自己的坦克不被击中")
        print("  获得更高的分数!")
        print()
        print("开始游戏...")
        print("=" * 50)
        
        # 创建并运行游戏
        game = Game()
        game.run()
        
    except KeyboardInterrupt:
        print("\n游戏被用户中断。")
    except Exception as e:
        print(f"\n游戏运行时发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("感谢游玩坦克大战!")


if __name__ == "__main__":
    main()