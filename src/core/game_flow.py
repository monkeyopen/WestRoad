from typing import List, Dict, Any
from .game_state import GameState
from .models.enums import GamePhase

class GameFlowController:
    def __init__(self, game_state: GameState):
        self.game_state = game_state

    def next_phase(self):
        """推进游戏阶段"""
        if self.game_state.current_phase == GamePhase.SETUP:
            self.game_state.current_phase = GamePhase.PLAYER_TURN
        elif self.game_state.current_phase == GamePhase.PLAYER_TURN:
            # 检查所有玩家是否已完成回合
            if self._all_players_completed_turn():
                self.game_state.current_phase = GamePhase.CATTLE_SALE
        elif self.game_state.current_phase == GamePhase.CATTLE_SALE:
            self.game_state.current_phase = GamePhase.END_GAME
        # 重置或更新玩家索引等
        self.game_state.increment_version()

    def _all_players_completed_turn(self) -> bool:
        # 简单实现：检查所有玩家是否已行动
        return True  # 实际应根据游戏状态判断