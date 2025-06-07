#!/usr/bin/env python3
"""
添加车辆颜色字段的数据库迁移脚本
"""

import sqlite3
import sys
from pathlib import Path

def add_color_column():
    """为vehicles表添加color字段"""
    try:
        # 连接数据库
        db_path = Path(__file__).parent / "charging_system.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 检查color字段是否已存在
        cursor.execute("PRAGMA table_info(vehicles)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'color' not in columns:
            print("添加color字段到vehicles表...")
            cursor.execute("ALTER TABLE vehicles ADD COLUMN color VARCHAR(50)")
            
            # 为现有记录设置默认颜色
            cursor.execute("UPDATE vehicles SET color = '白色' WHERE color IS NULL")
            
            conn.commit()
            print("✅ color字段添加成功")
        else:
            print("✅ color字段已存在，无需添加")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🔄 开始数据库迁移...")
    add_color_column()
    print("🎉 数据库迁移完成!") 