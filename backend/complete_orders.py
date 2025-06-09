#!/usr/bin/env python3
"""完成所有未结束订单的脚本"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import get_db
from app.models import ChargingQueue, ChargingRecord
from app.models.charging import QueueStatus
from datetime import datetime
import random

def main():
    db = next(get_db())
    
    try:
        print('=== 查找未完成的队列 ===')
        active_queues = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_(['waiting', 'queuing', 'charging'])
        ).all()
        
        print(f'找到 {len(active_queues)} 个未完成的队列')
        
        for queue in active_queues:
            print(f'处理队列ID: {queue.id}, 当前状态: {queue.status}')
            
            # 检查是否有对应的充电记录
            charging_record = None
            if hasattr(queue, 'queue_number') and queue.queue_number:
                charging_record = db.query(ChargingRecord).filter(
                    ChargingRecord.queue_number == queue.queue_number
                ).first()
            
            if not charging_record:
                # 尝试通过其他方式查找充电记录
                from app.models import Vehicle
                vehicle = db.query(Vehicle).filter(Vehicle.id == queue.vehicle_id).first()
                if vehicle:
                    # 查找最近的充电记录
                    charging_record = db.query(ChargingRecord).filter(
                        ChargingRecord.license_plate == vehicle.license_plate
                    ).order_by(ChargingRecord.created_at.desc()).first()
            
            # 更新队列状态为已完成
            queue.status = QueueStatus.COMPLETED
            queue.updated_at = datetime.now()
            
            # 如果有充电记录，也更新其状态
            if charging_record and hasattr(charging_record, 'status'):
                charging_record.status = 'completed'
                charging_record.end_time = datetime.now()
                charging_record.total_amount = random.uniform(10, 50)  # 模拟充电量
                charging_record.total_fee = random.uniform(15, 35)     # 模拟费用
                charging_record.updated_at = datetime.now()
                print(f'  - 更新充电记录: {getattr(charging_record, "record_number", "N/A")}')
            
            print(f'  - 队列 {queue.id} 状态更新为: {queue.status}')
        
        # 提交更改
        db.commit()
        print(f'\\n✅ 成功完成 {len(active_queues)} 个订单')
        
        # 验证结果
        remaining_active = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_(['waiting', 'queuing', 'charging'])
        ).count()
        
        print(f'剩余活跃队列数: {remaining_active}')
        
    except Exception as e:
        print(f'❌ 处理过程中出错: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 