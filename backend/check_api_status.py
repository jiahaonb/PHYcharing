#!/usr/bin/env python3
"""通过API查看订单状态脚本"""

import requests
import json
from datetime import datetime

def main():
    base_url = "http://localhost:8001/api/v1"
    
    # 检查充电桩状态
    print('=== 充电桩和订单状态 ===')
    try:
        response = requests.get(f"{base_url}/admin/scene/charging-piles")
        if response.status_code == 200:
            data = response.json()
            print(f'获取到 {len(data.get("fast_piles", []))} 个快充桩, {len(data.get("trickle_piles", []))} 个慢充桩')
            
            # 检查快充桩
            for pile in data.get("fast_piles", []):
                if pile.get("current_order"):
                    order = pile["current_order"]
                    print(f'快充桩{pile["id"]} - 正在充电: {order.get("license_plate", "N/A")} (状态: {order.get("status", "N/A")})')
                
                if pile.get("queue_orders"):
                    for i, order in enumerate(pile["queue_orders"]):
                        print(f'快充桩{pile["id"]} - 排队{i+1}: {order.get("license_plate", "N/A")} (状态: {order.get("status", "N/A")})')
            
            # 检查慢充桩
            for pile in data.get("trickle_piles", []):
                if pile.get("current_order"):
                    order = pile["current_order"]
                    print(f'慢充桩{pile["id"]} - 正在充电: {order.get("license_plate", "N/A")} (状态: {order.get("status", "N/A")})')
                
                if pile.get("queue_orders"):
                    for i, order in enumerate(pile["queue_orders"]):
                        print(f'慢充桩{pile["id"]} - 排队{i+1}: {order.get("license_plate", "N/A")} (状态: {order.get("status", "N/A")})')
        else:
            print(f'API请求失败: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'查询充电桩状态失败: {e}')
    
    # 检查队列管理
    print('\n=== 队列管理状态 ===')
    try:
        response = requests.get(f"{base_url}/admin/queue/")
        if response.status_code == 200:
            queues = response.json()
            print(f'总队列数: {len(queues)}')
            
            # 显示非completed状态的队列
            active_queues = [q for q in queues if q.get('status') not in ['completed', 'cancelled']]
            for queue in active_queues:
                print(f'队列ID: {queue.get("id")}, 状态: {queue.get("status")}, 车辆: {queue.get("license_plate", "N/A")}')
            
            print(f'活跃队列数: {len(active_queues)}')
        else:
            print(f'队列API请求失败: {response.status_code} - {response.text}')
    except Exception as e:
        print(f'查询队列状态失败: {e}')

if __name__ == "__main__":
    main() 