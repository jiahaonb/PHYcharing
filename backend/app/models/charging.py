from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class ChargingMode(enum.Enum):
    """充电模式枚举"""
    FAST = "fast"  # 快充
    TRICKLE = "trickle"  # 慢充

class ChargingPileStatus(enum.Enum):
    """充电桩状态枚举"""
    NORMAL = "normal"  # 正常
    CHARGING = "charging"  # 使用中
    FAULT = "fault"  # 故障
    OFFLINE = "offline"  # 离线

class QueueStatus(enum.Enum):
    """排队状态枚举"""
    WAITING = "waiting"  # 等候区等待
    QUEUING = "queuing"  # 充电区排队
    CHARGING = "charging"  # 正在充电
    COMPLETED = "completed"  # 充电完成
    CANCELLED = "cancelled"  # 已取消

class ChargingPile(Base):
    """充电桩模型"""
    __tablename__ = "charging_piles"
    
    id = Column(Integer, primary_key=True, index=True)
    pile_number = Column(String(20), unique=True, index=True, nullable=False)  # 充电桩编号
    charging_mode = Column(Enum(ChargingMode), nullable=False)  # 充电模式
    power = Column(Float, nullable=False)  # 充电功率(度/小时)
    status = Column(Enum(ChargingPileStatus), default=ChargingPileStatus.NORMAL)
    is_active = Column(Boolean, default=True)
    
    # 统计信息
    total_charging_count = Column(Integer, default=0)  # 累计充电次数
    total_charging_duration = Column(Float, default=0.0)  # 累计充电时长(小时)
    total_charging_amount = Column(Float, default=0.0)  # 累计充电量(度)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联充电记录
    charging_records = relationship("ChargingRecord", back_populates="charging_pile")
    
    def get_current_charging_order(self, db_session):
        """获取当前正在充电的订单"""
        return db_session.query(ChargingRecord).filter(
            ChargingRecord.charging_pile_id == self.id,
            ChargingRecord.status == "charging"
        ).first()
    
    def get_queuing_orders(self, db_session):
        """获取排队中的订单列表（按创建时间排序）"""
        return db_session.query(ChargingRecord).filter(
            ChargingRecord.charging_pile_id == self.id,
            ChargingRecord.status == "assigned"
        ).order_by(ChargingRecord.created_at).all()
    
    def get_all_active_orders(self, db_session):
        """获取所有活跃订单（充电中 + 排队中）"""
        return db_session.query(ChargingRecord).filter(
            ChargingRecord.charging_pile_id == self.id,
            ChargingRecord.status.in_(["charging", "assigned"])
        ).order_by(ChargingRecord.created_at).all()

class ChargingQueue(Base):
    """充电队列模型"""
    __tablename__ = "charging_queues"
    
    id = Column(Integer, primary_key=True, index=True)
    queue_number = Column(String(20), unique=True, index=True, nullable=False)  # 排队号码(F1, T1等)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    charging_mode = Column(Enum(ChargingMode), nullable=False)
    requested_amount = Column(Float, nullable=False)  # 请求充电量(度)
    status = Column(Enum(QueueStatus), default=QueueStatus.WAITING)
    charging_pile_id = Column(Integer, ForeignKey("charging_piles.id"), nullable=True)  # 分配的充电桩ID
    
    # 时间信息
    queue_time = Column(DateTime(timezone=True), server_default=func.now())  # 排队时间
    start_charging_time = Column(DateTime(timezone=True), nullable=True)  # 开始充电时间
    estimated_completion_time = Column(DateTime(timezone=True), nullable=True)  # 预计完成时间
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User")
    vehicle = relationship("Vehicle") 
    pile = relationship("ChargingPile")

class ChargingRecord(Base):
    """充电详单模型"""
    __tablename__ = "charging_records"
    
    id = Column(Integer, primary_key=True, index=True)
    record_number = Column(String(50), unique=True, index=True, nullable=False)  # 订单编号
    queue_number = Column(String(20), nullable=False)  # 排队号
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    license_plate = Column(String(20), nullable=False)  # 车牌号
    charging_pile_id = Column(Integer, ForeignKey("charging_piles.id"), nullable=True)  # 充电桩编号(分配时补充)
    
    # 充电信息
    charging_amount = Column(Float, nullable=False)  # 充电电量(度)
    charging_duration = Column(Float, nullable=True)  # 充电时长(小时) - 充电结束时更新
    remaining_time = Column(Integer, nullable=True)  # 剩余时间(分钟) - 开始充电时设置，每分钟递减
    start_time = Column(DateTime(timezone=True), nullable=True)  # 启动时间
    end_time = Column(DateTime(timezone=True), nullable=True)  # 停止时间
    
    # 费用信息
    electricity_fee = Column(Float, nullable=False)  # 充电费用
    service_fee = Column(Float, nullable=False)  # 服务费用
    total_fee = Column(Float, nullable=False)  # 总费用
    
    # 其他信息
    unit_price = Column(Float, nullable=True)  # 单位电价
    time_period = Column(String(20), nullable=True)  # 时段(峰/平/谷)
    charging_mode = Column(Enum(ChargingMode), nullable=False)  # 充电模式
    
    # 订单状态
    status = Column(String(20), default="created")  # created, assigned, charging, completed, cancelled
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 订单生成时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系
    user = relationship("User", back_populates="charging_records")
    vehicle = relationship("Vehicle", back_populates="charging_records")
    charging_pile = relationship("ChargingPile", back_populates="charging_records") 