from abc import ABC, abstractmethod
from typing import Dict, Any
from ..game_state import GameState
from ..models.enums import ActionType


class GameAction(ABC):
    """游戏行动基类"""

    def __init__(self, action_type: ActionType, action_data: Dict[str, Any]):
        self.action_type = action_type
        self.action_data = action_data
        self._validate_data()

    @abstractmethod
    def _validate_data(self):
        """验证行动数据"""
        pass

    @abstractmethod
    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行行动并返回结果"""
        pass

    @abstractmethod
    def is_valid(self, game_state: GameState) -> bool:
        """检查行动是否合法"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "action_type": self.action_type.value,
            "action_data": self.action_data
        }