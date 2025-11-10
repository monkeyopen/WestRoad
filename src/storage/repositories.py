from sqlalchemy.orm import Session
from .models import GameSession as GameSessionModel


class GameSessionRepository:
    """游戏会话存储库"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, session_id: str) -> GameSessionModel:
        """根据ID获取游戏会话"""
        return self.db.query(GameSessionModel).filter(GameSessionModel.id == session_id).first()

    def create(self, session_data: dict) -> GameSessionModel:
        """创建新的游戏会话"""
        session = GameSessionModel(**session_data)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update(self, session: GameSessionModel) -> GameSessionModel:
        """更新游戏会话"""
        self.db.commit()
        self.db.refresh(session)
        return session

    def delete(self, session_id: str):
        """删除游戏会话"""
        session = self.get_by_id(session_id)
        if session:
            self.db.delete(session)
            self.db.commit()

    def list_all(self):
        """获取所有游戏会话"""
        return self.db.query(GameSessionModel).all()
