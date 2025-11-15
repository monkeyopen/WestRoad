from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum
import uuid


@dataclass
class Card:
    """基础牌类"""
    card_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    card_type: Enum = None
    name: str = ""
    description: str = ""
    base_value: int = 0
    cost: int = 0
    special_ability: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "card_id": self.card_id,
            "card_type": self.card_type.value if self.card_type else None,
            "name": self.name,
            "description": self.description,
            "base_value": self.base_value,
            "cost": self.cost,
            "special_ability": self.special_ability,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Card':
        """从字典创建实例"""
        card = cls()
        card.card_id = data.get("card_id", str(uuid.uuid4()))
        card_type_str = data.get("card_type")
        if card_type_str:
            # 需要从外部传入CardType枚举
            pass
        card.name = data.get("name", "")
        card.description = data.get("description", "")
        card.base_value = data.get("base_value", 0)
        card.cost = data.get("cost", 0)
        card.special_ability = data.get("special_ability")
        card.metadata = data.get("metadata", {})
        return card

    