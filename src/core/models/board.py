# src/core/models/board.py
from typing import Dict, List, Optional, Any, ClassVar
from dataclasses import dataclass, field
from enum import Enum

from src.core.models import ActionType


class LocationType(Enum):
    """地点类型枚举 - 定义地图节点的功能类别"""
    START = "start"  # 起点
    KANSAS_CITY = "kansas_city"  # 堪萨斯城（卖牛地点）
    BRANCH = "branch"
    NORMAL = "normal"


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

    # 使用 ClassVar 明确表示这是类变量
    CONFIG_MAP: ClassVar[Dict[BuildingType, 'BuildingConfig']] = {}

    def __post_init__(self):
        # 注册到全局配置表
        BuildingConfig.CONFIG_MAP[self.building_type] = self


# 在模块加载时创建配置实例
# 这样 CONFIG_MAP 会自动填充
STATION_CONFIG = BuildingConfig(
    building_type=BuildingType.STATION,
    name="车站",
    worker_cost=3,
    victory_points=2,
    actions=["move", "build", "hire"],
    description="基础建筑"
)

RANCH_CONFIG = BuildingConfig(
    building_type=BuildingType.RANCH,
    name="牧场",
    worker_cost=2,
    victory_points=1,
    actions=["cattle_buy", "cattle_sell"],
    description="牛牌交易建筑"
)

# 新增三种建筑物配置
# 在 src/core/models/board.py 中添加以下配置

# 建筑类型1：贸易站 (Trading Post)
BUILDING_TYPE_1 = BuildingConfig(
    building_type=BuildingType.BUILDING_TYPE_1,
    name="贸易站",
    worker_cost=2,
    victory_points=3,
    actions=["trade", "draw_card"],
    description="允许玩家交易资源和抽取额外卡牌"
)

# 建筑类型2：工匠作坊 (Artisan Workshop)
BUILDING_TYPE_2 = BuildingConfig(
    building_type=BuildingType.BUILDING_TYPE_2,
    name="工匠作坊",
    worker_cost=3,
    victory_points=4,
    actions=["craft", "upgrade"],
    description="提供特殊建造能力和资源升级选项"
)

# 建筑类型3：市场广场 (Market Square)
BUILDING_TYPE_3 = BuildingConfig(
    building_type=BuildingType.BUILDING_TYPE_3,
    name="市场广场",
    worker_cost=1,
    victory_points=2,
    actions=["market_sale", "auction"],
    description="提供额外的销售渠道和议价能力"
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
    location_type: LocationType = LocationType.NORMAL
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
        return (self.location_type == LocationType.NORMAL and
                not self.has_building())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MapNode':
        """从字典创建节点实例"""
        # 处理枚举类型
        location_type = LocationType(data["location_type"]) if data.get("location_type") else LocationType.NORMAL
        building_type = BuildingType(data["building_type"]) if data.get("building_type") else None

        return cls(
            node_id=data["node_id"],
            name=data.get("name", ""),
            location_type=location_type,
            building_type=building_type,
            next_nodes=data.get("next_nodes", []),
            previous_nodes=data.get("previous_nodes", []),
            x=data.get("x", 0),
            y=data.get("y", 0),
            actions=data.get("actions", [])
        )


@dataclass
class BoardState:
    """版图状态"""
    def __init__(self):
        self.nodes = {}
        self.neutral_buildings = []
        self.player_buildings = {}
        self.available_locations = []
        self.kansas_city_state = {}

    def initialize_nodes(self):
        """初始化所有地图节点"""
        # 清空现有节点
        self.nodes = {}

        # 创建基础节点 (0-29)
        for i in range(120):
            self.nodes[i] = MapNode(
                node_id=i,
                name=f"节点{i}",
                location_type=LocationType.NORMAL,
                x=50 + i * 30,  # 简单水平布局
                y=300
            )

        # # 创建分支节点 (51-56, 61-65, 71-72, 81-86, 91-92, 101-108)
        # branch_nodes = list(range(51, 57)) + list(range(61, 66)) + [71, 72] + \
        #                list(range(81, 87)) + [91, 92] + list(range(101, 109))
        #
        # for node_id in branch_nodes:
        #     self.nodes[node_id] = MapNode(
        #         node_id=node_id,
        #         name=f"分支节点{node_id}",
        #         location_type=LocationType.BRANCH,
        #         x=200 + (node_id % 10) * 40,  # 简单布局
        #         y=150 + (node_id // 10) * 30
        #     )

        print(f"已初始化 {len(self.nodes)} 个地图节点")

    # 其他现有方法保持不变...
    def connect_nodes(self, from_id: int, to_id: int):
        """连接两个节点"""
        if from_id in self.nodes and to_id in self.nodes:
            if to_id not in self.nodes[from_id].next_nodes:
                self.nodes[from_id].next_nodes.append(to_id)
            if from_id not in self.nodes[to_id].previous_nodes:
                self.nodes[to_id].previous_nodes.append(from_id)

    def place_building(self, node_id: int, building_type: BuildingType):
        """在指定节点放置建筑"""
        if node_id in self.nodes:
            self.nodes[node_id].building_type = building_type
            print(f"在节点 {node_id} 放置了 {building_type.value}")

    def place_building(self, node_id: int, building_type: BuildingType, owner_id: Optional[str] = None):
        """在指定节点放置建筑"""
        if node_id in self.nodes:
            self.nodes[node_id].building_type = building_type
            print(f"在节点 {node_id} 放置了 {building_type.value}")
        else:
            print(f"错误：节点 {node_id} 不存在")


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