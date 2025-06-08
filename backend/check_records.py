#!/usr/bin/env python3
import sys
sys.path.append('.')

from app.core.database import get_db
from app.models.charging import ChargingRecord

# 创建数据库会话
db = next(get_db())

# 查询最新的充电记录
records = db.query(ChargingRecord).order_by(ChargingRecord.created_at.desc()).limit(10).all()

print(f'数据库中共有 {db.query(ChargingRecord).count()} 条充电记录')
print('\n最新的10条充电记录:')
print('-' * 120)
print(f'{"ID":<5} {"订单编号":<25} {"状态":<12} {"车牌号":<15} {"剩余时间":<10} {"创建时间":<20}')
print('-' * 120)

for record in records:
    remaining_str = f'{record.remaining_time}分钟' if record.remaining_time is not None else '未设置'
    print(f'{record.id:<5} {record.record_number:<25} {record.status:<12} {record.license_plate:<15} {remaining_str:<10} {record.created_at.strftime("%Y-%m-%d %H:%M:%S"):<20}')

# 查询目前正在充电的记录
charging_records = db.query(ChargingRecord).filter(ChargingRecord.status == 'charging').all()
print(f'\n目前正在充电的记录数量: {len(charging_records)}')
for record in charging_records:
    print(f'  - ID:{record.id} 订单号:{record.record_number} 车牌:{record.license_plate} 充电桩ID:{record.charging_pile_id} 剩余时间:{record.remaining_time}分钟')

# 查询分配给充电桩的记录
assigned_records = db.query(ChargingRecord).filter(ChargingRecord.status == 'assigned').all()
print(f'\n等待充电的记录数量: {len(assigned_records)}')
for record in assigned_records:
    print(f'  - ID:{record.id} 订单号:{record.record_number} 车牌:{record.license_plate} 充电桩ID:{record.charging_pile_id}')

# 查询所有有充电桩分配的记录
pile_assigned_records = db.query(ChargingRecord).filter(ChargingRecord.charging_pile_id.isnot(None)).all()
print(f'\n已分配充电桩的记录数量: {len(pile_assigned_records)}')
for record in pile_assigned_records:
    print(f'  - ID:{record.id} 订单号:{record.record_number} 车牌:{record.license_plate} 充电桩ID:{record.charging_pile_id} 状态:{record.status}')

db.close() 