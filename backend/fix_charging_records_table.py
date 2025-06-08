#!/usr/bin/env python3
"""
修复充电记录表结构
添加缺失的charging_mode、status、updated_at字段，并修复枚举值
"""

import sqlite3
import sys
from pathlib import Path

def fix_charging_records_table():
    """修复charging_records表，添加缺失的字段"""
    try:
        # 连接数据库
        db_path = Path(__file__).parent / "charging_system.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("检查charging_records表结构...")
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='charging_records'")
        if not cursor.fetchone():
            print("❌ charging_records表不存在")
            return False
        
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(charging_records)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"当前字段: {columns}")
        
        missing_fields = []
        
        # 检查charging_mode字段
        if 'charging_mode' not in columns:
            missing_fields.append('charging_mode')
        
        # 检查status字段
        if 'status' not in columns:
            missing_fields.append('status')
            
        # 检查updated_at字段
        if 'updated_at' not in columns:
            missing_fields.append('updated_at')
        
        if missing_fields:
            print(f"发现缺失字段: {missing_fields}")
            
            # 添加缺失的字段
            for field in missing_fields:
                if field == 'charging_mode':
                    print("添加charging_mode字段...")
                    cursor.execute("ALTER TABLE charging_records ADD COLUMN charging_mode VARCHAR(20)")
                    # 为现有记录设置默认值（使用枚举值FAST）
                    cursor.execute("UPDATE charging_records SET charging_mode = 'FAST' WHERE charging_mode IS NULL")
                elif field == 'status':
                    print("添加status字段...")
                    cursor.execute("ALTER TABLE charging_records ADD COLUMN status VARCHAR(20) DEFAULT 'created'")
                    # 为现有记录设置默认值
                    cursor.execute("UPDATE charging_records SET status = 'completed' WHERE status IS NULL")
                elif field == 'updated_at':
                    print("添加updated_at字段...")
                    cursor.execute("ALTER TABLE charging_records ADD COLUMN updated_at DATETIME")
                    # 为现有记录设置默认值（使用created_at的值）
                    cursor.execute("UPDATE charging_records SET updated_at = created_at WHERE updated_at IS NULL")
            
            conn.commit()
            print("✅ 字段添加成功")
        else:
            print("✅ 所有必需字段都已存在")
        
        # 修复charging_mode枚举值（从小写改为大写）
        print("检查并修复charging_mode枚举值...")
        cursor.execute("SELECT COUNT(*) FROM charging_records WHERE charging_mode = 'fast'")
        fast_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM charging_records WHERE charging_mode = 'trickle'")
        trickle_count = cursor.fetchone()[0]
        
        if fast_count > 0:
            print(f"修复 {fast_count} 条记录的charging_mode值：fast -> FAST")
            cursor.execute("UPDATE charging_records SET charging_mode = 'FAST' WHERE charging_mode = 'fast'")
        
        if trickle_count > 0:
            print(f"修复 {trickle_count} 条记录的charging_mode值：trickle -> TRICKLE")
            cursor.execute("UPDATE charging_records SET charging_mode = 'TRICKLE' WHERE charging_mode = 'trickle'")
        
        if fast_count > 0 or trickle_count > 0:
            conn.commit()
            print("✅ 枚举值修复成功")
        else:
            print("✅ 枚举值无需修复")
        
        # 验证修复结果
        cursor.execute("PRAGMA table_info(charging_records)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        print(f"修复后字段: {updated_columns}")
        
        # 检查charging_mode的值分布
        cursor.execute("SELECT charging_mode, COUNT(*) FROM charging_records GROUP BY charging_mode")
        mode_distribution = cursor.fetchall()
        if mode_distribution:
            print(f"charging_mode值分布: {mode_distribution}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔄 开始修复charging_records表...")
    if fix_charging_records_table():
        print("🎉 数据库修复完成!")
    else:
        print("❌ 数据库修复失败!")
        sys.exit(1)

if __name__ == "__main__":
    main() 