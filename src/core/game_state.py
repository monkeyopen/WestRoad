from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from uuid import uuid4
import random
from .models.board import LocationType, BuildingType
from .models.card import Card

# 使用相对导入
from .models.enums import GamePhase, PlayerColor
from .models.player import PlayerState, ResourceSet, CattleCard
from .models.board import BoardState, MapNode, BuildingType
from .models.labor_market import LaborMarket
from .models.deck_manager import DeckManager, DeckConfig
from .models.enums import CardType
from config.cards import DECK_CONFIGS
from .models.future_area import FutureArea


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

    # 未来区
    future_area: FutureArea = field(default_factory=FutureArea)

    def __init__(self, session_id: str):
        if not hasattr(self, 'session_id') or not self.session_id:
            self.session_id = str(uuid4())

        self.board_state = BoardState()
        self.deck_manager = DeckManager()  # 初始化牌堆管理器
        self._initialize_decks()  # 初始化所有牌堆
        self.labor_market = LaborMarket()  # 初始化人才市场

        # # 初始化未来区
        self.future_area = FutureArea()



    def _initialize_decks(self):
        """初始化所有牌堆"""
        # 将配置转换为DeckConfig对象
        deck_configs = {}
        for card_type_str, config in DECK_CONFIGS.items():
            card_type = CardType(card_type_str)
            deck_configs[card_type] = DeckConfig(
                card_type=card_type,
                total_count=config["total_count"],
                card_prototypes=config["card_prototypes"]
            )

        self.deck_manager.initialize_decks(deck_configs)

    def take_card_from_future_area(self, row: int, col: int, player_id: str) -> Dict[str, Any]:
        """
        从未来区取走一张牌

        Args:
            row: 行索引 (0或1)
            col: 列索引 (0, 1, 2)
            player_id: 玩家ID

        Returns:
            操作结果
        """
        # 获取玩家
        player = self.get_player_by_id(player_id)
        if not player:
            return {"success": False, "message": "玩家不存在"}

        # 从未来区取牌
        card = self.future_area.take_card(row, col, self.deck_manager)

        if not card:
            return {"success": False, "message": "该位置没有牌"}

        # 将牌添加到玩家手牌
        player.hand_cards.append(card)

        # 更新游戏状态
        self.increment_version()

        return {
            "success": True,
            "message": f"成功获取牌: {card['name']}",
            "player_id": player_id,
            "card": card,
            "new_hand_count": len(player.hand_cards)
        }

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
            # "players": [self._player_to_dict(p) for p in self.players],
            # "player_order": self.player_order,
            "board_state": self._board_to_dict(),
            # "cattle_market": self.cattle_market,
            # "available_workers": self.available_workers,
            "max_players": self.max_players,
            # "game_config": self.game_config,
            "version": self.version,
            # "last_updated": self.last_updated.isoformat(),
            "labor_market": self.labor_market.to_dict(),
            "deck_manager": self.deck_manager.to_dict(),
            "future_area": self.future_area.to_dict()
            # "action_history": self.action_history
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """从字典创建GameState实例"""
        game_state = cls(session_id=data["session_id"])

        # 设置基础属性
        game_state.game_version = data.get("game_version", "1.0")
        game_state.current_phase = GamePhase(data["current_phase"])
        game_state.current_round = data.get("current_round", 0)
        game_state.current_player_index = data.get("current_player_index", 0)

        # 处理时间字段
        if data.get("turn_start_time"):
            game_state.turn_start_time = datetime.fromisoformat(data["turn_start_time"])

        # 重建玩家
        game_state.players = []
        for player_data in data.get("players", []):
            player = PlayerState(
                player_id=player_data["player_id"],
                user_id=player_data["user_id"],
                player_color=PlayerColor(player_data["player_color"]),
                display_name=player_data["display_name"],
                resources=ResourceSet(**player_data["resources"])
            )
            # 设置其他玩家属性
            player.hand_cards = player_data.get("hand_cards", [])
            player.victory_points = player_data.get("victory_points", 0)
            player.stations_built = player_data.get("stations_built", 0)
            player.cattle_sold_count = player_data.get("cattle_sold_count", 0)
            player.buildings_built_count = player_data.get("buildings_built_count", 0)
            player.workers_hired_count = player_data.get("workers_hired_count", 0)

            game_state.players.append(player)

        # 重建版图状态
        game_state.board_state = BoardState.from_dict(data.get("board_state", {}))

        # 重建其他属性
        game_state.player_order = data.get("player_order", [])
        game_state.cattle_market = data.get("cattle_market", [])
        game_state.available_workers = data.get("available_workers", {})
        game_state.max_players = data.get("max_players", 4)
        game_state.game_config = data.get("game_config", {})
        game_state.version = data.get("version", 1)
        game_state.action_history = data.get("action_history", [])

        # 处理最后更新时间
        if data.get("last_updated"):
            game_state.last_updated = datetime.fromisoformat(data["last_updated"])

        if "labor_market" in data:
            game_state.labor_market = LaborMarket.from_dict(data["labor_market"])

        # 重建牌堆管理器
        if "deck_manager" in data:
            game_state.deck_manager = DeckManager.from_dict(data["deck_manager"])

        # 反序列化未来区
        if "future_area" in data:
            game_state.future_area = FutureArea.from_dict(data["future_area"])

        return game_state

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



    # 牌堆相关方法
    def draw_cards(self, card_type: CardType, count: int = 1) -> List[Card]:
        """抽取牌"""
        return self.deck_manager.draw_cards(card_type, count)

    def get_deck_status(self) -> Dict[CardType, Dict[str, int]]:
        """获取牌堆状态"""
        return self.deck_manager.get_deck_status()

    def discard_cards(self, card_type: CardType, cards: List[Card]):
        """弃牌"""
        self.deck_manager.discard_cards(card_type, cards)

    def reshuffle_deck(self, card_type: CardType):
        """重新洗牌"""
        self.deck_manager.reshuffle_deck(card_type)
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
        state = cls(data["session_id"])
        state.current_phase = GamePhase(data["current_phase"])
        # state.players = [PlayerState.from_dict(player_data) for player_data in data["players"]]
        state.board_state = BoardState.from_dict(data["board_state"])
        # state.cattle_market = data["cattle_market"]
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
        self.board_state.connect_nodes(10, 104)
        self.board_state.connect_nodes(104, 105)
        self.board_state.connect_nodes(105, 106)
        self.board_state.connect_nodes(106, 107)
        self.board_state.connect_nodes(107, 108)
        self.board_state.connect_nodes(108, 109)
        self.board_state.connect_nodes(109, 110)
        self.board_state.connect_nodes(110, 111)
        self.board_state.connect_nodes(111, 12)

        # 设置特殊地点的动作
        self.board_state.nodes[0].location_type = LocationType.START
        self.board_state.nodes[0].name = "起点"
        self.board_state.nodes[0].actions = ["move", "start_turn"]

        self.board_state.nodes[29].location_type = LocationType.KANSAS_CITY
        self.board_state.nodes[29].name = "堪萨斯城"
        self.board_state.nodes[29].actions = ["cattle_sale", "end_turn"]

        # 放置建筑物
        self._place_buildings()

        self.place_action_a_cards()

        # 创建铁路路径 (200->201->202->...->239)
        for i in range(200, 240):
            self.board_state.connect_nodes(i, i + 1)

        # 设置车站
        self.board_state.connect_nodes(4, 241)
        self.board_state.connect_nodes(241, 5)

        self.board_state.connect_nodes(7, 242)
        self.board_state.connect_nodes(242, 8)

        self.board_state.connect_nodes(10, 243)
        self.board_state.connect_nodes(243, 11)

        self.board_state.connect_nodes(13, 244)
        self.board_state.connect_nodes(244, 14)

        self.board_state.connect_nodes(16, 245)
        self.board_state.connect_nodes(245, 17)

        self.board_state.connect_nodes(21, 246)
        self.board_state.connect_nodes(246, 22)

        self.board_state.connect_nodes(25, 247)
        self.board_state.connect_nodes(247, 26)

        self.board_state.connect_nodes(29, 248)
        self.board_state.connect_nodes(248, 30)

        self.board_state.connect_nodes(33, 249)
        self.board_state.connect_nodes(249, 34)


        # 放置站长标记
        self._place_stations()

    def _place_stations(self):
        """
                在铁路初始化时放置站长标记
                在指定节点241/242/243/244/245放置站长标记
                """
        print("=== 放置站长标记 ===")

        # 从站长标记牌堆抽取5张牌
        building_cards = self.deck_manager.draw_cards(CardType.PUBLIC_BUILDING, 5)

        if len(building_cards) < 7:
            print(f"⚠️ 公有建筑物牌不足7张，只有{len(building_cards)}张")

        # 将卡牌的特殊能力映射到建筑物类型
        ability_to_building = {
            "station": BuildingType.STATION,
            "ranch": BuildingType.RANCH,
            "hazard": BuildingType.HAZARD,
            "telegraph": BuildingType.TELEGRAPH,
            "church": BuildingType.CHURCH,
            "bank": BuildingType.BUILDING_TYPE_1,
            "hotel": BuildingType.BUILDING_TYPE_1
        }

        # 在指定节点放置建筑物
        public_building_nodes = [1, 5, 9, 10, 12, 15, 17]

        for i, node_id in enumerate(public_building_nodes):
            if i < len(building_cards):
                card = building_cards[i]
                building_type = ability_to_building.get(card.special_ability)

                if building_type:
                    self._place_public_building(node_id, building_type, card)
                else:
                    print(f"❌ 未知的建筑类型: {card.special_ability}")
            else:
                print(f"⚠️ 节点{node_id}：没有足够的建筑物牌")

        print("✅ 公有建筑物放置完成")

    def _place_buildings(self):
        """
                在地图初始化时放置公有建筑物
                在指定节点1/5/9/10/12/15/17放置建筑物
                """
        print("=== 放置公有建筑物 ===")

        # 从公有建筑物牌堆抽取7张牌
        building_cards = self.deck_manager.draw_cards(CardType.PUBLIC_BUILDING, 7)

        if len(building_cards) < 7:
            print(f"⚠️ 公有建筑物牌不足7张，只有{len(building_cards)}张")

        # 将卡牌的特殊能力映射到建筑物类型
        ability_to_building = {
            "station": BuildingType.STATION,
            "ranch": BuildingType.RANCH,
            "hazard": BuildingType.HAZARD,
            "telegraph": BuildingType.TELEGRAPH,
            "church": BuildingType.CHURCH,
            "bank": BuildingType.BUILDING_TYPE_1,
            "hotel": BuildingType.BUILDING_TYPE_1
        }

        # 在指定节点放置建筑物
        public_building_nodes = [1, 5, 9, 10, 12, 15, 17]

        for i, node_id in enumerate(public_building_nodes):
            if i < len(building_cards):
                card = building_cards[i]
                building_type = ability_to_building.get(card.special_ability)

                if building_type:
                    self._place_public_building(node_id, building_type, card)
                else:
                    print(f"❌ 未知的建筑类型: {card.special_ability}")
            else:
                print(f"⚠️ 节点{node_id}：没有足够的建筑物牌")

        print("✅ 公有建筑物放置完成")

    def _place_public_building(self, node_id: int, building_type: BuildingType, card):
        """在指定节点放置公有建筑物"""
        if node_id not in self.board_state.nodes:
            print(f"❌ 节点{node_id}不存在")
            return

        node = self.board_state.nodes[node_id]

        # 检查节点是否可以建造
        if not node.is_buildable():
            print(f"❌ 节点{node_id}不可建造")
            return

        # 放置建筑物
        node.building_type = building_type

        # 根据建筑类型添加特定动作
        if building_type == BuildingType.STATION:
            node.add_action("train_move")
            node.add_action("build")
        elif building_type == BuildingType.RANCH:
            node.add_action("buy_cattle")
            node.add_action("hire_worker")
        elif building_type == BuildingType.HAZARD:
            node.add_action("avoid_hazard")
            node.add_action("gain_certificate")
        elif building_type == BuildingType.TELEGRAPH:
            node.add_action("send_message")
            node.add_action("remote_trade")
        elif building_type == BuildingType.CHURCH:
            node.add_action("pray")
            node.add_action("blessing")


        # 添加通用建筑动作
        node.add_action("use_public_building")

        print(f"✅ 节点{node_id}：放置{card.name}")

    def place_action_a_cards(self):
        """
        从动作A牌堆抽取7张牌，根据牌属性放置到对应支路
        """
        print("=== 放置动作A牌到对应支路 ===")

        # 从动作A牌堆抽取7张牌
        action_a_cards = self.deck_manager.draw_cards(CardType.ACTION_A, 7)
        print(f"从动作A牌堆抽取了 {len(action_a_cards)} 张牌")

        # 定义支路节点范围
        flood_nodes = [51, 52, 53, 54]  # 水灾支路
        drought_nodes = [61, 62, 63, 64]  # 旱灾支路
        rockfall_nodes = [81, 82, 83, 84]  # 落石支路
        tent_nodes = [101, 102, 103, 104, 105, 106, 107, 108, 109]  # 帐篷支路

        # 初始化支路状态（记录每个支路已放置的牌数）
        flood_count = 0
        drought_count = 0
        rockfall_count = 0
        tent_count = 0

        for i, card in enumerate(action_a_cards):
            print(f"\n处理第 {i + 1} 张牌: {card.name}")
            print(f"  特殊能力: {card.special_ability}")

            placed = False

            # 根据牌的特殊能力判断放置位置
            if "水灾" in card.description:
                # 水灾牌放在水灾支路
                if flood_count < len(flood_nodes):
                    target_node_id = flood_nodes[flood_count]
                    placed = self._place_card_on_node(card, target_node_id, "水灾")
                    if placed:
                        flood_count += 1
                        print(f"  ✅ 放置到水灾支路节点 {target_node_id}")
                else:
                    print("  ❌ 水灾支路已满，丢弃")

            elif "旱灾" in card.name or card.special_ability in ["-1", "-2"] and "旱灾" in card.description:
                # 旱灾牌放在旱灾支路
                if drought_count < len(drought_nodes):
                    target_node_id = drought_nodes[drought_count]
                    placed = self._place_card_on_node(card, target_node_id, "旱灾")
                    if placed:
                        drought_count += 1
                        print(f"  ✅ 放置到旱灾支路节点 {target_node_id}")
                else:
                    print("  ❌ 旱灾支路已满，丢弃")

            elif "落石" in card.name or card.special_ability in ["-1", "-2"] and "落石" in card.description:
                # 落石牌放在落石支路
                if rockfall_count < len(rockfall_nodes):
                    target_node_id = rockfall_nodes[rockfall_count]
                    placed = self._place_card_on_node(card, target_node_id, "落石")
                    if placed:
                        rockfall_count += 1
                        print(f"  ✅ 放置到落石支路节点 {target_node_id}")
                else:
                    print("  ❌ 落石支路已满，丢弃")

            elif "帐篷" in card.name or "帐篷" in card.description:
                # 帐篷牌放在帐篷支路
                if tent_count < len(tent_nodes):
                    target_node_id = tent_nodes[tent_count]
                    placed = self._place_card_on_node(card, target_node_id, "帐篷")
                    if placed:
                        tent_count += 1
                        print(f"  ✅ 放置到帐篷支路节点 {target_node_id}")
                else:
                    print("  ❌ 帐篷支路已满，丢弃")

            else:
                print(f"  ⚠️ 未知牌类型，丢弃: {card.name}")

            if not placed:
                print(f"  🗑️ 丢弃牌: {card.name}")

        print(f"\n✅ 放置完成统计:")
        print(f"  水灾支路: {flood_count}/{len(flood_nodes)} 张牌")
        print(f"  旱灾支路: {drought_count}/{len(drought_nodes)} 张牌")
        print(f"  落石支路: {rockfall_count}/{len(rockfall_nodes)} 张牌")
        print(f"  帐篷支路: {tent_count}/{len(tent_nodes)} 张牌")

    def _place_card_on_node(self, card, node_id, event_type):
        """
        将牌放置到指定节点上
        """
        # 检查节点是否存在
        if node_id not in self.board_state.nodes:
            print(f"  ❌ 节点 {node_id} 不存在")
            return False

        node = self.board_state.nodes[node_id]

        # 设置节点的事件类型和牌信息
        node.name = card.name
        node.event_type = event_type
        node.event_card = {
            "card_id": card.card_id,
            "name": card.name,
            "special_ability": card.special_ability,
            "description": card.description
        }

        # 添加事件相关动作
        if event_type in ["水灾", "旱灾", "落石"]:
            node.add_action("avoid_hazard")
            node.add_action("pay_toll")
        elif event_type == "帐篷":
            node.add_action("rest")
            node.add_action("trade")

        return True

    def get_available_building_actions(self, location_id: int, player_id: str) -> List[Dict[str, Any]]:
        """获取在指定位置可用的建筑物动作"""
        return self.board_state.get_available_actions_at_location(location_id, player_id)

    def can_use_building(self, location_id: int, player_id: str) -> bool:
        """检查玩家是否可以使用指定位置的建筑物"""
        building = self.board_state.get_building_at_location(location_id)
        if not building:
            return False

        # 检查工人数量
        player = self.get_player_by_id(player_id)
        if not player or player.resources.workers < building.worker_cost:
            return False

        # 检查建筑物所有权
        if building.owner_id and building.owner_id != player_id:
            return False

        return True

    def use_building(self, location_id: int, player_id: str) -> Dict[str, Any]:
        """使用建筑物（消耗工人）"""
        if not self.can_use_building(location_id, player_id):
            return {"success": False, "message": "无法使用该建筑物"}

        building = self.board_state.get_building_at_location(location_id)
        player = self.get_player_by_id(player_id)

        # 扣除工人
        player.resources.workers -= building.worker_cost

        # 更新游戏状态
        self.increment_version()

        return {
            "success": True,
            "message": f"使用{building.name}成功，消耗{building.worker_cost}工人",
            "player_id": player_id,
            "location_id": location_id,
            "building_type": building.building_type.value,
            "worker_cost": building.worker_cost,
            "remaining_workers": player.resources.workers
        }
