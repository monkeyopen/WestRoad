from typing import Dict, Any
from .base import GameAction
from ..game_state import GameState
from ..models.enums import ActionType


class UseAbilityAction(GameAction):
    """使用能力行动"""

    def __init__(self, action_data: Dict[str, Any]):
        super().__init__(ActionType.USE_ABILITY, action_data)

    def execute(self, game_state: GameState) -> Dict[str, Any]:
        """执行使用能力行动"""
        if not self.is_valid(game_state):
            return {"success": False, "message": "使用能力行动不合法"}

        player_id = self.action_data["player_id"]
        card_id = self.action_data["card_id"]
        ability_type = self.action_data.get("ability_type")  # 可选参数

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

        # 检查卡牌是否有特殊能力
        special_ability = card.get("special_ability")
        if not special_ability:
            return {"success": False, "message": "该牛牌没有特殊能力"}

        # 根据能力类型执行效果
        # 这里实现一些常见能力效果，实际游戏可能需要更复杂的逻辑
        if special_ability == "double_move":
            # 双倍移动能力：获得额外移动点数
            player.resources.workers += 1  # 假设获得1个工人（用于移动）
            message = "使用双倍移动能力，获得1个工人"
        elif special_ability == "extra_build":
            # 额外建造能力：获得建造资源
            player.resources.money += 2  # 假设获得2金钱
            message = "使用额外建造能力，获得2金钱"
        elif special_ability == "draw_card":
            # 抽牌能力：从牛牌市场抽一张牌
            if game_state.cattle_market:
                drawn_card = game_state.cattle_market.pop()
                player.hand_cards.append(drawn_card)
                message = f"使用抽牌能力，获得牛牌: {drawn_card.get('card_id')}"
            else:
                return {"success": False, "message": "牛牌市场为空，无法抽牌"}
        else:
            return {"success": False, "message": f"未知能力: {special_ability}"}

        # 更新游戏状态版本
        game_state.increment_version()

        return {
            "success": True,
            "message": message,
            "player_id": player_id,
            "card_id": card_id,
            "ability_used": special_ability
        }

    def is_valid(self, game_state: GameState) -> bool:
        """验证行动是否合法"""
        from ..rules.validator import ActionValidator
        validator = ActionValidator(game_state)
        is_valid, _ = validator.validate_action(self.action_type, self.action_data)
        return is_valid

    def _validate_data(self):
        """验证使用能力行动数据"""
        required_fields = ["player_id", "card_id"]
        for field in required_fields:
            if field not in self.action_data:
                raise ValueError(f"使用能力行动缺少必要字段: {field}")