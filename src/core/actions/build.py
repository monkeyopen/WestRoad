from typing import Dict, Any
from .base import GameAction
from ..game_state import GameState
from ..models.enums import ActionType


class BuildAction(GameAction):
    """建造行动类"""

    def __init__(self, action_data: Dict[str, Any]):
        super().__init__(ActionType.BUILD, action_data)
        self._validate_data()  # 在初始化时验证数据

    def _validate_data(self):
        """验证建造行动数据"""
        required_fields = ["player_id", "location_id", "building_type"]
        for field in required_fields:
            if field not in self.action_data:
                raise ValueError(f"建造行动缺少必要字段: {field}")

        # 验证建筑类型是否有效
        valid_building_types = ["station", "ranch", "hazard", "telegraph", "church"]
        if self.action_data["building_type"] not in valid_building_types:
            raise ValueError(f"无效的建筑类型: {self.action_data['building_type']}")

    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行建造行动"""
        if not self.is_valid(game_state):
            return {"success": False, "message": "建造行动不合法"}

        player_id = self.action_data["player_id"]
        location_id = self.action_data["location_id"]
        building_type = self.action_data["building_type"]

        player = game_state.get_player_by_id(player_id)
        if not player:
            return {"success": False, "message": "玩家不存在"}

        # 获取建筑成本
        building_cost = self._get_building_cost(building_type)

        # 检查玩家是否有足够资源
        if player.resources.money < building_cost:
            return {"success": False, "message": f"资源不足，需要{building_cost}金钱"}

        # 检查位置是否可建造
        if not self._is_buildable_location(game_state, location_id, player_id):
            return {"success": False, "message": "该位置不可建造"}

        # 扣除资源
        player.resources.money -= building_cost

        # 更新版图状态 - 在指定位置建造建筑
        self._update_board_state(game_state, location_id, player_id, building_type)

        # 更新玩家统计
        player.buildings_built_count += 1

        # 根据建筑类型给予额外奖励
        self._apply_building_bonus(player, building_type)

        # 更新游戏状态版本
        game_state.increment_version()

        return {
            "success": True,
            "message": f"建造{building_type}成功",
            "player_id": player_id,
            "location_id": location_id,
            "building_type": building_type,
            "cost": building_cost,
            "new_money": player.resources.money,
            "buildings_built": player.buildings_built_count
        }

    def is_valid(self, game_state: GameState) -> bool:
        """验证行动是否合法"""
        from ..rules.validator import ActionValidator
        validator = ActionValidator(game_state)
        is_valid, _ = validator.validate_action(self.action_type, self.action_data)
        return is_valid

    def _get_building_cost(self, building_type: str) -> int:
        """获取建筑成本"""
        costs = {
            "station": 3,  # 车站
            "ranch": 2,  # 牧场
            "hazard": 1,  # 危险建筑
            "telegraph": 4,  # 电报站
            "church": 3  # 教堂
        }
        return costs.get(building_type, 2)  # 默认成本为2

    def _is_buildable_location(self, game_state: GameState, location_id: int, player_id: str) -> bool:
        """检查位置是否可建造"""
        # 简化实现：检查位置是否在可用位置列表中
        # 实际游戏中需要更复杂的逻辑，如检查相邻关系、所有权等
        if hasattr(game_state.board_state, 'available_locations'):
            return location_id in game_state.board_state.available_locations
        return True  # 如果没有可用位置列表，默认允许建造

    def _update_board_state(self, game_state: GameState, location_id: int, player_id: str, building_type: str):
        """更新版图状态"""
        # 简化实现：在实际游戏中需要更新版图的具体位置状态
        # 这里只是记录到玩家建筑列表中
        if not hasattr(game_state.board_state, 'player_buildings'):
            game_state.board_state.player_buildings = {}

        if player_id not in game_state.board_state.player_buildings:
            game_state.board_state.player_buildings[player_id] = []

        building_info = {
            "location_id": location_id,
            "building_type": building_type,
            "built_by": player_id
        }
        game_state.board_state.player_buildings[player_id].append(building_info)

        # 从可用位置中移除（如果有）
        if hasattr(game_state.board_state,
                   'available_locations') and location_id in game_state.board_state.available_locations:
            game_state.board_state.available_locations.remove(location_id)

    def _apply_building_bonus(self, player, building_type: str):
        """应用建筑奖励"""
        bonuses = {
            "station": {"victory_points": 1},  # 车站给1胜利点
            "ranch": {"workers": 1},  # 牧场给1工人
            "telegraph": {"money": 2},  # 电报站给2金钱
            "church": {"victory_points": 2},  # 教堂给2胜利点
            "hazard": {"certificates": 1}  # 危险建筑给1证书
        }

        bonus = bonuses.get(building_type, {})
        for resource, amount in bonus.items():
            if hasattr(player.resources, resource):
                current_value = getattr(player.resources, resource)
                setattr(player.resources, resource, current_value + amount)