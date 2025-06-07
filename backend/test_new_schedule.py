#!/usr/bin/env python3
"""测试新的三阶段调度逻辑"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.charging_service import ChargingScheduleService
from app.models import ChargingQueue, ChargingPile, User, Vehicle, ChargingMode, QueueStatus
import traceback

def test_new_schedule():
    print("🧪 测试新的三阶段调度逻辑")
    
    db = SessionLocal()
    service = ChargingScheduleService(db)
    
    try:
        # 1. 查看初始状态
        print("\n📊 初始状态:")
        waiting_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.WAITING).count()
        queuing_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.QUEUING).count()
        charging_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.CHARGING).count()
        
        print(f"  等候区: {waiting_count} 辆")
        print(f"  排队区: {queuing_count} 辆")
        print(f"  充电中: {charging_count} 辆")
        
        # 2. 执行调度
        print("\n🔄 执行三阶段调度...")
        service.schedule_charging()
        
        # 3. 查看调度后状态
        print("\n📊 调度后状态:")
        waiting_count_after = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.WAITING).count()
        queuing_count_after = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.QUEUING).count()
        charging_count_after = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.CHARGING).count()
        
        print(f"  等候区: {waiting_count_after} 辆 (变化: {waiting_count_after - waiting_count:+d})")
        print(f"  排队区: {queuing_count_after} 辆 (变化: {queuing_count_after - queuing_count:+d})")
        print(f"  充电中: {charging_count_after} 辆 (变化: {charging_count_after - charging_count:+d})")
        
        # 4. 详细查看每个区域的车辆
        print("\n🚗 详细车辆分布:")
        
        # 等候区
        waiting_vehicles = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.WAITING).all()
        print(f"  等候区 ({len(waiting_vehicles)} 辆):")
        for v in waiting_vehicles:
            print(f"    - {v.queue_number} ({v.charging_mode.value})")
        
        # 排队区按充电桩分组
        piles = db.query(ChargingPile).all()
        for pile in piles:
            queuing_vehicles = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == pile.id,
                ChargingQueue.status == QueueStatus.QUEUING
            ).order_by(ChargingQueue.queue_time).all()
            
            charging_vehicle = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == pile.id,
                ChargingQueue.status == QueueStatus.CHARGING
            ).first()
            
            if queuing_vehicles or charging_vehicle:
                print(f"  充电桩 {pile.pile_number} ({pile.charging_mode.value}):")
                if charging_vehicle:
                    print(f"    充电位: {charging_vehicle.queue_number} (充电中)")
                else:
                    print(f"    充电位: [空闲]")
                    
                print(f"    排队区 ({len(queuing_vehicles)} 辆):")
                for i, v in enumerate(queuing_vehicles, 1):
                    print(f"      {i}. {v.queue_number}")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_new_schedule() 