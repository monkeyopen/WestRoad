#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_state import GameState
from src.core.actions.buy_cattle import BuyCattleAction
from src.core.actions.sell_cattle import SellCattleAction
from src.core.actions.use_ability import UseAbilityAction
from src.core.models.player import PlayerState, ResourceSet
from src.core.models.enums import PlayerColor


def test_cattle_actions():
    # 创建游戏状态
    game_state = GameState(session_id="test_session")

    # 添加玩家
    player = PlayerState(
        player_id="player1",
        user_id="user1",
        player_color=PlayerColor.RED,
        display_name="玩家1",
        resources=ResourceSet(money=10, workers=3)
    )
    game_state.players = [player]

    # 初始化牛牌市场
    game_state.cattle_market = [
        {"card_id": "cattle_001", "card_number": "1A", "base_value": 5, "cost": 3, "special_ability": "double_move"},
        {"card_id": "cattle_002", "card_number": "2B", "base_value": 3, "cost": 2, "special_ability": "extra_build"}
    ]

    print("初始状态:")
    print(f"玩家金钱: {player.resources.money}")
    print(f"玩家手牌: {len(player.hand_cards)}张")
    print(f"牛牌市场: {len(game_state.cattle_market)}张")

    # 测试购买牛牌
    buy_action = BuyCattleAction({
        "player_id": "player1",
        "card_id": "cattle_001"
    })

    result = buy_action.execute(game_state)
    print("\n购买牛牌结果:", result)
    print(f"购买后金钱: {player.resources.money}")
    print(f"购买后手牌: {len(player.hand_cards)}张")
    print(f"购买后市场: {len(game_state.cattle_market)}张")

    # 测试使用能力
    use_action = UseAbilityAction({
        "player_id": "player1",
        "card_id": "cattle_001"
    })

    result = use_action.execute(game_state)
    print("\n使用能力结果:", result)
    print(f"使用能力后工人数: {player.resources.workers}")

    # 测试卖出牛群
    sell_action = SellCattleAction({
        "player_id": "player1",
        "card_id": "cattle_001"
    })

    result = sell_action.execute(game_state)
    print("\n卖出牛群结果:", result)
    print(f"卖出后金钱: {player.resources.money}")
    print(f"卖出后胜利点: {player.victory_points}")
    print(f"卖出后手牌: {len(player.hand_cards)}张")


if __name__ == "__main__":
    test_cattle_actions()