#!/usr/bin/env python3
"""
测试实际充电信息字段的功能
"""
import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_actual_charging_fields():
    """测试实际充电信息字段"""
    print("🧪 开始测试实际充电信息字段...")
    
    # 1. 登录管理员账户
    print("1. 登录管理员账户...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 获取订单列表，查看现有订单
    print("2. 获取订单列表...")
    response = requests.get(f"{BASE_URL}/admin/orders", headers=headers)
    if response.status_code != 200:
        print(f"❌ 获取订单失败: {response.text}")
        return
    
    orders_data = response.json()
    orders = orders_data.get('orders', [])
    print(f"✅ 获取到 {len(orders)} 个订单")
    
    # 3. 查看第一个订单的字段
    if orders:
        order = orders[0]
        print(f"📋 订单 {order['id']} 的信息:")
        print(f"  - 计划充电量: {order.get('total_amount', 'N/A')}")
        print(f"  - 实际充电量: {order.get('actual_charging_amount', 'N/A')}")
        print(f"  - 计划费用: {order.get('total_fee', 'N/A')}")
        print(f"  - 实际充电费: {order.get('actual_electricity_fee', 'N/A')}")
        print(f"  - 实际服务费: {order.get('actual_service_fee', 'N/A')}")
        print(f"  - 实际总费用: {order.get('actual_total_fee', 'N/A')}")
        print(f"  - 订单状态: {order.get('status', 'N/A')}")
        
        # 4. 如果有未完成的订单，尝试完成它
        incomplete_orders = [o for o in orders if o.get('status') not in ['completed']]
        if incomplete_orders:
            test_order = incomplete_orders[0]
            print(f"4. 测试完成订单 {test_order['id']}...")
            
            response = requests.post(
                f"{BASE_URL}/admin/orders/{test_order['id']}/complete",
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ 订单完成成功")
                
                # 重新获取订单信息
                print("5. 重新获取订单信息查看实际字段...")
                response = requests.get(f"{BASE_URL}/admin/orders", headers=headers)
                updated_orders = response.json().get('orders', [])
                
                # 找到刚才完成的订单
                completed_order = next((o for o in updated_orders if o['id'] == test_order['id']), None)
                if completed_order:
                    print(f"📋 完成后的订单信息:")
                    print(f"  - 计划充电量: {completed_order.get('total_amount', 'N/A')}")
                    print(f"  - 实际充电量: {completed_order.get('actual_charging_amount', 'N/A')}")
                    print(f"  - 计划费用: {completed_order.get('total_fee', 'N/A')}")
                    print(f"  - 实际充电费: {completed_order.get('actual_electricity_fee', 'N/A')}")
                    print(f"  - 实际服务费: {completed_order.get('actual_service_fee', 'N/A')}")
                    print(f"  - 实际总费用: {completed_order.get('actual_total_fee', 'N/A')}")
                    print(f"  - 订单状态: {completed_order.get('status', 'N/A')}")
                    
                    # 验证实际字段是否有值
                    if completed_order.get('actual_charging_amount') is not None:
                        print("✅ 实际充电信息字段更新成功！")
                    else:
                        print("❌ 实际充电信息字段未更新")
            else:
                print(f"❌ 完成订单失败: {response.text}")
        else:
            print("4. 没有未完成的订单可供测试")
    else:
        print("❌ 没有订单数据")

if __name__ == "__main__":
    test_actual_charging_fields() 