import sys
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 现在可以正常导入
from src.storage.database import init_db
from config.settings import HOST, PORT, DEBUG
from src.utils.logging import setup_default_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    setup_default_logging()
    logger.info("🚀 启动大西铁路游戏后台服务")

    init_db()
    logger.info("✅ 数据库初始化完成")

    yield

    # 关闭时清理资源
    logger.info("🛑 服务关闭完成")


app = FastAPI(
    title="Great Western Trail Backend",
    description="Backend system for Great Western Trail digital version",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    logger.info("收到根路径请求")
    return {"message": "Great Western Trail Backend API"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "database": "connected"}


@app.get("/db/stats")
async def database_stats():
    """数据库统计信息端点"""
    from src.storage.database import get_db_stats
    stats = get_db_stats()
    return stats or {"error": "无法获取数据库统计信息"}

if __name__ == "__main__":
    logger.info(f"启动服务器: {HOST}:{PORT}")
    uvicorn.run(
        "src.main:app",  # 修改这里，使用模块路径
        host=HOST,
        port=PORT,
        reload=DEBUG
    )