from dataclasses import dataclass, field
from typing import List, Optional
from .enums import PlayerColor

@dataclass
class ResourceSet:
    """玩家资源集合"""
    money: int = 0
    workers: int = 0
    craftsmen: int = 0
    engineers: int = 0
    certificates: int = 0

@dataclass
class CattleCard:
    """牛牌定义"""
    card_id: str
    card_number: str
    base_value: int
    special_ability: Optional[str] = None
    owner_id: Optional[str] = None
    location: str = "deck"  # deck, hand, discard, cattle_market

@dataclass
class PlayerState:
    """玩家状态"""
    player_id: str
    user_id: str
    player_color: PlayerColor
    display_name: str
    position: int = 0  # 在版图上的当前位置
    previous_position: Optional[int] = None
    resources: ResourceSet = field(default_factory=ResourceSet)
    hand_cards: List[CattleCard] = field(default_factory=list)  # 手牌列表
    victory_points: int = 0  # 胜利分数
    stations_built: int = 0  # 已建车站数
    cattle_sold_count: int = 0  # 卖出牛数
    buildings_built_count: int = 0  # 建造建筑数
    workers_hired_count: int = 0  # 雇佣工人数