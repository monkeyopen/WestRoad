from typing import Dict, Any
from .base import GameAction
from ..game_state import GameState
from ..models.enums import ActionType


class SellCattleAction(GameAction):
    """卖出牛群行动"""

    def __init__(self, action_data: Dict[str, Any]):
        super().__init__(ActionType.SELL_CATTLE, action_data)
        self._validate_data()  # 在初始化时验证数据

    def _validate_data(self):
        """验证卖出牛群行动数据"""
        required_fields = ["player_id", "card_id"]
        for field in required_fields:
            if field not in self.action_data:
                raise ValueError(f"卖出牛群行动缺少必要字段: {field}")

    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行卖出牛群行动"""
        if not self.is_valid(game_state):
            return {"success": False, "message": "卖出牛群行动不合法"}

        player_id = self.action_data["player_id"]
        card_id = self.action_data["card_id"]

        player = game_state.get_player_by_id(player_id)
        if not player:
            return {"success": False, "message": "玩家不存在"}

        # 在玩家手牌中查找卡牌
        card = None
        for c in player.hand_cards:
            if c.get("card_id") == card_id:
                card = c
                break

        if not card:
            return {"success": False, "message": "牛牌不在手牌中"}

        # 计算牛牌价值（基础价值 + 可能的加成）
        base_value = card.get("base_value", 3)
        # 这里可以添加其他价值计算逻辑，如品种加成、特殊能力等
        value = base_value

        # 增加玩家金钱
        player.resources.money += value

        # 增加胜利点数
        player.victory_points += value

        # 从手牌中移除牛牌
        player.hand_cards.remove(card)

        # 增加卖出计数
        player.cattle_sold_count += 1

        # 更新游戏状态版本
        game_state.increment_version()

        return {
            "success": True,
            "message": "卖出牛群成功",
            "player_id": player_id,
            "card_id": card_id,
            "value": value,
            "new_money": player.resources.money,
            "new_victory_points": player.victory_points
        }

    def is_valid(self, game_state: GameState) -> bool:
        """验证行动是否合法"""
        from ..rules.validator import ActionValidator
        validator = ActionValidator(game_state)
        is_valid, _ = validator.validate_action(self.action_type, self.action_data)
        return is_valid