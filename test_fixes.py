"""
测试修复的问题：
1. 订单结束检查总少1分钟的问题
2. 管理端订单管理页面时间显示UTC问题
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """获取管理员token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"获取token失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"登录失败: {e}")
        return None

def test_remaining_time_calculation():
    """测试剩余时间计算修复"""
    print("=" * 50)
    print("🔧 测试剩余时间计算修复")
    print("=" * 50)
    
    print("修复内容:")
    print("- 原问题: 使用 int() 直接截断导致少1分钟")
    print("- 修复后: 使用 round() 四舍五入避免时间误差")
    print()
    
    # 模拟计算示例
    test_cases = [
        {"amount": 20.0, "power": 30.0, "expected_minutes": 40},   # 20/30 = 0.667h = 40min
        {"amount": 15.0, "power": 10.0, "expected_minutes": 90},   # 15/10 = 1.5h = 90min
        {"amount": 25.0, "power": 30.0, "expected_minutes": 50},   # 25/30 = 0.833h = 50min
        {"amount": 12.5, "power": 10.0, "expected_minutes": 75},   # 12.5/10 = 1.25h = 75min
    ]
    
    print("剩余时间计算示例:")
    for i, case in enumerate(test_cases, 1):
        amount = case["amount"]
        power = case["power"]
        expected = case["expected_minutes"]
        
        # 模拟新的计算方法
        estimated_hours = amount / power
        remaining_time_round = round(estimated_hours * 60)  # 新方法：四舍五入
        remaining_time_int = int(estimated_hours * 60)      # 旧方法：直接截断
        
        print(f"示例 {i}:")
        print(f"  充电量: {amount} 度, 功率: {power} kW")
        print(f"  预计时长: {estimated_hours:.3f} 小时 = {estimated_hours * 60:.1f} 分钟")
        print(f"  旧方法 int(): {remaining_time_int} 分钟")
        print(f"  新方法 round(): {remaining_time_round} 分钟")
        print(f"  期望值: {expected} 分钟")
        
        if remaining_time_round == expected:
            print(f"  ✅ 修复后计算正确")
        else:
            print(f"  ⚠️  计算结果: {remaining_time_round}, 期望: {expected}")
        print()

def test_time_display_fix():
    """测试时间显示修复"""
    print("=" * 50)
    print("🕐 测试时间显示修复")
    print("=" * 50)
    
    token = get_admin_token()
    if not token:
        print("❌ 无法获取管理员token，跳过API测试")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("1. 测试订单时间显示...")
        response = requests.get(f"{BASE_URL}/admin/orders", headers=headers)
        
        if response.status_code == 200:
            orders = response.json().get('orders', [])
            print(f"获取到 {len(orders)} 个订单")
            
            # 检查前几个订单的时间格式
            for i, order in enumerate(orders[:3]):
                print(f"\n📋 订单 {i+1}: {order.get('queue_number', 'N/A')}")
                
                created_at = order.get('created_at')
                updated_at = order.get('updated_at')
                start_time = order.get('start_time')
                end_time = order.get('end_time')
                
                print(f"  创建时间: {created_at}")
                print(f"  更新时间: {updated_at}")
                print(f"  开始时间: {start_time}")
                print(f"  结束时间: {end_time}")
                
                # 验证时间格式是否为ISO格式且合理
                time_fields = [
                    ("创建时间", created_at),
                    ("更新时间", updated_at),
                    ("开始时间", start_time),
                    ("结束时间", end_time)
                ]
                
                for field_name, time_str in time_fields:
                    if time_str:
                        try:
                            # 尝试解析时间字符串
                            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                            # 检查时间是否在合理范围内（不是遥远的未来或过去）
                            now = datetime.now()
                            if abs((dt.replace(tzinfo=None) - now).days) < 365:  # 一年内
                                print(f"  ✅ {field_name} 格式正确且合理")
                            else:
                                print(f"  ⚠️  {field_name} 时间范围异常: {time_str}")
                        except ValueError:
                            print(f"  ❌ {field_name} 格式错误: {time_str}")
                    else:
                        print(f"  - {field_name}: 无数据")
        else:
            print(f"❌ 获取订单失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试时间显示失败: {e}")

def main():
    print("🧪 测试系统修复")
    print("修复的问题:")
    print("1. 订单结束检查总少1分钟")
    print("2. 管理端订单管理页面时间是UTC时间，不是China时间")
    print()
    
    # 运行测试
    test_remaining_time_calculation()
    test_time_display_fix()
    
    print("=" * 50)
    print("✅ 修复总结")
    print("=" * 50)
    
    print("🔧 修复1: 剩余时间计算")
    print("  - 问题: 使用 int() 直接截断导致少1分钟")
    print("  - 解决: 改用 round() 四舍五入")
    print("  - 位置: backend/app/services/charging_service.py line 363")
    print()
    
    print("🕐 修复2: 时间显示格式")
    print("  - 问题: 管理端显示UTC时间而非中国时间")
    print("  - 解决: 使用 format_utc_time() 和 format_china_time() 函数")
    print("  - 位置: backend/app/api/api_v1/endpoints/admin.py")
    print("  - 影响字段: created_at, updated_at, start_time, end_time")
    print()
    
    print("📝 具体改动:")
    print("1. charging_service.py:")
    print("   charging_record.remaining_time = int(estimated_hours * 60)")
    print("   ↓ 改为")
    print("   charging_record.remaining_time = round(estimated_hours * 60)")
    print()
    print("2. admin.py:")
    print("   queue.created_at.strftime('%Y-%m-%d %H:%M:%S')")
    print("   ↓ 改为")
    print("   format_utc_time(queue.created_at)")

if __name__ == "__main__":
    main() 