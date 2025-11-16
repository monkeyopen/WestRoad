from src.core.models.player import PlayerState, ResourceSet, CardManager
from src.core.models.enums import PlayerColor, AuxiliaryAbility, WorkerType


def player_initialization():
    """测试玩家初始化"""
    player = PlayerState(
        player_id="test_player",
        user_id="test_user",
        player_color=PlayerColor.RED,
        display_name="测试玩家"
    )

    # 检查基础属性
    assert player.player_id == "test_player"
    assert player.display_name == "测试玩家"

    # 检查资源初始化
    assert player.resources.money == 0
    assert player.resources.temporary_honor == 0

    # 检查工人数量
    assert player.resources.cowboys == 0
    assert player.resources.drivers == 0
    assert player.resources.builders == 0

    # 检查辅助能力
    assert len(player.auxiliary_abilities) == 16


def auxiliary_abilities():
    """测试辅助能力系统"""
    player = PlayerState(
        player_id="test_player",
        user_id="test_user",
        player_color=PlayerColor.RED,
        display_name="测试玩家"
    )

    # 测试能力获取
    ability = player.get_auxiliary_ability(AuxiliaryAbility.GOLD_1)
    assert ability is not None
    assert ability.description == "获得1金钱"
    assert ability.is_usable

    # 测试能力使用
    assert player.can_use_ability(AuxiliaryAbility.GOLD_1)
    assert player.use_ability(AuxiliaryAbility.GOLD_1)
    assert ability.used_count == 1

    # 测试能力重置
    player.reset_abilities()
    assert ability.is_usable


def card_management():
    """测试卡牌管理"""
    player = PlayerState(
        player_id="test_player",
        user_id="test_user",
        player_color=PlayerColor.RED,
        display_name="测试玩家"
    )

    # 初始化牌堆
    test_cards = [
        {"card_id": "card_1", "name": "测试卡1", "card_type": "cattle"},
        {"card_id": "card_2", "name": "测试卡2", "card_type": "objective"},
        {"card_id": "card_3", "name": "测试卡3", "card_type": "cattle"}
    ]
    player.card_manager.draw_pile = test_cards.copy()

    # 测试抽牌
    drawn_cards = player.draw_cards(2)
    assert len(drawn_cards) == 2
    assert len(player.card_manager.hand_cards) == 2
    assert len(player.card_manager.draw_pile) == 1

    # 测试打出目标卡
    player.play_objective("card_2")
    assert len(player.card_manager.played_objectives) == 1
    assert len(player.card_manager.hand_cards) == 1

    # 测试获得牌
    station_master = {"card_id": "sm_1", "name": "站长标记", "card_type": "station_master"}
    player.acquire_card(station_master)
    assert len(player.card_manager.acquired_cards) == 1

    # 测试按类型获取牌
    station_masters = player.get_acquired_cards_by_type("station_master")
    assert len(station_masters) == 1
    assert station_masters[0]["name"] == "站长标记"


def worker_management():
    """测试工人管理"""
    player = PlayerState(
        player_id="test_player",
        user_id="test_user",
        player_color=PlayerColor.RED,
        display_name="测试玩家",
        resources=ResourceSet(cowboys=2, builders=1, drivers=1)
    )

    workers = player.get_total_workers()
    assert workers[WorkerType.COWBOY] == 2
    assert workers[WorkerType.BUILDER] == 1
    assert workers[WorkerType.DRIVER] == 1


def serialization():
    """测试序列化"""
    player = PlayerState(
        player_id="test_player",
        user_id="test_user",
        player_color=PlayerColor.RED,
        display_name="测试玩家",
        resources=ResourceSet(money=10, temporary_honor=5, cowboys=2)
    )

    # 添加一些卡牌
    player.card_manager.hand_cards = [{"card_id": "hand_1", "name": "手牌1"}]
    player.card_manager.played_objectives = [{"card_id": "obj_1", "name": "目标1"}]
    player.card_manager.acquired_cards = [{"card_id": "acq_1", "name": "获得牌1"}]

    # 序列化
    player_dict = player.to_dict()

    # 反序列化
    new_player = PlayerState.from_dict(player_dict)

    # 验证数据一致性
    assert new_player.player_id == player.player_id
    assert new_player.resources.temporary_honor == 5
    assert new_player.resources.cowboys == 2
    assert len(new_player.card_manager.hand_cards) == 1
    assert len(new_player.card_manager.played_objectives) == 1
    assert len(new_player.card_manager.acquired_cards) == 1
    assert len(new_player.auxiliary_abilities) == 16

if __name__ == "__main__":
    player_initialization()
    auxiliary_abilities()
    card_management()
    worker_management()
    serialization()