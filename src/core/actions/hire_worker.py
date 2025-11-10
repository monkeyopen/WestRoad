from typing import Dict, Any
from .base import GameAction
from ..game_state import GameState
from ..models.enums import ActionType


class HireWorkerAction(GameAction):
    """雇佣工人行动类"""

    def __init__(self, action_data: Dict[str, Any]):
        super().__init__(ActionType.HIRE_WORKER, action_data)
        self._validate_data()  # 在初始化时验证数据

    def _validate_data(self):
        """验证雇佣工人行动数据"""
        required_fields = ["player_id", "worker_type"]
        for field in required_fields:
            if field not in self.action_data:
                raise ValueError(f"雇佣工人行动缺少必要字段: {field}")

        # 验证工人类型是否有效
        valid_worker_types = ["craftsman", "engineer", "brakeman", "telegrapher"]
        if self.action_data["worker_type"] not in valid_worker_types:
            raise ValueError(f"无效的工人类型: {self.action_data['worker_type']}")

    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行雇佣工人行动"""
        if not self.is_valid(game_state):
            return {"success": False, "message": "雇佣工人行动不合法"}

        player_id = self.action_data["player_id"]
        worker_type = self.action_data["worker_type"]

        player = game_state.get_player_by_id(player_id)
        if not player:
            return {"success": False, "message": "玩家不存在"}

        # 获取雇佣成本
        cost = self._get_worker_cost(worker_type)

        # 检查玩家是否有足够资源
        if player.resources.money < cost:
            return {"success": False, "message": f"资源不足，需要{cost}金钱"}

        # 扣除资源
        player.resources.money -= cost

        # 增加工人
        if worker_type == "craftsman":
            player.resources.craftsmen += 1
        elif worker_type == "engineer":
            player.resources.engineers += 1
        elif worker_type == "brakeman":
            player.resources.brakemen += 1
        elif worker_type == "telegrapher":
            player.resources.telegraphers += 1

        # 更新游戏状态版本
        game_state.increment_version()

        return {
            "success": True,
            "message": f"雇佣{worker_type}成功",
            "player_id": player_id,
            "worker_type": worker_type,
            "cost": cost,
            "new_money": player.resources.money
        }

    def is_valid(self, game_state: GameState) -> bool:
        """验证行动是否合法"""
        from ..rules.validator import ActionValidator
        validator = ActionValidator(game_state)
        is_valid, _ = validator.validate_action(self.action_type, self.action_data)
        return is_valid

    def _get_worker_cost(self, worker_type: str) -> int:
        """获取工人雇佣成本"""
        costs = {
            "craftsman": 2,
            "engineer": 3,
            "brakeman": 1,
            "telegrapher": 4
        }
        return costs.get(worker_type, 2)  # 默认成本为2