#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import ChargingRecord, ChargingQueue

def test_record_query():
    record_number = 'MAN202506090507400001'
    
    db = SessionLocal()
    try:
        # 查找充电记录
        record = db.query(ChargingRecord).filter(
            ChargingRecord.record_number == record_number
        ).first()
        
        if record:
            print(f'✅ 找到充电记录: {record.record_number}')
            print(f'   队列号: {record.queue_number}')
            print(f'   状态: {getattr(record, "status", "无状态字段")}')
            
            # 查找对应的队列记录
            queue = db.query(ChargingQueue).filter(
                ChargingQueue.queue_number == record.queue_number
            ).first()
            
            if queue:
                print(f'✅ 找到队列记录: {queue.queue_number}')
                print(f'   队列状态: {queue.status}')
                print(f'   车辆ID: {queue.vehicle_id}')
                print(f'   充电桩ID: {queue.charging_pile_id}')
            else:
                print(f'❌ 没有找到对应的队列记录: {record.queue_number}')
                
                # 查看所有队列记录
                all_queues = db.query(ChargingQueue).all()
                print(f'📋 数据库中所有队列记录:')
                for q in all_queues[:5]:  # 只显示前5个
                    print(f'   - {q.queue_number}: {q.status}')
        else:
            print(f'❌ 没有找到充电记录: {record_number}')
            
            # 查看最近的充电记录
            recent_records = db.query(ChargingRecord).order_by(
                ChargingRecord.created_at.desc()
            ).limit(5).all()
            
            print(f'📋 最近的充电记录:')
            for r in recent_records:
                print(f'   - {r.record_number}: {r.queue_number}')
    finally:
        db.close()

if __name__ == '__main__':
    test_record_query() 