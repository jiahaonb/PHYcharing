import requests
import json

def test_admin_auth_and_api():
    """测试管理员认证和API调用"""
    
    base_url = "http://localhost:8000"
    
    print("=== 测试管理员认证和API调用 ===")
    
    # 管理员登录信息（根据实际情况调整）
    admin_credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # 1. 管理员登录
        print("1. 尝试管理员登录...")
        
        login_data = {
            "username": admin_credentials["username"],
            "password": admin_credentials["password"]
        }
        
        login_response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data)
        print(f"   登录状态码: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"   登录失败: {login_response.text}")
            return
            
        login_result = login_response.json()
        token = login_result.get("access_token")
        
        if not token:
            print("   未获取到访问令牌")
            return
            
        print("   登录成功，获取到token")
        
        # 2. 验证用户信息
        print("\n2. 验证用户信息...")
        headers = {"Authorization": f"Bearer {token}"}
        
        me_response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
        print(f"   用户信息状态码: {me_response.status_code}")
        
        if me_response.status_code == 200:
            user_info = me_response.json()
            print(f"   用户名: {user_info.get('username')}")
            print(f"   是否管理员: {user_info.get('is_admin')}")
            
            if not user_info.get('is_admin'):
                print("   ❌ 当前用户不是管理员")
                return
        else:
            print(f"   获取用户信息失败: {me_response.text}")
            return
        
        # 3. 测试车辆详情API
        print("\n3. 测试车辆详情API...")
        
        # 先获取车辆列表
        vehicles_response = requests.get(f"{base_url}/api/v1/admin/vehicles", headers=headers)
        print(f"   车辆列表状态码: {vehicles_response.status_code}")
        
        if vehicles_response.status_code == 200:
            vehicles = vehicles_response.json()
            print(f"   找到 {len(vehicles)} 辆车")
            
            if vehicles:
                test_vehicle_id = vehicles[0]["id"]
                print(f"   测试车辆ID: {test_vehicle_id}")
                
                # 测试车辆详情API
                detail_response = requests.get(
                    f"{base_url}/api/v1/admin/vehicles/{test_vehicle_id}/detail", 
                    headers=headers
                )
                print(f"   车辆详情API状态码: {detail_response.status_code}")
                print(f"   响应内容: {detail_response.text[:300]}...")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print("   ✅ 车辆详情API调用成功！")
                    print(f"   车辆信息: {detail_data.get('data', {}).get('license_plate', 'N/A')}")
                else:
                    print(f"   ❌ 车辆详情API调用失败")
            else:
                print("   没有车辆数据，无法测试")
        else:
            print(f"   获取车辆列表失败: {vehicles_response.text}")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_admin_auth_and_api() 