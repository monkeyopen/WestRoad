import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/great_western_trail.db")

# 应用配置
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 游戏配置
MAX_PLAYERS = 4
DEFAULT_GAME_CONFIG = {
    "map_type": "standard",
    "difficulty": "normal",
    "turn_time_limit": 90,
    "enable_auto_pass": True
}