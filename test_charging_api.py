#!/usr/bin/env python3
"""
测试充电记录API
"""

import requests
import json

def test_charging_records_api():
    """测试充电记录API"""
    base_url = "http://localhost:8000/api/v1"
    
    # 测试不需要认证的端点
    try:
        response = requests.get(f"{base_url}/charging/records", timeout=5)
        print(f"充电记录API状态码: {response.status_code}")
        
        if response.status_code == 401:
            print("需要认证 - 这是正常的")
        elif response.status_code == 500:
            print("服务器内部错误 - 需要修复")
            print(f"错误内容: {response.text}")
        else:
            print("API响应正常")
            
    except requests.exceptions.RequestException as e:
        print(f"无法连接到服务器: {e}")
        
def test_server_health():
    """测试服务器健康状态"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("服务器运行正常 - Swagger文档可访问")
        else:
            print(f"服务器状态异常: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"服务器可能未启动: {e}")

if __name__ == "__main__":
    print("测试服务器状态...")
    test_server_health()
    print("\n测试充电记录API...")
    test_charging_records_api() 