#!/usr/bin/env python3
"""
测试牌堆管理系统
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.models.deck_manager import DeckManager, DeckConfig
from src.core.models.enums import CardType
from config.cards import DECK_CONFIGS


def deck_system():
    """测试牌堆系统"""
    print("=== 测试牌堆管理系统 ===")

    # 创建牌堆管理器
    manager = DeckManager()

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
    manager.initialize_decks(deck_configs)

    # 显示牌堆状态
    print("\n=== 初始牌堆状态 ===")
    status = manager.get_deck_status()
    for card_type, stats in status.items():
        print(f"{card_type.value}: 剩余{stats['remaining']}张, "
              f"弃牌{stats['discarded']}张, 总计{stats['total']}张")

    # 测试抽牌
    print("\n=== 测试抽牌 ===")
    test_draws = [
        (CardType.CATTLE, 5),
        (CardType.ACTION_A, 3),
        (CardType.MISSION, 2)
    ]

    for card_type, count in test_draws:
        cards = manager.draw_cards(card_type, count)
        print(f"从{card_type.value}牌堆抽取{count}张牌:")
        for i, card in enumerate(cards):
            print(f"  {i + 1}. {card.name} (价值: {card.base_value})")

    # 显示抽牌后的状态
    print("\n=== 抽牌后状态 ===")
    status = manager.get_deck_status()
    for card_type, stats in status.items():
        print(f"{card_type.value}: 剩余{stats['remaining']}张, "
              f"弃牌{stats['discarded']}张, 总计{stats['total']}张")

    # 测试弃牌
    print("\n=== 测试弃牌 ===")
    # 抽取一些牌然后弃掉
    cards_to_discard = manager.draw_cards(CardType.ACTION_B, 2)
    print(f"抽取了 {len(cards_to_discard)} 张动作B牌准备弃掉")

    manager.discard_cards(CardType.ACTION_B, cards_to_discard)
    print("已弃牌")

    # 显示弃牌后的状态
    status = manager.get_deck_status()
    action_b_status = status[CardType.ACTION_B]
    print(f"动作B牌堆: 剩余{action_b_status['remaining']}张, "
          f"弃牌{action_b_status['discarded']}张")

    # 测试重新洗牌
    print("\n=== 测试重新洗牌 ===")
    manager.reshuffle_deck(CardType.ACTION_B)

    # 显示重新洗牌后的状态
    status = manager.get_deck_status()
    action_b_status = status[CardType.ACTION_B]
    print(f"重新洗牌后动作B牌堆: 剩余{action_b_status['remaining']}张, "
          f"弃牌{action_b_status['discarded']}张")

    # 测试序列化
    print("\n=== 测试序列化 ===")
    manager_dict = manager.to_dict()
    print("序列化成功")

    # 测试反序列化
    new_manager = DeckManager.from_dict(manager_dict)
    print("反序列化成功")

    # 验证反序列化后的状态
    new_status = new_manager.get_deck_status()
    print("\n=== 反序列化后状态 ===")
    for card_type, stats in new_status.items():
        print(f"{card_type.value}: 剩余{stats['remaining']}张, "
              f"弃牌{stats['discarded']}张, 总计{stats['total']}张")

    return True


def deck_exhaustion():
    """测试牌堆耗尽的情况"""
    print("\n=== 测试牌堆耗尽 ===")

    manager = DeckManager()

    # 将配置转换为DeckConfig对象
    deck_configs = {}
    for card_type_str, config in DECK_CONFIGS.items():
        card_type = CardType(card_type_str)
        deck_configs[card_type] = DeckConfig(
            card_type=card_type,
            total_count=config["total_count"],
            card_prototypes=config["card_prototypes"]
        )

    manager.initialize_decks(deck_configs)

    # 抽光所有牛牌
    cattle_deck = manager.get_deck(CardType.CATTLE)
    if cattle_deck:
        total_cattle = cattle_deck.get_remaining_count()
        print(f"牛牌堆初始有 {total_cattle} 张牌")

        # 抽取所有牌
        all_cattle_cards = cattle_deck.draw(total_cattle + 10)  # 尝试抽取比总数多的牌
        print(f"实际抽取了 {len(all_cattle_cards)} 张牛牌")

        # 检查牌堆状态
        status = manager.get_deck_status()
        cattle_status = status[CardType.CATTLE]
        print(f"牛牌堆状态: 剩余{cattle_status['remaining']}张, "
              f"弃牌{cattle_status['discarded']}张")

    return True


if __name__ == "__main__":
    success1 = deck_system()
    success2 = deck_exhaustion()

    if success1 and success2:
        print("\n🎉 所有测试通过!")
    else:
        print("\n💥 测试失败!")
        sys.exit(1)