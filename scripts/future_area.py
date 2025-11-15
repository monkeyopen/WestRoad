#!/usr/bin/env python3
"""
测试独立实现的未来区功能
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.models.future_area import FutureArea
from src.core.models.deck_manager import DeckManager, DeckConfig
from src.core.models.enums import CardType
from config.cards import DECK_CONFIGS


def future_area():
    """测试未来区功能"""
    print("=== 测试独立实现的未来区功能 ===")

    # 创建牌堆管理器
    deck_manager = DeckManager()

    # 将配置转换为DeckConfig对象
    deck_configs = {}
    for card_type_str, config in DECK_CONFIGS.items():
        card_type = CardType(card_type_str)
        deck_configs[card_type] = DeckConfig(
            card_type=card_type,
            total_count=config["total_count"],
            card_prototypes=config["card_prototypes"]
        )

    # 初始化牌堆
    deck_manager.initialize_decks(deck_configs)

    # 创建未来区
    future_area = FutureArea()

    # 初始化未来区
    future_area.initialize(deck_manager)

    # 显示未来区状态
    future_area.display()

    # 测试取牌功能
    print("\n=== 测试从未来区取牌 ===")

    # 取第一张牌
    card = future_area.take_card(0, 0, deck_manager)
    if card:
        print(f"取到牌: {card['name']}")
    else:
        print("取牌失败")

    # 显示取牌后的状态
    future_area.display()

    # 测试序列化
    print("\n=== 测试序列化 ===")
    future_dict = future_area.to_dict()
    print("序列化成功")

    # 测试反序列化
    new_future = FutureArea.from_dict(future_dict)
    print("反序列化成功")

    # 验证反序列化后的状态
    new_future.display()


if __name__ == "__main__":
    future_area()