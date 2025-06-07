#!/usr/bin/env python3
"""清理模拟充电记录脚本"""

from app.core.database import get_db
from app.models import ChargingRecord, ChargingQueue

def main():
    db = next(get_db())
    
    try:
        # 清理所有充电记录
        records_count = db.query(ChargingRecord).count()
        print(f'发现 {records_count} 条充电记录，开始清理...')
        
        if records_count > 0:
            # 删除所有充电记录
            db.query(ChargingRecord).delete()
            print(f'已删除 {records_count} 条充电记录')
        
        # 清理所有已完成或已取消的队列记录，只保留活跃的队列
        from app.models.charging import QueueStatus
        
        completed_queues = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_([QueueStatus.COMPLETED, QueueStatus.CANCELLED])
        ).all()
        
        print(f'发现 {len(completed_queues)} 条已完成/已取消的队列记录，开始清理...')
        
        for queue in completed_queues:
            print(f'删除队列记录: {queue.queue_number} - {queue.status}')
            db.delete(queue)
        
        # 提交更改
        db.commit()
        print('✅ 清理完成')
        
        # 显示剩余的活跃队列
        active_queues = db.query(ChargingQueue).all()
        print(f'剩余活跃队列: {len(active_queues)} 条')
        
    except Exception as e:
        print(f'清理失败: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 