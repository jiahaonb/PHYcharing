from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models import User, Vehicle, ChargingQueue, QueueStatus, ChargingPile, ChargingRecord
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
    queue_number: str  # 添加队列号
    vehicle_id: int  # 添加车辆ID
    vehicle_license: str  # 添加车牌号
    charging_mode: str  # 添加充电模式
    requested_amount: float  # 添加请求充电量
    pile_name: str
    position: int
    total_in_queue: int
    estimated_time: int
    request_time: datetime
    status: str
    start_charging_time: Optional[datetime] = None
    duration: Optional[int] = None
    # 添加实际充电数据字段
    actual_charging_amount: Optional[float] = None
    actual_electricity_fee: Optional[float] = None
    actual_service_fee: Optional[float] = None
    actual_total_fee: Optional[float] = None
    # 添加剩余时间字段
    remaining_time: Optional[int] = None
    
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
    from sqlalchemy.orm import joinedload
    
    # 查找用户的活跃队列（等待中、排队中、正在充电），并预加载车辆信息
    active_queues = db.query(ChargingQueue).options(
        joinedload(ChargingQueue.vehicle)
    ).filter(
        ChargingQueue.user_id == current_user.id,
        ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
    ).all()
    
    result = []
    for queue in active_queues:
        # 获取充电桩信息
        pile = None
        pile_name = "等候区"
        if queue.charging_pile_id:
            pile = db.query(ChargingPile).filter(ChargingPile.id == queue.charging_pile_id).first()
            if pile:
                pile_name = f"{pile.charging_mode.value}充电桩-{pile.pile_number}"
            else:
                pile_name = f"充电桩-{queue.charging_pile_id}"
        
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
        
        # 计算预计等待时间和获取剩余时间
        estimated_time = 0
        remaining_time = None
        
        if queue.status == QueueStatus.WAITING:
            # 等候区：根据前方排队人数估算等待时间
            if position > 1:
                estimated_time = (position - 1) * 30  # 每人平均30分钟
            else:
                estimated_time = 5  # 第一位预计5分钟内分配
        elif queue.status == QueueStatus.QUEUING:
            # 充电区排队：计算前方车辆的剩余时间
            if queue.charging_pile_id:
                # 查找当前正在充电的车辆剩余时间
                charging_vehicle = db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == queue.charging_pile_id,
                    ChargingQueue.status == QueueStatus.CHARGING
                ).first()
                
                if charging_vehicle:
                    charging_record = db.query(ChargingRecord).filter(
                        ChargingRecord.queue_number == charging_vehicle.queue_number
                    ).first()
                    if charging_record and charging_record.remaining_time:
                        estimated_time = charging_record.remaining_time
                
                # 加上前方排队车辆的时间
                estimated_time += (position - 1) * 30
            else:
                estimated_time = position * 30
        else:  # CHARGING
            # 正在充电：获取当前充电记录的剩余时间
            if charging_record and charging_record.remaining_time is not None:
                remaining_time = charging_record.remaining_time
                estimated_time = remaining_time
            else:
                estimated_time = 0
        
        # 计算充电时长（如果正在充电）
        duration = None
        if queue.status == QueueStatus.CHARGING and queue.start_charging_time:
            duration = int((datetime.now() - queue.start_charging_time).total_seconds() / 60)
        
        # 获取实际充电数据（如果有关联的充电记录）
        actual_charging_amount = None
        actual_electricity_fee = None
        actual_service_fee = None
        actual_total_fee = None
        
        # 查找关联的充电记录
        charging_record = db.query(ChargingRecord).filter(
            ChargingRecord.queue_number == queue.queue_number
        ).first()
        
        if charging_record:
            actual_charging_amount = charging_record.actual_charging_amount
            actual_electricity_fee = charging_record.actual_electricity_fee
            actual_service_fee = charging_record.actual_service_fee
            actual_total_fee = charging_record.actual_total_fee
        
        # 安全获取车辆牌照
        vehicle_license = "未知车辆"
        if queue.vehicle and queue.vehicle.license_plate:
            vehicle_license = queue.vehicle.license_plate
        
        # 安全获取充电模式
        charging_mode = "unknown"
        if queue.charging_mode:
            charging_mode = queue.charging_mode.value if hasattr(queue.charging_mode, 'value') else str(queue.charging_mode)
        
        result.append(QueueStatusResponse(
            id=queue.id,
            queue_number=queue.queue_number,
            vehicle_id=queue.vehicle_id,
            vehicle_license=vehicle_license,
            charging_mode=charging_mode,
            requested_amount=queue.requested_amount,
            pile_name=pile_name,
            position=position,
            total_in_queue=total_in_queue,
            estimated_time=estimated_time,
            request_time=queue.queue_time,
            status=queue.status.value,
            start_charging_time=queue.start_charging_time,
            duration=duration,
            actual_charging_amount=actual_charging_amount,
            actual_electricity_fee=actual_electricity_fee,
            actual_service_fee=actual_service_fee,
            actual_total_fee=actual_total_fee,
            remaining_time=remaining_time
        ))
    
    return result

@router.get("/charging/config", summary="获取充电配置信息（用户端）")
def get_charging_config_for_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取充电相关配置信息，用户端使用"""
    try:
        from app.services.config_service import config_service
        
        # 获取充电桩配置
        charging_config = config_service.get_charging_pile_config(db)
        
        # 获取计费配置
        billing_config = config_service.get_billing_config(db)
        
        return {
            "fast_charging_power": charging_config["fast_charging_power"],
            "trickle_charging_power": charging_config["trickle_charging_power"],
            "fast_charging_pile_num": charging_config["fast_charging_pile_num"],
            "trickle_charging_pile_num": charging_config["trickle_charging_pile_num"],
            "billing": billing_config
        }
    except Exception as e:
        # 返回默认值，避免阻塞用户功能
        print(f"获取配置失败: {e}")
        return {
            "fast_charging_power": 30.0,
            "trickle_charging_power": 7.0,
            "fast_charging_pile_num": 2,
            "trickle_charging_pile_num": 4,
            "billing": {
                "prices": {
                    "peak_time_price": 1.0,
                    "normal_time_price": 0.7,
                    "valley_time_price": 0.4,
                    "service_fee_price": 0.8
                },
                "time_periods": {
                    "peak_times": [[10, 15], [18, 21]],
                    "normal_times": [[7, 10], [15, 18], [21, 23]],
                    "valley_times": [[23, 7]]
                }
            }
        }

@router.get("/vehicles-monitoring", summary="车辆监控")
def get_vehicles_monitoring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户所有车辆的实时状态信息，用于用户端监控"""
    try:
        from sqlalchemy.orm import joinedload
        from app.models import Vehicle, ChargingQueue, ChargingRecord, QueueStatus
        
        # 只获取当前用户的车辆信息
        vehicles = db.query(Vehicle).options(joinedload(Vehicle.owner)).filter(
            Vehicle.owner_id == current_user.id
        ).all()
        
        # 获取所有活跃队列信息
        queues = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).all()
        
        # 创建车辆状态映射
        vehicle_status_map = {}
        vehicle_queue_map = {}
        for queue in queues:
            status = queue.status.value if hasattr(queue.status, 'value') else str(queue.status)
            vehicle_status_map[queue.vehicle_id] = status
            vehicle_queue_map[queue.vehicle_id] = queue
        
        result = []
        for vehicle in vehicles:
            try:
                # 获取车辆当前状态
                current_status = vehicle_status_map.get(vehicle.id, "registered")
                
                # 状态映射到中文显示
                status_text_map = {
                    "waiting": "等候",
                    "queuing": "等候", 
                    "charging": "充电中",
                    "registered": "暂留"
                }
                display_status = status_text_map.get(current_status, "暂留")
                
                # 获取车主信息
                owner_info = None
                if vehicle.owner:
                    owner_info = {
                        "username": vehicle.owner.username,
                        "email": vehicle.owner.email,
                        "phone": getattr(vehicle.owner, 'phone', None)
                    }
                
                # 获取队列信息（如果有）
                queue_info = None
                if vehicle.id in vehicle_queue_map:
                    queue = vehicle_queue_map[vehicle.id]
                    queue_info = {
                        "id": queue.id,
                        "queue_number": queue.queue_number,
                        "charging_mode": queue.charging_mode.value if hasattr(queue.charging_mode, 'value') else str(queue.charging_mode),
                        "requested_amount": queue.requested_amount,
                        "queue_time": queue.queue_time,
                        "estimated_completion_time": queue.estimated_completion_time,
                        "charging_pile_id": queue.charging_pile_id
                    }
                
                # 获取最后一次充电记录
                last_charging_record = db.query(ChargingRecord).filter(
                    ChargingRecord.vehicle_id == vehicle.id
                ).order_by(ChargingRecord.end_time.desc()).first()
                
                last_charging_time = None
                if last_charging_record:
                    last_charging_time = last_charging_record.end_time
                
                vehicle_data = {
                    "id": vehicle.id,
                    "license_plate": vehicle.license_plate,
                    "battery_capacity": vehicle.battery_capacity or 0.0,
                    "model": vehicle.model or "未知型号",
                    "status": display_status,
                    "status_code": current_status,  # 原始状态码，用于前端逻辑判断
                    "owner": owner_info,
                    "queue_info": queue_info,
                    "last_charging_time": last_charging_time,
                    "created_at": vehicle.created_at
                }
                result.append(vehicle_data)
                
            except Exception as e:
                print(f"处理车辆 {vehicle.id} 时出错: {e}")
                continue
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        print(f"获取车辆监控数据失败: {e}")
        return {"status": "error", "message": str(e), "data": []}

@router.get("/vehicles/{vehicle_id}/detail", summary="获取车辆详细信息")
def get_vehicle_detail(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定车辆的详细信息"""
    try:
        from sqlalchemy.orm import joinedload
        from app.models import Vehicle, ChargingQueue, ChargingRecord, QueueStatus
        
        # 获取车辆信息（仅允许查看自己的车辆）
        vehicle = db.query(Vehicle).options(joinedload(Vehicle.owner)).filter(
            Vehicle.id == vehicle_id,
            Vehicle.owner_id == current_user.id
        ).first()
        
        if not vehicle:
            return {"status": "error", "message": "车辆不存在或无权访问"}
        
        # 获取当前队列状态
        current_queue = db.query(ChargingQueue).filter(
            ChargingQueue.vehicle_id == vehicle_id,
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).first()
        
        # 获取最后一次充电记录
        last_charging_record = db.query(ChargingRecord).filter(
            ChargingRecord.vehicle_id == vehicle_id
        ).order_by(ChargingRecord.end_time.desc()).first()
        
        # 获取历史充电记录（最近5次）
        charging_history = db.query(ChargingRecord).filter(
            ChargingRecord.vehicle_id == vehicle_id
        ).order_by(ChargingRecord.end_time.desc()).limit(5).all()
        
        # 确定当前状态
        current_status = "registered"  # 默认为暂留
        if current_queue:
            current_status = current_queue.status.value if hasattr(current_queue.status, 'value') else str(current_queue.status)
        
        status_text_map = {
            "waiting": "等候",
            "queuing": "等候",
            "charging": "充电中", 
            "registered": "暂留"
        }
        display_status = status_text_map.get(current_status, "暂留")
        
        # 构建响应数据
        result = {
            "id": vehicle.id,
            "license_plate": vehicle.license_plate,
            "battery_capacity": vehicle.battery_capacity or 0.0,
            "model": vehicle.model or "未知型号",
            "status": display_status,
            "status_code": current_status,
            "owner": {
                "username": vehicle.owner.username if vehicle.owner else "未知",
                "email": vehicle.owner.email if vehicle.owner else "",
                "phone": getattr(vehicle.owner, 'phone', None) if vehicle.owner else None
            },
            "current_queue": None,
            "last_charging_time": last_charging_record.end_time if last_charging_record else None,
            "charging_history": [
                {
                    "id": record.id,
                    "record_number": record.record_number,
                    "charging_amount": record.charging_amount,
                    "charging_duration": record.charging_duration,
                    "start_time": record.start_time,
                    "end_time": record.end_time,
                    "total_fee": record.total_fee
                } for record in charging_history
            ],
            "created_at": vehicle.created_at
        }
        
        # 添加当前队列信息
        if current_queue:
            result["current_queue"] = {
                "id": current_queue.id,
                "queue_number": current_queue.queue_number,
                "charging_mode": current_queue.charging_mode.value if hasattr(current_queue.charging_mode, 'value') else str(current_queue.charging_mode),
                "requested_amount": current_queue.requested_amount,
                "queue_time": current_queue.queue_time,
                "estimated_completion_time": current_queue.estimated_completion_time,
                "charging_pile_id": current_queue.charging_pile_id
            }
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        print(f"获取车辆详情失败: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/vehicles/{vehicle_id}/end-charging", summary="结束充电")
def end_vehicle_charging(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """结束指定车辆的充电"""
    try:
        from app.models import ChargingQueue, QueueStatus, Vehicle
        from app.services.charging_service import ChargingScheduleService
        
        # 首先验证车辆属于当前用户
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == vehicle_id,
            Vehicle.owner_id == current_user.id
        ).first()
        
        if not vehicle:
            return {"status": "error", "message": "车辆不存在或无权访问"}
        
        # 查找正在充电的队列记录
        charging_queue = db.query(ChargingQueue).filter(
            ChargingQueue.vehicle_id == vehicle_id,
            ChargingQueue.status == QueueStatus.CHARGING
        ).first()
        
        if not charging_queue:
            return {"status": "error", "message": "该车辆当前不在充电状态"}
        
        # 使用充电服务结束充电
        service = ChargingScheduleService(db)
        record = service.complete_charging(charging_queue.id)
        
        return {
            "status": "success", 
            "message": "充电已结束",
            "data": {
                "record_id": record.id,
                "record_number": record.record_number,
                "total_fee": record.total_fee
            }
        }
        
    except Exception as e:
        print(f"结束充电失败: {e}")
        return {"status": "error", "message": str(e)}