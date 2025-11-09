from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from src.storage.database import Base


class GameSession(Base):
    """游戏会话数据库模型"""
    __tablename__ = "game_sessions"

    id = Column(String(64), primary_key=True, index=True)
    session_code = Column(String(8), unique=True, index=True)
    session_name = Column(String(100))
    session_type = Column(String(20))  # public, private, ranked, friendly
    max_players = Column(Integer, default=4)
    current_players = Column(Integer, default=1)
    game_state = Column(Text)  # 存储序列化的GameState JSON
    game_config = Column(JSON)
    session_status = Column(String(20))  # waiting, playing, paused, finished, aborted
    created_by = Column(String(64))
    host_player_id = Column(String(64))
    winner_player_id = Column(String(64))
    final_scores = Column(JSON)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)


class Player(Base):
    """玩家数据库模型"""
    __tablename__ = "players"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64))
    display_name = Column(String(100))
    elo_rating = Column(Integer, default=1200)
    total_games = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_played = Column(DateTime)