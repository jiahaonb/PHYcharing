#!/usr/bin/env python3
import requests
import json
import time

def test_piles_api():
    try:
        # 等待后端启动
        print("等待后端启动...")
        time.sleep(3)
        
        # 测试充电桩API
        response = requests.get('http://localhost:8088/api/v1/admin/piles')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            piles = response.json()
            print(f"充电桩数量: {len(piles)}")
            
            for pile in piles:
                print(f"充电桩{pile['pile_number']}: 模式={pile['charging_mode']}, 功率={pile['power']}")
        else:
            print(f"API错误: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("无法连接到后端服务器，请确认后端已启动")
    except Exception as e:
        print(f"错误: {e}")

# 测试停止充电API
def test_stop_charging():
    # 首先登录获取token
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    
    try:
        # 登录
        login_response = requests.post("http://localhost:8000/api/v1/auth/login", json=login_data)
        print(f"登录响应状态: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            # 测试停止充电API (使用队列ID 1)
            stop_response = requests.post("http://localhost:8000/api/v1/admin/queue/1/stop-charging", headers=headers)
            print(f"停止充电响应状态: {stop_response.status_code}")
            print(f"停止充电响应内容: {stop_response.text}")
            
            if stop_response.status_code == 500:
                print("发生500错误，查看详细错误信息")
        else:
            print(f"登录失败: {login_response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_piles_api()
    test_stop_charging() 