#!/usr/bin/env python3
"""测试排队数据API"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.api.api_v1.endpoints.admin import get_charging_queue_with_vehicles
from app.models import User, ChargingQueue, Vehicle, ChargingPile
import traceback

def test_queue_api():
    print("🧪 测试排队数据API")
    
    db = SessionLocal()
    
    try:
        # 1. 检查数据库连接
        print("📊 检查数据库状态...")
        
        # 获取管理员用户
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            print("❌ 没有找到管理员用户")
            return
        else:
            print(f"✅ 找到管理员用户: {admin_user.username}")
        
        # 2. 检查数据表状态
        queue_count = db.query(ChargingQueue).count()
        vehicle_count = db.query(Vehicle).count()
        pile_count = db.query(ChargingPile).count()
        
        print(f"📈 数据统计:")
        print(f"  - 排队记录: {queue_count}")
        print(f"  - 车辆记录: {vehicle_count}")
        print(f"  - 充电桩记录: {pile_count}")
        
        # 3. 逐步测试API调用
        print("\n🔍 逐步测试API...")
        
        # 先测试基本查询
        print("  - 测试基本队列查询...")
        queues = db.query(ChargingQueue).all()
        print(f"    找到 {len(queues)} 个队列记录")
        
        # 测试带关联的查询
        print("  - 测试带关联的查询...")
        from sqlalchemy.orm import joinedload
        queues_with_relations = db.query(ChargingQueue).options(
            joinedload(ChargingQueue.vehicle).joinedload(Vehicle.owner),
            joinedload(ChargingQueue.pile)
        ).all()
        print(f"    成功加载 {len(queues_with_relations)} 个带关联的队列记录")
        
        # 4. 直接调用API函数
        print("\n⚡ 调用API函数...")
        result = get_charging_queue_with_vehicles(admin_user, db)
        print(f"✅ API调用成功，返回 {len(result)} 条记录")
        
        for i, item in enumerate(result):
            print(f"  [{i+1}] 排队号: {item.get('queue_number', 'N/A')}, "
                  f"状态: {item.get('status', 'N/A')}, "
                  f"充电桩: {item.get('pile_id', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_queue_api() 