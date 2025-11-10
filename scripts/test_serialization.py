#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.game_state import GameState
from src.core.models.enums import PlayerColor, GamePhase
from src.core.models.player import PlayerState, ResourceSet, CattleCard


def test_serialization():
    # 创建游戏状态
    game_state = GameState("test_session")
    game_state.current_phase = GamePhase.PLAYER_TURN

    # 添加玩家
    player = PlayerState(
        player_id="player1",
        user_id="user1",
        player_color=PlayerColor.RED,
        display_name="测试玩家",
        resources=ResourceSet(money=10, workers=3)
    )
    game_state.players.append(player)

    # 序列化为JSON
    json_str = game_state.to_json()
    print("序列化后的JSON:")
    print(json_str)

    # 反序列化
    new_state = GameState.from_json(json_str)
    print("\n反序列化后的游戏状态:")
    print(f"会话ID: {new_state.session_id}")
    print(f"游戏阶段: {new_state.current_phase}")
    print(f"玩家数量: {len(new_state.players)}")
    if new_state.players:
        print(f"玩家1金钱: {new_state.players[0].resources.money}")


if __name__ == "__main__":
    test_serialization()