#!/usr/bin/env python3
"""
测试运行脚本 - 从项目根目录运行
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 运行测试
import pytest

if __name__ == "__main__":
    # 运行核心模块测试
    exit_code = pytest.main([
        "tests/unit/core/",
        "-v",
        "--tb=short"
    ])
    sys.exit(exit_code)