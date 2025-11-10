from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from uuid import uuid4
import random

# 使用相对导入
from .models.enums import GamePhase, PlayerColor
from .models.player import PlayerState, ResourceSet, CattleCard
from .models.board import BoardState, BuildingType


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
        """版图状态转换为字典"""
        return {
            "locations": {k: self._location_to_dict(v) for k, v in self.board_state.locations.items()},
            "neutral_buildings": self.board_state.neutral_buildings,
            "player_buildings": self.board_state.player_buildings,
            "available_locations": self.board_state.available_locations,
            "kansas_city_state": self.board_state.kansas_city_state
        }

    def _location_to_dict(self, location) -> Dict[str, Any]:
        """地点转换为字典"""
        return {
            "location_id": location.location_id,
            "location_type": location.location_type,
            "name": location.name,
            "owner_id": location.owner_id,
            "available_actions": location.available_actions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """从字典创建GameState实例"""
        # 创建基础实例
        game_state = cls(
            session_id=data["session_id"],
            game_version=data.get("game_version", "1.0"),
            current_phase=GamePhase(data["current_phase"]),
            current_round=data["current_round"],
            current_player_index=data["current_player_index"],
            player_order=data["player_order"],
            max_players=data.get("max_players", 4),
            game_config=data.get("game_config", {}),
            version=data["version"]
        )

        # 处理时间字段
        if data.get("turn_start_time"):
            game_state.turn_start_time = datetime.fromisoformat(data["turn_start_time"])
        if data.get("last_updated"):
            game_state.last_updated = datetime.fromisoformat(data["last_updated"])

        # 重建玩家状态
        game_state.players = []
        for player_data in data["players"]:
            resources_data = player_data["resources"]
            player = PlayerState(
                player_id=player_data["player_id"],
                user_id=player_data["user_id"],
                player_color=PlayerColor(player_data["player_color"]),
                display_name=player_data["display_name"],
                position=player_data["position"],
                previous_position=player_data.get("previous_position"),
                resources=ResourceSet(
                    money=resources_data["money"],
                    workers=resources_data["workers"],
                    craftsmen=resources_data["craftsmen"],
                    engineers=resources_data["engineers"],
                    certificates=resources_data["certificates"]
                ),
                hand_cards=player_data["hand_cards"],
                victory_points=player_data["victory_points"],
                stations_built=player_data["stations_built"],
                cattle_sold_count=player_data["cattle_sold_count"],
                buildings_built_count=player_data["buildings_built_count"],
                workers_hired_count=player_data["workers_hired_count"]
            )
            game_state.players.append(player)

        # 重建版图状态
        board_data = data["board_state"]
        game_state.board_state = BoardState(
            locations={int(k): Location(**v) for k, v in board_data["locations"].items()},
            neutral_buildings=board_data["neutral_buildings"],
            player_buildings=board_data["player_buildings"],
            available_locations=board_data["available_locations"],
            kansas_city_state=board_data["kansas_city_state"]
        )

        # 其他数据
        game_state.cattle_market = data["cattle_market"]
        game_state.available_workers = data["available_workers"]
        game_state.action_history = data.get("action_history", [])

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
        """初始化游戏地图 - 创建30个节点的有向图结构"""
        # 确保board_state已初始化
        if not hasattr(self.board_state, 'nodes') or not self.board_state.nodes:
            self.board_state.initialize_nodes()

        # 创建基础线性路径 (0->1->2->...->29)
        for i in range(29):
            self.board_state.connect_nodes(i, i + 1)

        # 添加分支路径（部分节点有多个后继）
        # 示例：节点5分支到节点6和节点7
        self.board_state.connect_nodes(5, 7)  # 5->7的捷径
        # 节点10分支到节点11和节点12
        self.board_state.connect_nodes(10, 12)  # 10->12的捷径
        # 节点15分支到节点16和节点18
        self.board_state.connect_nodes(15, 18)  # 15->18的捷径

        # 随机放置建筑物（后续可以根据规则调整）
        self._place_random_buildings()

    def _place_random_buildings(self):
        """随机放置建筑物（临时实现，后续按规则调整）"""
        building_types = list(BuildingType)
        for node_id in range(30):
            # 跳过起点和终点不放置建筑，或者特殊处理
            if node_id not in [0, 29]:  # 起点和终点不放置普通建筑
                building_type = random.choice(building_types[:5])  # 暂时只用前5种
                self.board_state.place_building(node_id, building_type)
