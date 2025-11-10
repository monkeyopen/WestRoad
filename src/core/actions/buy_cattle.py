from typing import Dict, Any
from .base import GameAction
from ..game_state import GameState
from ..models.enums import ActionType


class BuyCattleAction(GameAction):
    """购买牛牌行动"""

    def __init__(self, action_data: Dict[str, Any]):
        super().__init__(ActionType.BUY_CATTLE, action_data)

    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行购买牛牌行动"""
        if not self.is_valid(game_state):
            return {"success": False, "message": "购买牛牌行动不合法"}

        player_id = self.action_data["player_id"]
        card_id = self.action_data["card_id"]

        player = game_state.get_player_by_id(player_id)
        if not player:
            return {"success": False, "message": "玩家不存在"}

        # 在牛牌市场中查找卡牌
        card = None
        for c in game_state.cattle_market:
            if c.get("card_id") == card_id:
                card = c
                break

        if not card:
            return {"success": False, "message": "牛牌不存在或不可购买"}

        # 获取卡牌成本（假设卡牌有cost属性）
        cost = card.get("cost", 5)  # 默认成本5

        # 检查玩家是否有足够金钱
        if player.resources.money < cost:
            return {"success": False, "message": "金钱不足"}

        # 扣除金钱
        player.resources.money -= cost

        # 将牛牌添加到玩家手牌
        player.hand_cards.append(card)

        # 从牛牌市场移除该卡牌
        game_state.cattle_market.remove(card)

        # 更新游戏状态版本
        game_state.increment_version()

        return {
            "success": True,
            "message": "购买牛牌成功",
            "player_id": player_id,
            "card_id": card_id,
            "cost": cost,
            "new_money": player.resources.money
        }

    def is_valid(self, game_state: GameState) -> bool:
        """验证行动是否合法"""
        from ..rules.validator import ActionValidator
        validator = ActionValidator(game_state)
        is_valid, _ = validator.validate_action(self.action_type, self.action_data)
        return is_valid

    def _validate_data(self):
        """验证购买牛牌行动数据"""
        required_fields = ["player_id", "card_id"]
        for field in required_fields:
            if field not in self.action_data:
                raise ValueError(f"购买牛牌行动缺少必要字段: {field}")