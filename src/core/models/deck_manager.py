from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import random
from .enums import CardType
from .card import Card


@dataclass
class DeckConfig:
    """牌堆配置类"""
    card_type: CardType
    total_count: int  # 总数量
    card_prototypes: List[Dict[str, Any]]  # 牌的原型配置

    def __post_init__(self):
        """验证配置"""
        if len(self.card_prototypes) == 0:
            raise ValueError(f"牌堆 {self.card_type.value} 没有配置牌原型")

        # 计算原型牌的总数
        prototype_total = sum(proto.get("count", 1) for proto in self.card_prototypes)
        if prototype_total != self.total_count:
            raise ValueError(f"牌堆 {self.card_type.value} 配置不匹配: "
                             f"总数量={self.total_count}, 原型总数={prototype_total}")


@dataclass
class Deck:
    """牌堆类 - 管理一种类型的牌"""

    card_type: CardType
    cards: List[Card] = field(default_factory=list)
    discarded: List[Card] = field(default_factory=list)

    def initialize_from_config(self, config: DeckConfig):
        """根据配置初始化牌堆"""
        self.cards = []

        for prototype in config.card_prototypes:
            count = prototype.get("count", 1)
            for i in range(count):
                card = Card(
                    card_type=self.card_type,
                    name=prototype.get("name", f"{self.card_type.value}_card"),
                    description=prototype.get("description", ""),
                    base_value=prototype.get("base_value", 0),
                    cost=prototype.get("cost", 0),
                    special_ability=prototype.get("special_ability"),
                    metadata=prototype.get("metadata", {})
                )
                self.cards.append(card)

        # 洗牌
        self.shuffle()
        print(f"✅ 初始化 {self.card_type.value} 牌堆: {len(self.cards)} 张牌")

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> List[Card]:
        """从牌堆顶部抽取指定数量的牌（无放回）"""
        if count > len(self.cards):
            # 如果牌不够，可以尝试从弃牌堆重新洗牌（如果需要）
            available = len(self.cards)
            print(f"⚠️ 牌堆不足: 需要{count}张，但只有{available}张可用")
            count = available

        drawn_cards = self.cards[:count]
        self.cards = self.cards[count:]

        return drawn_cards

    def discard(self, cards: List[Card]):
        """将牌放入弃牌堆"""
        self.discarded.extend(cards)

    def reshuffle_discarded(self):
        """将弃牌堆重新洗牌并放回牌堆"""
        if self.discarded:
            self.cards.extend(self.discarded)
            self.discarded = []
            self.shuffle()
            print(f"✅ 已重新洗牌: {len(self.cards)} 张牌")

    def get_remaining_count(self) -> int:
        """获取剩余牌数量"""
        return len(self.cards)

    def get_discarded_count(self) -> int:
        """获取弃牌数量"""
        return len(self.discarded)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "card_type": self.card_type.value,
            "cards": [card.to_dict() for card in self.cards],
            "discarded": [card.to_dict() for card in self.discarded]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Deck':
        """从字典创建实例"""
        deck = cls(card_type=CardType(data["card_type"]))

        # 重建牌堆
        for card_data in data.get("cards", []):
            card = Card.from_dict(card_data)
            card.card_type = deck.card_type
            deck.cards.append(card)

        # 重建弃牌堆
        for card_data in data.get("discarded", []):
            card = Card.from_dict(card_data)
            card.card_type = deck.card_type
            deck.discarded.append(card)

        return deck


@dataclass
class DeckManager:
    """牌堆管理器 - 管理所有类型的牌堆"""

    decks: Dict[CardType, Deck] = field(default_factory=dict)

    def initialize_decks(self, configs: Dict[CardType, DeckConfig]):
        """根据配置初始化所有牌堆"""
        self.decks = {}

        for card_type, config in configs.items():
            deck = Deck(card_type=card_type)
            deck.initialize_from_config(config)
            self.decks[card_type] = deck

        print("✅ 所有牌堆初始化完成")

    def get_deck(self, card_type: CardType) -> Optional[Deck]:
        """获取指定类型的牌堆"""
        return self.decks.get(card_type)

    def draw_cards(self, card_type: CardType, count: int = 1) -> List[Card]:
        """从指定牌堆抽取牌"""
        deck = self.get_deck(card_type)
        if deck:
            return deck.draw(count)
        else:
            print(f"❌ 未找到牌堆: {card_type.value}")
            return []

    def discard_cards(self, card_type: CardType, cards: List[Card]):
        """将牌放入指定牌堆的弃牌堆"""
        deck = self.get_deck(card_type)
        if deck:
            deck.discard(cards)
        else:
            print(f"❌ 未找到牌堆: {card_type.value}")

    def reshuffle_deck(self, card_type: CardType):
        """重新洗牌指定牌堆的弃牌"""
        deck = self.get_deck(card_type)
        if deck:
            deck.reshuffle_discarded()
        else:
            print(f"❌ 未找到牌堆: {card_type.value}")

    def get_deck_status(self) -> Dict[CardType, Dict[str, int]]:
        """获取所有牌堆的状态"""
        status = {}
        for card_type, deck in self.decks.items():
            status[card_type] = {
                "remaining": deck.get_remaining_count(),
                "discarded": deck.get_discarded_count(),
                "total": deck.get_remaining_count() + deck.get_discarded_count()
            }
        return status

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            "decks": {
                card_type.value: deck.to_dict()
                for card_type, deck in self.decks.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeckManager':
        """从字典创建实例"""
        manager = cls()

        for card_type_str, deck_data in data.get("decks", {}).items():
            card_type = CardType(card_type_str)
            deck = Deck.from_dict(deck_data)
            manager.decks[card_type] = deck

        return manager


    