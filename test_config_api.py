import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login():
    """测试登录并获取token"""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        result = response.json()
        print("✅ 登录成功")
        return result.get("access_token")
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return None

def test_config_api(token):
    """测试配置API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试获取所有配置
    response = requests.get(f"{BASE_URL}/admin/config/", headers=headers)
    if response.status_code == 200:
        configs = response.json()
        print(f"✅ 获取配置成功，共 {len(configs)} 个配置项")
        # 显示前3个配置项
        for i, config in enumerate(configs[:3]):
            print(f"  {i+1}. {config['config_key']}: {config['config_value']}")
        return True
    else:
        print(f"❌ 获取配置失败: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("🚀 开始测试配置API...")
    
    # 先登录获取token
    token = test_login()
    if not token:
        print("❌ 无法获取访问令牌，测试终止")
        exit(1)
    
    # 测试配置API
    if test_config_api(token):
        print("✅ 配置API测试通过")
    else:
        print("❌ 配置API测试失败") 