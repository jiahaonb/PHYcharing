#!/usr/bin/env python3
"""
测试充电场景API的脚本
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_TOKEN = None

def login_admin():
    """管理员登录获取token"""
    global ADMIN_TOKEN
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": "admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            token_data = response.json()
            ADMIN_TOKEN = token_data.get("access_token")
            print("✅ 管理员登录成功")
            return True
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False

def test_api(endpoint, description):
    """测试API端点"""
    if not ADMIN_TOKEN:
        print("❌ 未获取到token，跳过测试")
        return
    
    try:
        headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: 成功 (返回 {len(data) if isinstance(data, list) else 1} 条记录)")
            return data
        else:
            print(f"❌ {description}: 失败 ({response.status_code})")
            print(f"   错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ {description}: 异常 - {e}")
        return None

def main():
    """主测试函数"""
    print("🔄 开始测试充电场景API...")
    print("-" * 50)
    
    # 1. 管理员登录
    if not login_admin():
        print("❌ 无法继续测试，退出")
        sys.exit(1)
    
    print("-" * 50)
    
    # 2. 测试各个API端点
    vehicles = test_api("/admin/scene/vehicles", "获取车辆数据")
    piles = test_api("/admin/scene/charging-piles", "获取充电桩数据")
    queues = test_api("/admin/scene/charging-queue", "获取队列数据")
    
    print("-" * 50)
    
    # 3. 数据概览
    if vehicles is not None:
        print(f"📊 车辆总数: {len(vehicles)}")
        if vehicles:
            print(f"   示例车辆: {vehicles[0].get('license_plate', 'N/A')}")
    
    if piles is not None:
        print(f"📊 充电桩总数: {len(piles)}")
        if piles:
            fast_piles = [p for p in piles if p.get('type') == 'fast']
            trickle_piles = [p for p in piles if p.get('type') == 'trickle']
            print(f"   快充桩: {len(fast_piles)} 个")
            print(f"   慢充桩: {len(trickle_piles)} 个")
    
    if queues is not None:
        print(f"📊 队列记录总数: {len(queues)}")
        if queues:
            waiting = [q for q in queues if q.get('status') == 'waiting']
            charging = [q for q in queues if q.get('status') == 'charging']
            print(f"   等待中: {len(waiting)} 个")
            print(f"   充电中: {len(charging)} 个")
    
    print("-" * 50)
    print("🎉 API测试完成!")

if __name__ == "__main__":
    main() 