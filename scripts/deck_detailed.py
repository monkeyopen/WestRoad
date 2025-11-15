#!/usr/bin/env python3
"""
增强版牌堆测试脚本 - 可以打印指定牌堆的剩余牌信息
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.models.deck_manager import DeckManager, DeckConfig
from src.core.models.enums import CardType
from config.cards import DECK_CONFIGS


def print_deck_status(manager, card_type):
    """打印指定牌堆的详细状态"""
    deck = manager.get_deck(card_type)
    if not deck:
        print(f"❌ 未找到牌堆: {card_type.value}")
        return

    status = manager.get_deck_status()
    deck_status = status.get(card_type, {})

    print(f"\n=== {card_type.value.upper()} 牌堆状态 ===")
    print(f"剩余牌数: {deck_status.get('remaining', 0)}")
    print(f"弃牌数: {deck_status.get('discarded', 0)}")
    print(f"总牌数: {deck_status.get('total', 0)}")

    # 打印剩余牌的前10张（如果有很多牌）
    if deck.cards:
        print(f"\n剩余牌示例 (前{min(10, len(deck.cards))}张):")
        for i, card in enumerate(deck.cards[:10]):
            print(f"  {i + 1}. {card.name} (价值: {card.base_value}, 成本: {card.cost})")
            if card.special_ability:
                print(f"     特殊能力: {card.special_ability}")
            if card.description:
                print(f"     描述: {card.description}")
    else:
        print("剩余牌: 无")

    # 打印弃牌堆的前5张（如果有）
    if deck.discarded:
        print(f"\n弃牌堆示例 (前{min(5, len(deck.discarded))}张):")
        for i, card in enumerate(deck.discarded[:5]):
            print(f"  {i + 1}. {card.name} (价值: {card.base_value})")
    else:
        print("弃牌堆: 空")


def print_all_decks_status(manager):
    """打印所有牌堆的状态摘要"""
    print("\n=== 所有牌堆状态摘要 ===")
    status = manager.get_deck_status()

    for card_type, stats in status.items():
        print(f"{card_type.value}: 剩余{stats['remaining']}张, "
              f"弃牌{stats['discarded']}张, 总计{stats['total']}张")


def deck_system_detailed():
    """详细测试牌堆系统"""
    print("=== 详细测试牌堆管理系统 ===")

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

    # 打印所有牌堆状态摘要
    print_all_decks_status(manager)

    # 打印指定牌堆的详细信息
    print("\n=== 初始化后的牌堆详细信息 ===")
    for card_type in [CardType.CATTLE, CardType.ACTION_A, CardType.MISSION]:
        print_deck_status(manager, card_type)

    # 测试抽牌并查看变化
    print("\n=== 测试抽牌后的变化 ===")

    # 从牛牌堆抽取5张牌
    cattle_cards = manager.draw_cards(CardType.CATTLE, 5)
    print(f"从牛牌堆抽取了 {len(cattle_cards)} 张牌:")
    for i, card in enumerate(cattle_cards):
        print(f"  {i + 1}. {card.name} (价值: {card.base_value})")

    # 从动作A牌堆抽取3张牌
    action_a_cards = manager.draw_cards(CardType.ACTION_A, 3)
    print(f"\n从动作A牌堆抽取了 {len(action_a_cards)} 张牌:")
    for i, card in enumerate(action_a_cards):
        print(f"  {i + 1}. {card.name} (特殊能力: {card.special_ability})")

    # 打印抽牌后的状态
    print("\n=== 抽牌后的牌堆状态 ===")
    print_all_decks_status(manager)

    # 打印抽牌后的详细信息
    print("\n=== 抽牌后的详细信息 ===")
    for card_type in [CardType.CATTLE, CardType.ACTION_A]:
        print_deck_status(manager, card_type)

    # 测试弃牌
    print("\n=== 测试弃牌 ===")

    # 将抽取的牛牌弃掉2张
    if cattle_cards:
        cards_to_discard = cattle_cards[:2]
        manager.discard_cards(CardType.CATTLE, cards_to_discard)
        print(f"已将 {len(cards_to_discard)} 张牛牌放入弃牌堆")

        # 打印弃牌后的状态
        print("\n=== 弃牌后的牛牌堆状态 ===")
        print_deck_status(manager, CardType.CATTLE)

    # 测试重新洗牌
    print("\n=== 测试重新洗牌 ===")

    # 将动作A牌堆的弃牌重新洗牌
    action_a_deck = manager.get_deck(CardType.ACTION_A)
    if action_a_deck and action_a_deck.discarded:
        print(f"动作A牌堆弃牌数: {len(action_a_deck.discarded)}")
        manager.reshuffle_deck(CardType.ACTION_A)

        # 打印重新洗牌后的状态
        print("\n=== 重新洗牌后的动作A牌堆状态 ===")
        print_deck_status(manager, CardType.ACTION_A)

    # 测试序列化和反序列化
    print("\n=== 测试序列化和反序列化 ===")

    # 序列化
    manager_dict = manager.to_dict()
    print("序列化成功")

    # 反序列化
    new_manager = DeckManager.from_dict(manager_dict)
    print("反序列化成功")

    # 验证反序列化后的状态
    print("\n=== 反序列化后的牌堆状态 ===")
    print_all_decks_status(new_manager)

    # 打印反序列化后的详细信息
    print("\n=== 反序列化后的详细信息 ===")
    for card_type in [CardType.CATTLE, CardType.ACTION_A]:
        print_deck_status(new_manager, card_type)

    return True


def interactive_test():
    """交互式测试 - 允许用户选择查看特定牌堆"""
    print("=== 交互式牌堆测试 ===")

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

    # 交互式菜单
    while True:
        print("\n" + "=" * 50)
        print("牌堆测试菜单")
        print("=" * 50)
        print("1. 查看所有牌堆状态摘要")
        print("2. 查看牛牌堆详细信息")
        print("3. 查看动作A牌堆详细信息")
        print("4. 查看动作B牌堆详细信息")
        print("5. 查看动作C牌堆详细信息")
        print("6. 查看任务牌堆详细信息")
        print("7. 从牛牌堆抽牌")
        print("8. 从动作A牌堆抽牌")
        print("9. 弃掉牛牌")
        print("10. 重新洗牌动作A牌堆")
        print("11. 查看测试牌堆详细信息")
        print("12. 从测试牌堆抽牌")
        print("0. 退出")

        choice = input("\n请选择操作 (0-10): ").strip()

        if choice == "0":
            print("退出测试")
            break

        elif choice == "1":
            print_all_decks_status(manager)

        elif choice == "2":
            print_deck_status(manager, CardType.CATTLE)

        elif choice == "3":
            print_deck_status(manager, CardType.ACTION_A)

        elif choice == "4":
            print_deck_status(manager, CardType.ACTION_B)

        elif choice == "5":
            print_deck_status(manager, CardType.ACTION_C)

        elif choice == "6":
            print_deck_status(manager, CardType.MISSION)

        elif choice == "7":
            try:
                count = int(input("请输入要抽取的牌数: "))
                cards = manager.draw_cards(CardType.CATTLE, count)
                print(f"抽取了 {len(cards)} 张牛牌:")
                for i, card in enumerate(cards):
                    print(f"  {i + 1}. {card.name} (价值: {card.base_value})")
            except ValueError:
                print("请输入有效的数字")

        elif choice == "8":
            try:
                count = int(input("请输入要抽取的牌数: "))
                cards = manager.draw_cards(CardType.ACTION_A, count)
                print(f"抽取了 {len(cards)} 张动作A牌:")
                for i, card in enumerate(cards):
                    print(f"  {i + 1}. {card.name} (特殊能力: {card.special_ability})")
            except ValueError:
                print("请输入有效的数字")

        elif choice == "9":
            try:
                count = int(input("请输入要弃掉的牛牌数: "))
                # 先抽取牌
                cards = manager.draw_cards(CardType.CATTLE, count)
                if cards:
                    manager.discard_cards(CardType.CATTLE, cards)
                    print(f"已弃掉 {len(cards)} 张牛牌")
                else:
                    print("没有牌可弃")
            except ValueError:
                print("请输入有效的数字")

        elif choice == "10":
            manager.reshuffle_deck(CardType.ACTION_A)
            print("已重新洗牌动作A牌堆")

        elif choice == "11":
            print_deck_status(manager, CardType.TEST)

        elif choice == "12":
            try:
                count = int(input("请输入要抽取的牌数: "))
                cards = manager.draw_cards(CardType.TEST, count)
                print(f"抽取了 {len(cards)} 张测试牌:")
                for i, card in enumerate(cards):
                    print(f"  {i + 1}. {card.name} (价值: {card.base_value})")
            except ValueError:
                print("请输入有效的数字")

        else:
            print("无效选择，请重新输入")

    return True


if __name__ == "__main__":
    print("选择测试模式:")
    print("1. 自动详细测试")
    print("2. 交互式测试")

    mode = input("请输入模式 (1 或 2): ").strip()

    if mode == "1":
        success = deck_system_detailed()
        print("\n🎉 详细测试完成!" if success else "\n💥 测试失败!")
    elif mode == "2":
        success = interactive_test()
        print("\n🎉 交互式测试完成!" if success else "\n💥 测试失败!")
    else:
        print("无效选择")
        sys.exit(1)
