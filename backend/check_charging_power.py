from app.core.database import get_db
from app.models import ChargingPile
from app.services.config_service import config_service

def check_charging_power():
    db = next(get_db())
    
    print("🔍 检查充电桩功率配置...")
    
    # 获取配置中的功率
    fast_power_config = config_service.get_charging_power("fast", db)
    trickle_power_config = config_service.get_charging_power("trickle", db)
    
    print(f"\n📊 配置文件中的功率:")
    print(f"  快充功率: {fast_power_config}kW")
    print(f"  慢充功率: {trickle_power_config}kW")
    
    # 获取数据库中的充电桩
    piles = db.query(ChargingPile).all()
    
    print(f"\n📊 数据库中的充电桩功率:")
    power_mismatch = False
    for pile in piles:
        mode = pile.charging_mode.value if hasattr(pile.charging_mode, 'value') else pile.charging_mode
        expected_power = fast_power_config if mode == 'fast' else trickle_power_config
        
        if pile.power != expected_power:
            print(f"  ❌ {pile.pile_number}: {pile.power}kW ({mode}) - 应为 {expected_power}kW")
            power_mismatch = True
        else:
            print(f"  ✅ {pile.pile_number}: {pile.power}kW ({mode})")
    
    if power_mismatch:
        print(f"\n🔧 发现功率不匹配，需要同步充电桩功率!")
        print("解决方案：调用管理员API /admin/piles/sync-config 同步配置")
    else:
        print(f"\n✅ 所有充电桩功率配置正确!")
    
    db.close()

if __name__ == "__main__":
    check_charging_power() 