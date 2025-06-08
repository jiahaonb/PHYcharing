#!/usr/bin/env python3
"""
测试API端点是否可访问
"""

import requests
import json

def test_api_endpoint():
    base_url = "http://localhost:8088/api/v1"
    
    # 测试健康检查
    try:
        print("🔍 测试健康检查端点...")
        resp = requests.get(f"{base_url}/health", timeout=5)
        print(f"健康检查: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ 后端服务正常运行")
        else:
            print("❌ 后端服务异常")
            return
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return
    
    # 测试充电配置端点（不需要认证的话）
    try:
        print("\n🔍 测试充电配置端点...")
        resp = requests.get(f"{base_url}/users/charging/config", timeout=5)
        print(f"充电配置: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            print("✅ 充电配置API正常:")
            print(f"  快充功率: {data.get('fast_charging_power')}kW")
            print(f"  慢充功率: {data.get('trickle_charging_power')}kW")
        elif resp.status_code == 401:
            print("⚠️ 需要认证才能访问")
        else:
            print(f"❌ API异常: {resp.text[:200]}")
            
    except Exception as e:
        print(f"❌ 测试充电配置API失败: {e}")

if __name__ == "__main__":
    test_api_endpoint() 