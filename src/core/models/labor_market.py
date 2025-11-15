from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random
from enum import Enum
from .enums import WorkerType


@dataclass
class LaborMarket:
    """人才市场类 - 4列12行的矩阵"""

    # 市场配置
    rows: int = 12
    columns: int = 4

    # 市场价格配置（每行的价格）
    row_prices: List[int] = field(default_factory=lambda: [i + 1 for i in range(15)])

    # 工人矩阵 (15行 × 5列)
    workers_matrix: List[List[Optional[WorkerType]]] = field(default_factory=list)

    def __post_init__(self):
        """初始化后自动填充工人矩阵"""
        if not self.workers_matrix:
            self.initialize_market()

    def initialize_market(self):
        """初始化人才市场 - 随机填充工人"""
        self.workers_matrix = []

        for row in range(self.rows):
            # 每行随机选择5个工人类型
            row_workers = random.choices(
                list(WorkerType),
                k=self.columns
            )
            self.workers_matrix.append(row_workers)

        print("✅ 人才市场初始化完成")

    def get_row_price(self, row_index: int) -> int:
        """获取指定行的价格"""
        if 0 <= row_index < len(self.row_prices):
            return self.row_prices[row_index]
        return 0

    def get_worker(self, row: int, column: int) -> Optional[WorkerType]:
        """获取指定位置的工人"""
        if 0 <= row < self.rows and 0 <= column < self.columns:
            return self.workers_matrix[row][column]
        return None

    def hire_worker(self, row: int, column: int) -> Optional[WorkerType]:
        """雇佣指定位置的工人（返回工人类型，并将位置设为空）"""
        if 0 <= row < self.rows and 0 <= column < self.columns:
            worker = self.workers_matrix[row][column]
            self.workers_matrix[row][column] = None
            return worker
        return None

    def refill_market(self):
        """补充市场空缺（将空位随机填充）"""
        for row in range(self.rows):
            for col in range(self.columns):
                if self.workers_matrix[row][col] is None:
                    self.workers_matrix[row][col] = random.choice(list(WorkerType))

        print("✅ 人才市场已补充")

    def to_dict(self) -> Dict[str, any]:
        """转换为字典（用于序列化）"""
        return {
            "rows": self.rows,
            "columns": self.columns,
            "row_prices": self.row_prices,
            "workers_matrix": [
                [worker.value if worker else None for worker in row]
                for row in self.workers_matrix
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'LaborMarket':
        """从字典创建实例"""
        market = cls()
        market.rows = data.get("rows", 15)
        market.columns = data.get("columns", 5)
        market.row_prices = data.get("row_prices", [i + 1 for i in range(15)])

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

    def display_market(self):
        """显示人才市场状态（用于调试）"""
        print("=== 人才市场 ===")
        print("行号 | 价格 | 工人类型")
        print("-" * 30)

        for i, row in enumerate(self.workers_matrix):
            price = self.get_row_price(i)
            workers_str = " | ".join([f"{w.value if w else '空'}" for w in row])
            print(f"{i:2d}  | ${price:2d} | {workers_str}")