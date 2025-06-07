#!/usr/bin/env python3
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models.charging import ChargingPile
from app.models.config import SystemConfig

def main():
    try:
        db = next(get_db())
        
        # 检查充电桩数据
        piles = db.query(ChargingPile).all()
        print(f"数据库中充电桩总数: {len(piles)}")
        
        for pile in piles:
            mode = pile.charging_mode.value if hasattr(pile.charging_mode, 'value') else pile.charging_mode
            print(f"充电桩{pile.pile_number}: 模式={mode}, 功率={pile.power}, 状态={pile.status}")
        
        print("\n" + "="*50)
        
        # 检查配置数据
        configs = db.query(SystemConfig).filter(
            SystemConfig.config_key.like('charging_piles.%power')
        ).all()
        
        print("相关功率配置:")
        for config in configs:
            print(f"{config.config_key}: {config.config_value}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 