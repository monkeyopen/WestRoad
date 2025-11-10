from typing import Dict, List, Optional, Tuple, Any, Tuple
from ..game_state import GameState
from ..models.enums import ActionType, GamePhase
from ..models.player import PlayerState


class ActionValidator:
    """行动验证器 - 验证游戏行动的合法性"""

    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def validate_action(self, action_type: ActionType, action_data: Dict) -> Tuple[bool, str]:
        """
        验证行动的合法性
        
        Args:
            action_type: 行动类型
            action_data: 行动数据
            
        Returns:
            (是否合法, 错误消息)
        """
        # 基础验证
        if not self._validate_basic_conditions(action_type):
            return False, "基础条件不满足"

        # 根据行动类型进行具体验证
        validator_method = getattr(self, f"_validate_{action_type.value}", None)
        if validator_method:
            return validator_method(action_data)
        else:
            return False, f"未知的行动类型: {action_type}"

    def _validate_basic_conditions(self, action_type: ActionType) -> bool:
        """验证基础游戏条件"""
        # 游戏必须已开始
        if not self.game_state.game_started:
            return False

        # 游戏不能已结束
        if self.game_state.game_finished:
            return False

        # 必须处于玩家回合阶段
        if self.game_state.current_phase != GamePhase.PLAYER_TURN:
            return False

        return True

    def _validate_move(self, action_data: Dict) -> Tuple[bool, str]:
        """验证移动行动"""
        player_id = action_data.get("player_id")
        steps = action_data.get("steps")
        target_location = action_data.get("target_location")

        # 验证玩家
        player = self.game_state.get_player_by_id(player_id)
        if not player:
            return False, "玩家不存在"

        # 验证当前玩家
        if player_id != self.game_state.current_player.player_id:
            return False, "不是当前玩家的回合"

        # 验证步数
        if not isinstance(steps, int) or steps <= 0:
            return False, "无效的移动步数"

        # 验证目标位置（简化验证，实际游戏需要更复杂的路径验证）
        if not isinstance(target_location, int) or target_location < 0:
            return False, "无效的目标位置"

        # 简化版路径验证 - 实际游戏中需要更复杂的逻辑
        current_pos = player.position
        if not self._is_valid_path(current_pos, target_location, steps):
            return False, "无效的移动路径"

        return True, "移动行动合法"

    def _validate_build(self, action_data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证建造行动"""
        player_id = action_data.get("player_id")
        location_id = action_data.get("location_id")
        building_type = action_data.get("building_type")

        if not player_id or not location_id or not building_type:
            return False, "缺少必要参数"

        player = self.game_state.get_player_by_id(player_id)
        if not player:
            return False, "玩家不存在"

        # 检查建筑类型是否有效
        valid_building_types = ["station", "ranch", "hazard", "telegraph", "church"]
        if building_type not in valid_building_types:
            return False, f"无效的建筑类型: {building_type}"

        # 检查玩家是否有足够资源（简化检查）
        building_cost = self._get_building_cost(building_type)
        if player.resources.money < building_cost:
            return False, f"资源不足，需要{building_cost}金钱"

        # 检查位置是否可建造
        if not self._is_buildable_location(location_id, player_id):
            return False, "该位置不可建造"

        return True, "验证通过"

    def _get_building_cost(self, building_type: str) -> int:
        """获取建筑成本（与BuildAction中保持一致）"""
        costs = {
            "station": 3,
            "ranch": 2,
            "hazard": 1,
            "telegraph": 4,
            "church": 3
        }
        return costs.get(building_type, 2)

    def _is_buildable_location(self, location_id: int, player_id: str) -> bool:
        """检查位置是否可建造"""
        # 简化实现
        return True

    def _validate_buy_cattle(self, action_data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证购买牛牌行动"""
        player_id = action_data.get("player_id")
        card_id = action_data.get("card_id")

        if not player_id or not card_id:
            return False, "缺少必要参数"

        player = self.game_state.get_player_by_id(player_id)
        if not player:
            return False, "玩家不存在"

        # 检查卡牌是否在牛牌市场中
        card_exists = any(card.get("card_id") == card_id for card in self.game_state.cattle_market)
        if not card_exists:
            return False, "牛牌不存在"

        # 检查玩家是否有足够金钱（具体成本需要在执行时计算）
        return True, "验证通过"

    def _validate_sell_cattle(self, action_data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证卖出牛群行动"""
        player_id = action_data.get("player_id")
        card_id = action_data.get("card_id")

        if not player_id or not card_id:
            return False, "缺少必要参数"

        player = self.game_state.get_player_by_id(player_id)
        if not player:
            return False, "玩家不存在"

        # 检查卡牌是否在玩家手牌中
        card_exists = any(card.get("card_id") == card_id for card in player.hand_cards)
        if not card_exists:
            return False, "牛牌不在手牌中"

        return True, "验证通过"

    def _validate_use_ability(self, action_data: Dict[str, Any]) -> Tuple[bool, str]:
        """验证使用能力行动"""
        player_id = action_data.get("player_id")
        card_id = action_data.get("card_id")

        if not player_id or not card_id:
            return False, "缺少必要参数"

        player = self.game_state.get_player_by_id(player_id)
        if not player:
            return False, "玩家不存在"

        # 检查卡牌是否在玩家手牌中
        card = next((card for card in player.hand_cards if card.get("card_id") == card_id), None)
        if not card:
            return False, "牛牌不在手牌中"

        # 检查卡牌是否有特殊能力
        if not card.get("special_ability"):
            return False, "该牛牌没有特殊能力"

        return True, "验证通过"

    def _validate_build(self, action_data: Dict) -> Tuple[bool, str]:
        """验证建造行动"""
        player_id = action_data.get("player_id")
        location_id = action_data.get("location_id")
        building_type = action_data.get("building_type")

        player = self.game_state.get_player_by_id(player_id)
        if not player:
            return False, "玩家不存在"

        # 验证资源
        if not self._has_sufficient_resources(player, building_type):
            return False, "资源不足"

        # 验证位置是否可建造
        if not self._is_buildable_location(location_id, player_id):
            return False, "位置不可建造"

        return True, "建造行动合法"

    def _is_valid_path(self, start: int, end: int, steps: int) -> bool:
        """验证移动路径是否合法（简化实现）"""
        # TODO: 实现实际的路径验证逻辑
        # 这里只是简单检查步数是否足够
        distance = abs(end - start)
        return steps >= distance

    def _has_sufficient_resources(self, player: PlayerState, action_type: str) -> bool:
        """检查玩家是否有足够资源"""
        # TODO: 根据行动类型检查具体资源需求
        return player.resources.money > 0  # 简化实现

    def _is_buildable_location(self, location_id: int, player_id: str) -> bool:
        """检查位置是否可建造"""
        # TODO: 实现实际的位置验证逻辑
        return True  # 简化实现
