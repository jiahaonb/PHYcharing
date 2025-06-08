import requests
import json

def test_admin_api():
    """测试管理端API调用"""
    
    base_url = "http://localhost:8000"
    
    print("=== 测试管理端车辆详情API ===")
    
    try:
        # 1. 首先测试不需要认证的API，确认服务正常
        print("1. 测试服务连接...")
        docs_response = requests.get(f"{base_url}/docs")
        print(f"   文档页面状态: {docs_response.status_code}")
        
        # 2. 尝试直接访问新的API端点（不带认证）
        print("\n2. 测试管理端车辆详情API（无认证）...")
        test_vehicle_id = 1  # 测试车辆ID
        api_url = f"{base_url}/api/v1/admin/vehicles/{test_vehicle_id}/detail"
        print(f"   请求URL: {api_url}")
        
        response = requests.get(api_url)
        print(f"   响应状态码: {response.status_code}")
        print(f"   响应内容: {response.text[:200]}...")
        
        if response.status_code == 401:
            print("   需要认证token，这是正常的")
        elif response.status_code == 404:
            print("   API端点不存在，可能是路由问题")
        elif response.status_code == 422:
            print("   参数验证失败")
        elif response.status_code == 500:
            print("   服务器内部错误")
        
        # 3. 测试是否有车辆数据
        print("\n3. 检查数据库中是否有车辆...")
        try:
            # 尝试获取车辆列表（如果有公开的API）
            vehicles_url = f"{base_url}/api/v1/admin/vehicles"
            vehicles_response = requests.get(vehicles_url)
            print(f"   车辆列表API状态: {vehicles_response.status_code}")
            
            if vehicles_response.status_code == 200:
                vehicles = vehicles_response.json()
                print(f"   找到 {len(vehicles)} 辆车")
                if vehicles:
                    print(f"   第一辆车ID: {vehicles[0].get('id')}")
            
        except Exception as e:
            print(f"   获取车辆列表失败: {e}")
        
        # 4. 检查API路由
        print("\n4. 检查可用的API路由...")
        try:
            openapi_response = requests.get(f"{base_url}/openapi.json")
            if openapi_response.status_code == 200:
                openapi_data = openapi_response.json()
                paths = openapi_data.get('paths', {})
                admin_paths = [path for path in paths.keys() if '/admin/' in path]
                print(f"   找到 {len(admin_paths)} 个管理端API:")
                for path in admin_paths[:10]:  # 只显示前10个
                    print(f"     {path}")
                
                # 检查我们的新API是否存在
                our_api = "/api/v1/admin/vehicles/{vehicle_id}/detail"
                if our_api in paths:
                    print(f"   ✅ 找到我们的新API: {our_api}")
                else:
                    print(f"   ❌ 没有找到我们的新API: {our_api}")
                    
        except Exception as e:
            print(f"   检查API路由失败: {e}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_admin_api() 