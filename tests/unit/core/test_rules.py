import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 现在可以正常导入
from src.core.game_state import GameState
from src.core.rules.engine import RuleEngine
from src.core.rules.validator import ActionValidator
from src.core.models.enums import ActionType, GamePhase, PlayerColor
from src.core.models.player import PlayerState, ResourceSet


# 将 fixture 移到类外部，成为模块级 fixture
@pytest.fixture
def sample_game_state():
    """创建示例游戏状态"""
    game_state = GameState(session_id="test_session")
    game_state.current_phase = GamePhase.PLAYER_TURN

    # 添加玩家
    player = PlayerState(
        player_id="player_001",
        user_id="user_123",
        player_color=PlayerColor.RED,
        display_name="测试玩家",
        position=5,
        resources=ResourceSet(money=10, workers=3)
    )
    game_state.players = [player]
    game_state.player_order = [0]
    game_state.current_player_index = 0

    return game_state


class TestActionValidator:
    """测试行动验证器"""

    def test_validate_move_action(self, sample_game_state):
        """测试移动行动验证"""
        validator = ActionValidator(sample_game_state)

        # 合法移动
        action_data = {
            "player_id": "player_001",
            "steps": 3,
            "target_location": 8
        }
        is_valid, message = validator.validate_action(ActionType.MOVE, action_data)
        assert is_valid
        assert "合法" in message

        # 非法移动 - 错误玩家
        invalid_data = action_data.copy()
        invalid_data["player_id"] = "invalid_player"
        is_valid, message = validator.validate_action(ActionType.MOVE, invalid_data)
        assert not is_valid


class TestRuleEngine:
    """测试规则引擎"""

    @pytest.fixture
    def rule_engine(self, sample_game_state):
        """创建规则引擎实例"""
        return RuleEngine(sample_game_state)

    def test_execute_move_action(self, rule_engine):
        """测试执行移动行动"""
        action_data = {
            "player_id": "player_001",
            "steps": 3,
            "target_location": 8
        }

        result = rule_engine.execute_action(ActionType.MOVE, action_data)

        assert result["success"]
        assert result["message"] == "行动执行成功"
        assert result["new_position"] == 8

        # 验证游戏状态已更新
        player = rule_engine.game_state.get_player_by_id("player_001")
        assert player.position == 8
        assert player.previous_position == 5

    def test_execute_invalid_action(self, rule_engine):
        """测试执行非法行动"""
        action_data = {
            "player_id": "invalid_player",  # 不存在的玩家
            "steps": 3,
            "target_location": 8
        }

        result = rule_engine.execute_action(ActionType.MOVE, action_data)

        assert not result["success"]
        assert "玩家不存在" in result["message"]