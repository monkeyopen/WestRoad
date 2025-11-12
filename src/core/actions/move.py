from typing import Dict, Any
from .base import GameAction
from ..game_state import GameState
from ..models.enums import ActionType


class MoveAction(GameAction):
    """移动行动 - 支持普通移动和固定步数移动"""

    def __init__(self, action_data: Dict[str, Any]):
        super().__init__(ActionType.MOVE, action_data)
        self._validate_data()

    def _validate_data(self):
        """验证移动行动数据"""
        required_fields = ["player_id", "target_location"]
        for field in required_fields:
            if field not in self.action_data:
                raise ValueError(f"移动行动缺少必要字段: {field}")

        # steps 现在是可选字段，如果未提供则计算步数
        if "steps" not in self.action_data:
            # 如果没有提供steps，则根据当前位置和目标位置计算
            pass  # 在执行时计算

    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行移动行动"""
        if not self.is_valid(game_state):
            return {"success": False, "message": "移动行动不合法"}

        player_id = self.action_data["player_id"]
        target_location = self.action_data["target_location"]

        player = game_state.get_player_by_id(player_id)
        if not player:
            return {"success": False, "message": "玩家不存在"}

        previous_position = player.position

        # 计算实际移动步数
        if "steps" in self.action_data:
            # 如果指定了步数，使用指定步数
            steps = self.action_data["steps"]
        else:
            # 否则计算实际距离
            steps = abs(target_location - previous_position)

        # 检查是否是固定1步移动（建筑物提供的特殊移动）
        is_fixed_one_step = self.action_data.get("fixed_one_step", False)
        if is_fixed_one_step:
            # 固定1步移动的验证：目标位置必须与当前位置相邻
            if abs(target_location - previous_position) != 1:
                return {"success": False, "message": "固定1步移动只能移动到相邻位置"}
            steps = 1  # 强制设置为1步

        # 验证移动合法性
        if not self._is_valid_move(game_state, previous_position, target_location, steps):
            return {"success": False, "message": "移动路径不合法"}

        # 更新玩家位置
        player.previous_position = previous_position
        player.position = target_location

        # 如果是普通移动（非建筑物提供的固定移动），可能需要消耗资源
        if not is_fixed_one_step:
            # 这里可以添加移动消耗逻辑，比如消耗工人等
            # player.resources.workers -= steps  # 示例：每步消耗1工人
            pass

        # 更新游戏状态版本
        game_state.increment_version()

        return {
            "success": True,
            "message": f"移动{steps}步成功" + ("（建筑物特殊移动）" if is_fixed_one_step else ""),
            "player_id": player_id,
            "from_position": previous_position,
            "to_position": target_location,
            "steps_used": steps,
            "is_fixed_one_step": is_fixed_one_step
        }

    def is_valid(self, game_state: GameState) -> bool:
        """验证行动是否合法"""
        from ..rules.validator import ActionValidator
        validator = ActionValidator(game_state)
        is_valid, _ = validator.validate_action(self.action_type, self.action_data)
        return is_valid

    def _is_valid_move(self, game_state: GameState, from_pos: int, to_pos: int, steps: int) -> bool:
        """验证移动是否合法"""
        # 这里实现路径验证逻辑
        # 简化实现：检查目标位置是否在地图节点中
        if hasattr(game_state.board_state, 'nodes'):
            return to_pos in game_state.board_state.nodes
        return 0 <= to_pos <= 50