from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True, nullable=False)  # 配置键
    config_value = Column(Text, nullable=False)  # 配置值（JSON字符串）
    config_type = Column(String(50), nullable=False)  # 配置类型
    description = Column(String(500))  # 配置描述
    category = Column(String(50), nullable=False)  # 配置分类
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 