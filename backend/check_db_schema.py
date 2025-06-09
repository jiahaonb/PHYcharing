#!/usr/bin/env python3
"""查看数据库结构脚本"""

import sqlite3

def main():
    try:
        # 连接数据库
        conn = sqlite3.connect('backend/app.db')
        cursor = conn.cursor()
        
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print('数据库中的表:')
        for table in tables:
            print(f'  - {table[0]}')
        
        # 查看charging_records表结构
        print('\n=== charging_records 表结构 ===')
        try:
            cursor.execute("PRAGMA table_info(charging_records)")
            columns = cursor.fetchall()
            if columns:
                for col in columns:
                    print(f'  {col[1]} ({col[2]})')
            else:
                print('  表不存在或没有列')
        except Exception as e:
            print(f'  查看charging_records表失败: {e}')
        
        # 查看charging_queues表结构
        print('\n=== charging_queues 表结构 ===')
        try:
            cursor.execute("PRAGMA table_info(charging_queues)")
            columns = cursor.fetchall()
            if columns:
                for col in columns:
                    print(f'  {col[1]} ({col[2]})')
            else:
                print('  表不存在或没有列')
        except Exception as e:
            print(f'  查看charging_queues表失败: {e}')
        
        # 查看活跃的队列
        print('\n=== 活跃队列数据 ===')
        try:
            cursor.execute("SELECT id, status, vehicle_id, charging_pile_id FROM charging_queues WHERE status IN ('waiting', 'queuing', 'charging')")
            queues = cursor.fetchall()
            for queue in queues:
                print(f'  队列ID: {queue[0]}, 状态: {queue[1]}, 车辆ID: {queue[2]}, 充电桩ID: {queue[3]}')
            print(f'  总计: {len(queues)} 个活跃队列')
        except Exception as e:
            print(f'  查询失败: {e}')
        
        # 查看所有充电记录
        print('\n=== 充电记录数据 ===')
        try:
            cursor.execute("SELECT COUNT(*) FROM charging_records")
            count = cursor.fetchone()[0]
            print(f'  总计充电记录: {count}')
            
            if count > 0:
                # 查看前几条记录
                cursor.execute("SELECT id, record_number, license_plate, status FROM charging_records LIMIT 5")
                records = cursor.fetchall()
                for record in records:
                    print(f'  记录ID: {record[0]}, 订单号: {record[1]}, 车牌: {record[2]}, 状态: {record[3]}')
        except Exception as e:
            print(f'  查询充电记录失败: {e}')
        
        conn.close()
        
    except Exception as e:
        print(f'数据库连接失败: {e}')

if __name__ == "__main__":
    main() 