#!/usr/bin/env python3
"""
应用启动脚本 - 从项目根目录运行
"""

import sys
import os
from pathlib import Path

# 确保当前目录是项目根目录
current_dir = Path(__file__).parent
if current_dir.name != "WestRoad":  # 根据你的项目名调整
    print("❌ 请在项目根目录运行此脚本")
    sys.exit(1)

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(current_dir))

# 导入并运行应用
from src.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 启动大西铁路游戏后台服务...")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )