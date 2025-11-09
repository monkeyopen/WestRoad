from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from ..core.game_state import GameState
from ..core.models.enums import GamePhase, PlayerColor
from ..core.models.player import PlayerState, ResourceSet
from ..storage.models import GameSession as GameSessionModel
from ..storage.repositories import GameSessionRepository


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

        # 保存到数据库
        session_model = GameSessionModel(
            id=game_state.session_id,
            session_name=session_name,
            max_players=max_players,
            current_players=1,
            game_state=game_state.to_json(),
            session_status="waiting",
            created_by=creator_id,
            host_player_id=creator_id,
            created_at=datetime.utcnow()
        )

        self.repository.create(session_model)

        return {
            "session_id": game_state.session_id,
            "session_name": session_name,
            "max_players": max_players,
            "current_players": 1,
            "players": [player.to_dict() for player in game_state.players]
        }

    def join_session(self, session_id: str, user_id: str, display_name: str) -> Dict[str, Any]:
        """加入游戏会话"""
        session = self.repository.get_by_id(session_id)
        if not session:
            raise ValueError("游戏会话不存在")

        # 加载游戏状态
        game_state = GameState.from_json(session.game_state)

        # 检查是否已满
        if len(game_state.players) >= game_state.max_players:
            raise ValueError("游戏会话已满")

        # 检查是否已加入
        for player in game_state.players:
            if player.user_id == user_id:
                raise ValueError("玩家已加入该会话")

        # 添加新玩家
        player_colors = [PlayerColor.RED, PlayerColor.BLUE, PlayerColor.GREEN, PlayerColor.YELLOW]
        used_colors = [p.player_color for p in game_state.players]
        available_colors = [color for color in player_colors if color not in used_colors]

        if not available_colors:
            raise ValueError("没有可用的玩家颜色")

        new_player = PlayerState(
            player_id=str(uuid4()),
            user_id=user_id,
            player_color=available_colors[0],
            display_name=display_name,
            resources=ResourceSet(money=10, workers=3)
        )

        game_state.players.append(new_player)
        game_state.player_order.append(len(game_state.players) - 1)

        # 更新数据库
        session.current_players = len(game_state.players)
        session.game_state = game_state.to_json()
        self.repository.update(session)

        return {
            "session_id": session_id,
            "player_id": new_player.player_id,
            "player_color": new_player.player_color.value,
            "display_name": display_name
        }

    def start_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """开始游戏会话"""
        session = self.repository.get_by_id(session_id)
        if not session:
            raise ValueError("游戏会话不存在")

        # 检查权限
        if session.host_player_id != user_id:
            raise ValueError("只有房主可以开始游戏")

        # 加载游戏状态
        game_state = GameState.from_json(session.game_state)

        # 检查玩家数量
        if len(game_state.players) < 2:
            raise ValueError("至少需要2名玩家才能开始游戏")

        # 更新游戏状态
        game_state.current_phase = GamePhase.PLAYER_TURN
        game_state.game_started = True

        # 更新数据库
        session.session_status = "playing"
        session.game_state = game_state.to_json()
        session.started_at = datetime.utcnow()
        self.repository.update(session)

        return {
            "session_id": session_id,
            "status": "playing",
            "current_phase": game_state.current_phase.value,
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