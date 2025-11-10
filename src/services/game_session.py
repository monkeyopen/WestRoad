from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from ..core.game_state import GameState
from ..core.models.enums import GamePhase, PlayerColor
from ..core.models.player import PlayerState, ResourceSet
from ..storage.models import GameSession as GameSessionModel
from ..storage.repositories import GameSessionRepository
from ..core.models.enums import ActionType
from ..core.game_flow import GameFlowController


class GameSessionService:
    """游戏会话服务"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = GameSessionRepository(db)

    def create_session(self, creator_id: str, session_name: str, max_players: int = 4) -> Dict[str, Any]:
        """创建新游戏会话"""
        # 创建游戏状态
        game_state = GameState(session_id=str(uuid4()))
        game_state.session_name = session_name
        game_state.max_players = max_players
        game_state.created_by = creator_id

        # 添加创建者为第一个玩家
        player = PlayerState(
            player_id=str(uuid4()),
            user_id=creator_id,
            player_color=PlayerColor.RED,
            display_name=f"玩家_{creator_id[:8]}",
            resources=ResourceSet(money=10, workers=3)
        )
        game_state.players.append(player)
        game_state.player_order.append(0)

        # 保存到数据库 - 传递字典而不是对象
        session_data = {
            "id": game_state.session_id,
            "session_name": session_name,
            "max_players": max_players,
            "current_players": 1,
            "game_state": game_state.to_json(),
            "session_status": "waiting",
            "created_by": creator_id,
            "host_player_id": creator_id,
            "created_at": datetime.utcnow()
        }

        session_model = self.repository.create(session_data)

        return {
            "session_id": game_state.session_id,
            "session_name": session_name,
            "max_players": max_players,
            "current_players": 1,
            "players": [player.to_dict() for player in game_state.players]
        }

    def join_session(self, session_id: str, user_id: str, display_name: str) -> Dict[str, Any]:
        """玩家加入游戏会话"""
        from ..core.models.enums import PlayerColor  # 导入枚举

        session = self.repository.get_by_id(session_id)
        if not session:
            return {"success": False, "message": "游戏会话不存在"}

        # 反序列化游戏状态
        game_state = GameState.from_json(session.game_state)

        # 检查会话是否已满
        if len(game_state.players) >= session.max_players:
            return {"success": False, "message": "游戏会话已满"}

        # 获取下一个可用颜色
        from uuid import uuid4
        available_colors = self._get_available_colors(game_state.players)
        if not available_colors:
            return {"success": False, "message": "没有可用的玩家颜色"}

        # 创建新玩家
        player = PlayerState(
            player_id=str(uuid4()),
            user_id=user_id,
            player_color=available_colors[0],
            display_name=display_name,
            resources=ResourceSet(money=10, workers=3)
        )
        game_state.players.append(player)
        game_state.player_order.append(len(game_state.players) - 1)

        # 更新数据库
        session.game_state = game_state.to_json()
        session.current_players = len(game_state.players)
        self.repository.update(session)

        return {
            "success": True,
            "message": "加入游戏成功",
            "session_id": session_id,
            "player_id": player.player_id
        }

    def _get_available_colors(self, players: List[PlayerState]) -> List[PlayerColor]:
        """获取可用的玩家颜色"""
        from ..core.models.enums import PlayerColor

        used_colors = [p.player_color for p in players]
        available_colors = [color for color in PlayerColor if color not in used_colors]
        return available_colors

    # 在GameSessionService的start_session方法中添加地图初始化
    def start_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """开始游戏会话"""
        session = self.repository.get_by_id(session_id)
        if not session:
            return {"success": False, "message": "游戏会话不存在"}

        # 检查权限
        if session.host_player_id != user_id:
            return {"success": False, "message": "只有房主可以开始游戏"}

        # 反序列化游戏状态
        game_state = GameState.from_json(session.game_state)

        # 检查玩家数量
        if len(game_state.players) < 2:
            return {"success": False, "message": "至少需要2名玩家才能开始游戏"}

        # 初始化游戏地图
        game_state.initialize_map()  # 新增：初始化地图

        # 更新游戏状态
        game_state.current_phase = GamePhase.PLAYER_TURN

        # 更新数据库
        session.session_status = "playing"
        session.game_state = game_state.to_json()
        session.started_at = datetime.utcnow()
        self.repository.update(session)

        return {
            "session_id": session_id,
            "status": "playing",
            "current_phase": game_state.current_phase.value,
            "map_initialized": True,  # 新增：地图已初始化标志
            "current_player": game_state.current_player.to_dict() if game_state.current_player else None
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取游戏会话信息"""
        session = self.repository.get_by_id(session_id)
        if not session:
            return None

        game_state = GameState.from_json(session.game_state)

        return {
            "session_id": session.id,
            "session_name": session.session_name,
            "max_players": session.max_players,
            "current_players": session.current_players,
            "session_status": session.session_status,
            "created_by": session.created_by,
            "host_player_id": session.host_player_id,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "game_state": game_state.to_dict()
        }

    def list_sessions(self, status: str = None) -> List[Dict[str, Any]]:
        """获取游戏会话列表"""
        if status:
            sessions = self.repository.get_by_status(status)
        else:
            sessions = self.repository.get_all()

        result = []
        for session in sessions:
            result.append({
                "session_id": session.id,
                "session_name": session.session_name,
                "max_players": session.max_players,
                "current_players": session.current_players,
                "session_status": session.session_status,
                "created_by": session.created_by,
                "created_at": session.created_at.isoformat() if session.created_at else None
            })

        return result

    def execute_action(self, session_id: str, action_type: ActionType, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行游戏行动"""
        session = self.repository.get_by_id(session_id)
        if not session:
            raise ValueError("游戏会话不存在")

        game_state = GameState.from_json(session.game_state)

        # 根据行动类型创建行动实例
        if action_type == ActionType.MOVE:
            from src.core.actions.move import MoveAction
            action = MoveAction(action_data)
        elif action_type == ActionType.BUILD:
            from src.core.actions.build import BuildAction
            action = BuildAction(action_data)
        elif action_type == ActionType.HIRE_WORKER:
            from src.core.actions.hire_worker import HireWorkerAction
            action = HireWorkerAction(action_data)
        elif action_type == ActionType.BUY_CATTLE:
            from src.core.actions.buy_cattle import BuyCattleAction
            action = BuyCattleAction(action_data)
        elif action_type == ActionType.SELL_CATTLE:
            from src.core.actions.sell_cattle import SellCattleAction
            action = SellCattleAction(action_data)
        elif action_type == ActionType.USE_ABILITY:
            from src.core.actions.use_ability import UseAbilityAction
            action = UseAbilityAction(action_data)
        # ... 其他行动类型

        # 执行行动
        result = action.execute(game_state)
        if result["success"]:
            # 更新游戏状态
            session.game_state = game_state.to_json()
            self.repository.update(session)

            # 检查是否需要推进阶段
            flow_controller = GameFlowController(game_state)
            flow_controller.next_phase()

        return result