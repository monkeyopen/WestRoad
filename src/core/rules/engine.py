from typing import Dict, Any
from .validator import ActionValidator
from ..game_state import GameState
from ..models.enums import ActionType, GamePhase

class RuleEngine:
    """游戏规则引擎 - 执行游戏规则"""

    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.validator = ActionValidator(game_state)

    def execute_action(self, action_type: ActionType, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行游戏行动

        Args:
            action_type: 行动类型
            action_data: 行动数据

        Returns:
            执行结果
        """
        # 1. 验证行动
        is_valid, message = self.validator.validate_action(action_type, action_data)
        if not is_valid:
            return {
                "success": False,
                "message": message,
                "action_type": action_type.value
            }

        # 2. 执行行动
        try:
            result = self._execute_validated_action(action_type, action_data)
            result["success"] = True
            result["message"] = "行动执行成功"
            result["action_type"] = action_type.value

            # 3. 更新游戏状态
            self._update_game_state(action_type, action_data)

            return result
        except Exception as e:
            return {
                "success": False,
                "message": f"行动执行失败: {str(e)}",
                "action_type": action_type.value
            }

    def _execute_validated_action(self, action_type: ActionType, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行已验证的行动"""
        executor_method = getattr(self, f"_execute_{action_type.value}", None)
        if executor_method:
            return executor_method(action_data)
        else:
            raise NotImplementedError(f"行动类型 {action_type} 未实现")

    def _execute_move(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行移动行动"""
        player_id = action_data["player_id"]
        steps = action_data["steps"]
        target_location = action_data["target_location"]

        player = self.game_state.get_player_by_id(player_id)
        previous_position = player.position

        # 更新玩家位置
        player.previous_position = previous_position
        player.position = target_location

        return {
            "player_id": player_id,
            "from_position": previous_position,
            "to_position": target_location,
            "steps_used": steps,
            "new_position": target_location
        }

    def _execute_build(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行建造行动"""
        player_id = action_data["player_id"]
        location_id = action_data["location_id"]
        building_type = action_data["building_type"]

        player = self.game_state.get_player_by_id(player_id)

        # 消耗资源（简化）
        building_cost = self._get_building_cost(building_type)
        player.resources.money -= building_cost

        # 更新版图状态
        # TODO: 实际实现需要更新版图状态
        # location = self.game_state.board_state.locations[location_id]
        # location.owner_id = player_id

        # 更新玩家统计
        player.buildings_built_count += 1

        return {
            "player_id": player_id,
            "location_id": location_id,
            "building_type": building_type,
            "cost": building_cost
        }

    def _update_game_state(self, action_type: ActionType, action_data: Dict[str, Any]):
        """更新游戏状态"""
        # 记录行动历史
        self.game_state.action_history.append({
            "action_type": action_type.value,
            "action_data": action_data,
            "timestamp": self.game_state.last_updated.isoformat(),
            "version": self.game_state.version
        })

        # 递增版本号
        self.game_state.increment_version()

        # 检查是否需要切换回合
        if self._should_end_turn(action_type):
            self._advance_to_next_player()

    def _should_end_turn(self, action_type: ActionType) -> bool:
        """检查是否应该结束当前回合"""
        # 某些行动会自动结束回合
        end_turn_actions = [ActionType.MOVE, ActionType.BUILD]
        return action_type in end_turn_actions

    def _advance_to_next_player(self):
        """切换到下一个玩家"""
        current_index = self.game_state.current_player_index
        next_index = (current_index + 1) % len(self.game_state.players)

        self.game_state.current_player_index = next_index
        self.game_state.current_round += 1 if next_index == 0 else 0

        # TODO: 检查游戏结束条件

    def _get_building_cost(self, building_type: str) -> int:
        """获取建筑成本（简化）"""
        costs = {
            "station": 3,
            "ranch": 2,
            "hazard": 1
        }
        return costs.get(building_type, 1)