# scripts/test_map_initialization.py
# !/usr/bin/env python3
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_state import GameState
from src.core.models.enums import GamePhase


def test_map_initialization():
    """测试地图初始化功能"""
    print("=== 测试地图初始化 ===")

    # 创建游戏状态
    game_state = GameState("test_session")
    game_state.current_phase = GamePhase.SETUP

    # 初始化地图
    game_state.initialize_map()

    # 验证地图结构
    print(f"地图节点数量: {len(game_state.board_state.nodes)}")
    print(f"节点0的后继节点: {game_state.board_state.get_available_paths(0)}")
    print(f"节点5的后继节点: {game_state.board_state.get_available_paths(5)}")

    # 显示部分节点的建筑信息
    for node_id in [1, 3, 5, 7, 10]:
        node = game_state.board_state.nodes[node_id]
        building = node.building_type.value if node.building_type else "无建筑"
        print(f"节点{node_id}: 建筑={building}, 后继={node.next_nodes}")

    # 序列化测试
    json_str = game_state.to_json()
    print(f"\n序列化成功: {len(json_str)} 字符")

    # 反序列化测试
    new_state = GameState.from_json(json_str)
    print(f"反序列化成功: {len(new_state.board_state.nodes)} 个节点")


if __name__ == "__main__":
    test_map_initialization()