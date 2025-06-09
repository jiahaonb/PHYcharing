#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的故障调度功能测试
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def login_admin():
    """管理员登录"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        else:
            print(f"登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"连接服务器失败: {e}")
        return None

def get_charging_piles(headers):
    """获取充电桩列表"""
    try:
        response = requests.get(f"{BASE_URL}/admin/piles", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取充电桩失败: {response.text}")
            return []
    except Exception as e:
        print(f"获取充电桩异常: {e}")
        return []

def get_queue_status(headers):
    """获取队列状态"""
    try:
        response = requests.get(f"{BASE_URL}/admin/queue/piles", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取队列状态失败: {response.text}")
            return []
    except Exception as e:
        print(f"获取队列状态异常: {e}")
        return []

def set_pile_fault(pile_id, strategy, headers):
    """设置充电桩故障"""
    try:
        response = requests.post(
            f"{BASE_URL}/admin/piles/{pile_id}/fault?strategy={strategy}", 
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ 充电桩 {pile_id} 故障设置成功: {response.json()['message']}")
            return True
        else:
            print(f"❌ 设置故障失败: {response.text}")
            return False
    except Exception as e:
        print(f"设置故障异常: {e}")
        return False

def recover_pile_fault(pile_id, headers):
    """恢复充电桩故障"""
    try:
        response = requests.post(
            f"{BASE_URL}/admin/piles/{pile_id}/recovery", 
            headers=headers
        )
        if response.status_code == 200:
            print(f"✅ 充电桩 {pile_id} 故障恢复成功: {response.json()['message']}")
            return True
        else:
            print(f"❌ 故障恢复失败: {response.text}")
            return False
    except Exception as e:
        print(f"故障恢复异常: {e}")
        return False

def print_system_status(headers, title):
    """打印系统状态"""
    print(f"\n{title}")
    print("=" * 50)
    
    # 获取充电桩状态
    piles = get_charging_piles(headers)
    print("充电桩状态:")
    for pile in piles:
        status = pile['status']
        active = "激活" if pile['is_active'] else "禁用"
        print(f"  {pile['pile_number']}: {status} ({active})")
    
    # 获取队列状态
    queues = get_queue_status(headers)
    print("\n队列状态:")
    for queue in queues:
        pile_name = queue['pile_name']
        queue_length = queue['queue_length']
        current_user = queue.get('current_user', '无')
        print(f"  {pile_name}: 队列长度={queue_length}, 当前用户={current_user}")
        
        # 显示队列详情
        if queue.get('queue_details'):
            for detail in queue['queue_details']:
                status = detail['status']
                username = detail['username']
                print(f"    - {username} ({status})")
    
    print()

def test_fault_scheduling():
    """测试故障调度功能"""
    print("🧪 故障调度功能API测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(3)
    
    # 登录管理员
    headers = login_admin()
    if not headers:
        print("❌ 无法登录管理员账户，请确保后端服务已启动")
        return
    
    print("✅ 管理员登录成功")
    
    # 显示初始状态
    print_system_status(headers, "初始系统状态")
    
    # 获取充电桩列表
    piles = get_charging_piles(headers)
    if not piles:
        print("❌ 没有找到充电桩")
        return
    
    # 找到一个正常的充电桩进行故障测试
    normal_pile = None
    for pile in piles:
        if pile['status'] == 'normal' and pile['is_active']:
            normal_pile = pile
            break
    
    if not normal_pile:
        print("❌ 没有找到正常状态的充电桩")
        return
    
    pile_id = normal_pile['id']
    pile_number = normal_pile['pile_number']
    
    print(f"\n🚨 测试充电桩 {pile_number} (ID: {pile_id}) 故障处理")
    
    # 测试优先调度策略
    print("\n--- 测试优先调度策略 ---")
    if set_pile_fault(pile_id, "priority", headers):
        print_system_status(headers, "故障后状态 - 优先调度")
    
    # 恢复故障
    print("\n--- 测试故障恢复 ---")
    if recover_pile_fault(pile_id, headers):
        print_system_status(headers, "故障恢复后状态")
    
    # 测试时间顺序调度策略
    print("\n--- 测试时间顺序调度策略 ---")
    if set_pile_fault(pile_id, "time_order", headers):
        print_system_status(headers, "故障后状态 - 时间顺序调度")
    
    # 再次恢复故障
    print("\n--- 再次测试故障恢复 ---")
    if recover_pile_fault(pile_id, headers):
        print_system_status(headers, "最终状态")
    
    print("\n✅ 故障调度功能测试完成")

if __name__ == "__main__":
    try:
        test_fault_scheduling()
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc() 