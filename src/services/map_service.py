# src/services/map_service.py
import random
from typing import Dict, Any
from ..core.models.board import BoardState, BuildingType, MapNode


class MapService:
    """地图服务 - 负责地图的创建和初始化"""

    def __init__(self):
        self.standard_map_layout = self._create_standard_layout()

    def _create_standard_layout(self) -> Dict[str, Any]:
        """创建标准地图布局"""
        return {
            "linear_path": list(range(30)),  # 0->1->2->...->29
            "branch_points": {
                5: [6, 7],  # 节点5分支到6和7
                10: [11, 12],  # 节点10分支到11和12
                15: [16, 18],  # 节点15分支到16和18
                20: [21, 23]  # 节点20分支到21和23
            },
            "building_placement": {
                # 定义每个节点应该放置的建筑类型
                1: BuildingType.STATION,
                3: BuildingType.RANCH,
                5: BuildingType.HAZARD,
                # ... 其他节点建筑配置
            }
        }

    def create_standard_map(self) -> BoardState:
        """创建标准游戏地图"""
        board = BoardState()
        board.initialize_nodes()

        # 创建基础路径
        layout = self.standard_map_layout

        # 连接线性路径
        for i in range(29):
            board.connect_nodes(i, i + 1)

        # 添加分支
        for branch_node, targets in layout["branch_points"].items():
            for target in targets:
                board.connect_nodes(branch_node, target)

        # 放置建筑物
        for node_id, building_type in layout["building_placement"].items():
            board.place_building(node_id, building_type)

        return board