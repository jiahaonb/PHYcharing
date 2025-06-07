#!/usr/bin/env python3
import requests
import time
import json

def test_api():
    print("等待后端启动...")
    time.sleep(5)
    
    try:
        # 测试基本连接
        response = requests.get('http://localhost:8000/')
        print(f"后端连接成功: {response.status_code}")
        
        # 测试充电桩API
        response = requests.get('http://localhost:8000/api/v1/admin/piles')
        print(f"充电桩API状态: {response.status_code}")
        
        if response.status_code == 200:
            piles = response.json()
            print(f"✅ 充电桩数量: {len(piles)}")
            
            for pile in piles:
                print(f"  充电桩{pile['pile_number']}: 模式={pile['charging_mode']}, 功率={pile['power']}kW")
        else:
            print(f"❌ API错误: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务器")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_api() 