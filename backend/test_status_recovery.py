#!/usr/bin/env python3
"""测试系统重启后充电桩状态恢复功能"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.charging_service import ChargingScheduleService
from app.services.system_scheduler import SystemScheduler
from app.models import ChargingPile, ChargingQueue, User, Vehicle, ChargingMode, ChargingPileStatus, QueueStatus
from sqlalchemy.orm import Session
import time

def test_status_recovery():
    print("🧪 测试系统重启后状态恢复功能")
    
    db = SessionLocal()
    service = ChargingScheduleService(db)
    
    try:
        # 1. 查看当前状态
        print("\n📊 测试前状态:")
        piles = db.query(ChargingPile).all()
        for pile in piles:
            charging_count = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == pile.id,
                ChargingQueue.status == QueueStatus.CHARGING
            ).count()
            print(f"  充电桩 {pile.pile_number}: {pile.status.value} (正在充电: {charging_count})")
        
        # 2. 模拟一些充电状态不一致的情况
        print("\n🔧 模拟状态不一致情况...")
        
        # 找一个有车辆正在充电的充电桩
        charging_queue = db.query(ChargingQueue).filter(
            ChargingQueue.status == QueueStatus.CHARGING
        ).first()
        
        if charging_queue and charging_queue.pile:
            # 将充电桩状态错误地设为正常（模拟重启后状态丢失）
            charging_queue.pile.status = ChargingPileStatus.NORMAL
            db.commit()
            print(f"  模拟状态丢失: 充电桩 {charging_queue.pile.pile_number} 状态设为正常，但实际有车辆 {charging_queue.queue_number} 正在充电")
        
        # 3. 执行状态恢复
        print("\n🔄 执行状态恢复...")
        scheduler = SystemScheduler()
        scheduler.restore_pile_status()
        
        # 4. 检查恢复结果
        print("\n✅ 状态恢复后:")
        db.refresh(charging_queue.pile)  # 刷新数据
        piles = db.query(ChargingPile).all()
        for pile in piles:
            charging_count = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == pile.id,
                ChargingQueue.status == QueueStatus.CHARGING
            ).count()
            
            status_ok = "✅" if (charging_count > 0 and pile.status == ChargingPileStatus.CHARGING) or \
                              (charging_count == 0 and pile.status != ChargingPileStatus.CHARGING) \
                          else "❌"
                          
            print(f"  {status_ok} 充电桩 {pile.pile_number}: {pile.status.value} (正在充电: {charging_count})")
        
        # 5. 测试完整的系统状态恢复
        print("\n🚀 测试完整系统状态恢复...")
        scheduler.recover_system_state()
        
        print("\n🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_status_recovery() 