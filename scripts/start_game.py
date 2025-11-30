#!/usr/bin/env python3
"""
大西部之路游戏启动脚本
交互式创建新游戏会话
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_state import GameState
from src.core.models.player import PlayerState, ResourceSet
from src.core.models.enums import PlayerColor, GamePhase
from src.core.models.board import BoardState, LocationType
from src.utils.logging import get_logger

logger = get_logger(__name__)


class GameStarter:
    """游戏启动器"""

    def __init__(self):
        self.game_state = None
        self.available_colors = list(PlayerColor)

    def start_interactive_setup(self):
        """交互式游戏设置"""
        print("🎮🎮 欢迎来到大西部之路! 🎮🎮")
        print("=" * 50)

        # 获取游戏人数
        player_count = self._get_player_count()

        # 创建游戏状态
        self._create_game_state(player_count)

        # 设置玩家信息
        self._setup_players(player_count)

        # 初始化地图
        self._initialize_map()

        # 显示游戏初始状态
        self._display_initial_state()

        return self.game_state

    def _get_player_count(self):
        """获取玩家数量"""
        while True:
            try:
                count = input("请输入游戏人数 (2-4人): ").strip()
                count = int(count)
                if 2 <= count <= 4:
                    return count
                else:
                    print("❌ 人数必须在2-4人之间")
            except ValueError:
                print("❌ 请输入有效的数字")

    def _create_game_state(self, player_count):
        """创建游戏状态"""
        session_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # 初始化游戏各项状态
        self.game_state = GameState(session_id=session_id, player_count=player_count)
        self.game_state.session_name = f"大西部之路游戏_{session_id}"
        self.game_state.max_players = player_count
        self.game_state.current_phase = GamePhase.SETUP
        logger.info(f"创建游戏会话: {session_id}, 人数: {player_count}")

    def _setup_players(self, player_count):
        """设置玩家信息"""
        print("\n👥 玩家设置")
        print("-" * 30)

        self.game_state.players = []

        for i in range(player_count):
            player_info = self._get_player_info(i + 1)
            player = self._create_player(player_info, i)
            self.game_state.players.append(player)

            print(f"✅ 玩家{i + 1}创建完成: {player.display_name} ({player.player_color.value})")

    def _get_player_info(self, player_num):
        """获取玩家信息"""
        print(f"\n玩家 {player_num} 信息:")

        # 获取玩家名称
        while True:
            name = input(f"请输入玩家{player_num}的名称: ").strip()
            if name:
                break
            print("❌ 名称不能为空")

        # 选择颜色
        color = self._select_color(player_num)

        return {"name": name, "color": color}

    def _select_color(self, player_num):
        """选择玩家颜色"""
        print(f"\n玩家{player_num}可选颜色:")
        for i, color in enumerate(self.available_colors, 1):
            print(f"  {i}. {color.value}")

        while True:
            try:
                choice = input(f"请选择颜色 (1-{len(self.available_colors)}): ").strip()
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(self.available_colors):
                    selected_color = self.available_colors.pop(choice_idx)
                    return selected_color
                else:
                    print(f"❌ 请输入1-{len(self.available_colors)}之间的数字")
            except ValueError:
                print("❌ 请输入有效的数字")

    def _create_player(self, player_info, player_index):
        """创建玩家对象"""
        from uuid import uuid4

        return PlayerState(
            player_id=str(uuid4()),
            user_id=f"user_{player_index + 1}",
            player_color=player_info["color"],
            display_name=player_info["name"],
            position=0,  # 起始位置
            resources=ResourceSet(
                money=6,  # 初始金钱
                cowboys=1,
                builders=1,
                drivers=1,
                certificates=0,
                temporary_honor=0  # 临时荣誉数量
            ),
            victory_points=0,
            # hand_cards=[],
            buildings_built_count=0,
            cattle_sold_count=0
        )

    def _initialize_map(self):
        """初始化游戏地图"""
        print("\n🗺️  初始化游戏地图...")

        self.game_state.initialize_map()
        logger.info("地图初始化完成")

    def _display_initial_state(self):
        """显示游戏初始状态"""
        print("\n" + "=" * 60)
        print("🎉 游戏初始化完成! 🎉")
        print("=" * 60)

        print(f"游戏会话: {self.game_state.session_name}")
        print(f"游戏阶段: {self.game_state.current_phase.value}")
        print(f"玩家数量: {len(self.game_state.players)}")

        print("\n玩家信息:")
        print("-" * 40)
        for i, player in enumerate(self.game_state.players, 1):
            print(f"玩家{i}: {player.display_name}")
            print(f"  颜色: {player.player_color.value}")
            print(f"  位置: {player.position}")
            print(f"  资源: 💰{player.resources.money} 👷{player.resources.cowboys} 📜{player.resources.certificates}")
            print(f"  胜利点: {player.victory_points}")
            print()

        print("地图信息:")
        print("-" * 40)
        # 验证地图结构
        print(f"地图节点数量: {len(self.game_state.board_state.nodes)}")

        # 检查起点和终点
        start_node = self.game_state.board_state.nodes[0]
        print(f"起点: {start_node.name}, 类型: {start_node.location_type.value}")
        print(f"起点动作: {start_node.actions}")

        end_node = self.game_state.board_state.nodes[29]
        print(f"终点: {end_node.name}, 类型: {end_node.location_type.value}")
        print(f"终点动作: {end_node.actions}")

        print("\n游戏即将开始...")
        input("按回车键继续...")


def main():
    """主函数"""
    try:
        starter = GameStarter()
        game_state = starter.start_interactive_setup()

        # 这里可以添加游戏主循环的调用
        # start_game_loop(game_state)

        logger.info("游戏启动完成")
        return game_state

    except Exception as e:
        logger.error(f"游戏启动失败: {e}")
        print(f"❌ 游戏启动失败: {e}")
        return None


if __name__ == "__main__":
    game_state = main()

    if game_state:
        print("\n✅ 游戏准备就绪!")
        print("接下来可以开始游戏主循环...")
    else:
        print("\n❌ 游戏启动失败，请检查错误信息")
        sys.exit(1)
