# src/core/models/card_manager.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import random


@dataclass
class CardManager:
    """卡牌管理系统"""
    draw_pile: List[Dict[str, Any]] = field(default_factory=list)  # 抽牌堆
    hand_cards: List[Dict[str, Any]] = field(default_factory=list)  # 手牌堆
    discard_pile: List[Dict[str, Any]] = field(default_factory=list)  # 弃牌堆
    played_objectives: List[Dict[str, Any]] = field(default_factory=list)  # 已打出目标（记录每张牌）
    acquired_cards: List[Dict[str, Any]] = field(default_factory=list)  # 已获得其他牌（记录每张牌）

    def draw_cards(self, count: int = 1) -> List[Dict[str, Any]]:
        """从抽牌堆抽牌"""
        drawn_cards = []

        for _ in range(count):
            if not self.draw_pile:
                # 洗牌
                self.reshuffle_discard_pile()

            if self.draw_pile:
                card = self.draw_pile.pop(0)
                self.hand_cards.append(card)
                drawn_cards.append(card)

        return drawn_cards

    def reshuffle_discard_pile(self):
        """将弃牌堆洗入抽牌堆"""
        if self.discard_pile:
            random.shuffle(self.discard_pile)
            self.draw_pile = self.discard_pile.copy()
            self.discard_pile.clear()

    def discard_card(self, card_id: str) -> bool:
        """从手牌弃掉一张牌"""
        for i, card in enumerate(self.hand_cards):
            if card.get("card_id") == card_id:
                discarded_card = self.hand_cards.pop(i)
                self.discard_pile.append(discarded_card)
                return True
        return False

    def discard_hand_card_by_index(self, index: int) -> bool:
        """根据索引弃掉手牌"""
        if 0 <= index < len(self.hand_cards):
            card = self.hand_cards.pop(index)
            self.discard_pile.append(card)
            return True
        return False

    def play_objective(self, card_id: str) -> bool:
        """打出一张目标卡"""
        for i, card in enumerate(self.hand_cards):
            if card.get("card_id") == card_id and card.get("card_type") == "objective":
                played_card = self.hand_cards.pop(i)
                self.played_objectives.append(played_card)
                return True
        return False

    def acquire_card(self, card_data: Dict[str, Any]) -> None:
        """获得一张牌（站长标记、灾害标记、帐篷标记等）"""
        self.acquired_cards.append(card_data)

    def get_acquired_card_by_type(self, card_type: str) -> List[Dict[str, Any]]:
        """根据类型获取已获得的牌"""
        return [card for card in self.acquired_cards if card.get("card_type") == card_type]

    def get_card_counts(self) -> Dict[str, int]:
        """获取各类卡牌数量"""
        return {
            "draw_pile": len(self.draw_pile),
            "hand_cards": len(self.hand_cards),
            "discard_pile": len(self.discard_pile),
            "played_objectives": len(self.played_objectives),
            "acquired_cards": len(self.acquired_cards)
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "draw_pile": self.draw_pile,
            "hand_cards": self.hand_cards,
            "discard_pile": self.discard_pile,
            "played_objectives": self.played_objectives,
            "acquired_cards": self.acquired_cards
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """从字典重建"""
        return cls(
            draw_pile=data.get("draw_pile", []),
            hand_cards=data.get("hand_cards", []),
            discard_pile=data.get("discard_pile", []),
            played_objectives=data.get("played_objectives", []),
            acquired_cards=data.get("acquired_cards", [])
        )