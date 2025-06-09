#!/usr/bin/env python3
"""
数据库迁移脚本：向 charging_records 表添加实际充电信息字段
"""
import sqlite3
import os
from datetime import datetime

def migrate_database():
    """添加实际充电信息字段到 charging_records 表"""
    
    # 数据库文件路径
    db_paths = [
        "charging_system.db",
        "app.db",
        "../charging_system.db"
    ]
    
    # 寻找数据库文件
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ 未找到数据库文件")
        return False
    
    print(f"📍 使用数据库文件: {db_path}")
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='charging_records'
        """)
        
        if not cursor.fetchone():
            print("❌ charging_records 表不存在")
            return False
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(charging_records)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_fields = [
            'actual_charging_amount',
            'actual_electricity_fee', 
            'actual_service_fee',
            'actual_total_fee'
        ]
        
        # 添加缺失的字段
        for field in new_fields:
            if field not in columns:
                print(f"➕ 添加字段: {field}")
                cursor.execute(f"""
                    ALTER TABLE charging_records 
                    ADD COLUMN {field} REAL
                """)
            else:
                print(f"✅ 字段已存在: {field}")
        
        # 提交更改
        conn.commit()
        print("✅ 数据库迁移完成")
        
        # 验证新字段
        cursor.execute("PRAGMA table_info(charging_records)")
        all_columns = [column[1] for column in cursor.fetchall()]
        
        print("\n📋 charging_records 表字段:")
        for col in all_columns:
            if col in new_fields:
                print(f"  🆕 {col}")
            else:
                print(f"     {col}")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 开始数据库迁移...")
    migrate_database() 