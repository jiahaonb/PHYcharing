#!/usr/bin/env python3
"""
测试业务逻辑修复：重复请求验证和状态同步
"""

import sys
sys.path.append('.')

from app.core.database import get_db
from app.models import ChargingQueue, ChargingPile, User, Vehicle, QueueStatus, ChargingMode
from app.services.charging_service import ChargingScheduleService

def test_duplicate_request_prevention():
    """测试防止重复充电请求"""
    print("=== 测试防止重复充电请求 ===")
    
    db = next(get_db())
    service = ChargingScheduleService(db)
    
    # 获取测试用户和车辆
    user = db.query(User).first()
    vehicle = db.query(Vehicle).first()
    
    if not user or not vehicle:
        print("没有找到测试用户或车辆")
        return
    
    print(f"测试用户: {user.username} (ID: {user.id})")
    print(f"测试车辆: {vehicle.license_plate} (ID: {vehicle.id})")
    
    try:
        # 第一次提交充电请求
        print("\n1. 第一次提交充电请求...")
        queue_number1 = service.submit_charging_request(
            user_id=user.id,
            vehicle_id=vehicle.id,
            charging_mode=ChargingMode.FAST,
            requested_amount=50.0
        )
        print(f"   成功提交，排队号: {queue_number1}")
        
        # 尝试第二次提交（应该被阻止）
        print("\n2. 尝试第二次提交充电请求...")
        try:
            queue_number2 = service.submit_charging_request(
                user_id=user.id,
                vehicle_id=vehicle.id,
                charging_mode=ChargingMode.FAST,
                requested_amount=30.0
            )
            print(f"   错误：居然成功了，排队号: {queue_number2}")
        except Exception as e:
            print(f"   正确：被阻止了，错误信息: {str(e)}")
            
        # 取消第一个请求
        print("\n3. 取消第一个请求...")
        first_queue = db.query(ChargingQueue).filter(
            ChargingQueue.queue_number == queue_number1
        ).first()
        if first_queue:
            service.cancel_charging(first_queue.id)
            print("   已取消第一个请求")
        
        # 再次尝试提交（现在应该可以）
        print("\n4. 取消后再次提交...")
        queue_number3 = service.submit_charging_request(
            user_id=user.id,
            vehicle_id=vehicle.id,
            charging_mode=ChargingMode.TRICKLE,
            requested_amount=40.0
        )
        print(f"   成功提交，排队号: {queue_number3}")
        
    except Exception as e:
        print(f"测试过程出错: {str(e)}")
        import traceback
        traceback.print_exc()

def test_pile_status_sync():
    """测试充电桩状态同步"""
    print("\n=== 测试充电桩状态同步 ===")
    
    db = next(get_db())
    
    # 查看所有充电桩及其当前状态
    print("\n充电桩状态检查:")
    piles = db.query(ChargingPile).all()
    for pile in piles:
        # 检查是否有正在充电的车辆
        charging_queue = db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile.id,
            ChargingQueue.status == QueueStatus.CHARGING
        ).first()
        
        # 检查是否有排队的车辆
        queuing_count = db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile.id,
            ChargingQueue.status == QueueStatus.QUEUING
        ).count()
        
        actual_status = "空闲"
        if charging_queue:
            actual_status = f"充电中({charging_queue.user.username if charging_queue.user else '未知用户'})"
        elif queuing_count > 0:
            actual_status = f"有{queuing_count}人排队"
        
        print(f"   {pile.pile_number}: 基础状态={pile.status.value}, 实际状态={actual_status}")

def test_queue_status_display():
    """测试用户排队状态显示"""
    print("\n=== 测试用户排队状态显示 ===")
    
    db = next(get_db())
    
    users = db.query(User).all()
    for user in users:
        # 模拟用户端API调用
        active_queues = db.query(ChargingQueue).filter(
            ChargingQueue.user_id == user.id,
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).all()
        
        print(f"\n用户 {user.username} 的活跃排队:")
        if not active_queues:
            print("   无活跃排队")
        else:
            for queue in active_queues:
                pile_name = "等候区"
                if queue.charging_pile_id:
                    pile = db.query(ChargingPile).filter(ChargingPile.id == queue.charging_pile_id).first()
                    if pile:
                        pile_name = f"{pile.charging_mode.value}充电桩-{pile.pile_number}"
                
                print(f"   {queue.queue_number}: {pile_name}, 状态={queue.status.value}")

if __name__ == "__main__":
    try:
        test_duplicate_request_prevention()
        test_pile_status_sync()
        test_queue_status_display()
        print("\n=== 测试完成 ===")
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc() 