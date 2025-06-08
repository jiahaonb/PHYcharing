#!/usr/bin/env python3
"""
创建充电记录表
确保数据库包含所有必要的表
"""

from sqlalchemy import create_engine, text
from app.core.database import Base, engine
from app.models.charging import ChargingRecord, ChargingPile, ChargingQueue
from app.models.user import User, Vehicle

def create_tables():
    """创建所有表"""
    try:
        
        print("正在创建数据库表...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        print("数据库表创建完成！")
        
        # 检查表是否存在（SQLite语法）
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            
            print(f"当前数据库中的表: {tables}")
            
            required_tables = ['users', 'vehicles', 'charging_piles', 'charging_queues', 'charging_records']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"缺少的表: {missing_tables}")
            else:
                print("所有必需的表都已存在！")
        
    except Exception as e:
        print(f"创建表时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_tables() 