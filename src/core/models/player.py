from dataclasses import asdict, dataclass, field
from typing import List, Dict, Any, Optional

from .card_manager import CardManager
from .enums import WorkerType, AuxiliaryAbility, PlayerColor


@dataclass
class ResourceSet:
    """玩家资源集合"""
    money: int = 0
    # 3种工人数量
    cowboys: int = 0  # 牛仔
    builders: int = 0  # 工匠
    drivers: int = 0  # 工程师
    certificates: int = 0
    temporary_honor: int = 0  # 临时荣誉数量

    def to_dict(self) -> Dict[str, Any]:
        return {
            "money": self.money,
            "cowboys": self.cowboys,
            "drivers": self.drivers,
            "builders": self.builders,
            "certificates": self.certificates,
            "temporary_honor": self.temporary_honor
        }


@dataclass
class AuxiliaryAbilityState:
    """辅助能力状态"""
    ability_type: AuxiliaryAbility
    description: str
    is_usable: bool = False
    used_count: int = 0
    max_uses: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ability_type": self.ability_type.value,
            "description": self.description,
            "is_usable": self.is_usable,
            "used_count": self.used_count,
            "max_uses": self.max_uses
        }


@dataclass
class CattleCard:
    """牛牌定义"""
    card_id: str
    card_number: str
    base_value: int
    special_ability: Optional[str] = None
    owner_id: Optional[str] = None
    location: str = "deck"  # deck, hand, discard, cattle_market


# src/core/models/player.py
@dataclass
class PlayerState:
    """玩家完整状态"""

    # 基础信息
    player_id: str
    user_id: str
    player_color: PlayerColor
    display_name: str

    # 位置状态
    position: int = 0
    previous_position: Optional[int] = None

    # 资源状态
    resources: ResourceSet = field(default_factory=ResourceSet)

    # 卡牌管理
    card_manager: CardManager = field(default_factory=CardManager)

    # 游戏进度
    victory_points: int = 0
    stations_built: int = 0
    cattle_sold_count: int = 0
    buildings_built_count: int = 0
    workers_hired_count: int = 0

    # 16种辅助能力
    auxiliary_abilities: List[AuxiliaryAbilityState] = field(default_factory=list)

    def __post_init__(self):
        """初始化后设置默认的辅助能力"""
        if not self.auxiliary_abilities:
            self._initialize_auxiliary_abilities()

    def _initialize_auxiliary_abilities(self):
        """初始化16种辅助能力"""
        ability_descriptions = {
            AuxiliaryAbility.GOLD_1: "获得1金钱",
            AuxiliaryAbility.GOLD_2: "获得2金钱",
            AuxiliaryAbility.DRAW_1: "抽1张牌",
            AuxiliaryAbility.DRAW_2: "抽2张牌",
            AuxiliaryAbility.REVERSE_1: "倒车1次",
            AuxiliaryAbility.REVERSE_2: "倒车2次",
            AuxiliaryAbility.FORWARD_1: "前进1步",
            AuxiliaryAbility.FORWARD_2: "前进2步",
            AuxiliaryAbility.DROP_1: "丢弃1张牌",
            AuxiliaryAbility.DROP_2: "丢弃2张牌",
            AuxiliaryAbility.SPEED_1: "速度+1",
            AuxiliaryAbility.SPEED_2: "速度+2",
            AuxiliaryAbility.CARD_CAPACITY_1: "手牌上限+1",
            AuxiliaryAbility.CARD_CAPACITY_2: "手牌上限+1",
            AuxiliaryAbility.HONOR_LIMIT_1: "荣誉上限+1",
            AuxiliaryAbility.HONOR_LIMIT_2: "荣誉上限+2"
        }

        for ability_type, description in ability_descriptions.items():
            # 设置不同能力的使用限制
            is_usable = False
            if ability_type in [AuxiliaryAbility.GOLD_1, AuxiliaryAbility.DRAW_1]:
                is_usable = True

            self.auxiliary_abilities.append(
                AuxiliaryAbilityState(ability_type, description, is_usable=is_usable)
            )

    def get_auxiliary_ability(self, ability_type: AuxiliaryAbility) -> Optional[AuxiliaryAbilityState]:
        """获取指定类型的辅助能力"""
        for ability in self.auxiliary_abilities:
            if ability.ability_type == ability_type:
                return ability
        return None

    def can_use_ability(self, ability_type: AuxiliaryAbility) -> bool:
        """检查是否能使用指定能力"""
        ability = self.get_auxiliary_ability(ability_type)
        return ability is not None and ability.is_usable

    def use_ability(self, ability_type: AuxiliaryAbility) -> bool:
        """使用辅助能力"""
        ability = self.get_auxiliary_ability(ability_type)
        if not ability or not ability.is_usable:
            return False

        ability.used_count += 1

        # 检查使用次数限制
        if ability.max_uses and ability.used_count >= ability.max_uses:
            ability.is_usable = False

        return True

    def reset_abilities(self):
        """重置所有能力状态（例如新回合开始）"""
        for ability in self.auxiliary_abilities:
            # 重置部分能力的使用状态
            if ability.max_uses is None or ability.used_count < ability.max_uses:
                ability.is_usable = True

    # 卡牌管理代理方法
    def draw_cards(self, count: int = 1) -> List[Dict[str, Any]]:
        """抽牌"""
        return self.card_manager.draw_cards(count)

    def discard_card(self, card_id: str) -> bool:
        """弃牌"""
        return self.card_manager.discard_card(card_id)

    def play_objective(self, card_id: str) -> bool:
        """打出目标卡"""
        return self.card_manager.play_objective(card_id)

    def acquire_card(self, card_data: Dict[str, Any]) -> None:
        """获得一张牌"""
        self.card_manager.acquire_card(card_data)

    def get_acquired_cards_by_type(self, card_type: str) -> List[Dict[str, Any]]:
        """根据类型获取已获得的牌"""
        return self.card_manager.get_acquired_card_by_type(card_type)

    def get_card_summary(self) -> Dict[str, Any]:
        """获取卡牌汇总信息"""
        counts = self.card_manager.get_card_counts()
        acquired_types = {}

        # 统计已获得牌的类型分布
        for card in self.card_manager.acquired_cards:
            card_type = card.get("card_type", "unknown")
            acquired_types[card_type] = acquired_types.get(card_type, 0) + 1

        return {
            "card_counts": counts,
            "acquired_card_types": acquired_types,
            "played_objectives": self.card_manager.played_objectives,
            "acquired_cards": self.card_manager.acquired_cards
        }

    def get_total_workers(self) -> Dict[WorkerType, int]:
        """获取各种工人的总数"""
        return {
            WorkerType.COWBOY: self.resources.cowboys,
            WorkerType.BUILDER: self.resources.builders,
            WorkerType.DRIVER: self.resources.drivers
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "player_id": self.player_id,
            "user_id": self.user_id,
            "player_color": self.player_color.value,
            "display_name": self.display_name,
            "position": self.position,
            "previous_position": self.previous_position,
            "resources": self.resources.to_dict(),
            "card_manager": self.card_manager.to_dict(),
            "victory_points": self.victory_points,
            "stations_built": self.stations_built,
            "cattle_sold_count": self.cattle_sold_count,
            "buildings_built_count": self.buildings_built_count,
            "workers_hired_count": self.workers_hired_count,
            "auxiliary_abilities": [ability.to_dict() for ability in self.auxiliary_abilities]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典创建实例"""
        # 处理player_color
        from .enums import PlayerColor
        player_color = PlayerColor(data["player_color"])

        # 处理resources
        resources_data = data.get("resources", {})
        resources = ResourceSet(**resources_data)

        # 处理card_manager
        card_manager_data = data.get("card_manager", {})
        card_manager = CardManager.from_dict(card_manager_data)

        # 创建实例
        player = cls(
            player_id=data["player_id"],
            user_id=data["user_id"],
            player_color=player_color,
            display_name=data["display_name"],
            resources=resources,
            card_manager=card_manager
        )

        # 设置其他属性
        player.position = data.get("position", 0)
        player.previous_position = data.get("previous_position")
        player.victory_points = data.get("victory_points", 0)
        player.stations_built = data.get("stations_built", 0)
        player.cattle_sold_count = data.get("cattle_sold_count", 0)
        player.buildings_built_count = data.get("buildings_built_count", 0)
        player.workers_hired_count = data.get("workers_hired_count", 0)

        # 处理辅助能力
        abilities_data = data.get("auxiliary_abilities", [])
        player.auxiliary_abilities = []
        for ability_data in abilities_data:
            from .enums import AuxiliaryAbility
            ability = AuxiliaryAbilityState(
                ability_type=AuxiliaryAbility(ability_data["ability_type"]),
                description=ability_data["description"],
                is_usable=ability_data.get("is_usable", True),
                used_count=ability_data.get("used_count", 0),
                max_uses=ability_data.get("max_uses")
            )
            player.auxiliary_abilities.append(ability)

        return player
