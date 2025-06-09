#!/usr/bin/env python3
"""检查充电记录状态脚本"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import get_db
from app.models import ChargingRecord
from datetime import datetime

def main():
    db = next(get_db())
    
    try:
        print('=== 检查充电记录状态 ===')
        
        # 获取所有充电记录
        all_records = db.query(ChargingRecord).all()
        print(f'总充电记录数: {len(all_records)}')
        
        if all_records:
            # 按状态分组统计
            status_count = {}
            for record in all_records:
                status = getattr(record, 'status', 'unknown')
                status_count[status] = status_count.get(status, 0) + 1
            
            print('\n状态统计:')
            for status, count in status_count.items():
                print(f'  {status}: {count}')
            
            # 显示非completed状态的记录
            non_completed = [r for r in all_records if getattr(r, 'status', '') != 'completed']
            if non_completed:
                print(f'\n=== 非completed状态的记录 ({len(non_completed)}个) ===')
                for record in non_completed:
                    print(f'  记录ID: {record.id}, 订单号: {getattr(record, "record_number", "N/A")}, 状态: {getattr(record, "status", "N/A")}, 车牌: {getattr(record, "license_plate", "N/A")}')
            else:
                print('\n✅ 所有充电记录都已完成')
        
    except Exception as e:
        print(f'❌ 检查过程中出错: {e}')
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main() 