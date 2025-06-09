#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障调度功能测试
测试三种调度原则：
1. 优先调度 
2. 时间顺序调度
3. 故障恢复调度
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.core.database import get_db
from backend.app.services.charging_service import ChargingScheduleService
from backend.app.models import ChargingPile, ChargingQueue, ChargingRecord, ChargingMode, QueueStatus, ChargingPileStatus
from backend.app.models.user import User, Vehicle
from sqlalchemy.orm import Session

def print_system_status(db: Session, title: str):
    """打印系统状态"""
    print(f"\n{title}")
    print("=" * 50)
    
    # 打印充电桩状态
    piles = db.query(ChargingPile).all()
    print("充电桩状态:")
    for pile in piles:
        print(f"  {pile.pile_number}: {pile.status.value} ({'激活' if pile.is_active else '禁用'})")
    
    # 打印队列状态
    queues = db.query(ChargingQueue).filter(
        ChargingQueue.status.in_([
            QueueStatus.WAITING, 
            QueueStatus.QUEUING, 
            QueueStatus.CHARGING,
            QueueStatus.FAULT_WAITING
        ])
    ).order_by(ChargingQueue.queue_number).all()
    
    print("\n队列状态:")
    status_groups = {
        QueueStatus.WAITING: "等候区",
        QueueStatus.FAULT_WAITING: "故障区", 
        QueueStatus.QUEUING: "充电区排队",
        QueueStatus.CHARGING: "充电中"
    }
    
    for status, group_name in status_groups.items():
        group_queues = [q for q in queues if q.status == status]
        if group_queues:
            print(f"  {group_name}: {[q.queue_number for q in group_queues]}")
    
    print()

def setup_test_scenario(db: Session):
    """设置测试场景"""
    print("🔧 设置测试场景...")
    
    service = ChargingScheduleService(db)
    
    # 确保有测试用户和车辆
    test_user = db.query(User).filter(User.username == "testuser").first()
    if not test_user:
        test_user = User(username="testuser", email="test@example.com", hashed_password="test")
        db.add(test_user)
        db.commit()
    
    # 创建测试车辆
    test_vehicles = []
    for i in range(6):
        license_plate = f"京A{1000+i:04d}"
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
        if not vehicle:
            vehicle = Vehicle(
                license_plate=license_plate,
                model=f"测试车型{i+1}",
                battery_capacity=50.0,
                owner_id=test_user.id
            )
            db.add(vehicle)
            test_vehicles.append(vehicle)
        else:
            test_vehicles.append(vehicle)
    
    db.commit()
    
    # 清理现有队列
    db.query(ChargingQueue).delete()
    db.query(ChargingRecord).delete()
    db.commit()
    
    # 恢复所有充电桩状态
    for pile in db.query(ChargingPile).all():
        pile.status = ChargingPileStatus.NORMAL
        pile.is_active = True
    db.commit()
    
    # 创建快充车辆队列
    fast_vehicles = test_vehicles[:3]
    for i, vehicle in enumerate(fast_vehicles):
        queue_number = service.submit_charging_request(
            user_id=test_user.id,
            vehicle_id=vehicle.id,
            charging_mode=ChargingMode.FAST,
            requested_amount=30.0
        )
        print(f"  创建快充请求: {queue_number}")
    
    # 创建慢充车辆队列
    slow_vehicles = test_vehicles[3:]
    for i, vehicle in enumerate(slow_vehicles):
        queue_number = service.submit_charging_request(
            user_id=test_user.id,
            vehicle_id=vehicle.id,
            charging_mode=ChargingMode.TRICKLE,
            requested_amount=40.0
        )
        print(f"  创建慢充请求: {queue_number}")
    
    # 启动一些充电
    fast_charging_queues = db.query(ChargingQueue).filter(
        ChargingQueue.charging_mode == ChargingMode.FAST,
        ChargingQueue.status == QueueStatus.QUEUING
    ).limit(2).all()
    
    for queue in fast_charging_queues:
        service.start_charging(queue.id)
        print(f"  启动充电: {queue.queue_number}")
    
    print("✅ 测试场景设置完成")
    return test_user

def test_priority_fault_scheduling(db: Session):
    """测试优先调度故障处理"""
    print("\n🚨 测试原则1：优先调度故障处理")
    print("-" * 30)
    
    service = ChargingScheduleService(db)
    
    print_system_status(db, "故障前系统状态")
    
    # 找到一个有车辆的快充桩
    fast_pile = db.query(ChargingPile).filter(
        ChargingPile.charging_mode == ChargingMode.FAST
    ).first()
    
    print(f"将充电桩 {fast_pile.pile_number} 设置为故障...")
    service.handle_pile_fault(fast_pile.id, "priority")
    
    print_system_status(db, "故障后系统状态 - 使用优先调度")

def test_time_order_fault_scheduling(db: Session):
    """测试时间顺序调度故障处理"""
    print("\n🚨 测试原则2：时间顺序调度故障处理")
    print("-" * 30)
    
    # 重新设置场景
    setup_test_scenario(db)
    
    service = ChargingScheduleService(db)
    
    print_system_status(db, "故障前系统状态")
    
    # 找到一个有车辆的快充桩
    fast_pile = db.query(ChargingPile).filter(
        ChargingPile.charging_mode == ChargingMode.FAST
    ).first()
    
    print(f"将充电桩 {fast_pile.pile_number} 设置为故障...")
    service.handle_pile_fault(fast_pile.id, "time_order")
    
    print_system_status(db, "故障后系统状态 - 使用时间顺序调度")

def test_fault_recovery_scheduling(db: Session):
    """测试故障恢复调度"""
    print("\n🔧 测试原则3：故障恢复调度")
    print("-" * 30)
    
    service = ChargingScheduleService(db)
    
    # 找到故障的充电桩
    fault_pile = db.query(ChargingPile).filter(
        ChargingPile.status == ChargingPileStatus.FAULT
    ).first()
    
    if fault_pile:
        print_system_status(db, "故障恢复前系统状态")
        
        print(f"恢复充电桩 {fault_pile.pile_number} 故障...")
        service.handle_pile_recovery(fault_pile.id)
        
        print_system_status(db, "故障恢复后系统状态")
    else:
        print("没有找到故障的充电桩")

def test_fault_area_priority(db: Session):
    """测试故障区优先调度"""
    print("\n⚡ 测试故障区优先调度")
    print("-" * 30)
    
    service = ChargingScheduleService(db)
    
    # 新增一些等候区车辆
    test_user = db.query(User).filter(User.username == "testuser").first()
    
    # 创建新车辆
    new_vehicle = Vehicle(
        license_plate="京A9999",
        model="新测试车型",
        battery_capacity=50.0,
        owner_id=test_user.id
    )
    db.add(new_vehicle)
    db.commit()
    
    # 提交新的充电请求
    queue_number = service.submit_charging_request(
        user_id=test_user.id,
        vehicle_id=new_vehicle.id,
        charging_mode=ChargingMode.FAST,
        requested_amount=25.0
    )
    print(f"新增等候区车辆: {queue_number}")
    
    print_system_status(db, "新增等候区车辆后")
    
    # 触发调度，看故障区车辆是否优先
    service.schedule_charging()
    
    print_system_status(db, "重新调度后（故障区应优先分配）")

def main():
    """主测试函数"""
    print("🧪 故障调度功能测试")
    print("=" * 50)
    
    db = next(get_db())
    
    try:
        # 设置测试场景
        test_user = setup_test_scenario(db)
        
        # 测试优先调度
        test_priority_fault_scheduling(db)
        
        # 测试时间顺序调度
        test_time_order_fault_scheduling(db)
        
        # 测试故障恢复调度
        test_fault_recovery_scheduling(db)
        
        # 测试故障区优先调度
        test_fault_area_priority(db)
        
        print("\n✅ 所有测试完成")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    main() 