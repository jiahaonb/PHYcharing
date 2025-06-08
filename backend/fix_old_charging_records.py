#!/usr/bin/env python3
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.charging import ChargingRecord
from datetime import datetime

# 创建数据库会话
db = next(get_db())

print("修复旧的充电记录...")

# 查找所有使用旧订单编号格式的记录（CHG开头）
old_records = db.query(ChargingRecord).filter(
    ChargingRecord.record_number.like('CHG%')
).all()

print(f"找到 {len(old_records)} 条旧格式的充电记录:")

for record in old_records:
    print(f"  - ID:{record.id} 订单号:{record.record_number} 车牌:{record.license_plate} 状态:{record.status}")
    
    # 如果状态还是charging，将其设置为completed
    if record.status == 'charging':
        print(f"    将状态从 'charging' 更新为 'completed'")
        record.status = 'completed'
        record.end_time = datetime.now()
        record.remaining_time = 0
        
    # 如果状态是created或assigned，将其设置为completed
    elif record.status in ['created', 'assigned']:
        print(f"    将状态从 '{record.status}' 更新为 'completed'")
        record.status = 'completed'
        record.end_time = datetime.now()
        record.remaining_time = 0

# 提交更改
try:
    db.commit()
    print("\n✅ 成功更新旧的充电记录状态")
    
    # 再次检查
    still_charging = db.query(ChargingRecord).filter(ChargingRecord.status == 'charging').all()
    print(f"\n现在仍在充电的记录数量: {len(still_charging)}")
    for record in still_charging:
        print(f"  - ID:{record.id} 订单号:{record.record_number} 车牌:{record.license_plate}")
        
except Exception as e:
    print(f"\n❌ 更新失败: {e}")
    db.rollback()
    
finally:
    db.close() 