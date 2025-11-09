#!/usr/bin/env python3
"""
检查数据库状态脚本
"""

import sys
import os
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DATABASE_URL


def check_database():
    """检查数据库状态"""

    # 从DATABASE_URL中提取文件路径
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        print(f"数据库文件路径: {db_path}")

        # 检查文件是否存在
        if os.path.exists(db_path):
            print("✅ 数据库文件存在")
            file_size = os.path.getsize(db_path)
            print(f"📊 文件大小: {file_size} 字节")

            # 连接数据库
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # 查询表
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()

                print("📋 数据库中的表:")
                for table in tables:
                    table_name = table[0]
                    print(f"  - {table_name}")

                    # 显示表结构
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    print(f"    表结构: {[col[1] for col in columns]}")

                conn.close()
                print("✅ 数据库连接正常")

            except Exception as e:
                print(f"❌ 数据库连接错误: {e}")
        else:
            print("❌ 数据库文件不存在")
            print("💡 请运行: python scripts/init_db.py")
    else:
        print(f"❌ 不支持的数据库类型: {DATABASE_URL}")


if __name__ == "__main__":
    check_database()