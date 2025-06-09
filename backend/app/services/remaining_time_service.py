"""
剩余时间管理服务
负责每分钟更新正在充电的订单的剩余时间
并在实际充电量达到计划充电量时自动停止充电
"""

import threading
import time
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.charging import ChargingRecord, ChargingQueue, ChargingPile
from app.models import QueueStatus
from app.services.charging_service import ChargingScheduleService

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
        """更新所有正在充电订单的剩余时间、实际充电量和实际费用，并检查自动停止条件"""
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
            auto_stopped_orders = []
            
            for record in charging_records:
                old_remaining = record.remaining_time
                
                # 更新实际充电量和费用
                self._update_actual_charging_data(record, db)
                
                # 检查是否应该自动停止充电
                should_auto_stop = self._check_auto_stop_condition(record, db)
                
                if should_auto_stop:
                    # 自动停止充电
                    try:
                        charging_service = ChargingScheduleService(db)
                        # 找到对应的队列记录
                        queue_record = db.query(ChargingQueue).filter(
                            ChargingQueue.queue_number == record.queue_number,
                            ChargingQueue.status == QueueStatus.CHARGING
                        ).first()
                        
                        if queue_record:
                            charging_service.complete_charging(queue_record.id)
                            auto_stopped_orders.append(record.record_number)
                            print(f"🔄 自动停止充电: 订单 {record.record_number} (实际充电量达到计划充电量)")
                    except Exception as e:
                        print(f"❌ 自动停止充电失败 {record.record_number}: {e}")
                        # 如果自动停止失败，继续正常的时间递减
                        record.remaining_time = max(0, record.remaining_time - 1)
                        if record.remaining_time == 0:
                            completed_orders.append(record.record_number)
                else:
                    # 正常减少1分钟
                    record.remaining_time = max(0, record.remaining_time - 1)
                    
                    if record.remaining_time == 0:
                        # 时间到期，也需要自动停止充电
                        try:
                            charging_service = ChargingScheduleService(db)
                            queue_record = db.query(ChargingQueue).filter(
                                ChargingQueue.queue_number == record.queue_number,
                                ChargingQueue.status == QueueStatus.CHARGING
                            ).first()
                            
                            if queue_record:
                                charging_service.complete_charging(queue_record.id)
                                completed_orders.append(record.record_number)
                                print(f"⏰ 时间到期自动停止: 订单 {record.record_number}")
                        except Exception as e:
                            print(f"❌ 时间到期自动停止失败 {record.record_number}: {e}")
                            completed_orders.append(record.record_number)
                    elif record.remaining_time != old_remaining:
                        updated_count += 1
            
            if updated_count > 0 or completed_orders or auto_stopped_orders:
                db.commit()
                if updated_count > 0:
                    print(f"⏰ 更新了 {updated_count} 个订单的剩余时间和实际充电数据")
                if completed_orders:
                    print(f"⏰ {len(completed_orders)} 个订单时间到期自动停止: {', '.join(completed_orders)}")
                if auto_stopped_orders:
                    print(f"🔄 {len(auto_stopped_orders)} 个订单充电完成自动停止: {', '.join(auto_stopped_orders)}")
        
        except Exception as e:
            db.rollback()
            print(f"❌ 更新剩余时间时出错: {e}")
        finally:
            db.close()
    
    def _update_actual_charging_data(self, record: ChargingRecord, db: Session):
        """更新充电记录的实际充电量和实际费用"""
        try:
            # 获取充电桩信息
            pile = db.query(ChargingPile).filter(
                ChargingPile.id == record.charging_pile_id
            ).first()
            
            if not pile or not record.start_time:
                return
            
            # 计算当前实际充电时长（小时）
            current_time = datetime.now()
            if record.start_time.tzinfo is None:
                # 处理时区问题
                from app.utils.timezone import CHINA_TZ
                start_time = record.start_time.replace(tzinfo=CHINA_TZ)
            else:
                start_time = record.start_time
            
            current_time_aware = current_time.replace(tzinfo=CHINA_TZ) if current_time.tzinfo is None else current_time
            actual_duration = (current_time_aware - start_time).total_seconds() / 3600
            
            # 计算当前实际充电量（不超过计划充电量）
            current_actual_amount = min(pile.power * actual_duration, record.charging_amount)
            
            # 更新实际充电量
            record.actual_charging_amount = round(current_actual_amount, 2)
            
            # 计算实际费用
            self._calculate_actual_fees(record, current_actual_amount, start_time)
            
        except Exception as e:
            print(f"❌ 更新实际充电数据失败 {record.record_number}: {e}")
    
    def _calculate_actual_fees(self, record: ChargingRecord, actual_amount: float, start_time: datetime):
        """计算实际费用：实际费用 = 实际充电量 * (电量单价 + 服务费单价)"""
        try:
            from app.core.config import settings
            
            # 判断时段
            hour = start_time.hour
            
            # 判断时段
            if any(start <= hour < end for start, end in settings.PEAK_TIME_RANGES):
                electricity_unit_price = settings.PEAK_TIME_PRICE
                time_period = "峰时"
            elif any(start <= hour < end for start, end in settings.NORMAL_TIME_RANGES):
                electricity_unit_price = settings.NORMAL_TIME_PRICE
                time_period = "平时"
            else:
                electricity_unit_price = settings.VALLEY_TIME_PRICE
                time_period = "谷时"
            
            service_unit_price = settings.SERVICE_FEE_PRICE
            
            # 按照新的计费公式：实际费用 = 实际充电量 * (电量单价 + 服务费单价)
            total_unit_price = electricity_unit_price + service_unit_price
            
            # 计算实际费用
            actual_electricity_fee = actual_amount * electricity_unit_price
            actual_service_fee = actual_amount * service_unit_price
            actual_total_fee = actual_amount * total_unit_price
            
            # 更新记录
            record.actual_electricity_fee = round(actual_electricity_fee, 2)
            record.actual_service_fee = round(actual_service_fee, 2)
            record.actual_total_fee = round(actual_total_fee, 2)
            record.unit_price = electricity_unit_price
            record.time_period = time_period
            
            # 更新充电时长
            if record.start_time:
                current_time = datetime.now()
                if record.start_time.tzinfo is None:
                    from app.utils.timezone import CHINA_TZ
                    start_time_aware = record.start_time.replace(tzinfo=CHINA_TZ)
                else:
                    start_time_aware = record.start_time
                
                current_time_aware = current_time.replace(tzinfo=CHINA_TZ) if current_time.tzinfo is None else current_time
                duration_hours = (current_time_aware - start_time_aware).total_seconds() / 3600
                record.charging_duration = round(duration_hours, 2)
            
        except Exception as e:
            print(f"❌ 计算实际费用失败 {record.record_number}: {e}")
    
    def _check_auto_stop_condition(self, record: ChargingRecord, db: Session) -> bool:
        """检查是否应该自动停止充电
        
        条件：实际充电量 >= 计划充电量
        """
        try:
            # 获取充电桩信息
            pile = db.query(ChargingPile).filter(
                ChargingPile.id == record.charging_pile_id
            ).first()
            
            if not pile or not record.start_time:
                return False
            
            # 计算当前实际充电时长（小时）
            current_time = datetime.now()
            if record.start_time.tzinfo is None:
                # 处理时区问题
                from app.utils.timezone import CHINA_TZ
                start_time = record.start_time.replace(tzinfo=CHINA_TZ)
            else:
                start_time = record.start_time
            
            current_time_aware = current_time.replace(tzinfo=CHINA_TZ) if current_time.tzinfo is None else current_time
            actual_duration = (current_time_aware - start_time).total_seconds() / 3600
            
            # 计算当前实际充电量
            current_actual_amount = pile.power * actual_duration
            
            # 检查是否达到计划充电量
            if current_actual_amount >= record.charging_amount:
                print(f"📊 订单 {record.record_number} 充电完成检查: 实际{current_actual_amount:.2f}度 >= 计划{record.charging_amount:.2f}度")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 检查自动停止条件失败 {record.record_number}: {e}")
            return False
    
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