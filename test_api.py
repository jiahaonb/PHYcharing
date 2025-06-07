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

def test_user_queue_status(token):
    """测试用户队列状态API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/users/queue/status", headers=headers)
    print(f"\n🔍 测试用户队列状态API:")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ API正常工作")
        print(f"返回数据: {response.json()}")
    else:
        print(f"❌ API错误: {response.text}")

def test_admin_queue_summary(token):
    """测试管理员队列概览API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/admin/queue/summary", headers=headers)
    print(f"\n🔍 测试管理员队列概览API:")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ API正常工作")
        print(f"返回数据: {response.json()}")
    else:
        print(f"❌ API错误: {response.text}")

def test_admin_queue_piles(token):
    """测试管理员充电桩队列API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/admin/queue/piles", headers=headers)
    print(f"\n🔍 测试管理员充电桩队列API:")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ API正常工作")
        print(f"返回数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ API错误: {response.text}")

def test_admin_queue_logs(token):
    """测试管理员队列日志API"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/admin/queue/logs", headers=headers)
    print(f"\n🔍 测试管理员队列日志API:")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ API正常工作")
        print(f"返回数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ API错误: {response.text}")

if __name__ == "__main__":
    print("🚀 开始测试新增的API端点...")
    
    # 获取访问token
    token = test_login()
    if not token:
        print("❌ 无法获取访问token，退出测试")
        exit(1)
    
    # 测试各个API端点
    test_user_queue_status(token)
    test_admin_queue_summary(token)
    test_admin_queue_piles(token)
    test_admin_queue_logs(token)
    
    print("\n🎉 API测试完成！") 