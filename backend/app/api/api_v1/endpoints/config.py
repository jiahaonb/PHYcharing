import json
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.config import SystemConfig
from app.models.user import User
from .auth import get_current_user
from app.services.config_service import config_service

router = APIRouter()


# Pydantic 模型
class ConfigItem(BaseModel):
    config_key: str
    config_value: str
    config_type: str
    description: str = None
    category: str
    is_active: bool = True

    class Config:
        from_attributes = True


class ConfigUpdate(BaseModel):
    config_value: str
    description: str = None
    is_active: bool = True


class ConfigResponse(BaseModel):
    id: int
    config_key: str
    config_value: str
    config_type: str
    description: str = None
    category: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 配置分类定义
CONFIG_CATEGORIES = {
    "charging_piles": "充电桩配置",
    "queue_settings": "队列配置", 
    "billing": "计费配置",
    "system": "系统配置",
    "notifications": "通知配置",
    "security": "安全配置",
    "server": "服务器配置",
    "database": "数据库配置"
}


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


@router.get("/categories", response_model=Dict[str, str])
async def get_config_categories():
    """获取配置分类列表"""
    return CONFIG_CATEGORIES


@router.get("/", response_model=List[ConfigResponse])
async def get_all_configs(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有配置项"""
    query = db.query(SystemConfig)
    if category:
        query = query.filter(SystemConfig.category == category)
    
    configs = query.order_by(SystemConfig.category, SystemConfig.config_key).all()
    return configs


@router.get("/{config_key}", response_model=ConfigResponse)
async def get_config(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取单个配置项"""
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置项 {config_key} 不存在"
        )
    return config


@router.put("/{config_key}", response_model=ConfigResponse)
async def update_config(
    config_key: str,
    config_update: ConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新配置项"""
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置项 {config_key} 不存在"
        )
    
    # 验证配置值格式
    try:
        if config.config_type in ["integer", "float"]:
            # 验证数值类型
            if config.config_type == "integer":
                int(config_update.config_value)
            else:
                float(config_update.config_value)
        elif config.config_type == "boolean":
            # 验证布尔类型
            if config_update.config_value.lower() not in ["true", "false", "1", "0"]:
                raise ValueError("布尔值必须是 true/false 或 1/0")
        elif config.config_type == "json":
            # 验证JSON格式
            json.loads(config_update.config_value)
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置值格式错误: {str(e)}"
        )
    
    # 更新配置
    config.config_value = config_update.config_value
    if config_update.description is not None:
        config.description = config_update.description
    config.is_active = config_update.is_active
    
    db.commit()
    db.refresh(config)
    
    # 清空缓存
    config_service.invalidate_cache()
    
    return config


@router.post("/", response_model=ConfigResponse)
async def create_config(
    config_item: ConfigItem,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """创建新配置项"""
    # 检查配置键是否已存在
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == config_item.config_key).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置项 {config_item.config_key} 已存在"
        )
    
    # 验证配置值格式
    try:
        if config_item.config_type in ["integer", "float"]:
            if config_item.config_type == "integer":
                int(config_item.config_value)
            else:
                float(config_item.config_value)
        elif config_item.config_type == "boolean":
            if config_item.config_value.lower() not in ["true", "false", "1", "0"]:
                raise ValueError("布尔值必须是 true/false 或 1/0")
        elif config_item.config_type == "json":
            json.loads(config_item.config_value)
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置值格式错误: {str(e)}"
        )
    
    config = SystemConfig(**config_item.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    
    # 清空缓存
    config_service.invalidate_cache()
    
    return config


@router.delete("/{config_key}")
async def delete_config(
    config_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """删除配置项"""
    config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"配置项 {config_key} 不存在"
        )
    
    db.delete(config)
    db.commit()
    
    # 清空缓存
    config_service.invalidate_cache()
    
    return {"message": f"配置项 {config_key} 已删除"}


@router.post("/batch-update")
async def batch_update_configs(
    updates: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """批量更新配置项"""
    results = []
    errors = []
    
    for update_data in updates:
        try:
            config_key = update_data.get("config_key")
            config_value = update_data.get("config_value")
            
            if not config_key or config_value is None:
                errors.append(f"配置项缺少必要字段: {update_data}")
                continue
                
            config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
            if not config:
                errors.append(f"配置项 {config_key} 不存在")
                continue
            
            # 验证和更新配置值
            config.config_value = str(config_value)
            if "description" in update_data:
                config.description = update_data["description"]
            if "is_active" in update_data:
                config.is_active = update_data["is_active"]
                
            results.append(config_key)
            
        except Exception as e:
            errors.append(f"更新 {config_key} 失败: {str(e)}")
    
    if results:
        db.commit()
    
    # 清空缓存
    config_service.invalidate_cache()
    
    return {
        "success_count": len(results),
        "error_count": len(errors),
        "updated_configs": results,
        "errors": errors
    }


@router.get("/export/yaml")
async def export_config_yaml(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """导出配置为YAML格式"""
    import yaml
    
    configs = db.query(SystemConfig).filter(SystemConfig.is_active == True).all()
    
    # 组织配置数据
    config_data = {}
    for config in configs:
        category = config.category
        if category not in config_data:
            config_data[category] = {}
        
        # 处理配置值
        try:
            if config.config_type == "integer":
                value = int(config.config_value)
            elif config.config_type == "float":
                value = float(config.config_value)
            elif config.config_type == "boolean":
                value = config.config_value.lower() in ["true", "1"]
            elif config.config_type == "json":
                value = json.loads(config.config_value)
            else:
                value = config.config_value
        except:
            value = config.config_value
        
        config_data[category][config.config_key] = value
    
    return {"yaml_content": yaml.dump(config_data, default_flow_style=False, allow_unicode=True)} 