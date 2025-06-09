#!/usr/bin/env python3
"""
测试故障设置和恢复API
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8088/api/v1"

# 测试用户凭证 - 需要是管理员账户
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_and_get_token():
    """登录并获取访问令牌"""
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"登录请求失败: {e}")
        return None

def get_auth_headers(token):
    """获取包含认证的请求头"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_get_piles(token):
    """获取充电桩列表"""
    print("\n🔍 获取充电桩列表...")
    
    try:
        headers = get_auth_headers(token)
        response = requests.get(f"{BASE_URL}/admin/piles", headers=headers)
        
        if response.status_code == 200:
            piles = response.json()
            print(f"✅ 成功获取 {len(piles)} 个充电桩")
            
            for pile in piles[:3]:  # 显示前3个
                print(f"  - ID: {pile['id']}, 编号: {pile['pile_number']}, 状态: {pile['status']}")
            
            return piles
        else:
            print(f"❌ 获取充电桩失败: {response.status_code} - {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def test_set_fault(token, pile_id, strategy="priority"):
    """测试设置故障"""
    print(f"\n🚨 设置充电桩 {pile_id} 为故障状态 (策略: {strategy})...")
    
    try:
        headers = get_auth_headers(token)
        url = f"{BASE_URL}/admin/piles/{pile_id}/fault"
        params = {"strategy": strategy}
        
        response = requests.post(url, headers=headers, params=params)
        
        print(f"请求URL: {url}")
        print(f"请求参数: {params}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 故障设置成功: {result}")
            return True
        else:
            print(f"❌ 故障设置失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_recover_fault(token, pile_id):
    """测试故障恢复"""
    print(f"\n🔧 恢复充电桩 {pile_id} 故障状态...")
    
    try:
        headers = get_auth_headers(token)
        url = f"{BASE_URL}/admin/piles/{pile_id}/recovery"
        
        response = requests.post(url, headers=headers)
        
        print(f"请求URL: {url}")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 故障恢复成功: {result}")
            return True
        else:
            print(f"❌ 故障恢复失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_fault_vehicles_api(token):
    """测试故障车辆API"""
    print("\n📋 获取故障区车辆...")
    
    try:
        headers = get_auth_headers(token)
        response = requests.get(f"{BASE_URL}/admin/scene/fault-vehicles", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 故障车辆API响应成功")
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 故障车辆API失败: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

# 测试故障API
def test_fault_api():
    try:
        # 测试不需要token的本地API调用
        response = requests.get("http://localhost:8088/api/v1/admin/scene/fault-vehicles")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("API响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 检查数据结构
            print("\n数据分析:")
            print(f"快充故障数量: {len(data.get('fast_fault', []))}")
            print(f"慢充故障数量: {len(data.get('trickle_fault', []))}")
            
            # 检查每个故障订单的数据
            for order in data.get('fast_fault', []):
                print(f"快充故障订单: record_number={order.get('record_number')}, queue_number={order.get('queue_number')}")
            
            for order in data.get('trickle_fault', []):
                print(f"慢充故障订单: record_number={order.get('record_number')}, queue_number={order.get('queue_number')}")
                
        else:
            print(f"API调用失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 故障设置和恢复API测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 登录获取令牌
    print("🔐 正在登录...")
    token = login_and_get_token()
    
    if not token:
        print("❌ 无法获取访问令牌，请检查用户名和密码")
        exit(1)
    
    print("✅ 登录成功，获得访问令牌")
    
    # 获取充电桩列表
    piles = test_get_piles(token)
    
    if not piles:
        print("❌ 无法获取充电桩列表")
        exit(1)
    
    # 选择第一个充电桩进行测试
    test_pile_id = piles[0]["id"]
    print(f"\n🎯 使用充电桩 ID {test_pile_id} 进行测试")
    
    # 测试故障设置
    fault_success = test_set_fault(token, test_pile_id, "priority")
    
    # 测试故障车辆API
    test_fault_vehicles_api(token)
    
    # 测试故障恢复
    if fault_success:
        recovery_success = test_recover_fault(token, test_pile_id)
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")

    # 测试故障API
    test_fault_api() 