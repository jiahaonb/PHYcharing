from app.core.database import SessionLocal
from app.models.charging import ChargingQueue
from app.models.user import ChargingOrder

def check_f20_status():
    db = SessionLocal()
    try:
        print("🔍 检查F20车辆状态:")
        
        # 检查充电队列中的F20
        f20_queue = db.query(ChargingQueue).filter(ChargingQueue.queue_number == 'F20').first()
        if f20_queue:
            print(f"  队列记录存在:")
            print(f"    队列号: {f20_queue.queue_number}")
            print(f"    状态: {f20_queue.status}")
            print(f"    充电桩: {f20_queue.charging_pile_id}")
            print(f"    位置: {f20_queue.position}")
            print(f"    订单ID: {f20_queue.order_id}")
        else:
            print("  ❌ 队列记录不存在")
        
        # 检查相关订单
        if f20_queue and f20_queue.order_id:
            order = db.query(ChargingOrder).filter(ChargingOrder.id == f20_queue.order_id).first()
            if order:
                print(f"  关联订单:")
                print(f"    订单号: {order.order_number}")
                print(f"    状态: {order.status}")
                print(f"    车牌: {order.license_plate}")
        
        # 检查所有活跃的队列
        print("\n📋 所有活跃队列:")
        active_queues = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_(['WAITING', 'QUEUING', 'CHARGING'])
        ).all()
        
        if not active_queues:
            print("  无活跃队列")
        else:
            for queue in active_queues:
                print(f"  {queue.queue_number} - {queue.status} - 桩:{queue.charging_pile_id} - 位置:{queue.position}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_f20_status() 