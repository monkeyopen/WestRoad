from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from uuid import uuid4
import random
from .models.board import LocationType, BuildingType

# 使用相对导入
from .models.enums import GamePhase, PlayerColor
from .models.player import PlayerState, ResourceSet, CattleCard
from .models.board import BoardState, MapNode, BuildingType


@dataclass
class GameState:
    """
    游戏状态类 - 权威的游戏状态容器
    """

    # 基础标识信息
    session_id: str = field(default_factory=lambda: str(uuid4()))
    game_version: str = "1.0"

    # 游戏流程状态
    current_phase: GamePhase = GamePhase.SETUP
    current_round: int = 0
    current_player_index: int = 0  # 当前回合玩家的索引
    turn_start_time: Optional[datetime] = None

    # 玩家状态
    players: List[PlayerState] = field(default_factory=list)
    player_order: List[int] = field(default_factory=list)  # 玩家顺序索引

    # 版图状态
    board_state: BoardState = field(default_factory=BoardState)

    # 卡牌状态
    cattle_market: List[Dict[str, Any]] = field(default_factory=list)  # 牛牌市场
    available_workers: Dict[str, int] = field(default_factory=dict)  # 可用工人

    # 游戏配置
    max_players: int = 4
    game_config: Dict[str, Any] = field(default_factory=dict)

    # 版本控制（乐观锁）
    version: int = 1
    last_updated: datetime = field(default_factory=datetime.now)

    # 游戏历史
    action_history: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def current_player(self) -> Optional[PlayerState]:
        """获取当前回合玩家"""
        if self.players and 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None

    @property
    def game_started(self) -> bool:
        """游戏是否已开始"""
        return self.current_phase != GamePhase.SETUP

    @property
    def game_finished(self) -> bool:
        """游戏是否已结束"""
        return self.current_phase == GamePhase.END_GAME

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            "session_id": self.session_id,
            "game_version": self.game_version,
            "current_phase": self.current_phase.value,
            "current_round": self.current_round,
            "current_player_index": self.current_player_index,
            "turn_start_time": self.turn_start_time.isoformat() if self.turn_start_time else None,
            "players": [self._player_to_dict(p) for p in self.players],
            "player_order": self.player_order,
            "board_state": self._board_to_dict(),
            "cattle_market": self.cattle_market,
            "available_workers": self.available_workers,
            "max_players": self.max_players,
            "game_config": self.game_config,
            "version": self.version,
            "last_updated": self.last_updated.isoformat(),
            "action_history": self.action_history
        }

    def _player_to_dict(self, player: PlayerState) -> Dict[str, Any]:
        """玩家状态转换为字典"""
        from .models.enums import PlayerColor  # 导入枚举

        # 处理 player_color 字段
        player_color = player.player_color
        if hasattr(player_color, 'value'):
            player_color_value = player_color.value
        else:
            player_color_value = player_color

        return {
            "player_id": player.player_id,
            "user_id": player.user_id,
            "player_color": player_color_value,
            "display_name": player.display_name,
            "resources": {
                "money": player.resources.money,
                "workers": player.resources.workers,
                "craftsmen": player.resources.craftsmen,
                "engineers": player.resources.engineers,
                "certificates": player.resources.certificates
            },
            "hand_cards": player.hand_cards,
            "victory_points": player.victory_points,
            "stations_built": player.stations_built,
            "cattle_sold_count": player.cattle_sold_count,
            "buildings_built_count": player.buildings_built_count,
            "workers_hired_count": player.workers_hired_count
        }

    def _board_to_dict(self) -> Dict[str, Any]:
        """版图状态转换为字典 - 修复版本"""
        if hasattr(self.board_state, 'nodes'):
            # 使用nodes结构的序列化
            return {
                "nodes": {k: self._node_to_dict(v) for k, v in self.board_state.nodes.items()},
                "neutral_buildings": getattr(self.board_state, 'neutral_buildings', []),
                "player_buildings": getattr(self.board_state, 'player_buildings', {}),
                "available_locations": getattr(self.board_state, 'available_locations', []),
                "kansas_city_state": getattr(self.board_state, 'kansas_city_state', {})
            }
        else:
            # 回退到原逻辑
            return {
                "locations": {},
                "neutral_buildings": [],
                "player_buildings": {},
                "available_locations": [],
                "kansas_city_state": {}
            }

    def _node_to_dict(self, node: MapNode) -> Dict[str, Any]:
        """将地图节点转换为字典"""
        return {
            "node_id": node.node_id,
            "name": node.name,
            "location_type": node.location_type.value,
            "building_type": node.building_type.value if node.building_type else None,
            "next_nodes": node.next_nodes,
            "previous_nodes": node.previous_nodes,
            "x": node.x,
            "y": node.y,
            "actions": node.actions,
            # 移除 owner_id 属性，因为 MapNode 没有这个属性
            # "owner_id": node.owner_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """从字典创建GameState实例 - 修复版本"""
        game_state = cls(session_id=data["session_id"])

        # ... 其他初始化代码 ...

        # 修复版图状态重建
        board_data = data.get("board_state", {})
        if "nodes" in board_data:

            game_state.board_state = BoardState()
            game_state.board_state.nodes = {}

            for node_id_str, node_data in board_data["nodes"].items():
                node_id = int(node_id_str)
                game_state.board_state.nodes[node_id] = MapNode(
                    node_id=node_id,
                    building_type=BuildingType(node_data["building_type"]),
                    next_nodes=node_data["next_nodes"],
                    owner_id=node_data.get("owner_id")
                )

            # 设置其他属性
            game_state.board_state.neutral_buildings = board_data.get("neutral_buildings", [])
            game_state.board_state.player_buildings = board_data.get("player_buildings", {})
            game_state.board_state.available_locations = board_data.get("available_locations", [])
            game_state.board_state.kansas_city_state = board_data.get("kansas_city_state", {})

        return game_state

    def clone(self) -> 'GameState':
        """创建游戏状态的深拷贝"""
        return GameState.from_dict(self.to_dict())

    def increment_version(self) -> None:
        """递增版本号"""
        self.version += 1
        self.last_updated = datetime.now()

    def get_player_by_id(self, player_id: str) -> Optional[PlayerState]:
        """根据玩家ID获取玩家状态"""
        for player in self.players:
            if player.player_id == player_id:
                return player
        return None

    def get_player_index(self, player_id: str) -> Optional[int]:
        """获取玩家索引"""
        for i, player in enumerate(self.players):
            if player.player_id == player_id:
                return i
        return None

    def to_json(self) -> str:
        """将游戏状态序列化为 JSON 字符串"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str):
        """从 JSON 字符串反序列化游戏状态"""
        data = json.loads(json_str)
        state = cls(data["session_id"], data.get("version", 0))
        state.current_phase = GamePhase(data["current_phase"])
        state.players = [PlayerState.from_dict(player_data) for player_data in data["players"]]
        state.board_state = BoardState.from_dict(data["board_state"])
        state.cattle_market = data["cattle_market"]
        return state

    # 在GameState类中添加地图初始化方法
    def initialize_map(self):
        """初始化游戏地图 - 创建50个节点的有向图结构"""
        # 确保board_state已初始化
        if not hasattr(self.board_state, 'nodes') or not self.board_state.nodes:
            self.board_state.initialize_nodes()

        # 创建基础线性路径 (0->1->2->...->29)
        for i in range(29):
            self.board_state.connect_nodes(i, i + 1)

        # 水灾支路
        self.board_state.connect_nodes(1, 51)
        self.board_state.connect_nodes(51, 52)
        self.board_state.connect_nodes(52, 53)
        self.board_state.connect_nodes(53, 54)
        self.board_state.connect_nodes(54, 55)
        self.board_state.connect_nodes(55, 56)
        self.board_state.connect_nodes(56, 5)

        # 旱灾支路
        self.board_state.connect_nodes(5, 61)
        self.board_state.connect_nodes(61, 62)
        self.board_state.connect_nodes(62, 63)
        self.board_state.connect_nodes(63, 64)
        self.board_state.connect_nodes(64, 65)
        self.board_state.connect_nodes(65, 9)

        # 分支1
        self.board_state.connect_nodes(9, 71)
        self.board_state.connect_nodes(71, 72)
        self.board_state.connect_nodes(72, 12)

        # 落石支路
        self.board_state.connect_nodes(12, 81)
        self.board_state.connect_nodes(81, 82)
        self.board_state.connect_nodes(82, 83)
        self.board_state.connect_nodes(83, 84)
        self.board_state.connect_nodes(84, 85)
        self.board_state.connect_nodes(85, 86)
        self.board_state.connect_nodes(86, 15)

        # 分支2
        self.board_state.connect_nodes(15, 91)
        self.board_state.connect_nodes(91, 17)

        # 分支3
        self.board_state.connect_nodes(17, 92)
        self.board_state.connect_nodes(92, 19)

        # 帐篷支路
        self.board_state.connect_nodes(10, 101)
        self.board_state.connect_nodes(101, 102)
        self.board_state.connect_nodes(102, 103)
        self.board_state.connect_nodes(103, 104)
        self.board_state.connect_nodes(104, 105)
        self.board_state.connect_nodes(105, 106)
        self.board_state.connect_nodes(106, 107)
        self.board_state.connect_nodes(107, 108)
        self.board_state.connect_nodes(108, 12)



        # 设置特殊地点的动作
        self.board_state.nodes[0].location_type = LocationType.START
        self.board_state.nodes[0].name = "起点"
        self.board_state.nodes[0].actions = ["move", "start_turn"]

        self.board_state.nodes[29].location_type = LocationType.KANSAS_CITY
        self.board_state.nodes[29].name = "堪萨斯城"
        self.board_state.nodes[29].actions = ["cattle_sale", "end_turn"]

        # 设置分支点为特殊类型
        for branch_id in [5, 10, 15, 20]:
            self.board_state.nodes[branch_id].location_type = LocationType.BRANCH
            self.board_state.nodes[branch_id].name = f"分支点{branch_id}"
            self.board_state.nodes[branch_id].add_action("choose_path")

        # 放置建筑物
        self._place_buildings()

    def _place_buildings(self):
        """放置建筑物"""
        # 使用预定义的建筑放置点
        building_placement = {
            1: BuildingType.STATION,
            3: BuildingType.RANCH,
            6: BuildingType.HAZARD,
            8: BuildingType.TELEGRAPH,
            11: BuildingType.CHURCH,
            13: BuildingType.STATION,
            16: BuildingType.RANCH,
            18: BuildingType.HAZARD,
            21: BuildingType.TELEGRAPH,
            24: BuildingType.CHURCH,
            26: BuildingType.STATION
        }

        for node_id, building_type in building_placement.items():
            self.board_state.place_building(node_id, building_type)
