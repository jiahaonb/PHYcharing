"""
剩余时间管理服务
负责每分钟更新正在充电的订单的剩余时间
"""

import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.charging import ChargingRecord

class RemainingTimeService:
    """剩余时间管理服务"""
    
    def __init__(self):
        self._stop_event = threading.Event()
        self._timer_thread = None
        self._is_running = False
    
    def start(self):
        """启动剩余时间更新服务"""
        if self._is_running:
            return
        
        self._is_running = True
        self._stop_event.clear()
        
        def timer_worker():
            while not self._stop_event.is_set():
                try:
                    self.update_remaining_times()
                except Exception as e:
                    print(f"❌ 更新剩余时间失败: {e}")
                
                # 每60秒更新一次
                self._stop_event.wait(60)
        
        self._timer_thread = threading.Thread(target=timer_worker, daemon=True)
        self._timer_thread.start()
        print("⏰ 剩余时间更新服务已启动")
    
    def stop(self):
        """停止剩余时间更新服务"""
        if not self._is_running:
            return
        
        self._is_running = False
        self._stop_event.set()
        
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join(timeout=5)
        
        print("⏰ 剩余时间更新服务已停止")
    
    def update_remaining_times(self):
        """更新所有正在充电订单的剩余时间"""
        db = next(get_db())
        try:
            # 获取所有正在充电的订单
            charging_records = db.query(ChargingRecord).filter(
                ChargingRecord.status == "charging",
                ChargingRecord.remaining_time.is_not(None),
                ChargingRecord.remaining_time > 0
            ).all()
            
            updated_count = 0
            completed_orders = []
            
            for record in charging_records:
                old_remaining = record.remaining_time
                # 减少1分钟
                record.remaining_time = max(0, record.remaining_time - 1)
                
                if record.remaining_time == 0:
                    completed_orders.append(record.record_number)
                    print(f"⏰ 订单 {record.record_number} 剩余时间归零")
                elif record.remaining_time != old_remaining:
                    updated_count += 1
            
            if updated_count > 0 or completed_orders:
                db.commit()
                if updated_count > 0:
                    print(f"⏰ 更新了 {updated_count} 个订单的剩余时间")
                if completed_orders:
                    print(f"⏰ {len(completed_orders)} 个订单时间到期: {', '.join(completed_orders)}")
        
        except Exception as e:
            db.rollback()
            print(f"❌ 更新剩余时间时出错: {e}")
        finally:
            db.close()
    
    def get_order_remaining_time(self, record_number: str) -> int:
        """获取指定订单的剩余时间"""
        db = next(get_db())
        try:
            record = db.query(ChargingRecord).filter(
                ChargingRecord.record_number == record_number
            ).first()
            
            if record:
                return record.remaining_time or 0
            return 0
        
        except Exception as e:
            print(f"❌ 获取订单剩余时间失败: {e}")
            return 0
        finally:
            db.close()
    
    def set_order_remaining_time(self, record_number: str, minutes: int):
        """手动设置订单剩余时间"""
        db = next(get_db())
        try:
            record = db.query(ChargingRecord).filter(
                ChargingRecord.record_number == record_number
            ).first()
            
            if record:
                record.remaining_time = max(0, minutes)
                db.commit()
                print(f"⏰ 手动设置订单 {record_number} 剩余时间为 {minutes} 分钟")
                return True
            return False
        
        except Exception as e:
            db.rollback()
            print(f"❌ 设置订单剩余时间失败: {e}")
            return False
        finally:
            db.close()

# 创建全局服务实例
remaining_time_service = RemainingTimeService() 