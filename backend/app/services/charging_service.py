from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import ChargingPile, ChargingQueue, ChargingRecord, ChargingMode, QueueStatus, ChargingPileStatus
from app.core.config import settings
import asyncio

class ChargingScheduleService:
    """充电调度服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_queue_number(self, charging_mode: ChargingMode) -> str:
        """生成排队号码"""
        prefix = "F" if charging_mode == ChargingMode.FAST else "T"
        
        # 获取当前该模式的最大号码
        last_queue = self.db.query(ChargingQueue).filter(
            ChargingQueue.queue_number.like(f"{prefix}%")
        ).order_by(ChargingQueue.queue_number.desc()).first()
        
        if last_queue:
            last_number = int(last_queue.queue_number[1:])  # 去掉前缀字母
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number}"
    
    def submit_charging_request(self, user_id: int, vehicle_id: int, 
                              charging_mode: ChargingMode, requested_amount: float) -> str:
        """提交充电请求"""
        # 检查车辆当前状态，只有"暂留"状态的车辆才能申请充电
        existing_queue = self.db.query(ChargingQueue).filter(
            ChargingQueue.vehicle_id == vehicle_id,
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).first()
        
        if existing_queue:
            # 根据状态返回不同的错误信息
            status_map = {
                QueueStatus.WAITING: "等候",
                QueueStatus.QUEUING: "等候",
                QueueStatus.CHARGING: "充电中"
            }
            current_status = status_map.get(existing_queue.status, "未知")
            raise Exception(f"该车辆当前状态为【{current_status}】，无法重复申请充电。请先完成当前充电或取消请求")
        
        # 检查等候区容量
        waiting_count = self.db.query(ChargingQueue).filter(
            ChargingQueue.status == QueueStatus.WAITING
        ).count()
        
        if waiting_count >= settings.WAITING_AREA_SIZE:
            raise Exception("等候区已满，请稍后再试")
        
        # 生成排队号码
        queue_number = self.generate_queue_number(charging_mode)
        
        # 创建排队记录
        queue_record = ChargingQueue(
            queue_number=queue_number,
            user_id=user_id,
            vehicle_id=vehicle_id,
            charging_mode=charging_mode,
            requested_amount=requested_amount,
            status=QueueStatus.WAITING
        )
        
        self.db.add(queue_record)
        self.db.commit()
        
        # 触发调度
        self.schedule_charging()
        
        return queue_number
    
    def schedule_charging(self):
        """三阶段FCFS调度算法：等候区→排队区→充电位"""
        print("🔄 开始三阶段充电调度...")
        
        # 阶段1: 等候区 → 排队区调度（快慢充分开）
        self._schedule_waiting_to_queuing(ChargingMode.FAST)
        self._schedule_waiting_to_queuing(ChargingMode.TRICKLE)
        
        # 阶段2: 排队区 → 充电位调度（快慢充分开）
        self._schedule_queuing_to_charging(ChargingMode.FAST)
        self._schedule_queuing_to_charging(ChargingMode.TRICKLE)
        
        print("✅ 三阶段调度完成")
    
    def _schedule_waiting_to_queuing(self, charging_mode: ChargingMode):
        """阶段1: 将等候区车辆调度到排队区"""
        print(f"📋 调度{charging_mode.value}充电等候区车辆...")
        
        # 获取该模式的所有充电桩
        all_piles = self.db.query(ChargingPile).filter(
            ChargingPile.charging_mode == charging_mode,
            ChargingPile.is_active == True
        ).all()
        
        # 获取该模式等候区的车辆（按FCFS排序）
        waiting_vehicles = self.db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == charging_mode,
            ChargingQueue.status == QueueStatus.WAITING
        ).order_by(ChargingQueue.queue_time).all()
        
        print(f"  等候区车辆数: {len(waiting_vehicles)}")
        
        # 为每个等候车辆寻找有空闲排队位的充电桩
        for vehicle in waiting_vehicles:
            assigned = False
            
            # 按充电桩ID顺序遍历（保证FCFS公平性）
            for pile in sorted(all_piles, key=lambda p: p.id):
                # 计算该充电桩当前排队人数（不包括正在充电的）
                current_queue_count = self.db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status == QueueStatus.QUEUING
                ).count()
                
                # 如果充电桩有空闲排队位（最多3个排队位）
                if current_queue_count < settings.CHARGING_QUEUE_LEN:
                    self._assign_to_queue(vehicle, pile)
                    assigned = True
                    print(f"  ✅ 车辆 {vehicle.queue_number} 分配到充电桩 {pile.pile_number} 排队区")
                    break
            
            # 如果没有可用的排队位，等候车辆继续等待
            if not assigned:
                print(f"  ⏳ 车辆 {vehicle.queue_number} 继续等候（无空闲排队位）")
                break
                
    def _schedule_queuing_to_charging(self, charging_mode: ChargingMode):
        """阶段2: 将排队区车辆调度到充电位"""
        print(f"⚡ 调度{charging_mode.value}充电排队区车辆...")
        
        # 获取该模式的所有充电桩
        all_piles = self.db.query(ChargingPile).filter(
            ChargingPile.charging_mode == charging_mode,
            ChargingPile.is_active == True
        ).all()
        
        for pile in all_piles:
            # 检查充电桩是否有正在充电的车辆
            charging_vehicle = self.db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == pile.id,
                ChargingQueue.status == QueueStatus.CHARGING
            ).first()
            
            if not charging_vehicle:
                # 充电位空闲，找到第一个排队的车辆开始充电
                next_vehicle = self.db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status == QueueStatus.QUEUING
                ).order_by(ChargingQueue.queue_time).first()
                
                if next_vehicle:
                    self.start_charging(next_vehicle.id)
                    print(f"  ⚡ 车辆 {next_vehicle.queue_number} 在充电桩 {pile.pile_number} 开始充电")
    
    def _assign_to_queue(self, queue_record: ChargingQueue, pile: ChargingPile):
        """将车辆分配到充电桩排队区"""
        queue_record.charging_pile_id = pile.id
        queue_record.status = QueueStatus.QUEUING
        
        # 计算预计完成时间
        waiting_time = self.calculate_waiting_time(pile)
        charging_time = queue_record.requested_amount / pile.power
        
        queue_record.estimated_completion_time = datetime.now() + timedelta(hours=waiting_time + charging_time)
        
        self.db.commit()
    
    def find_optimal_pile(self, queue_record: ChargingQueue, 
                         available_piles: List[ChargingPile]) -> Optional[ChargingPile]:
        """找到最优充电桩（完成充电时间最短）"""
        best_pile = None
        min_completion_time = float('inf')
        
        matching_piles = [p for p in available_piles if p.charging_mode == queue_record.charging_mode]
        
        for pile in matching_piles:
            # 计算该充电桩的总等待时间
            waiting_time = self.calculate_waiting_time(pile)
            
            # 计算自己的充电时间
            charging_time = queue_record.requested_amount / pile.power
            
            # 总完成时间 = 等待时间 + 充电时间
            total_time = waiting_time + charging_time
            
            if total_time < min_completion_time:
                min_completion_time = total_time
                best_pile = pile
        
        return best_pile
    
    def calculate_waiting_time(self, pile: ChargingPile) -> float:
        """计算充电桩的等待时间"""
        queued_vehicles = self.db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile.id,
            ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).order_by(ChargingQueue.created_at).all()
        
        total_waiting_time = 0.0
        for vehicle in queued_vehicles:
            # 每个车的充电时间
            charging_time = vehicle.requested_amount / pile.power
            total_waiting_time += charging_time
        
        return total_waiting_time
    

    
    def start_charging(self, queue_id: int):
        """开始充电"""
        queue_record = self.db.query(ChargingQueue).filter(
            ChargingQueue.id == queue_id
        ).first()
        
        if queue_record and queue_record.status == QueueStatus.QUEUING:
            # 更新队列状态
            queue_record.status = QueueStatus.CHARGING
            queue_record.start_charging_time = datetime.now()
            
            # 同步更新充电桩状态为正在充电
            if queue_record.charging_pile_id:
                pile = self.db.query(ChargingPile).filter(
                    ChargingPile.id == queue_record.charging_pile_id
                ).first()
                if pile:
                    # 将充电桩状态更新为使用中
                    from app.models import ChargingPileStatus
                    pile.status = ChargingPileStatus.CHARGING
                    print(f"🔋 充电桩 {pile.pile_number} 状态更新为使用中")
            
            self.db.commit()
    
    def complete_charging(self, queue_id: int) -> ChargingRecord:
        """完成充电并生成详单"""
        queue_record = self.db.query(ChargingQueue).filter(
            ChargingQueue.id == queue_id
        ).first()
        
        if not queue_record or queue_record.status != QueueStatus.CHARGING:
            raise Exception("无效的充电记录")
        
        # 计算费用
        end_time = datetime.now()
        start_time = queue_record.start_charging_time
        actual_duration = (end_time - start_time).total_seconds() / 3600  # 转换为小时
        
        # 获取充电桩信息
        pile = self.db.query(ChargingPile).filter(
            ChargingPile.id == queue_record.charging_pile_id
        ).first()
        
        # 计算实际充电量
        actual_amount = min(queue_record.requested_amount, pile.power * actual_duration)
        
        # 计算费用
        electricity_fee, service_fee, total_fee, unit_price, time_period = self.calculate_fees(
            actual_amount, start_time, end_time
        )
        
        # 创建充电记录
        record_number = self.generate_record_number()
        charging_record = ChargingRecord(
            record_number=record_number,
            user_id=queue_record.user_id,
            vehicle_id=queue_record.vehicle_id,
            charging_pile_id=queue_record.charging_pile_id,
            charging_amount=actual_amount,
            charging_duration=actual_duration,
            start_time=start_time,
            end_time=end_time,
            electricity_fee=electricity_fee,
            service_fee=service_fee,
            total_fee=total_fee,
            unit_price=unit_price,
            time_period=time_period
        )
        
        # 更新充电桩统计
        pile.total_charging_count += 1
        pile.total_charging_duration += actual_duration
        pile.total_charging_amount += actual_amount
        
        # 更新队列状态
        queue_record.status = QueueStatus.COMPLETED
        
        # 检查该充电桩是否有下一个排队的车辆
        next_vehicle = self.db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == queue_record.charging_pile_id,
            ChargingQueue.status == QueueStatus.QUEUING
        ).order_by(ChargingQueue.queue_time).first()
        
        # 如果没有下一个车辆，将充电桩状态恢复为正常
        if not next_vehicle:
            from app.models import ChargingPileStatus
            pile.status = ChargingPileStatus.NORMAL
            print(f"🔋 充电桩 {pile.pile_number} 状态恢复为正常")
        
        self.db.add(charging_record)
        self.db.commit()
        
        if next_vehicle:
            # 自动开始下一个车辆的充电
            self.start_charging(next_vehicle.id)
        
        return charging_record
    
    def calculate_fees(self, amount: float, start_time: datetime, end_time: datetime) -> Tuple[float, float, float, float, str]:
        """计算费用"""
        # 简化计算，使用开始时间的电价
        hour = start_time.hour
        
        # 判断时段
        if any(start <= hour < end for start, end in settings.PEAK_TIME_RANGES):
            unit_price = settings.PEAK_TIME_PRICE
            time_period = "峰时"
        elif any(start <= hour < end for start, end in settings.NORMAL_TIME_RANGES):
            unit_price = settings.NORMAL_TIME_PRICE
            time_period = "平时"
        else:
            unit_price = settings.VALLEY_TIME_PRICE
            time_period = "谷时"
        
        electricity_fee = unit_price * amount
        service_fee = settings.SERVICE_FEE_PRICE * amount
        total_fee = electricity_fee + service_fee
        
        return electricity_fee, service_fee, total_fee, unit_price, time_period
    
    def generate_record_number(self) -> str:
        """生成详单编号"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        
        # 获取今天的记录数量
        today_count = self.db.query(ChargingRecord).filter(
            ChargingRecord.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        return f"CR{timestamp}{today_count + 1:04d}"
    
    def modify_charging_request(self, queue_id: int, new_mode: Optional[ChargingMode] = None, 
                               new_amount: Optional[float] = None):
        """修改充电请求"""
        queue_record = self.db.query(ChargingQueue).filter(
            ChargingQueue.id == queue_id
        ).first()
        
        if not queue_record:
            raise Exception("排队记录不存在")
        
        if queue_record.status == QueueStatus.CHARGING:
            raise Exception("正在充电中，无法修改请求")
        
        if queue_record.status == QueueStatus.WAITING:
            # 等候区可以修改
            if new_mode and new_mode != queue_record.charging_mode:
                # 修改充电模式，重新生成排队号
                queue_record.charging_mode = new_mode
                queue_record.queue_number = self.generate_queue_number(new_mode)
            
            if new_amount:
                queue_record.requested_amount = new_amount
                
            self.db.commit()
            
        elif queue_record.status == QueueStatus.QUEUING:
            # 充电区只能修改充电量
            if new_mode and new_mode != queue_record.charging_mode:
                raise Exception("充电区不允许修改充电模式")
            
            if new_amount:
                queue_record.requested_amount = new_amount
                # 重新计算预计完成时间
                pile = self.db.query(ChargingPile).filter(
                    ChargingPile.id == queue_record.charging_pile_id
                ).first()
                waiting_time = self.calculate_waiting_time(pile)
                charging_time = new_amount / pile.power
                queue_record.estimated_completion_time = datetime.now() + timedelta(hours=waiting_time + charging_time)
                
            self.db.commit()
    
    def cancel_charging(self, queue_id: int):
        """取消充电"""
        queue_record = self.db.query(ChargingQueue).filter(
            ChargingQueue.id == queue_id
        ).first()
        
        if not queue_record:
            raise Exception("排队记录不存在")
        
        if queue_record.status == QueueStatus.CHARGING:
            # 如果正在充电，生成部分充电记录
            self.complete_charging(queue_id)
        else:
            # 如果是排队状态，直接取消并检查充电桩状态
            pile = None
            if queue_record.charging_pile_id:
                pile = self.db.query(ChargingPile).filter(
                    ChargingPile.id == queue_record.charging_pile_id
                ).first()
            
            queue_record.status = QueueStatus.CANCELLED
            self.db.commit()
            
            # 如果充电桩存在，检查是否需要恢复状态
            if pile:
                remaining_vehicles = self.db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
                ).count()
                
                if remaining_vehicles == 0:
                    from app.models import ChargingPileStatus
                    pile.status = ChargingPileStatus.NORMAL
                    print(f"🔋 充电桩 {pile.pile_number} 状态恢复为正常（取消后无车辆）")
                    self.db.commit()
        
        # 重新调度
        self.schedule_charging()
    
    def handle_pile_fault(self, pile_id: int, recovery_strategy: str = "priority"):
        """处理充电桩故障"""
        pile = self.db.query(ChargingPile).filter(
            ChargingPile.id == pile_id
        ).first()
        
        if not pile:
            raise Exception("充电桩不存在")
        
        pile.status = ChargingPileStatus.FAULT
        
        # 停止当前充电车辆的计费
        charging_vehicle = self.db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile_id,
            ChargingQueue.status == QueueStatus.CHARGING
        ).first()
        
        if charging_vehicle:
            self.complete_charging(charging_vehicle.id)
        
        # 处理故障队列中的车辆
        fault_queue_vehicles = self.db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile_id,
            ChargingQueue.status == QueueStatus.QUEUING
        ).all()
        
        if recovery_strategy == "priority":
            self.priority_reschedule(fault_queue_vehicles, pile.charging_mode)
        else:
            self.time_order_reschedule(fault_queue_vehicles, pile.charging_mode)
        
        self.db.commit()
    
    def priority_reschedule(self, fault_vehicles: List[ChargingQueue], charging_mode: ChargingMode):
        """优先级调度"""
        # 将故障队列车辆重新分配到其他同类型充电桩
        for vehicle in fault_vehicles:
            vehicle.charging_pile_id = None
            vehicle.status = QueueStatus.WAITING
        
        # 重新调度
        self.schedule_charging()
    
    def time_order_reschedule(self, fault_vehicles: List[ChargingQueue], charging_mode: ChargingMode):
        """时间顺序调度"""
        # 获取其他同类型充电桩的排队车辆
        other_queued_vehicles = self.db.query(ChargingQueue).filter(
            ChargingQueue.charging_mode == charging_mode,
            ChargingQueue.status == QueueStatus.QUEUING,
            ChargingQueue.charging_pile_id != fault_vehicles[0].charging_pile_id if fault_vehicles else None
        ).all()
        
        # 合并所有车辆并按排队号码排序
        all_vehicles = fault_vehicles + other_queued_vehicles
        all_vehicles.sort(key=lambda x: x.queue_number)
        
        # 清空所有车辆的充电桩分配
        for vehicle in all_vehicles:
            vehicle.charging_pile_id = None
            vehicle.status = QueueStatus.WAITING
        
        # 重新调度
        self.schedule_charging()
    
    def restore_pile_status(self):
        """手动恢复充电桩状态（用于调试或紧急修复）"""
        print("🔄 手动恢复充电桩状态...")
        
        try:
            # 获取所有充电桩
            all_piles = self.db.query(ChargingPile).all()
            
            restored_count = 0
            for pile in all_piles:
                # 检查该充电桩是否有正在充电的车辆
                charging_vehicle = self.db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status == QueueStatus.CHARGING
                ).first()
                
                if charging_vehicle:
                    # 有车辆正在充电，状态应为使用中
                    if pile.status != ChargingPileStatus.CHARGING:
                        pile.status = ChargingPileStatus.CHARGING
                        restored_count += 1
                        print(f"🔋 充电桩 {pile.pile_number} 状态恢复为使用中 (车辆: {charging_vehicle.queue_number})")
                else:
                    # 没有车辆正在充电，状态应为正常（除非是故障或离线）
                    if pile.status == ChargingPileStatus.CHARGING:
                        pile.status = ChargingPileStatus.NORMAL
                        restored_count += 1
                        print(f"🔋 充电桩 {pile.pile_number} 状态恢复为正常")
            
            if restored_count > 0:
                self.db.commit()
                print(f"✅ 恢复了 {restored_count} 个充电桩状态")
            else:
                print("✅ 所有充电桩状态正常，无需恢复")
                
        except Exception as e:
            print(f"❌ 恢复充电桩状态失败: {e}")
            self.db.rollback() 