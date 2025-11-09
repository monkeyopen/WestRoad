"""
数据库配置模块
负责数据库连接、会话管理和初始化
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import logging

from config.settings import DATABASE_URL, DEBUG

# 配置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
try:
    engine = create_engine(
        DATABASE_URL,
        # SQLite 特定配置
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
        # 开发环境显示SQL语句
        echo=DEBUG,
        # 连接池配置
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    logger.info(f"✅ 数据库引擎创建成功: {DATABASE_URL}")
except Exception as e:
    logger.error(f"❌ 创建数据库引擎失败: {e}")
    raise

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

# 声明基类
Base = declarative_base()

def get_db():
    """
    获取数据库会话的依赖函数
    用于FastAPI的依赖注入系统
    """
    db = SessionLocal()
    try:
        yield db
        logger.debug("✅ 数据库会话使用完成")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"❌ 数据库会话错误: {e}")
        raise
    finally:
        db.close()
        logger.debug("🔒 数据库会话已关闭")

def init_db():
    """
    初始化数据库表结构
    """
    try:
        # 导入所有模型以确保它们被注册
        from src.storage import models  # noqa: F401

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表结构初始化成功")

        # 检查表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"📋 已创建的表: {tables}")

        return True
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False

def check_db_connection():
    """
    检查数据库连接是否正常
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"❌ 数据库连接检查失败: {e}")
        return False

def get_db_stats():
    """
    获取数据库统计信息
    """
    try:
        with engine.connect() as conn:
            # 获取表数量
            table_count = conn.execute(
                text("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            ).scalar()

            # 获取数据库大小（SQLite）
            if DATABASE_URL.startswith("sqlite"):
                db_file = DATABASE_URL.replace("sqlite:///", "")
                if os.path.exists(db_file):
                    size = os.path.getsize(db_file)
                else:
                    size = 0
            else:
                size = "N/A"

            return {
                "table_count": table_count,
                "database_size_bytes": size,
                "database_url": DATABASE_URL,
                "connection_healthy": check_db_connection()
            }
    except Exception as e:
        logger.error(f"❌ 获取数据库统计信息失败: {e}")
        return None

# 数据库健康检查类
class DatabaseHealth:
    """数据库健康状态管理"""

    @staticmethod
    def is_healthy():
        """检查数据库是否健康"""
        return check_db_connection()

    @staticmethod
    def get_status():
        """获取详细状态信息"""
        stats = get_db_stats()
        if stats:
            return {
                "status": "healthy" if stats["connection_healthy"] else "unhealthy",
                "details": stats
            }
        return {
            "status": "unknown",
            "details": {"error": "无法获取数据库状态"}
        }

# 数据库会话上下文管理器
class DatabaseSession:
    """
    数据库会话上下文管理器
    用于手动管理数据库会话
    """

    def __init__(self):
        self.db = None

    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            if exc_type is not None:
                self.db.rollback()
                logger.warning("🔄 数据库会话已回滚")
            else:
                self.db.commit()
                logger.debug("✅ 数据库会话已提交")
            self.db.close()

# 模块初始化时检查连接
if __name__ != "__main__":
    # 模块导入时检查数据库连接
    if check_db_connection():
        logger.info("✅ 数据库连接正常")
    else:
        logger.error("❌ 数据库连接失败")