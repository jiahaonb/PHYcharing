#!/usr/bin/env python3
"""测试队列时间显示修复"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_user_token():
    """获取用户token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": "test1",
            "password": "password123"
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_queue_status_times():
    """测试队列状态时间显示"""
    print("=" * 60)
    print("🕐 测试队列状态时间显示修复")
    print("=" * 60)
    
    token = get_user_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("📋 获取用户队列状态...")
        response = requests.get(f"{BASE_URL}/users/queue/status", headers=headers)
        
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ 成功获取 {len(orders)} 个队列订单")
            
            if len(orders) == 0:
                print("📝 当前没有排队订单")
                return
            
            for i, order in enumerate(orders, 1):
                print(f"\n📋 订单 {i}: {order['queue_number']}")
                print(f"   车牌号: {order['vehicle_license']}")
                print(f"   状态: {order['status']}")
                print(f"   充电模式: {order['charging_mode']}")
                print(f"   位置: {order['pile_name']}")
                
                if order.get('position'):
                    print(f"   排队位置: 第{order['position']}位")
                
                # 检查时间信息
                estimated_time = order.get('estimated_time', 0)
                remaining_time = order.get('remaining_time')
                
                print(f"\n   ⏰ 时间信息:")
                if estimated_time > 0:
                    time_label = "剩余时间" if order['status'] == 'charging' else "预计等待"
                    print(f"      {time_label}: {estimated_time} 分钟")
                else:
                    print("      预计时间: 0 分钟 ⚠️")
                
                if remaining_time is not None:
                    print(f"      实际剩余: {remaining_time} 分钟")
                else:
                    print("      实际剩余: 未设置")
                
                # 检查实际充电数据
                if order['status'] == 'charging':
                    print(f"\n   ⚡ 充电数据:")
                    if order.get('actual_charging_amount'):
                        print(f"      实际充电量: {order['actual_charging_amount']:.2f} 度")
                    if order.get('actual_total_fee'):
                        print(f"      实际费用: ¥{order['actual_total_fee']:.2f}")
                
                # 状态建议
                if order['status'] == 'waiting' and estimated_time == 0:
                    print("   🚨 建议: 等候区预计时间为0，可能有问题")
                elif order['status'] == 'queuing' and estimated_time == 0:
                    print("   🚨 建议: 排队区预计时间为0，可能有问题")
                elif order['status'] == 'charging' and remaining_time is None:
                    print("   🚨 建议: 充电中但没有剩余时间数据")
        else:
            print(f"❌ 获取失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_charging_records():
    """检查充电记录的剩余时间"""
    print("\n" + "=" * 60)
    print("📊 检查充电记录剩余时间")
    print("=" * 60)
    
    try:
        # 直接查询管理端API获取订单信息
        response = requests.get(f"{BASE_URL}/admin/orders")
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('orders', [])
            
            print(f"📋 总订单数: {len(orders)}")
            
            charging_orders = [o for o in orders if o['status'] == 'charging']
            print(f"⚡ 充电中订单: {len(charging_orders)}")
            
            for order in charging_orders:
                print(f"\n订单 {order['queue_number']}:")
                print(f"  车牌: {order['license_plate']}")
                print(f"  剩余时间: {order.get('remaining_time', 'N/A')} 分钟")
                print(f"  实际充电量: {order.get('actual_charging_amount', 'N/A')}")
                print(f"  实际费用: {order.get('actual_total_fee', 'N/A')}")
        else:
            print(f"❌ 获取管理端订单失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查充电记录异常: {e}")

def main():
    print("🧪 队列时间显示修复测试")
    print("修复内容:")
    print("1. 改进预计时间计算逻辑")
    print("2. 添加实际剩余时间显示")
    print("3. 区分不同状态的时间标签")
    print("4. 显示实际充电数据")
    print()
    
    test_queue_status_times()
    test_charging_records()
    
    print("\n" + "=" * 60)
    print("✅ 修复总结")
    print("=" * 60)
    print("🔧 修复项目:")
    print("1. 队列状态API返回剩余时间数据")
    print("2. 改进预计时间计算逻辑:")
    print("   - 等候区: 第一位5分钟，其他位置30分钟/人")
    print("   - 排队区: 基于前方车辆剩余时间")
    print("   - 充电中: 显示实际剩余时间")
    print("3. 前端显示优化:")
    print("   - 区分预计等待/剩余时间标签")
    print("   - 显示实际剩余时间")
    print("   - 添加颜色区分")

if __name__ == "__main__":
    main() 