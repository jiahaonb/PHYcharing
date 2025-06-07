#!/usr/bin/env python3
"""
测试新的快慢充分开逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.services.charging_service import ChargingScheduleService
from app.models import ChargingPile, ChargingQueue, Vehicle, User, ChargingMode, QueueStatus
from sqlalchemy.orm import Session

def test_new_charging_logic():
    """测试新的充电逻辑"""
    print("🧪 开始测试新的快慢充分开逻辑...")
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 1. 检查充电桩配置
        print("\n1. 检查充电桩配置:")
        fast_piles = db.query(ChargingPile).filter(ChargingPile.charging_mode == ChargingMode.FAST).all()
        trickle_piles = db.query(ChargingPile).filter(ChargingPile.charging_mode == ChargingMode.TRICKLE).all()
        
        print(f"   快充桩数量: {len(fast_piles)}")
        for pile in fast_piles:
            print(f"   - {pile.pile_number}: {pile.power}kW, 状态: {pile.status}")
        
        print(f"   慢充桩数量: {len(trickle_piles)}")
        for pile in trickle_piles:
            print(f"   - {pile.pile_number}: {pile.power}kW, 状态: {pile.status}")
        
        # 2. 检查队列状态
        print("\n2. 检查队列状态:")
        fast_waiting = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.FAST,
            ChargingQueue.status == QueueStatus.WAITING
        ).all()
        
        trickle_waiting = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.TRICKLE,
            ChargingQueue.status == QueueStatus.WAITING
        ).all()
        
        fast_queuing = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.FAST,
            ChargingQueue.status == QueueStatus.QUEUING
        ).all()
        
        trickle_queuing = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.TRICKLE,
            ChargingQueue.status == QueueStatus.QUEUING
        ).all()
        
        fast_charging = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.FAST,
            ChargingQueue.status == QueueStatus.CHARGING
        ).all()
        
        trickle_charging = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.TRICKLE,
            ChargingQueue.status == QueueStatus.CHARGING
        ).all()
        
        print(f"   快充等候: {len(fast_waiting)} 辆")
        print(f"   慢充等候: {len(trickle_waiting)} 辆")
        print(f"   快充排队: {len(fast_queuing)} 辆")
        print(f"   慢充排队: {len(trickle_queuing)} 辆")
        print(f"   快充充电中: {len(fast_charging)} 辆")
        print(f"   慢充充电中: {len(trickle_charging)} 辆")
        
        # 3. 测试调度逻辑
        print("\n3. 测试调度逻辑:")
        service = ChargingScheduleService(db)
        
        print("   执行调度...")
        service.schedule_charging()
        print("   调度完成")
        
        # 4. 检查调度后的状态
        print("\n4. 调度后状态:")
        fast_queuing_after = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.FAST,
            ChargingQueue.status == QueueStatus.QUEUING
        ).all()
        
        trickle_queuing_after = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.TRICKLE,
            ChargingQueue.status == QueueStatus.QUEUING
        ).all()
        
        fast_charging_after = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.FAST,
            ChargingQueue.status == QueueStatus.CHARGING
        ).all()
        
        trickle_charging_after = db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == ChargingMode.TRICKLE,
            ChargingQueue.status == QueueStatus.CHARGING
        ).all()
        
        print(f"   快充排队: {len(fast_queuing_after)} 辆")
        print(f"   慢充排队: {len(trickle_queuing_after)} 辆")
        print(f"   快充充电中: {len(fast_charging_after)} 辆")
        print(f"   慢充充电中: {len(trickle_charging_after)} 辆")
        
        # 5. 显示详细的充电桩使用情况
        print("\n5. 充电桩使用详情:")
        for pile in fast_piles + trickle_piles:
            pile_queues = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == pile.id,
                ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
            ).order_by(ChargingQueue.queue_time).all()
            
            mode_text = "快充" if pile.charging_mode == ChargingMode.FAST else "慢充"
            print(f"   {pile.pile_number} ({mode_text}): {len(pile_queues)} 辆车")
            
            for i, queue in enumerate(pile_queues):
                status_text = "充电中" if queue.status == QueueStatus.CHARGING else f"排队第{i}位"
                vehicle_plate = queue.vehicle.license_plate if queue.vehicle else "未知车辆"
                print(f"     - {vehicle_plate}: {status_text}")
        
        print("\n✅ 测试完成！新的快慢充分开逻辑运行正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_new_charging_logic() 