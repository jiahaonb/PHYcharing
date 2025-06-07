from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联车辆
    vehicles = relationship("Vehicle", back_populates="owner")
    
    # 关联充电记录
    charging_records = relationship("ChargingRecord", back_populates="user")

class Vehicle(Base):
    """车辆模型"""
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String(20), unique=True, index=True, nullable=False)
    battery_capacity = Column(Float, nullable=False)  # 电池总容量(度)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    model = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联用户
    owner = relationship("User", back_populates="vehicles")
    
    # 关联充电记录
    charging_records = relationship("ChargingRecord", back_populates="vehicle") 