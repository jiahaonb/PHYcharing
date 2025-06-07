#!/usr/bin/env python3
"""测试HTTP API请求"""

import requests
import json

def test_http_api():
    print("🌐 测试HTTP API请求")
    
    # 首先测试服务是否启动
    try:
        print("🔍 检查服务状态...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ 服务正常运行，状态码: {response.status_code}")
        print(f"📝 响应内容: {response.json()}")
    except Exception as e:
        print(f"❌ 服务无法访问: {e}")
        return
    
    # 测试用户登录获取token
    try:
        print("\n🔐 测试用户登录...")
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data=login_data,
            timeout=10
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ 登录成功，获取到token")
            
            # 测试排队数据API
            print("\n📊 测试排队数据API...")
            headers = {"Authorization": f"Bearer {token}"}
            queue_response = requests.get(
                "http://localhost:8000/api/v1/admin/scene/charging-queue",
                headers=headers,
                timeout=10
            )
            
            print(f"📊 排队API状态码: {queue_response.status_code}")
            if queue_response.status_code == 200:
                queue_data = queue_response.json()
                print(f"✅ 排队API成功，返回 {len(queue_data)} 条记录")
                for item in queue_data:
                    print(f"  - {item.get('queue_number')}: {item.get('status')}")
            else:
                print(f"❌ 排队API失败")
                print(f"响应内容: {queue_response.text}")
        else:
            print(f"❌ 登录失败，状态码: {login_response.status_code}")
            print(f"响应内容: {login_response.text}")
            
    except Exception as e:
        print(f"❌ HTTP请求失败: {e}")

if __name__ == "__main__":
    test_http_api() 