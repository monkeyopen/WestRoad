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
    """建筑物类型枚举"""
    STATION = "station"
    RANCH = "ranch"
    HAZARD = "hazard"
    TELEGRAPH = "telegraph"
    CHURCH = "church"
    # 新增三种建筑物类型
    BUILDING_TYPE_1 = "building_type_1"  # 移动1步 + 建造
    BUILDING_TYPE_2 = "building_type_2"  # 买牛 + 建造
    BUILDING_TYPE_3 = "building_type_3"  # 买牛 + 移动1步


@dataclass
class BuildingConfig:
    """建筑物配置类"""
    building_type: BuildingType
    name: str
    worker_cost: int  # 需要的工人数量
    victory_points: int  # 分数
    actions: List[str]  # 动作列表（最多3个）
    description: str = ""

    # 静态配置表
    CONFIG_MAP: Dict[BuildingType, 'BuildingConfig'] = {}

    def __post_init__(self):
        # 注册到配置表
        BuildingConfig.CONFIG_MAP[self.building_type] = self


# 定义所有建筑物的配置
BuildingConfig(
    building_type=BuildingType.STATION,
    name="车站",
    worker_cost=1,
    victory_points=2,
    actions=["move", "build"],
    description="提供移动和建造能力"
)

BuildingConfig(
    building_type=BuildingType.RANCH,
    name="牧场",
    worker_cost=1,
    victory_points=1,
    actions=["hire_worker", "buy_cattle"],
    description="提供雇佣工人和购买牛牌能力"
)

BuildingConfig(
    building_type=BuildingType.HAZARD,
    name="危险建筑",
    worker_cost=0,
    victory_points=0,
    actions=["use_ability", "move"],
    description="提供使用能力和移动能力"
)

BuildingConfig(
    building_type=BuildingType.TELEGRAPH,
    name="电报站",
    worker_cost=2,
    victory_points=3,
    actions=["buy_cattle", "sell_cattle"],
    description="提供买卖牛牌能力"
)

BuildingConfig(
    building_type=BuildingType.CHURCH,
    name="教堂",
    worker_cost=1,
    victory_points=2,
    actions=["build", "hire_worker"],
    description="提供建造和雇佣工人能力"
)

# 新增三种建筑物配置
BuildingConfig(
    building_type=BuildingType.BUILDING_TYPE_1,
    name="贸易站",  # 示例名称
    worker_cost=1,
    victory_points=1,
    actions=["move", "build"],  # 移动1步 + 建造
    description="提供短距离移动和建造能力"
)

BuildingConfig(
    building_type=BuildingType.BUILDING_TYPE_2,
    name="畜牧场",  # 示例名称
    worker_cost=2,
    victory_points=2,
    actions=["buy_cattle", "build"],  # 买牛 + 建造
    description="专注于牲畜交易和基础设施建设"
)

BuildingConfig(
    building_type=BuildingType.BUILDING_TYPE_3,
    name="驿站",  # 示例名称
    worker_cost=1,
    victory_points=1,
    actions=["buy_cattle", "move"],  # 买牛 + 移动1步
    description="结合牲畜交易和快速移动"
)


@dataclass
class Building:
    """建筑物实例类"""
    building_type: BuildingType
    location_id: int
    owner_id: Optional[str] = None  # 拥有者ID
    is_neutral: bool = False  # 是否是中立建筑

    @property
    def config(self) -> BuildingConfig:
        """获取建筑物配置"""
        return BuildingConfig.CONFIG_MAP[self.building_type]

    @property
    def name(self) -> str:
        """建筑物名称"""
        return self.config.name

    @property
    def worker_cost(self) -> int:
        """需要的工人数量"""
        return self.config.worker_cost

    @property
    def victory_points(self) -> int:
        """胜利分数"""
        return self.config.victory_points

    @property
    def actions(self) -> List[str]:
        """可执行的动作列表"""
        return self.config.actions

    @property
    def description(self) -> str:
        """建筑物描述"""
        return self.config.description

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "building_type": self.building_type.value,
            "location_id": self.location_id,
            "owner_id": self.owner_id,
            "is_neutral": self.is_neutral,
            "name": self.name,
            "worker_cost": self.worker_cost,
            "victory_points": self.victory_points,
            "actions": self.actions,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Building':
        """从字典创建实例"""
        building_type = BuildingType(data["building_type"])
        building = cls(
            building_type=building_type,
            location_id=data["location_id"],
            owner_id=data.get("owner_id"),
            is_neutral=data.get("is_neutral", False)
        )
        return building


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
    """版图状态"""
    nodes: Dict[int, MapNode] = field(default_factory=dict)
    buildings: Dict[int, Building] = field(default_factory=dict)  # 位置 -> 建筑物映射
    neutral_buildings: List[Building] = field(default_factory=list)
    player_buildings: Dict[str, List[Building]] = field(default_factory=dict)  # 玩家ID -> 建筑物列表
    available_locations: List[int] = field(default_factory=list)
    kansas_city_state: Dict[str, Any] = field(default_factory=dict)

    def place_building(self, location_id: int, building_type: BuildingType, owner_id: Optional[str] = None):
        """在指定位置放置建筑物"""
        building = Building(
            building_type=building_type,
            location_id=location_id,
            owner_id=owner_id,
            is_neutral=(owner_id is None)  # 没有拥有者就是中立建筑
        )

        self.buildings[location_id] = building

        # 更新玩家建筑列表或中立建筑列表
        if owner_id:
            if owner_id not in self.player_buildings:
                self.player_buildings[owner_id] = []
            self.player_buildings[owner_id].append(building)
        else:
            self.neutral_buildings.append(building)

        # 从可用位置中移除
        if location_id in self.available_locations:
            self.available_locations.remove(location_id)

    def get_building_at_location(self, location_id: int) -> Optional[Building]:
        """获取指定位置的建筑物"""
        return self.buildings.get(location_id)

    def get_player_buildings(self, player_id: str) -> List[Building]:
        """获取玩家的所有建筑物"""
        return self.player_buildings.get(player_id, [])

    def get_available_actions_at_location(self, location_id: int, player_id: str) -> List[Dict[str, Any]]:
        """获取在指定位置可用的动作"""
        building = self.get_building_at_location(location_id)
        if not building:
            return []

        # 检查玩家是否有权使用这个建筑物
        if building.owner_id and building.owner_id != player_id:
            return []  # 建筑物有拥有者且不是当前玩家

        return self._get_building_actions(building, player_id)

    def _get_building_actions(self, building: Building, player_id: str) -> List[Dict[str, Any]]:
        """获取建筑物提供的动作配置"""
        action_configs = {
            "move": {"action_type": ActionType.MOVE, "params": {}},
            "move_one_step": {"action_type": ActionType.MOVE, "params": {"fixed_one_step": True}},
            "build": {"action_type": ActionType.BUILD, "params": {}},
            "hire_worker": {"action_type": ActionType.HIRE_WORKER, "params": {}},
            "buy_cattle": {"action_type": ActionType.BUY_CATTLE, "params": {}},
            "sell_cattle": {"action_type": ActionType.SELL_CATTLE, "params": {}},
            "use_ability": {"action_type": ActionType.USE_ABILITY, "params": {}}
        }

        available_actions = []
        for action_key in building.actions:
            if action_key in action_configs:
                config = action_configs[action_key].copy()
                config["params"]["player_id"] = player_id
                config["params"]["location_id"] = building.location_id

                # 为建造动作自动设置位置
                if action_key == "build":
                    config["params"]["building_type"] = "some_type"  # 需要具体类型

                available_actions.append(config)

        return available_actions

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "nodes": {k: self._node_to_dict(v) for k, v in self.nodes.items()},
            "buildings": {k: v.to_dict() for k, v in self.buildings.items()},
            "neutral_buildings": [b.to_dict() for b in self.neutral_buildings],
            "player_buildings": {k: [b.to_dict() for b in v] for k, v in self.player_buildings.items()},
            "available_locations": self.available_locations,
            "kansas_city_state": self.kansas_city_state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BoardState':
        """从字典创建实例"""
        board = cls()

        # 重建节点
        if "nodes" in data:
            for node_id_str, node_data in data["nodes"].items():
                node_id = int(node_id_str)
                board.nodes[node_id] = MapNode.from_dict(node_data)

        # 重建建筑物
        if "buildings" in data:
            for location_str, building_data in data["buildings"].items():
                location_id = int(location_str)
                board.buildings[location_id] = Building.from_dict(building_data)

        # 重建其他数据
        board.neutral_buildings = [Building.from_dict(b) for b in data.get("neutral_buildings", [])]
        board.player_buildings = {
            player_id: [Building.from_dict(b) for b in buildings]
            for player_id, buildings in data.get("player_buildings", {}).items()
        }
        board.available_locations = data.get("available_locations", [])
        board.kansas_city_state = data.get("kansas_city_state", {})

        return board