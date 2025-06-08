"""
充电详单服务
管理充电详单的创建、更新和查询
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from app.models.charging import ChargingRecord, ChargingMode
from app.models.user import User
from app.models.vehicle import Vehicle


class ChargingOrderService:
    """充电详单服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_charging_order(
        self,
        user_id: int,
        vehicle_id: int,
        charging_mode: ChargingMode,
        charging_amount: float
    ) -> ChargingRecord:
        """
        创建充电详单
        在用户提交充电请求时调用
        """
        # 生成订单编号
        record_number = self._generate_order_number()
        
        # 创建充电详单记录
        charging_record = ChargingRecord(
            record_number=record_number,
            user_id=user_id,
            vehicle_id=vehicle_id,
            charging_amount=charging_amount,
            charging_mode=charging_mode,
            status="created"
        )
        
        self.db.add(charging_record)
        self.db.commit()
        self.db.refresh(charging_record)
        
        return charging_record
    
    def assign_charging_pile(
        self,
        record_id: int,
        charging_pile_id: int
    ) -> ChargingRecord:
        """
        分配充电桩
        当充电桩分配给用户时调用
        """
        record = self.db.query(ChargingRecord).filter(
            ChargingRecord.id == record_id
        ).first()
        
        if not record:
            raise ValueError("充电详单不存在")
        
        record.charging_pile_id = charging_pile_id
        record.status = "assigned"
        
        self.db.commit()
        self.db.refresh(record)
        
        return record
    
    def start_charging(
        self,
        record_id: int
    ) -> ChargingRecord:
        """
        开始充电
        当充电开始时调用
        """
        record = self.db.query(ChargingRecord).filter(
            ChargingRecord.id == record_id
        ).first()
        
        if not record:
            raise ValueError("充电详单不存在")
        
        record.start_time = datetime.now()
        record.status = "charging"
        
        self.db.commit()
        self.db.refresh(record)
        
        return record
    
    def complete_charging(
        self,
        record_id: int,
        actual_charging_amount: float,
        electricity_price: float,
        service_fee_price: float,
        time_period: str
    ) -> ChargingRecord:
        """
        完成充电
        当充电结束时调用，计算最终费用
        """
        record = self.db.query(ChargingRecord).filter(
            ChargingRecord.id == record_id
        ).first()
        
        if not record:
            raise ValueError("充电详单不存在")
        
        # 记录结束时间
        end_time = datetime.now()
        record.end_time = end_time
        
        # 计算充电时长（小时）
        if record.start_time:
            duration = (end_time - record.start_time).total_seconds() / 3600
            record.charging_duration = round(duration, 2)
        
        # 更新实际充电量
        record.charging_amount = actual_charging_amount
        
        # 计算费用
        electricity_fee = actual_charging_amount * electricity_price
        service_fee = actual_charging_amount * service_fee_price
        total_fee = electricity_fee + service_fee
        
        record.electricity_fee = round(electricity_fee, 2)
        record.service_fee = round(service_fee, 2)
        record.total_fee = round(total_fee, 2)
        record.unit_price = electricity_price
        record.time_period = time_period
        record.status = "completed"
        
        self.db.commit()
        self.db.refresh(record)
        
        return record
    
    def cancel_charging_order(
        self,
        record_id: int
    ) -> ChargingRecord:
        """
        取消充电详单
        """
        record = self.db.query(ChargingRecord).filter(
            ChargingRecord.id == record_id
        ).first()
        
        if not record:
            raise ValueError("充电详单不存在")
        
        record.status = "cancelled"
        
        self.db.commit()
        self.db.refresh(record)
        
        return record
    
    def get_user_charging_orders(
        self,
        user_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[ChargingRecord]:
        """
        获取用户的充电详单
        """
        query = self.db.query(ChargingRecord).filter(
            ChargingRecord.user_id == user_id
        )
        
        if status:
            query = query.filter(ChargingRecord.status == status)
        
        query = query.order_by(ChargingRecord.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_all_charging_orders(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        username: Optional[str] = None,
        license_plate: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取所有充电详单（管理员用）
        """
        query = self.db.query(ChargingRecord)
        
        # 用户名过滤
        if username:
            query = query.join(User).filter(
                User.username.ilike(f"%{username}%")
            )
        
        # 车牌号过滤
        if license_plate:
            query = query.join(Vehicle).filter(
                Vehicle.license_plate.ilike(f"%{license_plate}%")
            )
        
        # 状态过滤
        if status:
            query = query.filter(ChargingRecord.status == status)
        
        # 日期范围过滤
        if start_date:
            query = query.filter(ChargingRecord.created_at >= start_date)
        
        if end_date:
            query = query.filter(ChargingRecord.created_at <= end_date)
        
        # 获取总数
        total = query.count()
        
        # 分页
        query = query.order_by(ChargingRecord.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        records = query.all()
        
        return {
            "items": records,
            "total": total
        }
    
    def get_charging_order_statistics(self) -> Dict[str, Any]:
        """
        获取充电详单统计信息（管理员用）
        """
        # 总订单数
        total_orders = self.db.query(ChargingRecord).count()
        
        # 今日订单数
        today = datetime.now().date()
        today_orders = self.db.query(ChargingRecord).filter(
            ChargingRecord.created_at >= today
        ).count()
        
        # 总收入
        total_revenue = self.db.query(ChargingRecord.total_fee).filter(
            ChargingRecord.status == "completed"
        ).scalar() or 0
        
        # 今日收入
        today_revenue = self.db.query(ChargingRecord.total_fee).filter(
            ChargingRecord.created_at >= today,
            ChargingRecord.status == "completed"
        ).scalar() or 0
        
        return {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "total_revenue": round(total_revenue, 2),
            "today_revenue": round(today_revenue, 2)
        }
    
    def _generate_order_number(self) -> str:
        """
        生成订单编号
        格式：CO + 年月日 + 4位随机数
        """
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = str(uuid.uuid4()).replace("-", "")[:4].upper()
        return f"CO{date_str}{random_str}"


# 时段和电价计算工具函数
def get_current_time_period() -> str:
    """获取当前时段"""
    hour = datetime.now().hour
    
    # 峰时: 10:00-15:00, 18:00-21:00
    if (10 <= hour < 15) or (18 <= hour < 21):
        return "峰时"
    
    # 谷时: 23:00-次日7:00
    elif hour >= 23 or hour < 7:
        return "谷时"
    
    # 平时: 其他时间
    else:
        return "平时"


def get_electricity_price(time_period: str) -> float:
    """根据时段获取电价"""
    price_map = {
        "峰时": 1.0,
        "平时": 0.7,
        "谷时": 0.4
    }
    return price_map.get(time_period, 0.7)


def get_service_fee_price() -> float:
    """获取服务费单价"""
    return 0.8 