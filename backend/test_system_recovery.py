#!/usr/bin/env python3
"""
测试系统重启后的状态恢复功能
"""

import sys
sys.path.append('.')

from app.core.database import get_db
from app.models import ChargingQueue, ChargingPile, User, QueueStatus, ChargingPileStatus, ChargingMode
from app.services.system_scheduler import SystemScheduler
from sqlalchemy.orm import Session

def test_system_recovery():
    """测试系统状态恢复"""
    print("=== 系统状态恢复测试 ===")
    
    db = next(get_db())
    
    # 1. 检查当前数据状态
    print("\n1. 当前数据状态:")
    users = db.query(User).count()
    piles = db.query(ChargingPile).count()
    queues = db.query(ChargingQueue).count()
    
    print(f"   用户数: {users}")
    print(f"   充电桩数: {piles}")
    print(f"   排队记录数: {queues}")
    
    # 2. 显示排队记录详情
    print("\n2. 排队记录详情:")
    queue_records = db.query(ChargingQueue).all()
    for q in queue_records:
        pile_info = f"桩ID={q.charging_pile_id}" if q.charging_pile_id else "等候区"
        print(f"   队列 {q.queue_number}: 用户ID={q.user_id}, {pile_info}, 状态={q.status.value}")
    
    # 3. 显示充电桩状态
    print("\n3. 充电桩状态:")
    pile_records = db.query(ChargingPile).all()
    for p in pile_records:
        print(f"   {p.pile_number}: {p.charging_mode.value}, 状态={p.status.value}, 激活={p.is_active}")
    
    # 4. 运行系统恢复
    print("\n4. 运行系统状态恢复...")
    scheduler = SystemScheduler()
    scheduler.recover_system_state()
    
    # 5. 显示恢复后的状态
    print("\n5. 恢复后的排队记录:")
    queue_records = db.query(ChargingQueue).all()
    for q in queue_records:
        pile_info = f"桩ID={q.charging_pile_id}" if q.charging_pile_id else "等候区"
        print(f"   队列 {q.queue_number}: 用户ID={q.user_id}, {pile_info}, 状态={q.status.value}")

def test_user_queue_status():
    """测试用户排队状态查询"""
    print("\n=== 用户排队状态查询测试 ===")
    
    db = next(get_db())
    
    # 获取第一个用户
    user = db.query(User).first()
    if not user:
        print("没有找到用户，无法测试")
        return
    
    print(f"测试用户: {user.username} (ID: {user.id})")
    
    # 查询用户的活跃队列
    active_queues = db.query(ChargingQueue).filter(
        ChargingQueue.user_id == user.id,
        ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
    ).all()
    
    print(f"用户活跃队列数: {len(active_queues)}")
    
    for queue in active_queues:
        pile_name = "等候区"
        if queue.charging_pile_id:
            pile = db.query(ChargingPile).filter(ChargingPile.id == queue.charging_pile_id).first()
            if pile:
                pile_name = f"{pile.charging_mode.value}充电桩-{pile.pile_number}"
        
        print(f"   {queue.queue_number}: {pile_name}, 状态={queue.status.value}")

if __name__ == "__main__":
    try:
        test_system_recovery()
        test_user_queue_status()
        print("\n=== 测试完成 ===")
    except Exception as e:
        print(f"测试失败: {str(e)}")
        import traceback
        traceback.print_exc() 