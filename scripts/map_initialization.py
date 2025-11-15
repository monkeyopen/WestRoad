# scripts/test_map_initialization.py
# !/usr/bin/env python3
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_state import GameState
from src.core.models.enums import GamePhase
from src.core.models.board import LocationType


# 确保导入 BuildingConfig 和相关的配置实例
try:
    from src.core.models.board import BuildingConfig, BuildingType
    # 导入配置实例以确保它们被创建
    from src.core.models.board import (
        STATION_CONFIG, RANCH_CONFIG,
        BUILDING_TYPE_1, BUILDING_TYPE_2, BUILDING_TYPE_3
    )
    print("✅ BuildingConfig 和相关配置导入成功")
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    # 如果导入失败，尝试替代方案
    from src.core.models.board import BuildingConfig, BuildingType

def map_initialization():
    """测试地图初始化功能"""
    print("=== 测试地图初始化 ===")

    # 创建游戏状态
    game_state = GameState("test_session")
    game_state.current_phase = GamePhase.SETUP

    # 初始化地图
    game_state.initialize_map()

    # 验证地图结构
    print(f"地图节点数量: {len(game_state.board_state.nodes)}")

    # 检查起点和终点
    start_node = game_state.board_state.nodes[0]
    print(f"起点: {start_node.name}, 类型: {start_node.location_type.value}")
    print(f"起点动作: {start_node.actions}")

    end_node = game_state.board_state.nodes[29]
    print(f"终点: {end_node.name}, 类型: {end_node.location_type.value}")
    print(f"终点动作: {end_node.actions}")

    # 详细检查分支点及其所有后继节点
    branch_nodes = [5, 10, 15, 20]
    print("\n=== 分支点详细信息 ===")
    for node_id in branch_nodes:
        node = game_state.board_state.nodes[node_id]
        print(f"\n分支点{node_id}:")
        print(f"  类型: {node.location_type.value}")
        print(f"  名称: {node.name}")
        print(f"  建筑: {node.building_type.value if node.building_type else '无'}")
        print(f"  后继节点: {node.next_nodes}")
        print(f"  前驱节点: {node.previous_nodes}")
        print(f"  可用动作: {node.actions}")

        # 打印每个后继节点的详细信息
        for next_node_id in node.next_nodes:
            next_node = game_state.board_state.nodes[next_node_id]
            print(
                f"    -> 节点{next_node_id}: {next_node.name}, 建筑: {next_node.building_type.value if next_node.building_type else '无'}")

    # 检查建筑放置
    print("\n=== 建筑放置情况 ===")
    building_nodes = []
    for node_id, node in game_state.board_state.nodes.items():
        if node.building_type:
            building_nodes.append((node_id, node))
            print(f"节点{node_id}: {node.building_type.value} (类型: {node.location_type.value})")
            # 从 BuildingConfig.CONFIG_MAP 获取建筑配置
            building_config = BuildingConfig.CONFIG_MAP.get(node.building_type)

            if building_config:
                # 获取该建筑的动作列表
                actions = building_config.actions
                print(f"节点{node_id}的建筑 {node.building_type.value} 可执行的动作: {actions}")
            else:
                print(f"未找到建筑类型 {node.building_type.value} 的配置")

    # 打印所有节点的连接关系
    print("\n=== 完整节点连接关系 ===")
    for node_id in range(30):
        node = game_state.board_state.nodes[node_id]
        if node.next_nodes:  # 只打印有后继节点的节点
            print(f"节点{node_id} -> {node.next_nodes}")

    # 序列化测试
    print("\n=== 序列化测试 ===")
    json_str = game_state.to_json()
    print(f"序列化成功: {len(json_str)} 字符")

    # 反序列化测试
    new_state = GameState.from_json(json_str)
    print(f"反序列化成功: {len(new_state.board_state.nodes)} 个节点")

    # 验证反序列化后的地图结构
    print("\n=== 反序列化验证 ===")
    print(f"反序列化后起点: {new_state.board_state.nodes[0].name}")

    # 验证分支点5的后继节点
    node_5 = new_state.board_state.nodes[5]
    print(f"反序列化后节点5的后继节点: {node_5.next_nodes}")
    for next_id in node_5.next_nodes:
        next_node = new_state.board_state.nodes[next_id]
        print(
            f"  节点{next_id}: {next_node.name}, 建筑: {next_node.building_type.value if next_node.building_type else '无'}")


if __name__ == "__main__":
    map_initialization()