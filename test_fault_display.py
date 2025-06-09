#!/usr/bin/env python3
"""
故障队列显示功能测试
测试故障区车辆数据的API端点
"""

import requests
import json
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8088/api/v1"

def test_fault_vehicles_api():
    """测试故障区车辆API"""
    print("🔍 测试故障区车辆API...")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/scene/fault-vehicles")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API响应成功")
            print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 验证数据结构
            if isinstance(data, dict):
                fast_fault = data.get('fast_fault', [])
                trickle_fault = data.get('trickle_fault', [])
                total_fault = data.get('total_fault', 0)
                
                print(f"📊 故障队列统计:")
                print(f"  - 快充故障: {len(fast_fault)} 辆")
                print(f"  - 慢充故障: {len(trickle_fault)} 辆")
                print(f"  - 总计故障: {total_fault} 辆")
                
                # 显示故障车辆详情
                if fast_fault:
                    print("⚡ 快充故障车辆:")
                    for i, vehicle in enumerate(fast_fault, 1):
                        print(f"  {i}. {vehicle.get('queue_number', 'N/A')} - {vehicle.get('license_plate', 'N/A')}")
                
                if trickle_fault:
                    print("🔋 慢充故障车辆:")
                    for i, vehicle in enumerate(trickle_fault, 1):
                        print(f"  {i}. {vehicle.get('queue_number', 'N/A')} - {vehicle.get('license_plate', 'N/A')}")
                
            else:
                print("⚠️ 数据格式不正确")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保后端服务正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_waiting_vehicles_api():
    """测试等候区车辆API（对比）"""
    print("\n🔍 测试等候区车辆API（对比）...")
    
    try:
        response = requests.get(f"{BASE_URL}/admin/scene/waiting-vehicles")
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 等候区API响应成功")
            
            if isinstance(data, dict):
                fast_waiting = data.get('fast_waiting', [])
                trickle_waiting = data.get('trickle_waiting', [])
                total_waiting = data.get('total_waiting', 0)
                
                print(f"📊 等候队列统计:")
                print(f"  - 快充等候: {len(fast_waiting)} 辆")
                print(f"  - 慢充等候: {len(trickle_waiting)} 辆")
                print(f"  - 总计等候: {total_waiting} 辆")
                
        else:
            print(f"❌ 等候区API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 等候区API测试失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("📱 故障队列显示功能测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 测试故障区API
    test_fault_vehicles_api()
    
    # 测试等候区API作为对比
    test_waiting_vehicles_api()
    
    print("\n" + "=" * 50)
    print("✅ 测试完成") 