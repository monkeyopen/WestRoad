# src/core/models/labor_market.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import random
from .enums import WorkerType
from .deck_manager import DeckManager
from .enums import CardType


@dataclass
class LaborMarket:
    """人才市场类 - 4列12行的矩阵"""

    # 市场配置
    rows: int = 12
    columns: int = 4

    # 市场价格配置(每行的价格)
    row_prices: List[int] = field(default_factory=lambda: [i + 1 for i in range(15)])

    # 工人矩阵 (12行×4列)
    workers_matrix: List[List[Optional[WorkerType]]] = field(default_factory=list)

    # 下一个要填充的格子索引 (0-47)
    next_fill_index: int = 0

    def __post_init__(self):
        """初始化后自动创建空矩阵"""
        # 初始化空矩阵
        self.workers_matrix = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        print("✅ 人才市场空矩阵初始化完成")

    def initialize_from_action_b_deck(self, deck_manager):
        """
        从action_b牌堆中抽取工人来初始化人才市场的前7个格子
        """
        print("=== 从action_b牌堆初始化人才市场前7个格子 ===")

        # 从action_b牌堆抽取7张牌
        action_b_cards = deck_manager.draw_cards(CardType.ACTION_B, 7)

        if len(action_b_cards) < 7:
            print(f"⚠️ action_b牌堆不足7张牌，只有{len(action_b_cards)}张")

        # 将action_b卡牌映射为工人类型
        worker_mapping = {
            "牛仔": WorkerType.COWBOY,
            "建筑工人": WorkerType.BUILDER,
            "司机": WorkerType.DRIVER
        }

        # 填充前7个格子
        for i in range(min(7, len(action_b_cards))):
            card = action_b_cards[i]
            worker_type = worker_mapping.get(card.name)

            if worker_type:
                # 计算行和列
                row = i // self.columns
                col = i % self.columns

                self.workers_matrix[row][col] = worker_type
                print(f"  位置[{row},{col}]：{card.name} -> {worker_type.value}")
            else:
                # 如果卡牌名称不匹配，使用随机工人类型
                random_worker = random.choice(list(WorkerType))
                row = i // self.columns
                col = i % self.columns

                self.workers_matrix[row][col] = random_worker
                print(f"  位置[{row},{col}]：{card.name}（未映射）-> 随机{random_worker.value}")

        # 设置下一个要填充的格子索引
        self.next_fill_index = min(7, len(action_b_cards))
        print(f"✅ 人才市场初始化完成：已填充{self.next_fill_index}个格子，下一个填充索引: {self.next_fill_index}")

        # 显示初始化后的状态
        self.display_market()

    def fill_next_slot(self, deck_manager):
        """
        按照顺序填充下一个格子
        """
        if self.next_fill_index >= self.rows * self.columns:
            print("⚠️ 人才市场已满，无法继续填充")
            return False

        # 从action_b牌堆抽取1张牌
        action_b_cards = deck_manager.draw_cards(CardType.ACTION_B, 1)

        if not action_b_cards:
            print("⚠️ action_b牌堆为空，无法填充")
            return False

        card = action_b_cards[0]

        # 将action_b卡牌映射为工人类型
        worker_mapping = {
            "牛仔": WorkerType.COWBOY,
            "建筑工人": WorkerType.BUILDER,
            "司机": WorkerType.DRIVER
        }

        # 计算行和列
        row = self.next_fill_index // self.columns
        col = self.next_fill_index % self.columns

        worker_type = worker_mapping.get(card.name)

        if worker_type:
            self.workers_matrix[row][col] = worker_type
            print(f"✅ 填充位置[{row},{col}]：{card.name} -> {worker_type.value}")
        else:
            # 如果卡牌名称不匹配，使用随机工人类型
            random_worker = random.choice(list(WorkerType))
            self.workers_matrix[row][col] = random_worker
            print(f"✅ 填充位置[{row},{col}]：{card.name}（未映射）-> 随机{random_worker.value}")

        # 更新下一个要填充的格子索引
        self.next_fill_index += 1
        print(f"下一个填充索引: {self.next_fill_index}")

        return True

    def hire_worker(self, row: int, column: int) -> Optional[WorkerType]:
        """雇佣指定位置的工人(返回工人类型,并将位置设为空)"""
        if 0 <= row < self.rows and 0 <= column < self.columns:
            worker = self.workers_matrix[row][column]
            self.workers_matrix[row][column] = None
            return worker
        return None

    def refill_market(self, deck_manager):
        """补充市场空缺 - 按照顺序填充下一个格子"""
        print("=== 按照顺序补充人才市场 ===")
        return self.fill_next_slot(deck_manager)

    def get_worker(self, row: int, column: int) -> Optional[WorkerType]:
        """获取指定位置的工人"""
        if 0 <= row < self.rows and 0 <= column < self.columns:
            return self.workers_matrix[row][column]
        return None

    def get_row_price(self, row_index: int) -> int:
        """获取指定行的价格"""
        if 0 <= row_index < len(self.row_prices):
            return self.row_prices[row_index]
        return 0

    def display_market(self):
        """显示人才市场状态(用于调试)"""
        print("\n=== 人才市场当前状态 ===")
        print("行号 | 价格 | 工人类型")
        print("-" * 40)

        for i in range(self.rows):
            price = self.get_row_price(i)
            workers = []
            for j in range(self.columns):
                worker = self.workers_matrix[i][j]
                workers.append(worker.value if worker else "空")

            workers_str = " | ".join(workers)
            print(f"{i:2d} | ${price:2d} | {workers_str}")

    def to_dict(self) -> Dict[str, any]:
        """转换为字典(用于序列化)"""
        return {
            "rows": self.rows,
            "columns": self.columns,
            "row_prices": self.row_prices,
            "workers_matrix": [
                [worker.value if worker else None for worker in row]
                for row in self.workers_matrix
            ],
            "next_fill_index": self.next_fill_index
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'LaborMarket':
        """从字典创建实例"""
        market = cls()
        market.rows = data.get("rows", 12)
        market.columns = data.get("columns", 4)
        market.row_prices = data.get("row_prices", [i + 1 for i in range(15)])
        market.next_fill_index = data.get("next_fill_index", 0)

        # 重建工人矩阵
        workers_data = data.get("workers_matrix", [])
        market.workers_matrix = []
        for row_data in workers_data:
            row = []
            for worker_value in row_data:
                if worker_value:
                    row.append(WorkerType(worker_value))
                else:
                    row.append(None)
            market.workers_matrix.append(row)

        return market