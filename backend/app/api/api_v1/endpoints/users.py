from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models import User, Vehicle, ChargingQueue, QueueStatus, ChargingPile
from .auth import get_current_user

router = APIRouter()

class VehicleCreate(BaseModel):
    license_plate: str
    battery_capacity: float
    model: str = None

class VehicleResponse(BaseModel):
    id: int
    license_plate: str
    battery_capacity: float
    model: str = None
    
    class Config:
        from_attributes = True

class QueueStatusResponse(BaseModel):
    id: int
    pile_name: str
    position: int
    total_in_queue: int
    estimated_time: int
    request_time: datetime
    status: str
    start_charging_time: Optional[datetime] = None
    duration: Optional[int] = None
    
    class Config:
        from_attributes = True

@router.post("/vehicles", response_model=VehicleResponse, summary="添加车辆")
def create_vehicle(
    vehicle: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加车辆"""
    # 检查车牌号是否已存在
    if db.query(Vehicle).filter(Vehicle.license_plate == vehicle.license_plate).first():
        raise HTTPException(status_code=400, detail="车牌号已存在")
    
    db_vehicle = Vehicle(
        license_plate=vehicle.license_plate,
        battery_capacity=vehicle.battery_capacity,
        model=vehicle.model,
        owner_id=current_user.id
    )
    
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    return db_vehicle

@router.get("/vehicles", response_model=List[VehicleResponse], summary="获取用户车辆列表")
def get_user_vehicles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的车辆列表"""
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id).all()
    return vehicles

@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse, summary="获取特定车辆信息")
def get_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取特定车辆信息"""
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.owner_id == current_user.id
    ).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")
    
    return vehicle

@router.put("/vehicles/{vehicle_id}", response_model=VehicleResponse, summary="更新车辆信息")
def update_vehicle(
    vehicle_id: int,
    vehicle: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新车辆信息"""
    db_vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.owner_id == current_user.id
    ).first()
    
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")
    
    # 检查车牌号是否已被其他车辆使用
    existing_vehicle = db.query(Vehicle).filter(
        Vehicle.license_plate == vehicle.license_plate,
        Vehicle.id != vehicle_id
    ).first()
    if existing_vehicle:
        raise HTTPException(status_code=400, detail="车牌号已存在")
    
    # 更新车辆信息
    db_vehicle.license_plate = vehicle.license_plate
    db_vehicle.battery_capacity = vehicle.battery_capacity
    db_vehicle.model = vehicle.model
    
    db.commit()
    db.refresh(db_vehicle)
    
    return db_vehicle

@router.delete("/vehicles/{vehicle_id}", summary="删除车辆")
def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除车辆"""
    db_vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.owner_id == current_user.id
    ).first()
    
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="车辆不存在")
    
    db.delete(db_vehicle)
    db.commit()
    
    return {"message": "车辆删除成功"}

@router.get("/queue/status", response_model=List[QueueStatusResponse], summary="获取用户排队状态")
def get_user_queue_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户当前的排队状态"""
    # 查找用户的活跃队列（等待中、排队中、正在充电）
    active_queues = db.query(ChargingQueue).filter(
        ChargingQueue.user_id == current_user.id,
        ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
    ).all()
    
    result = []
    for queue in active_queues:
        # 获取充电桩信息
        pile = db.query(ChargingPile).filter(ChargingPile.id == queue.charging_pile_id).first()
        pile_name = f"{pile.charging_mode.value}充电桩-{pile.pile_number}" if pile else f"充电桩-{queue.charging_pile_id}"
        
        # 计算排队位置和总人数
        if queue.charging_pile_id:
            # 已分配充电桩的情况
            queuing_before = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == queue.charging_pile_id,
                ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING]),
                ChargingQueue.queue_time < queue.queue_time
            ).count()
            
            total_in_queue = db.query(ChargingQueue).filter(
                ChargingQueue.charging_pile_id == queue.charging_pile_id,
                ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
            ).count()
            
            position = queuing_before + 1
        else:
            # 等候区的情况
            waiting_before = db.query(ChargingQueue).filter(
                ChargingQueue.charging_mode == queue.charging_mode,
                ChargingQueue.status == QueueStatus.WAITING,
                ChargingQueue.queue_time < queue.queue_time
            ).count()
            
            total_in_queue = db.query(ChargingQueue).filter(
                ChargingQueue.charging_mode == queue.charging_mode,
                ChargingQueue.status == QueueStatus.WAITING
            ).count()
            
            position = waiting_before + 1
        
        # 计算预计等待时间（简单估算：每人平均30分钟）
        if queue.status == QueueStatus.WAITING:
            estimated_time = (position - 1) * 30
        elif queue.status == QueueStatus.QUEUING:
            estimated_time = (position - 1) * 30
        else:  # CHARGING
            estimated_time = 0
        
        # 计算充电时长（如果正在充电）
        duration = None
        if queue.status == QueueStatus.CHARGING and queue.start_charging_time:
            duration = int((datetime.now() - queue.start_charging_time).total_seconds() / 60)
        
        result.append(QueueStatusResponse(
            id=queue.id,
            pile_name=pile_name,
            position=position,
            total_in_queue=total_in_queue,
            estimated_time=estimated_time,
            request_time=queue.queue_time,
            status=queue.status.value,
            start_charging_time=queue.start_charging_time,
            duration=duration
        ))
    
    return result 