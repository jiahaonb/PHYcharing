#!/usr/bin/env python3
"""查看活跃订单脚本"""

from app.core.database import get_db
from app.models import ChargingQueue, ChargingRecord, Vehicle, User

def main():
    db = next(get_db())
    
    print('=== 未完成的队列记录 ===')
    active_queues = db.query(ChargingQueue).filter(
        ChargingQueue.status.in_(['waiting', 'queuing', 'charging'])
    ).all()
    
    for queue in active_queues:
        vehicle = db.query(Vehicle).filter(Vehicle.id == queue.vehicle_id).first()
        user = db.query(User).filter(User.id == queue.user_id).first()
        vehicle_info = f"{vehicle.license_plate}" if vehicle else f"车辆ID:{queue.vehicle_id}"
        user_info = f"{user.username}" if user else f"用户ID:{queue.user_id}"
        
        print(f'队列ID: {queue.id}, 状态: {queue.status}, 车辆: {vehicle_info}, 用户: {user_info}, 充电桩ID: {queue.charging_pile_id}')
    
    print(f'\n总计活跃队列: {len(active_queues)}')
    
    print('\n=== 所有充电记录 ===')
    try:
        # 查看充电记录表结构
        records = db.query(ChargingRecord).all()
        print(f'总计充电记录: {len(records)}')
        
        if records:
            first_record = records[0]
            print(f'示例记录属性: {[attr for attr in dir(first_record) if not attr.startswith("_")]}')
            
        # 查找非completed状态的记录
        non_completed = [r for r in records if hasattr(r, 'status') and r.status != 'completed']
        for record in non_completed:
            print(f'记录ID: {record.id}, 订单号: {getattr(record, "record_number", "N/A")}, 状态: {getattr(record, "status", "N/A")}, 车牌: {getattr(record, "license_plate", "N/A")}')
        
        print(f'\n总计非完成记录: {len(non_completed)}')
        
    except Exception as e:
        print(f'查询充电记录失败: {e}')
    
    db.close()
    return active_queues

if __name__ == "__main__":
    main() 