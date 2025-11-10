# src/core/models/board.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class BuildingType(Enum):
    """建筑物类型枚举"""
    STATION = "station"  # 车站
    RANCH = "ranch"  # 牧场
    HAZARD = "hazard"  # 危险建筑
    TELEGRAPH = "telegraph"  # 电报站
    CHURCH = "church"  # 教堂
    # 预留15种其他建筑类型
    BUILDING_6 = "building_6"
    BUILDING_7 = "building_7"
    # ... 一直到 BUILDING_20


@dataclass
class MapNode:
    """地图节点类"""
    node_id: int  # 0-29
    building_type: Optional[BuildingType] = None
    next_nodes: List[int] = field(default_factory=list)  # 后继节点ID列表
    previous_nodes: List[int] = field(default_factory=list)  # 前驱节点ID列表
    x: float = 0.0  # 可视化坐标
    y: float = 0.0  # 可视化坐标

    def add_next_node(self, node_id: int):
        """添加后继节点"""
        if node_id not in self.next_nodes:
            self.next_nodes.append(node_id)

    def add_previous_node(self, node_id: int):
        """添加前驱节点"""
        if node_id not in self.previous_nodes:
            self.previous_nodes.append(node_id)


@dataclass
class BoardState:
    """版图状态 - 管理30个节点的有向图"""
    nodes: Dict[int, MapNode] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后自动创建30个节点"""
        if not self.nodes:
            self.initialize_nodes()

    def initialize_nodes(self):
        """初始化30个空节点"""
        self.nodes = {i: MapNode(node_id=i) for i in range(30)}

    def connect_nodes(self, from_node_id: int, to_node_id: int):
        """连接两个节点"""
        if from_node_id in self.nodes and to_node_id in self.nodes:
            self.nodes[from_node_id].add_next_node(to_node_id)
            self.nodes[to_node_id].add_previous_node(from_node_id)

    def get_available_paths(self, current_node_id: int) -> List[int]:
        """获取从当前节点可到达的路径"""
        if current_node_id in self.nodes:
            return self.nodes[current_node_id].next_nodes.copy()
        return []

    def place_building(self, node_id: int, building_type: BuildingType):
        """在指定节点放置建筑"""
        if node_id in self.nodes:
            self.nodes[node_id].building_type = building_type

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "nodes": {
                node_id: {
                    "node_id": node.node_id,
                    "building_type": node.building_type.value if node.building_type else None,
                    "next_nodes": node.next_nodes,
                    "previous_nodes": node.previous_nodes,
                    "x": node.x,
                    "y": node.y
                }
                for node_id, node in self.nodes.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoardState':
        """从字典重建"""
        board = cls()
        if "nodes" in data:
            for node_id, node_data in data["nodes"].items():
                node = MapNode(
                    node_id=node_data["node_id"],
                    building_type=BuildingType(node_data["building_type"]) if node_data["building_type"] else None,
                    next_nodes=node_data["next_nodes"],
                    previous_nodes=node_data["previous_nodes"],
                    x=node_data.get("x", 0.0),
                    y=node_data.get("y", 0.0)
                )
                board.nodes[int(node_id)] = node
        return board