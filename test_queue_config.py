#!/usr/bin/env python3
"""
测试充电桩排队位配置获取功能
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_admin_token():
    """获取管理员token"""
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"登录失败: {response.status_code} - {response.text}")
        return None

def test_queue_config_api(token):
    """测试队列配置API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("=== 测试充电桩排队位配置获取 ===")
    
    # 1. 获取特定配置项
    try:
        response = requests.get(
            f"{BASE_URL}/admin/config/queue_settings.charging_queue_len",
            headers=headers
        )
        
        if response.status_code == 200:
            config = response.json()
            print(f"✅ 获取配置成功:")
            print(f"   配置键: {config['config_key']}")
            print(f"   配置值: {config['config_value']}")
            print(f"   配置类型: {config['config_type']}")
            print(f"   描述: {config.get('description', '无')}")
            print(f"   分类: {config['category']}")
            print(f"   是否激活: {config['is_active']}")
            
            return int(config['config_value'])
        else:
            print(f"❌ 获取配置失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_update_config(token, new_value):
    """测试更新配置"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== 测试更新配置为 {new_value} ===")
    
    update_data = {
        "config_value": str(new_value),
        "description": f"每个充电桩的排队位数量（测试更新为{new_value}）",
        "is_active": True
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/config/queue_settings.charging_queue_len",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            config = response.json()
            print(f"✅ 更新配置成功:")
            print(f"   新配置值: {config['config_value']}")
            return True
        else:
            print(f"❌ 更新配置失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_scene_api(token):
    """测试场景动画API是否能正确获取配置"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n=== 测试场景动画相关API ===")
    
    # 测试充电桩API
    try:
        response = requests.get(
            f"{BASE_URL}/admin/scene/charging-piles",
            headers=headers
        )
        
        if response.status_code == 200:
            piles = response.json()
            print(f"✅ 获取充电桩数据成功，数量: {len(piles)}")
            
            if piles:
                pile = piles[0]
                print(f"   示例充电桩: {pile.get('pile_id', 'N/A')}")
                print(f"   排队订单数: {len(pile.get('queue_orders', []))}")
                
        else:
            print(f"❌ 获取充电桩数据失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    print("开始测试充电桩排队位配置...")
    
    # 获取token
    token = get_admin_token()
    if not token:
        print("无法获取管理员token，退出测试")
        exit(1)
    
    # 测试获取当前配置
    current_value = test_queue_config_api(token)
    if current_value is None:
        print("无法获取当前配置，退出测试")
        exit(1)
    
    print(f"\n当前排队位数量配置: {current_value}")
    
    # 测试更新配置
    test_values = [5, 4, 3]  # 测试不同的值
    
    for test_value in test_values:
        if test_value != current_value:
            print(f"\n--- 测试设置为 {test_value} ---")
            if test_update_config(token, test_value):
                # 验证更新后的值
                updated_value = test_queue_config_api(token)
                if updated_value == test_value:
                    print(f"✅ 配置更新验证成功: {updated_value}")
                else:
                    print(f"❌ 配置更新验证失败: 期望{test_value}, 实际{updated_value}")
            break
    
    # 恢复原始值
    print(f"\n--- 恢复原始配置 {current_value} ---")
    test_update_config(token, current_value)
    
    # 测试场景API
    test_scene_api(token)
    
    print("\n测试完成！")
    print("\n💡 提示:")
    print("1. 前端页面现在会从配置中动态获取排队位数量")
    print("2. 在管理员'系统配置'页面修改'queue_settings.charging_queue_len'")
    print("3. 在充电场景动画页面点击'重载配置'按钮应用新配置")
    print("4. 排队位的矩形框数量会根据配置动态生成") 