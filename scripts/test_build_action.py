#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_state import GameState
from src.core.actions.build import BuildAction
from src.core.models.player import PlayerState, ResourceSet
from src.core.models.enums import PlayerColor


def test_build_action():
    # 创建游戏状态
    game_state = GameState(session_id="test_build_session")

    # 添加玩家
    player = PlayerState(
        player_id="player1",
        user_id="user1",
        player_color=PlayerColor.RED,
        display_name="建造测试玩家",
        resources=ResourceSet(money=10, workers=3)
    )
    game_state.players = [player]

    # 初始化版图状态
    if not hasattr(game_state.board_state, 'available_locations'):
        game_state.board_state.available_locations = [5, 10, 15]
    if not hasattr(game_state.board_state, 'player_buildings'):
        game_state.board_state.player_buildings = {}

    print("初始状态:")
    print(f"玩家金钱: {player.resources.money}")
    print(f"已建建筑: {player.buildings_built_count}")
    print(f"可用位置: {game_state.board_state.available_locations}")

    # 测试建造车站
    build_action = BuildAction({
        "player_id": "player1",
        "location_id": 5,
        "building_type": "station"
    })

    result = build_action.execute(game_state)
    print("\n建造车站结果:", result)
    print(f"建造后金钱: {player.resources.money}")
    print(f"建造后建筑数: {player.buildings_built_count}")
    print(f"建造后可用位置: {game_state.board_state.available_locations}")
    print(f"玩家建筑列表: {game_state.board_state.player_buildings.get('player1', [])}")

    # 测试建造牧场
    build_action2 = BuildAction({
        "player_id": "player1",
        "location_id": 10,
        "building_type": "ranch"
    })

    result2 = build_action2.execute(game_state)
    print("\n建造牧场结果:", result2)
    print(f"建造后金钱: {player.resources.money}")
    print(f"建造后工人数: {player.resources.workers}")  # 牧场应该给工人奖励
    print(f"建造后建筑数: {player.buildings_built_count}")

    # 测试资源不足的情况
    build_action3 = BuildAction({
        "player_id": "player1",
        "location_id": 15,
        "building_type": "telegraph"  # 电报站需要4金钱，但玩家只剩3金钱
    })

    result3 = build_action3.execute(game_state)
    print("\n资源不足测试结果:", result3)


if __name__ == "__main__":
    test_build_action()