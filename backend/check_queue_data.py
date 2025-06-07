#!/usr/bin/env python3
"""检查队列数据脚本"""

from app.core.database import get_db
from app.models import ChargingQueue, Vehicle, User

def main():
    db = next(get_db())
    
    # 检查队列数据
    queues = db.query(ChargingQueue).all()
    print(f'数据库中队列总数: {len(queues)}')
    
    for queue in queues:
        vehicle_info = "未知车辆"
        if queue.vehicle:
            vehicle_info = f"{queue.vehicle.license_plate}"
        
        user_info = "未知用户"
        if queue.user:
            user_info = f"{queue.user.username}"
            
        print(f'队列{queue.id}: 状态={queue.status}, 车辆={vehicle_info}, 用户={user_info}, 充电桩ID={queue.charging_pile_id}')
    
    # 检查各状态的队列数量
    from app.models.charging import QueueStatus
    
    waiting_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.WAITING).count()
    queuing_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.QUEUING).count()  
    charging_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.CHARGING).count()
    completed_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.COMPLETED).count()
    cancelled_count = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.CANCELLED).count()
    
    print(f"\n状态统计:")
    print(f"等待中(WAITING): {waiting_count}")
    print(f"排队中(QUEUING): {queuing_count}")
    print(f"充电中(CHARGING): {charging_count}")
    print(f"已完成(COMPLETED): {completed_count}")
    print(f"已取消(CANCELLED): {cancelled_count}")
    
    db.close()

if __name__ == "__main__":
    main() 