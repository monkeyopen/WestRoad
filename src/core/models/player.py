from dataclasses import dataclass, field
from typing import List, Optional
from .enums import PlayerColor

from dataclasses import asdict, dataclass, field
from typing import List, Dict, Any


@dataclass
class ResourceSet:
    """玩家资源集合"""
    money: int = 0
    workers: int = 0
    craftsmen: int = 0
    engineers: int = 0
    certificates: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


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

    def to_dict(self) -> Dict[str, Any]:
        """将玩家状态转换为字典"""
        from .enums import PlayerColor  # 导入枚举

        data = {
            "player_id": self.player_id,
            "user_id": self.user_id,
            "player_color": self.player_color.value if isinstance(self.player_color,
                                                                  PlayerColor) else self.player_color,
            "display_name": self.display_name,
            "resources": self.resources.to_dict(),
            "hand_cards": self.hand_cards,
            "victory_points": self.victory_points,
            "buildings_built_count": self.buildings_built_count,
            "cattle_sold_count": self.cattle_sold_count
        }
        return data


    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建玩家状态"""
        from .enums import PlayerColor  # 导入枚举

        # 处理 player_color 字段
        player_color = data.get("player_color")
        if isinstance(player_color, str):
            # 如果是字符串，尝试转换为枚举
            try:
                player_color = PlayerColor(player_color)
            except ValueError:
                # 如果无法转换，保持原值
                pass

        # 处理 resources 字段
        resources_data = data.get("resources", {})
        resources = ResourceSet(**resources_data)

        # 创建实例
        return cls(
            player_id=data.get("player_id"),
            user_id=data.get("user_id"),
            player_color=player_color,
            display_name=data.get("display_name"),
            resources=resources,
            hand_cards=data.get("hand_cards", []),
            victory_points=data.get("victory_points", 0),
            buildings_built_count=data.get("buildings_built_count", 0),
            cattle_sold_count=data.get("cattle_sold_count", 0)
        )
