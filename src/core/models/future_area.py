# src/core/models/future_area.py

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import random

from .enums import CardType
from .deck_manager import DeckManager, DeckConfig


class FutureAreaColumnType(Enum):
    """未来区列类型枚举"""
    ACTION_A = "action_a"  # 第一列：动作A牌
    ACTION_B = "action_b"  # 第二列：动作B牌
    ACTION_C = "action_c"  # 第三列：动作C牌


@dataclass
class FutureArea:
    """
    未来区类 - 管理2×3的未来区网格
    第一列：动作A牌堆
    第二列：动作B牌堆
    第三列：动作C牌堆
    """

    # 未来区配置 (2行3列)
    grid: List[List[Optional[Dict[str, Any]]]] = field(default_factory=list)

    # 列类型映射
    column_types: Dict[int, FutureAreaColumnType] = field(default_factory=dict)

    def __post_init__(self):
        """初始化后执行"""
        # 初始化列类型映射
        self.column_types = {
            0: FutureAreaColumnType.ACTION_A,
            1: FutureAreaColumnType.ACTION_B,
            2: FutureAreaColumnType.ACTION_C
        }

        # 初始化2×3网格
        if not self.grid:
            self.grid = [[None, None, None], [None, None, None]]

    def initialize(self, deck_manager: DeckManager):
        """
        初始化未来区

        Args:
            deck_manager: 牌堆管理器
        """
        print("=== 初始化未来区 ===")

        # 清空网格
        self.grid = [[None, None, None], [None, None, None]]

        # 填充每一列
        for col in range(3):
            self._fill_column(col, deck_manager)

        print("✅ 未来区初始化完成")

    def _fill_column(self, col: int, deck_manager: DeckManager):
        """
        填充指定列

        Args:
            col: 列索引 (0, 1, 2)
            deck_manager: 牌堆管理器
        """
        # 获取列对应的牌堆类型
        column_type = self.column_types[col]

        # 根据列类型确定牌堆类型
        if column_type == FutureAreaColumnType.ACTION_A:
            card_type = CardType.ACTION_A
        elif column_type == FutureAreaColumnType.ACTION_B:
            card_type = CardType.ACTION_B
        elif column_type == FutureAreaColumnType.ACTION_C:
            card_type = CardType.ACTION_C
        else:
            card_type = CardType.ACTION_A  # 默认

        # 从对应牌堆抽取2张牌
        cards = deck_manager.draw_cards(card_type, 2)

        # 填充到该列的两行
        for row in range(2):
            if row < len(cards):
                self.grid[row][col] = self._card_to_dict(cards[row])
                print(f"  未来区[{row}][{col}]: {cards[row].name} ({card_type.value})")
            else:
                self.grid[row][col] = None

    def _card_to_dict(self, card) -> Dict[str, Any]:
        """将卡牌对象转换为字典"""
        return {
            "card_id": card.card_id,
            "name": card.name,
            "card_type": card.card_type.value,
            "base_value": getattr(card, 'base_value', 0),
            "cost": getattr(card, 'cost', 0),
            "special_ability": getattr(card, 'special_ability', None),
            "description": getattr(card, 'description', "")
        }

    def get_card(self, row: int, col: int) -> Optional[Dict[str, Any]]:
        """
        获取指定位置的牌

        Args:
            row: 行索引 (0或1)
            col: 列索引 (0, 1, 2)

        Returns:
            牌信息字典，如果位置为空则返回None
        """
        if not (0 <= row < 2 and 0 <= col < 3):
            return None

        return self.grid[row][col]

    def take_card(self, row: int, col: int, deck_manager: DeckManager) -> Optional[Dict[str, Any]]:
        """
        从未来区取走一张牌，并补充新牌

        Args:
            row: 行索引 (0或1)
            col: 列索引 (0, 1, 2)
            deck_manager: 牌堆管理器

        Returns:
            被取走的牌信息，如果位置为空则返回None
        """
        if not (0 <= row < 2 and 0 <= col < 3):
            return None

        # 获取当前位置的牌
        card = self.grid[row][col]

        if card is None:
            return None

        # 清空该位置
        self.grid[row][col] = None

        # 补充新牌到该位置
        self._refill_position(row, col, deck_manager)

        return card

    def _refill_position(self, row: int, col: int, deck_manager: DeckManager):
        """
        补充指定位置

        Args:
            row: 行索引 (0或1)
            col: 列索引 (0, 1, 2)
            deck_manager: 牌堆管理器
        """
        # 获取列对应的牌堆类型
        column_type = self.column_types[col]

        # 根据列类型确定牌堆类型
        if column_type == FutureAreaColumnType.ACTION_A:
            card_type = CardType.ACTION_A
        elif column_type == FutureAreaColumnType.ACTION_B:
            card_type = CardType.ACTION_B
        elif column_type == FutureAreaColumnType.ACTION_C:
            card_type = CardType.ACTION_C
        else:
            card_type = CardType.ACTION_A  # 默认

        # 从对应牌堆抽取1张牌
        cards = deck_manager.draw_cards(card_type, 1)

        # 填充到指定位置
        if cards:
            self.grid[row][col] = self._card_to_dict(cards[0])
            print(f"  补充未来区[{row}][{col}]: {cards[0].name}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典 (用于序列化)"""
        return {
            "grid": self.grid,
            "column_types": {k: v.value for k, v in self.column_types.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FutureArea':
        """从字典创建实例"""
        future_area = cls()

        # 恢复网格
        if "grid" in data:
            future_area.grid = data["grid"]

        # 恢复列类型映射
        if "column_types" in data:
            future_area.column_types = {}
            for k, v in data["column_types"].items():
                future_area.column_types[int(k)] = FutureAreaColumnType(v)

        return future_area

    def display(self):
        """显示未来区状态 (用于调试)"""
        print("\n=== 未来区状态 ===")
        print("    列0(动作A)  列1(动作B)  列2(动作C)")

        for row in range(2):
            row_display = f"行{row}: "
            for col in range(3):
                card = self.grid[row][col]
                if card:
                    # 显示牌名缩写
                    name_abbr = card['name'][:6] + "..." if len(card['name']) > 6 else card['name']
                    row_display += f"{name_abbr:^12}"
                else:
                    row_display += f"{'空':^12}"
            print(row_display)