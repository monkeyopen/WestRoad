from typing import Dict, List, Optional, Tuple
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