#!/usr/bin/env python3
"""
人才市场测试脚本
测试从action_b牌堆初始化人才市场前两行的功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.models.labor_market import LaborMarket
from src.core.models.enums import WorkerType, CardType
from src.core.models.deck_manager import DeckManager, DeckConfig
from config.cards import DECK_CONFIGS


def labor_market_initialization():
    """测试人才市场初始化功能"""
    print("=== 测试人才市场初始化 ===")

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

    # 创建人才市场
    labor_market = LaborMarket(player_count=2)

    # 从action_b牌堆初始化前两行
    labor_market.initialize_from_action_b_deck(deck_manager)

    # 验证初始化结果
    print("\n=== 验证初始化结果 ===")

    # 检查前两行是否已填充
    for row in range(2):
        for col in range(4):
            worker = labor_market.get_worker(row, col)
            if worker:
                print(f"位置[{row},{col}]：{worker.value}")
            else:
                print(f"位置[{row},{col}]：空")

    # 检查后十行是否为空
    for row in range(2, 12):
        for col in range(4):
            worker = labor_market.get_worker(row, col)
            if worker:
                print(f"❌ 错误：位置[{row},{col}]应该为空，但有值: {worker.value}")
                return False
            else:
                print(f"位置[{row},{col}]：空 (正确)")

    print("✅ 人才市场初始化测试通过")
    return True


def hire_and_refill():
    """测试雇佣工人和补充功能"""
    print("\n=== 测试雇佣和补充功能 ===")

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

    # 创建人才市场
    labor_market = LaborMarket()

    # 从action_b牌堆初始化前两行
    labor_market.initialize_from_action_b_deck(deck_manager)

    # 记录初始牌堆状态
    initial_status = deck_manager.get_deck_status()[CardType.ACTION_B]
    initial_remaining = initial_status["remaining"]

    print("初始牌堆状态:")
    print(f"  Action_B牌堆: 剩余{initial_remaining}张")

    # 雇佣一个工人
    print("\n雇佣位置[0,0]的工人:")
    hired_worker = labor_market.hire_worker(0, 0)
    if hired_worker:
        print(f"  雇佣成功: {hired_worker.value}")
    else:
        print("❌ 雇佣失败")
        return False

    # 检查位置是否变为空
    worker_after_hire = labor_market.get_worker(0, 0)
    if worker_after_hire:
        print("❌ 错误：雇佣后位置应该为空")
        return False
    else:
        print("✅ 雇佣后位置为空 (正确)")

    # 补充市场
    print("\n补充人才市场:")
    labor_market.refill_market(deck_manager)

    # 检查牌堆是否又减少了一张牌
    final_status = deck_manager.get_deck_status()[CardType.ACTION_B]
    final_remaining = final_status["remaining"]

    print(f"\n最终牌堆状态:")
    print(f"  Action_B牌堆: 剩余{final_remaining}张")

    if final_remaining != initial_remaining - 1:
        print(f"❌ 错误：牌堆应该减少1张牌，但实际减少了{initial_remaining - final_remaining}张")
        return False

    print("✅ 雇佣和补充测试通过")
    return True


def serialization():
    """测试序列化和反序列化功能"""
    print("\n=== 测试序列化和反序列化 ===")

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

    # 创建人才市场
    labor_market = LaborMarket()

    # 从action_b牌堆初始化前两行
    labor_market.initialize_from_action_b_deck(deck_manager)

    # 序列化
    market_dict = labor_market.to_dict()
    print("✅ 序列化成功")

    # 反序列化
    new_market = LaborMarket.from_dict(market_dict)
    print("✅ 反序列化成功")

    # 验证反序列化后的数据
    print("\n验证反序列化结果:")

    # 检查前两行是否一致
    for row in range(2):
        for col in range(4):
            original = labor_market.get_worker(row, col)
            restored = new_market.get_worker(row, col)

            if original != restored:
                print(f"❌ 错误：位置[{row},{col}]不一致")
                print(f"  原始: {original.value if original else '空'}")
                print(f"  恢复: {restored.value if restored else '空'}")
                return False
            else:
                print(f"位置[{row},{col}]：一致")

    # 检查后十行是否一致（应该都为空）
    for row in range(2, 12):
        for col in range(4):
            original = labor_market.get_worker(row, col)
            restored = new_market.get_worker(row, col)

            if original != restored:
                print(f"❌ 错误：位置[{row},{col}]不一致")
                return False

    print("✅ 序列化和反序列化测试通过")
    return True


def insufficient_cards():
    """测试牌不足的情况"""
    print("\n=== 测试牌不足的情况 ===")

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

    # 先抽取大部分action_b牌，只留少量
    action_b_deck = deck_manager.get_deck(CardType.ACTION_B)
    if action_b_deck:
        total_cards = action_b_deck.get_remaining_count()
        cards_to_draw = total_cards - 3  # 只留3张牌
        drawn_cards = action_b_deck.draw(cards_to_draw)
        print(f"预先抽取了{len(drawn_cards)}张action_b牌，剩余{action_b_deck.get_remaining_count()}张")

    # 创建人才市场
    labor_market = LaborMarket()

    # 从action_b牌堆初始化前两行（牌不够）
    labor_market.initialize_from_action_b_deck(deck_manager)

    # 检查结果
    print("\n检查牌不足时的初始化结果:")
    filled_count = 0
    for row in range(2):
        for col in range(4):
            worker = labor_market.get_worker(row, col)
            if worker:
                filled_count += 1
                print(f"位置[{row},{col}]：{worker.value}")
            else:
                print(f"位置[{row},{col}]：空")

    print(f"总共填充了{filled_count}个位置")

    if filled_count > 3:  # 最多只能填充3个位置（因为只有3张牌）
        print("❌ 错误：填充的位置数超过了可用牌数")
        return False

    print("✅ 牌不足情况测试通过")
    return True


if __name__ == "__main__":
    print("开始人才市场测试")
    print("=" * 50)

    # 运行所有测试
    tests = [
        labor_market_initialization,
        # hire_and_refill,
        # serialization,
        # insufficient_cards
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试 {test.__name__} 发生异常: {e}")
            results.append(False)

    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print("=" * 50)

    all_passed = True
    for i, test in enumerate(tests):
        status = "✅ 通过" if results[i] else "❌ 失败"
        print(f"{i + 1}. {test.__name__}: {status}")
        if not results[i]:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉🎉 所有测试通过!")
        sys.exit(0)
    else:
        print("💥💥 部分测试失败!")
        sys.exit(1)