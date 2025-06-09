"""
测试新的排队状态界面功能
验证：
1. 显示用户的所有当前订单
2. 车辆矩形模块显示
3. 等候区修改充电模式和充电量
4. 充电区修改充电量和取消充电
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def get_user_token():
    """获取用户token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"获取token失败: {response.status_code}")
        return None

def test_user_queue_status():
    """测试用户排队状态API"""
    print("=" * 60)
    print("🧪 测试用户排队状态API")
    print("=" * 60)
    
    token = get_user_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("1. 获取用户排队状态...")
        response = requests.get(f"{BASE_URL}/users/queue/status", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ 成功获取 {len(orders)} 个订单")
            
            for i, order in enumerate(orders, 1):
                print(f"\n📋 订单 {i}:")
                print(f"   订单号: {order['queue_number']}")
                print(f"   车牌号: {order['vehicle_license']}")
                print(f"   充电模式: {order['charging_mode']}")
                print(f"   充电量: {order['requested_amount']}度")
                print(f"   状态: {order['status']}")
                print(f"   位置: {order['pile_name']}")
                if order['position']:
                    print(f"   排队位置: 第{order['position']}位")
                if order['estimated_time'] > 0:
                    print(f"   预计等待: {order['estimated_time']}分钟")
                
                # 根据状态显示操作
                if order['status'] == 'waiting':
                    print(f"   🔧 可操作: 修改请求、取消排队")
                elif order['status'] == 'queuing':
                    print(f"   🔧 可操作: 修改充电量、取消排队")
                elif order['status'] == 'charging':
                    print(f"   🔧 可操作: 结束充电")
            
            if len(orders) == 0:
                print("   📝 当前没有排队订单")
        else:
            print(f"❌ 获取失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_modify_charging_request():
    """测试修改充电请求功能"""
    print("\n" + "=" * 60)
    print("🔧 测试修改充电请求功能")
    print("=" * 60)
    
    token = get_user_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. 获取当前订单
        print("1. 获取当前订单...")
        response = requests.get(f"{BASE_URL}/users/queue/status", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            if not orders:
                print("   📝 没有订单可以修改")
                return
            
            waiting_orders = [o for o in orders if o['status'] == 'waiting']
            queuing_orders = [o for o in orders if o['status'] == 'queuing']
            
            # 2. 测试修改等候区订单（完整修改）
            if waiting_orders:
                order = waiting_orders[0]
                print(f"\n2. 测试修改等候区订单 {order['queue_number']}...")
                
                modify_data = {
                    "charging_mode": "trickle" if order['charging_mode'] == 'fast' else "fast",
                    "requested_amount": order['requested_amount'] + 5
                }
                
                print(f"   原充电模式: {order['charging_mode']}")
                print(f"   新充电模式: {modify_data['charging_mode']}")
                print(f"   原充电量: {order['requested_amount']}度")
                print(f"   新充电量: {modify_data['requested_amount']}度")
                
                response = requests.put(
                    f"{BASE_URL}/charging/modify/{order['id']}", 
                    headers=headers,
                    json=modify_data
                )
                
                if response.status_code == 200:
                    print("   ✅ 等候区订单修改成功")
                else:
                    print(f"   ❌ 修改失败: {response.status_code}")
                    print(f"   错误信息: {response.text}")
            
            # 3. 测试修改充电区订单（仅充电量）
            if queuing_orders:
                order = queuing_orders[0]
                print(f"\n3. 测试修改充电区订单 {order['queue_number']}...")
                
                modify_data = {
                    "requested_amount": order['requested_amount'] + 2
                }
                
                print(f"   原充电量: {order['requested_amount']}度")
                print(f"   新充电量: {modify_data['requested_amount']}度")
                
                response = requests.put(
                    f"{BASE_URL}/charging/modify/{order['id']}", 
                    headers=headers,
                    json=modify_data
                )
                
                if response.status_code == 200:
                    print("   ✅ 充电区订单修改成功")
                else:
                    print(f"   ❌ 修改失败: {response.status_code}")
                    print(f"   错误信息: {response.text}")
                
                # 4. 尝试修改充电区的充电模式（应该失败）
                print(f"\n4. 测试修改充电区充电模式（应该失败）...")
                
                invalid_modify_data = {
                    "charging_mode": "trickle" if order['charging_mode'] == 'fast' else "fast"
                }
                
                response = requests.put(
                    f"{BASE_URL}/charging/modify/{order['id']}", 
                    headers=headers,
                    json=invalid_modify_data
                )
                
                if response.status_code == 400:
                    print("   ✅ 正确阻止了充电区充电模式修改")
                else:
                    print(f"   ❌ 应该阻止修改但没有: {response.status_code}")
                    
        else:
            print(f"❌ 获取订单失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_cancel_charging():
    """测试取消充电功能"""
    print("\n" + "=" * 60)
    print("🚫 测试取消充电功能")
    print("=" * 60)
    
    token = get_user_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 获取可以取消的订单
        print("1. 获取可取消的订单...")
        response = requests.get(f"{BASE_URL}/users/queue/status", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            cancelable_orders = [o for o in orders if o['status'] in ['waiting', 'queuing']]
            
            if cancelable_orders:
                order = cancelable_orders[0]
                print(f"\n2. 测试取消订单 {order['queue_number']}...")
                print(f"   车牌号: {order['vehicle_license']}")
                print(f"   状态: {order['status']}")
                
                response = requests.delete(
                    f"{BASE_URL}/charging/cancel/{order['id']}", 
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("   ✅ 订单取消成功")
                else:
                    print(f"   ❌ 取消失败: {response.status_code}")
                    print(f"   错误信息: {response.text}")
            else:
                print("   📝 没有可取消的订单")
                
        else:
            print(f"❌ 获取订单失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_ui_data_format():
    """测试UI所需的数据格式"""
    print("\n" + "=" * 60)
    print("🎨 测试UI数据格式")
    print("=" * 60)
    
    token = get_user_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("1. 检查API返回的数据格式...")
        response = requests.get(f"{BASE_URL}/users/queue/status", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            
            required_fields = [
                'id', 'queue_number', 'vehicle_id', 'vehicle_license', 
                'charging_mode', 'requested_amount', 'pile_name', 
                'position', 'estimated_time', 'request_time', 'status'
            ]
            
            if orders:
                order = orders[0]
                print(f"\n2. 检查订单数据字段...")
                
                missing_fields = []
                for field in required_fields:
                    if field not in order:
                        missing_fields.append(field)
                    else:
                        print(f"   ✅ {field}: {order[field]}")
                
                if missing_fields:
                    print(f"\n   ❌ 缺少字段: {missing_fields}")
                else:
                    print(f"\n   ✅ 所有必需字段都存在")
                    
                # 检查状态映射
                print(f"\n3. 检查状态映射...")
                status_map = {
                    'waiting': '等候区',
                    'queuing': '排队中',
                    'charging': '充电中'
                }
                
                for order in orders:
                    status = order['status']
                    if status in status_map:
                        print(f"   ✅ 状态 {status} -> {status_map[status]}")
                    else:
                        print(f"   ❌ 未知状态: {status}")
                        
            else:
                print("   📝 没有订单数据可以检查")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试新的排队状态界面功能")
    
    # 运行所有测试
    test_user_queue_status()
    test_modify_charging_request()
    test_cancel_charging()
    test_ui_data_format()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60) 