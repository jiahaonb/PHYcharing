import requests
import json
from datetime import datetime

def test_admin_vehicle_detail_api():
    """测试管理端车辆详情API"""
    
    # API基础URL
    base_url = "http://localhost:8000"
    
    # 测试用的管理员登录信息（需要根据实际情况调整）
    admin_login_data = {
        "username": "admin",  # 请替换为实际的管理员用户名
        "password": "admin123"  # 请替换为实际的管理员密码
    }
    
    try:
        # 1. 登录获取token
        print("1. 尝试管理员登录...")
        login_response = requests.post(f"{base_url}/auth/login", data=admin_login_data)
        
        if login_response.status_code != 200:
            print(f"登录失败: {login_response.status_code}")
            print(login_response.text)
            return False
            
        token_data = login_response.json()
        token = token_data.get("access_token")
        
        if not token:
            print("未获取到访问令牌")
            return False
            
        print("登录成功，获取到token")
        
        # 2. 设置请求头
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 3. 获取车辆列表
        print("\n2. 获取车辆列表...")
        vehicles_response = requests.get(f"{base_url}/admin/vehicles", headers=headers)
        
        if vehicles_response.status_code != 200:
            print(f"获取车辆列表失败: {vehicles_response.status_code}")
            print(vehicles_response.text)
            return False
            
        vehicles = vehicles_response.json()
        print(f"找到 {len(vehicles)} 辆车")
        
        if not vehicles:
            print("没有车辆数据，无法测试车辆详情API")
            return False
            
        # 4. 测试新的车辆详情API
        test_vehicle_id = vehicles[0]["id"]
        print(f"\n3. 测试车辆详情API (车辆ID: {test_vehicle_id})...")
        
        detail_response = requests.get(f"{base_url}/admin/vehicles/{test_vehicle_id}/detail", headers=headers)
        
        if detail_response.status_code != 200:
            print(f"获取车辆详情失败: {detail_response.status_code}")
            print(detail_response.text)
            return False
            
        detail_data = detail_response.json()
        print("获取车辆详情成功!")
        
        # 5. 验证返回的数据结构
        print("\n4. 验证返回数据结构...")
        
        if detail_data.get("status") != "success":
            print(f"API返回状态异常: {detail_data.get('status')}")
            return False
            
        vehicle_detail = detail_data.get("data")
        if not vehicle_detail:
            print("返回数据中没有车辆详情")
            return False
            
        # 检查必要字段
        required_fields = ["id", "license_plate", "battery_capacity", "model", "status", "status_code", "owner"]
        missing_fields = []
        
        for field in required_fields:
            if field not in vehicle_detail:
                missing_fields.append(field)
                
        if missing_fields:
            print(f"缺少必要字段: {missing_fields}")
            return False
            
        print("数据结构验证通过")
        
        # 6. 打印详细信息
        print("\n5. 车辆详情信息:")
        print(f"  车牌号: {vehicle_detail['license_plate']}")
        print(f"  状态: {vehicle_detail['status']} ({vehicle_detail['status_code']})")
        print(f"  电池容量: {vehicle_detail['battery_capacity']}度")
        print(f"  车型: {vehicle_detail['model']}")
        
        if vehicle_detail.get('owner'):
            print(f"  车主: {vehicle_detail['owner']['username']}")
            
        if vehicle_detail.get('current_queue'):
            print("\n  当前队列信息:")
            queue = vehicle_detail['current_queue']
            print(f"    队列号: {queue.get('queue_number')}")
            print(f"    充电模式: {queue.get('charging_mode')}")
            print(f"    请求充电量: {queue.get('requested_amount')}度")
            print(f"    状态: {queue.get('status')}")
            
            if queue.get('charging_pile'):
                pile = queue['charging_pile']
                print(f"    分配充电桩: {pile.get('pile_number')}")
                
        if vehicle_detail.get('charging_history'):
            print(f"\n  历史充电记录: {len(vehicle_detail['charging_history'])}条")
            for i, record in enumerate(vehicle_detail['charging_history'][:3]):  # 只显示前3条
                print(f"    {i+1}. 记录号: {record.get('record_number')}")
                print(f"       充电量: {record.get('charging_amount')}度")
                print(f"       总费用: ¥{record.get('total_fee')}")
                
        print("\n测试完成: API工作正常!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("连接错误: 请确保后端服务正在运行 (http://localhost:8000)")
        return False
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        return False

if __name__ == "__main__":
    print("=== 管理端车辆详情API测试 ===")
    print("请确保:")
    print("1. 后端服务正在运行 (http://localhost:8000)")
    print("2. 数据库中有管理员用户和车辆数据")
    print("3. 修改脚本中的管理员登录信息\n")
    
    success = test_admin_vehicle_detail_api()
    if success:
        print("\n✅ 所有测试通过!")
    else:
        print("\n❌ 测试失败!") 