#!/usr/bin/env python3

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.database import get_db
from app.models import ChargingQueue, QueueStatus, ChargingPile, User, Vehicle
from sqlalchemy.orm import Session
from datetime import datetime

def main():
    db = next(get_db())
    
    try:
        # 检查现有数据
        print("=== 当前队列状态 ===")
        queues = db.query(ChargingQueue).all()
        print(f"总队列数: {len(queues)}")
        
        for queue in queues:
            print(f"ID: {queue.id}, 状态: {queue.status.value}, 用户: {queue.user_id}, 车辆: {queue.vehicle_id}")
        
        # 检查充电中的队列
        charging_queues = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.CHARGING).all()
        print(f"\n充电中的队列: {len(charging_queues)} 条")
        
        if not charging_queues:
            print("没有找到充电中的记录，创建一个测试记录...")
            
            # 创建测试数据
            users = db.query(User).limit(1).all()
            vehicles = db.query(Vehicle).limit(1).all()
            piles = db.query(ChargingPile).limit(1).all()
            
            if users and vehicles and piles:
                test_queue = ChargingQueue(
                    queue_number="TEST01",
                    user_id=users[0].id,
                    vehicle_id=vehicles[0].id,
                    charging_pile_id=piles[0].id,
                    requested_amount=50.0,
                    status=QueueStatus.CHARGING,
                    start_charging_time=datetime.now()
                )
                db.add(test_queue)
                db.commit()
                print(f"创建了测试充电记录，ID: {test_queue.id}")
            else:
                print("缺少基础数据：用户、车辆或充电桩")
        
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main() 