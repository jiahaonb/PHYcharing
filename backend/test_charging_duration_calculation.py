#!/usr/bin/env python3
"""
测试充电时长计算的一致性
验证前端和后端使用相同的功率配置
"""

import sys
sys.path.append('.')

from app.core.database import get_db
from app.services.config_service import config_service

def test_charging_duration_calculation():
    """测试充电时长计算"""
    print("🔍 测试充电时长计算一致性...")
    
    # 获取数据库连接
    db = next(get_db())
    
    try:
        # 获取配置
        fast_power = config_service.get_charging_power("fast", db)
        trickle_power = config_service.get_charging_power("trickle", db)
        
        print(f"📊 配置文件中的功率:")
        print(f"  快充功率: {fast_power}kW")
        print(f"  慢充功率: {trickle_power}kW")
        
        # 测试用例
        test_cases = [
            {"amount": 12.0, "mode": "fast", "name": "12度快充"},
            {"amount": 30.0, "mode": "fast", "name": "30度快充"},
            {"amount": 12.0, "mode": "trickle", "name": "12度慢充"},
        ]
        
        print(f"\n📋 充电时长计算测试:")
        for case in test_cases:
            amount = case["amount"]
            mode = case["mode"]
            name = case["name"]
            
            # 选择对应功率
            power = fast_power if mode == "fast" else trickle_power
            
            # 计算时长
            hours = amount / power
            minutes = hours * 60
            
            print(f"  {name}:")
            print(f"    电量: {amount}度")
            print(f"    功率: {power}kW")
            print(f"    时长: {hours:.2f}小时 = {minutes:.1f}分钟")
            
            # 检查是否为问题中的情况
            if amount == 12.0 and mode == "fast":
                if abs(minutes - 24.0) < 0.1:
                    print(f"    ✅ 正确！12度÷30kW=24分钟")
                else:
                    print(f"    ❌ 错误！应该是24分钟，不是{minutes:.1f}分钟")
            
            if amount == 30.0 and mode == "fast":
                if abs(minutes - 60.0) < 0.1:
                    print(f"    ✅ 正确！30度÷30kW=60分钟")
                elif abs(minutes - 36.0) < 0.1:
                    print(f"    ❌ 错误！用了50kW计算：30度÷50kW=36分钟")
                else:
                    print(f"    ❓ 未知计算：{minutes:.1f}分钟")
            
            print()
        
        print("🎯 重点验证用户反馈的情况:")
        print("  如果前端显示1小时，后端生成36分钟，原因是:")
        print("  - 前端可能用了12度÷12kW=1小时 (错误功率)")
        print("  - 后端可能用了30度÷50kW=36分钟 (错误功率)")
        print("  - 正确应该都使用30kW功率")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_charging_duration_calculation() 