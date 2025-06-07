from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import ChargingQueue, ChargingPile, QueueStatus, ChargingPileStatus
from app.services.charging_service import ChargingScheduleService
from app.core.database import get_db
import asyncio
import logging

logger = logging.getLogger(__name__)

class SystemScheduler:
    """系统调度器 - 处理系统启动时的状态恢复和自动调度"""
    
    def __init__(self):
        self.db = next(get_db())
        self.charging_service = ChargingScheduleService(self.db)
    
    def get_fresh_db(self):
        """获取新的数据库会话"""
        return next(get_db())
    
    def recover_system_state(self):
        """系统启动时恢复状态"""
        logger.info("开始恢复系统状态...")
        
        try:
            # 1. 检查和修复孤立的排队记录
            self.fix_orphaned_queues()
            
            # 2. 重新调度等候区的车辆
            self.reschedule_waiting_vehicles()
            
            # 3. 检查排队中的车辆是否可以开始充电
            self.check_queuing_vehicles()
            
            # 4. 清理无效状态
            self.cleanup_invalid_states()
            
            logger.info("系统状态恢复完成")
            
        except Exception as e:
            logger.error(f"系统状态恢复失败: {str(e)}")
    
    def fix_orphaned_queues(self):
        """修复孤立的排队记录（充电桩ID无效或充电桩不存在）"""
        logger.info("检查孤立的排队记录...")
        
        # 查找充电桩ID无效的队列记录
        orphaned_queues = self.db.query(ChargingQueue).filter(
            ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING]),
            ChargingQueue.charging_pile_id.isnot(None)
        ).all()
        
        fixed_count = 0
        for queue in orphaned_queues:
            # 检查充电桩是否存在且可用
            pile = self.db.query(ChargingPile).filter(
                ChargingPile.id == queue.charging_pile_id,
                ChargingPile.is_active == True
            ).first()
            
            if not pile:
                # 充电桩不存在或不可用，将车辆移回等候区
                queue.charging_pile_id = None
                queue.status = QueueStatus.WAITING
                queue.estimated_completion_time = None
                fixed_count += 1
                logger.info(f"修复孤立队列记录: {queue.queue_number}")
        
        if fixed_count > 0:
            self.db.commit()
            logger.info(f"修复了 {fixed_count} 个孤立队列记录")
    
    def reschedule_waiting_vehicles(self):
        """重新调度等候区的车辆"""
        logger.info("重新调度等候区车辆...")
        
        # 获取所有等候区的车辆
        waiting_vehicles = self.db.query(ChargingQueue).filter(
            ChargingQueue.status == QueueStatus.WAITING
        ).order_by(ChargingQueue.queue_time).all()
        
        if waiting_vehicles:
            logger.info(f"发现 {len(waiting_vehicles)} 个等候区车辆，开始重新调度")
            self.charging_service.schedule_charging()
        else:
            logger.info("等候区无车辆需要调度")
    
    def check_queuing_vehicles(self):
        """检查排队中的车辆是否可以开始充电"""
        logger.info("检查排队中的车辆...")
        
        # 使用新的数据库会话确保数据最新
        db = self.get_fresh_db()
        charging_service = ChargingScheduleService(db)
        
        # 获取所有充电桩
        piles = db.query(ChargingPile).filter(
            ChargingPile.is_active == True,
            ChargingPile.status == ChargingPileStatus.NORMAL
        ).all()
        
        started_count = 0
        for pile in piles:
            # 检查该充电桩是否有正在充电的车辆
            charging_vehicle = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == pile.id,
                ChargingQueue.status == QueueStatus.CHARGING
            ).first()
            
            if not charging_vehicle:
                # 该充电桩空闲，检查是否有排队的车辆
                next_vehicle = db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status == QueueStatus.QUEUING
                ).order_by(ChargingQueue.queue_time).first()
                
                if next_vehicle:
                    # 开始充电
                    charging_service.start_charging(next_vehicle.id)
                    started_count += 1
                    logger.info(f"自动开始充电: {next_vehicle.queue_number} 在充电桩 {pile.pile_number}")
        
        if started_count > 0:
            logger.info(f"自动开始了 {started_count} 个充电任务")
        else:
            logger.info("没有需要自动开始的充电任务")
    
    def cleanup_invalid_states(self):
        """清理无效状态"""
        logger.info("清理无效状态...")
        
        # 清理状态为已完成但时间过早的记录（可能是系统异常导致的）
        # 这里可以根据业务需求添加具体的清理逻辑
        pass
    
    def start_periodic_scheduler(self):
        """启动周期性调度器"""
        logger.info("启动周期性调度器...")
        
        async def periodic_check():
            while True:
                try:
                    # 每30秒检查一次是否需要调度
                    await asyncio.sleep(30)
                    
                    # 检查排队中的车辆是否可以开始充电
                    self.check_queuing_vehicles()
                    
                    # 重新调度等候区车辆
                    self.reschedule_waiting_vehicles()
                    
                except Exception as e:
                    logger.error(f"周期性调度出错: {str(e)}")
        
        # 在后台运行周期性检查
        asyncio.create_task(periodic_check())

# 全局调度器实例
system_scheduler = SystemScheduler() 