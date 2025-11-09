from typing import Dict, Any
from .base import GameAction
from ..game_state import GameState
from ..models.enums import ActionType


class MoveAction(GameAction):
    """移动行动"""

    def __init__(self, action_data: Dict[str, Any]):
        super().__init__(ActionType.MOVE, action_data)

    def _validate_data(self):
        """验证移动行动数据"""
        required_fields = ["player_id", "steps", "target_location"]
        for field in required_fields:
            if field not in self.action_data:
                raise ValueError(f"移动行动缺少必要字段: {field}")

    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行移动行动"""
        if not self.is_valid(game_state):
            return {
                "success": False,
                "message": "移动行动不合法"
            }

        player_id = self.action_data["player_id"]
        steps = self.action_data["steps"]
        target_location = self.action_data["target_location"]

        player = game_state.get_player_by_id(player_id)
        previous_position = player.position

        # 更新玩家位置
        player.previous_position = previous_position
        player.position = target_location

        return {
            "success": True,
            "message": "移动成功",
            "player_id": player_id,
            "from_position": previous_position,
            "to_position": target_location,
            "steps_used": steps
        }

    def is_valid(self, game_state: GameState) -> bool:
        """检查移动行动是否合法"""
        # 使用规则引擎验证
        from ..rules.validator import ActionValidator
        validator = ActionValidator(game_state)
        is_valid, message = validator.validate_action(self.action_type, self.action_data)
        return is_valid