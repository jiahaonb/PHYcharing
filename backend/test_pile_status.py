#!/usr/bin/env python3
"""测试充电桩状态更新逻辑"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.charging_service import ChargingScheduleService
from app.models import ChargingPile, ChargingQueue, User, Vehicle, ChargingMode, ChargingPileStatus, QueueStatus
from sqlalchemy.orm import Session
import time

def test_pile_status():
    print("🧪 测试充电桩状态更新逻辑")
    
    db = SessionLocal()
    service = ChargingScheduleService(db)
    
    try:
        # 1. 查看当前充电桩状态
        print("\n📊 当前充电桩状态:")
        piles = db.query(ChargingPile).all()
        for pile in piles:
            print(f"  充电桩 {pile.pile_number}: {pile.status.value} ({pile.charging_mode.value})")
        
        # 2. 查看排队情况
        print("\n🚗 当前排队情况:")
        queues = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).all()
        
        for queue in queues:
            pile_info = f"充电桩{queue.pile.pile_number}" if queue.pile else "未分配"
            print(f"  排队号 {queue.queue_number}: {queue.status.value} - {pile_info}")
        
        # 3. 提交一个充电请求测试
        print("\n🔋 提交测试充电请求...")
        
        # 获取第一个用户和车辆
        user = db.query(User).first()
        vehicle = db.query(Vehicle).first()
        
        if user and vehicle:
            queue_number = service.submit_charging_request(
                user_id=user.id,
                vehicle_id=vehicle.id,
                charging_mode=ChargingMode.FAST,
                requested_amount=30.0
            )
            print(f"  ✅ 提交成功，排队号: {queue_number}")
            
            # 4. 调度充电
            print("\n⚡ 执行充电调度...")
            service.schedule_charging()
            
            # 5. 查看调度后的状态
            print("\n📊 调度后充电桩状态:")
            db.refresh(queue)  # 刷新数据
            piles = db.query(ChargingPile).all()
            for pile in piles:
                print(f"  充电桩 {pile.pile_number}: {pile.status.value}")
                
                # 查看该充电桩是否有正在充电的车辆
                charging_vehicles = db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status == QueueStatus.CHARGING
                ).count()
                
                queuing_vehicles = db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status == QueueStatus.QUEUING
                ).count()
                
                print(f"    - 正在充电: {charging_vehicles} 台")
                print(f"    - 排队中: {queuing_vehicles} 台")
            
            # 6. 手动开始充电测试
            print("\n🚀 测试开始充电...")
            charging_queue = db.query(ChargingQueue).filter(
                ChargingQueue.status == QueueStatus.QUEUING
            ).first()
            
            if charging_queue:
                print(f"  找到排队车辆: {charging_queue.queue_number}")
                service.start_charging(charging_queue.id)
                
                # 检查充电桩状态是否更新
                db.refresh(charging_queue)
                if charging_queue.pile:
                    db.refresh(charging_queue.pile)
                    print(f"  充电桩 {charging_queue.pile.pile_number} 状态: {charging_queue.pile.status.value}")
                    
                    if charging_queue.pile.status == ChargingPileStatus.CHARGING:
                        print("  ✅ 充电桩状态正确更新为使用中!")
                    else:
                        print("  ❌ 充电桩状态未正确更新!")
                
                # 7. 测试完成充电
                print("\n🏁 测试完成充电...")
                time.sleep(1)  # 等待一秒
                record = service.complete_charging(charging_queue.id)
                print(f"  ✅ 充电完成，生成记录: {record.record_number}")
                
                # 检查充电桩状态是否恢复
                if charging_queue.pile:
                    db.refresh(charging_queue.pile)
                    print(f"  充电桩 {charging_queue.pile.pile_number} 状态: {charging_queue.pile.status.value}")
                    
                    if charging_queue.pile.status == ChargingPileStatus.NORMAL:
                        print("  ✅ 充电桩状态正确恢复为正常!")
                    else:
                        print("  ❌ 充电桩状态未正确恢复!")
            
        else:
            print("  ❌ 未找到用户或车辆，无法测试")
            
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_pile_status() 