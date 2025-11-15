#!/usr/bin/env python3
"""
测试人才市场模块
"""

import sys
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.models.labor_market import LaborMarket
from src.core.models.enums import WorkerType


def labor_market():
    """测试人才市场功能"""
    print("=== 测试人才市场模块 ===")

    # 创建人才市场
    market = LaborMarket()

    # 显示市场状态
    market.display_market()

    # 测试雇佣工人
    print("\n=== 测试雇佣工人 ===")

    # 雇佣第0行第0列的工人
    worker = market.hire_worker(0, 0)
    if worker:
        print(f"雇佣成功: {worker.value}")
    else:
        print("雇佣失败")

    # 显示雇佣后的市场状态
    print("\n雇佣后的市场状态:")
    market.display_market()

    # 测试补充市场
    print("\n=== 测试补充市场 ===")
    market.refill_market()
    market.display_market()

    # 测试序列化
    print("\n=== 测试序列化 ===")
    market_dict = market.to_dict()
    print(f"序列化成功: {len(market_dict['workers_matrix'])} 行")

    # 测试反序列化
    new_market = LaborMarket.from_dict(market_dict)
    print("反序列化成功")
    new_market.display_market()

    # 测试价格获取
    print("\n=== 测试价格获取 ===")
    for i in range(5):
        price = market.get_row_price(i)
        print(f"第{i}行价格: ${price}")

    return True


# 在游戏状态中添加人才市场访问方法
def get_labor_market_info(self) -> Dict[str, Any]:
    """获取人才市场信息"""
    return {
        "rows": self.labor_market.rows,
        "columns": self.labor_market.columns,
        "row_prices": self.labor_market.row_prices,
        "workers": [
            [worker.value if worker else None for worker in row]
            for row in self.labor_market.workers_matrix
        ]
    }


def hire_worker_from_market(self, player_id: str, row: int, column: int) -> Dict[str, Any]:
    """从人才市场雇佣工人"""
    player = self.get_player_by_id(player_id)
    if not player:
        return {"success": False, "message": "玩家不存在"}

    # 获取行价格
    price = self.labor_market.get_row_price(row)

    # 检查玩家是否有足够金钱
    if player.resources.money < price:
        return {"success": False, "message": "金钱不足"}

    # 雇佣工人
    worker_type = self.labor_market.hire_worker(row, column)
    if not worker_type:
        return {"success": False, "message": "雇佣失败，位置无效或已空"}

    # 扣除金钱
    player.resources.money -= price

    # 根据工人类型增加相应资源
    if worker_type == WorkerType.DRIVER:
        player.resources.drivers += 1
    elif worker_type == WorkerType.COWBOY:
        player.resources.cowboys += 1
    elif worker_type == WorkerType.BUILDER:
        player.resources.builders += 1

    # 更新游戏状态版本
    self.increment_version()

    return {
        "success": True,
        "message": f"雇佣{worker_type.value}成功",
        "worker_type": worker_type.value,
        "cost": price,
        "new_money": player.resources.money
    }


if __name__ == "__main__":
    success = labor_market()
    sys.exit(0 if success else 1)
