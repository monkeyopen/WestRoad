#!/usr/bin/env python3
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.game_session import GameSessionService
from src.storage.database import SessionLocal
from src.core.models.enums import ActionType


def test_full_game():
    db = SessionLocal()
    service = GameSessionService(db)

    # 创建会话
    session_data = service.create_session("player1", "测试游戏", 2)
    session_id = session_data["session_id"]

    # 加入玩家
    service.join_session(session_id, "player2", "玩家2")

    # 开始游戏
    service.start_session(session_id, "player1")

    # 执行一系列行动
    actions = [
        (ActionType.MOVE, {"player_id": "player1", "steps": 3, "target_location": 5}),
        (ActionType.BUILD, {"player_id": "player1", "location_id": 5, "building_type": "station"}),
        (ActionType.HIRE_WORKER, {"player_id": "player1", "worker_type": "craftsman"}),
        # ... 更多行动
    ]

    for action_type, action_data in actions:
        result = service.execute_action(session_id, action_type, action_data)
        print(f"执行行动: {action_type}, 结果: {result}")

    # 获取最终游戏状态
    session_info = service.get_session(session_id)
    print("游戏结束状态:", session_info)

    db.close()


if __name__ == "__main__":
    test_full_game()