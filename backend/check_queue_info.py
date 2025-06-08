from app.core.database import get_db
from app.models import ChargingQueue

def check_queue_info():
    db = next(get_db())
    
    print("📋 检查所有队列记录...")
    queues = db.query(ChargingQueue).all()
    
    print(f"总共有 {len(queues)} 条队列记录:")
    for q in queues:
        status = q.status.value if hasattr(q.status, 'value') else q.status
        print(f"  ID:{q.id} 排队号:{q.queue_number} 状态:{status} 车辆ID:{q.vehicle_id}")
    
    # 检查队列ID 4
    queue_4 = db.query(ChargingQueue).filter(ChargingQueue.id == 4).first()
    if queue_4:
        print(f"\n✅ 队列ID 4 存在:")
        print(f"  排队号: {queue_4.queue_number}")
        print(f"  状态: {queue_4.status.value if hasattr(queue_4.status, 'value') else queue_4.status}")
        print(f"  车辆ID: {queue_4.vehicle_id}")
        print(f"  充电模式: {queue_4.charging_mode.value if hasattr(queue_4.charging_mode, 'value') else queue_4.charging_mode}")
        print(f"  申请电量: {queue_4.requested_amount}")
    else:
        print(f"\n❌ 队列ID 4 不存在!")
    
    db.close()

if __name__ == "__main__":
    check_queue_info() 