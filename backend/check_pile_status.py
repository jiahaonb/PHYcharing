#!/usr/bin/env python3
"""检查充电桩状态脚本"""

from app.core.database import get_db
from app.models import ChargingPile

def main():
    db = next(get_db())
    
    # 检查充电桩状态
    piles = db.query(ChargingPile).all()
    print(f'数据库中充电桩总数: {len(piles)}')
    
    for pile in piles:
        status_value = pile.status.value if hasattr(pile.status, 'value') else str(pile.status)
        print(f'充电桩{pile.pile_number}: 状态对象={pile.status}, 状态值={status_value}')
    
    db.close()

if __name__ == "__main__":
    main() 