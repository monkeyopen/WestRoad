"""
日志工具模块
负责应用程序的日志配置和管理
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """
    设置应用程序的日志配置

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径，如果为None则不写入文件
        enable_console: 是否启用控制台输出
    """

    # 确保日志目录存在
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # 日志配置字典
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]"
            },
            "simple": {
                "format": "%(levelname)s: %(message)s"
            },
            "json": {
                "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s", "file": "%(filename)s", "line": %(lineno)d}',
                "datefmt": "%Y-%m-%dT%H:%M:%SZ"
            }
        },
        "handlers": {
            "null": {
                "class": "logging.NullHandler"
            }
        },
        "loggers": {
            "great_western_trail": {
                "level": log_level,
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # 避免SQL日志过于冗长
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": []
        }
    }

    # 添加控制台处理器
    if enable_console:
        log_config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "simple",
            "level": log_level
        }
        log_config["root"]["handlers"].append("console")
        log_config["loggers"]["great_western_trail"]["handlers"] = ["console"]

    # 添加文件处理器
    if log_file:
        log_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "detailed",
            "encoding": "utf8"
        }
        log_config["root"]["handlers"].append("file")
        if "handlers" in log_config["loggers"]["great_western_trail"]:
            log_config["loggers"]["great_western_trail"]["handlers"].append("file")
        else:
            log_config["loggers"]["great_western_trail"]["handlers"] = ["file"]

    # 应用配置
    logging.config.dictConfig(log_config)

    # 记录启动日志
    logger = logging.getLogger("great_western_trail")
    logger.info("✅ 日志系统初始化完成")
    logger.info(f"📊 日志级别: {log_level}")
    if log_file:
        logger.info(f"📁 日志文件: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器

    Args:
        name: 日志记录器名称，通常使用 __name__

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    return logger

class LogManager:
    """日志管理器，提供高级日志功能"""

    def __init__(self, name: str = "great_western_trail"):
        self.logger = get_logger(name)
        self.performance_logger = get_logger(f"{name}.performance")

    def log_performance(self, operation: str, duration_ms: float, **kwargs):
        """记录性能日志"""
        extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
        self.performance_logger.info(
            f"⏱️ {operation} - 耗时: {duration_ms:.2f}ms {extra_info}"
        )

    def log_error_with_context(self, error: Exception, context: dict = None):
        """记录带上下文的错误日志"""
        context_str = ""
        if context:
            context_str = " | " + " ".join([f"{k}={v}" for k, v in context.items()])

        self.logger.error(f"❌ {error.__class__.__name__}: {error}{context_str}")

    def log_game_event(self, event_type: str, session_id: str, player_id: str = None, details: dict = None):
        """记录游戏事件"""
        player_info = f"玩家: {player_id}" if player_id else ""
        details_str = f" | {details}" if details else ""
        self.logger.info(f"🎮 {event_type} | 会话: {session_id} {player_info}{details_str}")

# 默认日志配置
def setup_default_logging():
    """设置默认日志配置"""
    log_file = PROJECT_ROOT / "logs" / "great_western_trail.log"
    setup_logging(
        log_level="INFO",
        log_file=str(log_file),
        enable_console=True
    )

# 开发环境日志配置
def setup_development_logging():
    """设置开发环境日志配置"""
    log_file = PROJECT_ROOT / "logs" / "development.log"
    setup_logging(
        log_level="DEBUG",
        log_file=str(log_file),
        enable_console=True
    )

# 生产环境日志配置
def setup_production_logging():
    """设置生产环境日志配置"""
    log_file = PROJECT_ROOT / "logs" / "production.log"
    setup_logging(
        log_level="WARNING",
        log_file=str(log_file),
        enable_console=False  # 生产环境通常不输出到控制台
    )

# 模块导入时自动设置默认日志
try:
    setup_default_logging()
except Exception as e:
    # 如果自动设置失败，至少确保有基本的日志配置
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logging.warning(f"日志自动配置失败，使用基础配置: {e}")