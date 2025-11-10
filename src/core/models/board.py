# src/core/models/board.py
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class LocationType(Enum):
    """地点类型枚举 - 定义地图节点的功能类别"""
    START = "start"  # 起点
    KANSAS_CITY = "kansas_city"  # 堪萨斯城（卖牛地点）
    BUILDING = "building"  # 建筑点（可建造或使用建筑）
    BRANCH = "branch"  # 分支点（可选择不同路径）
    END = "end"  # 终点（游戏结束点）
    HAZARD = "hazard"  # 危险点（特殊效果区域）
    TELEGRAPH = "telegraph"  # 电报站（特殊功能点）
    CHURCH = "church"  # 教堂（特殊功能点）
    RANCH = "ranch"  # 牧场（特殊功能点）
    STATION = "station"  # 车站（特殊功能点）


class BuildingType(Enum):
    """建筑物类型枚举 - 定义可在建筑点上建造的具体建筑"""
    STATION = "station"  # 车站
    RANCH = "ranch"  # 牧场
    HAZARD = "hazard"  # 危险建筑
    TELEGRAPH = "telegraph"  # 电报站
    CHURCH = "church"  # 教堂
    # 预留15种其他建筑类型
    BUILDING_6 = "building_6"
    BUILDING_7 = "building_7"
    BUILDING_8 = "building_8"
    BUILDING_9 = "building_9"
    BUILDING_10 = "building_10"
    BUILDING_11 = "building_11"
    BUILDING_12 = "building_12"
    BUILDING_13 = "building_13"
    BUILDING_14 = "building_14"
    BUILDING_15 = "building_15"
    BUILDING_16 = "building_16"
    BUILDING_17 = "building_17"
    BUILDING_18 = "building_18"
    BUILDING_19 = "building_19"
    BUILDING_20 = "building_20"


@dataclass
class MapNode:
    """
    地图节点类 - 代表地图上的一个具体位置

    属性:
    - node_id: 节点唯一ID (0-29)
    - name: 节点名称
    - location_type: 地点类型 (LocationType枚举)
    - building_type: 建筑类型 (BuildingType枚举，可选)
    - next_nodes: 可前往的后继节点ID列表
    - previous_nodes: 可返回的前驱节点ID列表
    - x, y: 可视化坐标 (用于前端展示)
    - actions: 在该节点可执行的动作列表
    """
    node_id: int
    name: str = ""
    location_type: LocationType = LocationType.BUILDING
    building_type: Optional[BuildingType] = None
    next_nodes: List[int] = field(default_factory=list)
    previous_nodes: List[int] = field(default_factory=list)
    x: float = 0.0
    y: float = 0.0
    actions: List[str] = field(default_factory=list)

    def add_next_node(self, node_id: int):
        """添加一个后继节点"""
        if node_id not in self.next_nodes:
            self.next_nodes.append(node_id)

    def add_previous_node(self, node_id: int):
        """添加一个前驱节点"""
        if node_id not in self.previous_nodes:
            self.previous_nodes.append(node_id)

    def add_action(self, action: str):
        """添加一个可执行动作"""
        if action not in self.actions:
            self.actions.append(action)

    def remove_action(self, action: str):
        """移除一个动作"""
        if action in self.actions:
            self.actions.remove(action)

    def has_building(self) -> bool:
        """检查节点是否有建筑"""
        return self.building_type is not None

    def is_buildable(self) -> bool:
        """检查节点是否可以建造建筑"""
        return (self.location_type == LocationType.BUILDING and
                not self.has_building())


@dataclass
class BoardState:
    """
    版图状态类 - 管理整个游戏地图

    属性:
    - nodes: 所有地图节点的字典 (key为节点ID)

    方法:
    - initialize_nodes: 初始化30个节点
    - connect_nodes: 连接两个节点
    - get_available_paths: 获取从当前节点可到达的路径
    - place_building: 在指定节点放置建筑
    - to_dict: 转换为字典格式 (用于序列化)
    - from_dict: 从字典重建对象 (用于反序列化)
    """
    nodes: Dict[int, MapNode] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后自动创建30个节点"""
        if not self.nodes:
            self.initialize_nodes()

    def initialize_nodes(self):
        """初始化30个空节点"""
        self.nodes = {}
        for i in range(110):
            # 设置节点名称和类型
            name = f"位置{i}"
            location_type = LocationType.BUILDING

            # 特殊节点处理
            if i == 0:
                name = "起点"
                location_type = LocationType.START
            elif i == 29:
                name = "堪萨斯城"
                location_type = LocationType.KANSAS_CITY

            # 创建节点
            self.nodes[i] = MapNode(
                node_id=i,
                name=name,
                location_type=location_type,
                actions=["move"]  # 默认所有位置都可以移动
            )

    def connect_nodes(self, from_node_id: int, to_node_id: int):
        """连接两个节点 (创建有向边)"""
        if from_node_id in self.nodes and to_node_id in self.nodes:
            # 从 from_node 到 to_node 添加一条边
            self.nodes[from_node_id].add_next_node(to_node_id)
            # 同时，to_node 的前驱节点添加 from_node
            self.nodes[to_node_id].add_previous_node(from_node_id)

    def get_available_paths(self, current_node_id: int) -> List[int]:
        """获取从当前节点可到达的路径"""
        if current_node_id in self.nodes:
            return self.nodes[current_node_id].next_nodes.copy()
        return []

    def place_building(self, node_id: int, building_type: BuildingType):
        """在指定节点放置建筑"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.building_type = building_type

            # 根据建筑类型添加特定动作
            if building_type == BuildingType.STATION:
                node.add_action("train_move")
            elif building_type == BuildingType.RANCH:
                node.add_action("buy_cattle")
            elif building_type == BuildingType.HAZARD:
                node.add_action("avoid_hazard")
            elif building_type == BuildingType.TELEGRAPH:
                node.add_action("send_message")
            elif building_type == BuildingType.CHURCH:
                node.add_action("pray")

            # 通用建筑动作
            node.add_action("use_building")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 (用于序列化)"""
        return {
            "nodes": {
                node_id: {
                    "node_id": node.node_id,
                    "name": node.name,
                    "location_type": node.location_type.value,
                    "building_type": node.building_type.value if node.building_type else None,
                    "next_nodes": node.next_nodes,
                    "previous_nodes": node.previous_nodes,
                    "x": node.x,
                    "y": node.y,
                    "actions": node.actions
                }
                for node_id, node in self.nodes.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoardState':
        """从字典重建对象 (用于反序列化)"""
        board = cls()
        if "nodes" in data:
            for node_id, node_data in data["nodes"].items():
                # 解析地点类型
                location_type = LocationType(node_data["location_type"])

                # 解析建筑类型 (如果有)
                building_type = None
                if node_data["building_type"]:
                    building_type = BuildingType(node_data["building_type"])

                # 创建节点
                node = MapNode(
                    node_id=node_data["node_id"],
                    name=node_data["name"],
                    location_type=location_type,
                    building_type=building_type,
                    next_nodes=node_data["next_nodes"],
                    previous_nodes=node_data["previous_nodes"],
                    x=node_data.get("x", 0.0),
                    y=node_data.get("y", 0.0),
                    actions=node_data.get("actions", [])
                )
                board.nodes[int(node_id)] = node
        return board

    def get_node(self, node_id: int) -> Optional[MapNode]:
        """获取指定节点"""
        return self.nodes.get(node_id)

    def get_building_nodes(self) -> List[MapNode]:
        """获取所有有建筑的节点"""
        return [node for node in self.nodes.values() if node.has_building()]

    def get_buildable_nodes(self) -> List[MapNode]:
        """获取所有可建造的节点"""
        return [node for node in self.nodes.values() if node.is_buildable()]