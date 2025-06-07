from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models import User, Vehicle, ChargingPile, ChargingQueue, ChargingRecord, ChargingPileStatus, QueueStatus
from app.services.charging_service import ChargingScheduleService
from .auth import get_current_user

router = APIRouter()

class ChargingPileResponse(BaseModel):
    id: int
    pile_number: str
    charging_mode: str
    power: float
    status: str
    is_active: bool
    total_charging_count: int
    total_charging_duration: float
    total_charging_amount: float
    
    class Config:
        from_attributes = True

class QueueInfoResponse(BaseModel):
    id: int
    queue_number: str
    user_id: int
    vehicle_id: int
    requested_amount: float
    queue_time: datetime
    
    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    time_period: str
    pile_number: str
    charging_count: int
    charging_duration: float
    charging_amount: float
    electricity_fee: float
    service_fee: float
    total_fee: float

class VehicleInfoResponse(BaseModel):
    id: int
    license_plate: str
    battery_capacity: float
    model: str = None
    owner_username: str
    owner_email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PileQueueResponse(BaseModel):
    pile_id: int
    pile_name: str
    pile_status: str
    queue_length: int
    current_user: Optional[str] = None
    estimated_wait_time: int
    queue_details: List[dict] = []

class QueueDetailResponse(BaseModel):
    position: int
    username: str
    vehicle_info: str
    request_time: datetime
    status: str

class QueueLogResponse(BaseModel):
    timestamp: datetime
    pile_name: str
    user: str
    action: str
    description: str

class VehicleWithOwnerResponse(BaseModel):
    id: int
    license_plate: str
    battery_capacity: float
    model: str = None
    status: str = 'registered'
    owner: Optional[dict] = None
    
    class Config:
        from_attributes = True

class ChargingPileWithSpotsResponse(BaseModel):
    id: int
    pile_id: str
    type: str
    status: str
    power: float
    
    class Config:
        from_attributes = True

class QueueWithVehicleResponse(BaseModel):
    id: int
    queue_number: str
    status: str
    pile_id: str = None
    vehicle: Optional[VehicleWithOwnerResponse] = None
    estimated_completion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

def get_admin_user(current_user: User = Depends(get_current_user)):
    """获取管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

@router.post("/piles/{pile_id}/start", summary="启动充电桩")
def start_charging_pile(
    pile_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """启动充电桩"""
    pile = db.query(ChargingPile).filter(ChargingPile.id == pile_id).first()
    if not pile:
        raise HTTPException(status_code=404, detail="充电桩不存在")
    
    pile.is_active = True
    pile.status = ChargingPileStatus.NORMAL
    db.commit()
    
    return {"message": f"充电桩 {pile.pile_number} 已启动"}

@router.post("/piles/{pile_id}/stop", summary="关闭充电桩")
def stop_charging_pile(
    pile_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """关闭充电桩"""
    pile = db.query(ChargingPile).filter(ChargingPile.id == pile_id).first()
    if not pile:
        raise HTTPException(status_code=404, detail="充电桩不存在")
    
    pile.is_active = False
    pile.status = ChargingPileStatus.OFFLINE
    db.commit()
    
    return {"message": f"充电桩 {pile.pile_number} 已关闭"}

@router.get("/piles", response_model=List[ChargingPileResponse], summary="查看所有充电桩状态")
def get_all_charging_piles(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """查看所有充电桩状态"""
    piles = db.query(ChargingPile).all()
    return piles

@router.get("/piles/{pile_id}/queue", response_model=List[QueueInfoResponse], summary="查看充电桩队列信息")
def get_pile_queue(
    pile_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """查看充电桩等候服务的车辆信息"""
    queue_info = db.query(ChargingQueue).filter(
        ChargingQueue.charging_pile_id == pile_id
    ).all()
    
    return queue_info

@router.get("/reports/daily", summary="获取日报表")
def get_daily_report(
    date: str,  # YYYY-MM-DD格式
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取日报表"""
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # 查询当日充电记录
        records = db.query(ChargingRecord).filter(
            ChargingRecord.created_at >= target_date,
            ChargingRecord.created_at < target_date.replace(day=target_date.day + 1)
        ).all()
        
        # 按充电桩分组统计
        pile_stats = {}
        for record in records:
            pile_number = record.charging_pile.pile_number
            if pile_number not in pile_stats:
                pile_stats[pile_number] = {
                    "charging_count": 0,
                    "charging_duration": 0.0,
                    "charging_amount": 0.0,
                    "electricity_fee": 0.0,
                    "service_fee": 0.0,
                    "total_fee": 0.0
                }
            
            pile_stats[pile_number]["charging_count"] += 1
            pile_stats[pile_number]["charging_duration"] += record.charging_duration
            pile_stats[pile_number]["charging_amount"] += record.charging_amount
            pile_stats[pile_number]["electricity_fee"] += record.electricity_fee
            pile_stats[pile_number]["service_fee"] += record.service_fee
            pile_stats[pile_number]["total_fee"] += record.total_fee
        
        # 转换为响应格式
        report_data = []
        for pile_number, stats in pile_stats.items():
            report_data.append({
                "time_period": date,
                "pile_number": pile_number,
                **stats
            })
        
        return report_data
        
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用YYYY-MM-DD格式")

@router.post("/piles/init", summary="初始化充电桩")
def init_charging_piles(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """初始化充电桩数据"""
    # 检查是否已初始化
    existing_piles = db.query(ChargingPile).count()
    if existing_piles > 0:
        return {"message": "充电桩已初始化"}
    
    from app.models import ChargingMode
    from app.core.config import settings
    
    # 创建快充桩
    for i in range(settings.FAST_CHARGING_PILE_NUM):
        fast_pile = ChargingPile(
            pile_number=f"F{i+1:02d}",
            charging_mode=ChargingMode.FAST,
            power=settings.FAST_CHARGING_POWER,
            status=ChargingPileStatus.NORMAL,
            is_active=True
        )
        db.add(fast_pile)
    
    # 创建慢充桩
    for i in range(settings.TRICKLE_CHARGING_PILE_NUM):
        trickle_pile = ChargingPile(
            pile_number=f"T{i+1:02d}",
            charging_mode=ChargingMode.TRICKLE,
            power=settings.TRICKLE_CHARGING_POWER,
            status=ChargingPileStatus.NORMAL,
            is_active=True
        )
        db.add(trickle_pile)
    
    db.commit()
    
    return {"message": "充电桩初始化完成"}

@router.get("/vehicles", response_model=List[VehicleInfoResponse], summary="查看所有用户车辆")
def get_all_vehicles(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """查看所有用户的车辆信息"""
    vehicles = db.query(Vehicle).join(User).all()
    
    # 转换为响应格式
    result = []
    for vehicle in vehicles:
        result.append({
            "id": vehicle.id,
            "license_plate": vehicle.license_plate,
            "battery_capacity": vehicle.battery_capacity,
            "model": vehicle.model,
            "owner_username": vehicle.owner.username,
            "owner_email": vehicle.owner.email,
            "created_at": vehicle.created_at
        })
    
    return result

@router.get("/queue/summary", summary="获取队列总结信息")
def get_queue_summary(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取队列总结信息"""
    # 获取等待中的队列数量
    waiting_count = db.query(ChargingQueue).filter(
        ChargingQueue.status == QueueStatus.WAITING
    ).count()
    
    # 获取充电中的数量
    charging_count = db.query(ChargingQueue).filter(
        ChargingQueue.status == QueueStatus.CHARGING
    ).count()
    
    # 总排队人数
    total_queues = waiting_count + charging_count
    
    # 计算平均等待时间（简单估算）
    avg_wait_time = waiting_count * 15 if waiting_count > 0 else 0  # 每人平均15分钟
    
    return {
        "total_queues": total_queues,
        "waiting_count": waiting_count,
        "charging_count": charging_count,
        "avg_wait_time": avg_wait_time
    }

@router.post("/piles/{pile_id}/fault", summary="设置充电桩故障")
def set_pile_fault(
    pile_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """设置充电桩故障状态"""
    service = ChargingScheduleService(db)
    try:
        service.handle_pile_fault(pile_id, "priority")
        return {"message": "充电桩故障处理完成"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/queue/piles", response_model=List[PileQueueResponse], summary="获取各充电桩队列状态")
def get_pile_queues(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取各充电桩的队列状态"""
    piles = db.query(ChargingPile).all()
    
    result = []
    for pile in piles:
        # 获取该充电桩的队列 - 修复状态筛选逻辑
        queues = db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile.id,
            ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).order_by(ChargingQueue.queue_time).all()
        
        # 获取当前正在充电的用户
        current_user = None
        charging_queue = db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile.id,
            ChargingQueue.status == QueueStatus.CHARGING
        ).first()
        if charging_queue and charging_queue.user:
            current_user = charging_queue.user.username
        
        # 构建队列详情
        queue_details = []
        for i, queue in enumerate(queues):
            # 安全地获取用户和车辆信息
            username = queue.user.username if queue.user else "未知用户"
            vehicle_info = "未知车辆"
            if queue.vehicle:
                vehicle_info = f"{queue.vehicle.license_plate} ({queue.vehicle.model or '未知型号'})"
            
            queue_details.append({
                "position": i + 1,
                "username": username,
                "vehicle_info": vehicle_info,
                "request_time": queue.queue_time,
                "status": queue.status.value
            })
        
        # 估算等待时间 - 修复状态判断
        queuing_count = len([q for q in queues if q.status == QueueStatus.QUEUING])
        estimated_wait_time = queuing_count * 30  # 每人30分钟
        
        # 确定充电桩的实际状态（基于使用情况）
        actual_pile_status = pile.status.value
        if charging_queue:
            # 如果有车正在充电，状态显示为"充电中"
            actual_pile_status = "charging"
        elif pile.status == ChargingPileStatus.NORMAL and pile.is_active:
            # 正常且激活的充电桩，如果没有人充电则显示为"空闲"
            actual_pile_status = "idle"
        
        result.append(PileQueueResponse(
            pile_id=pile.id,
            pile_name=f"{pile.charging_mode.value}充电桩-{pile.pile_number}",
            pile_status=actual_pile_status,
            queue_length=len(queues),
            current_user=current_user,
            estimated_wait_time=estimated_wait_time,
            queue_details=queue_details
        ))
    
    return result

@router.get("/queue/logs", response_model=List[QueueLogResponse], summary="获取队列变化日志")
def get_queue_logs(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取队列变化日志"""
    try:
        # 这里返回一些模拟的队列变化日志
        # 在实际应用中，你可能需要一个专门的日志表来记录这些操作
        
        current_time = datetime.now()
        
        # 获取最近的一些队列操作 - 使用 joinedload 预加载关联关系
        from sqlalchemy.orm import joinedload
        recent_queues = db.query(ChargingQueue).options(
            joinedload(ChargingQueue.user),
            joinedload(ChargingQueue.pile)
        ).order_by(ChargingQueue.queue_time.desc()).limit(10).all()
        
        logs = []
        for queue in recent_queues:
            # 安全地获取充电桩信息
            pile_name = "未分配充电桩"
            if queue.charging_pile_id:
                pile_name = f"充电桩-{queue.charging_pile_id}"
                if queue.pile:
                    pile_name = f"{queue.pile.charging_mode.value}充电桩-{queue.pile.pile_number}"
            
            # 安全地获取用户信息
            username = "未知用户"
            if queue.user:
                username = queue.user.username
            
            if queue.status == QueueStatus.WAITING:
                action = "加入队列"
                description = f"用户 {username} 加入 {pile_name} 排队"
            elif queue.status == QueueStatus.CHARGING:
                action = "开始充电"
                description = f"用户 {username} 在 {pile_name} 开始充电"
            elif queue.status == QueueStatus.COMPLETED:
                action = "完成充电"
                description = f"用户 {username} 在 {pile_name} 完成充电"
            else:
                action = "状态变化"
                description = f"用户 {username} 在 {pile_name} 状态变为 {queue.status.value}"
            
            logs.append(QueueLogResponse(
                timestamp=queue.queue_time,
                pile_name=pile_name,
                user=username,
                action=action,
                description=description
            ))
        
        return logs
    
    except Exception as e:
        # 如果出现任何错误，返回空列表而不是让服务器崩溃
        print(f"Error in get_queue_logs: {str(e)}")
        return []

@router.get("/scene/vehicles", response_model=List[VehicleWithOwnerResponse], summary="获取所有车辆（包含车主信息）")
def get_vehicles_with_owners(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有车辆及其车主信息，用于充电场景动画"""
    try:
        # 使用joinedload预加载关联数据
        from sqlalchemy.orm import joinedload
        vehicles = db.query(Vehicle).options(joinedload(Vehicle.owner)).all()
        
        result = []
        for vehicle in vehicles:
            try:
                owner_info = None
                if vehicle.owner:
                    owner_info = {
                        "username": vehicle.owner.username,
                        "email": vehicle.owner.email,
                        "phone": getattr(vehicle.owner, 'phone', None)
                    }
                
                vehicle_data = {
                    "id": vehicle.id,
                    "license_plate": vehicle.license_plate,
                    "battery_capacity": vehicle.battery_capacity or 0.0,
                    "model": vehicle.model or "未知型号",
                    "status": "registered",  # 默认状态
                    "owner": owner_info
                }
                result.append(vehicle_data)
            except Exception as e:
                print(f"处理车辆 {vehicle.id} 时出错: {e}")
                continue
        
        return result
    except Exception as e:
        print(f"获取车辆数据时出错: {e}")
        return []

@router.get("/scene/charging-piles", response_model=List[ChargingPileWithSpotsResponse], summary="获取充电桩信息（用于场景动画）")
def get_charging_piles_for_scene(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取充电桩信息，用于充电场景动画"""
    try:
        piles = db.query(ChargingPile).all()
        
        result = []
        for pile in piles:
            try:
                # 安全地获取充电模式
                charging_mode = pile.charging_mode
                if hasattr(charging_mode, 'value'):
                    mode_str = charging_mode.value
                else:
                    mode_str = str(charging_mode)
                
                # 安全地获取状态
                status = pile.status
                if hasattr(status, 'value'):
                    status_str = status.value
                else:
                    status_str = str(status)
                
                pile_data = {
                    "id": pile.id,
                    "pile_id": pile.pile_number,
                    "type": "fast" if mode_str == "fast" else "trickle",
                    "status": status_str,
                    "power": pile.power or 0.0
                }
                result.append(pile_data)
            except Exception as e:
                print(f"处理充电桩 {pile.id} 时出错: {e}")
                continue
        
        return result
    except Exception as e:
        print(f"获取充电桩数据时出错: {e}")
        return []

@router.get("/scene/charging-queue", response_model=List[QueueWithVehicleResponse], summary="获取排队信息（包含车辆详情）")
def get_charging_queue_with_vehicles(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取排队信息及车辆详情，用于充电场景动画"""
    try:
        # 使用joinedload预加载关联数据
        from sqlalchemy.orm import joinedload
        queues = db.query(ChargingQueue).options(
            joinedload(ChargingQueue.vehicle).joinedload(Vehicle.owner),
            joinedload(ChargingQueue.pile)
        ).all()
        
        result = []
        for queue in queues:
            try:
                vehicle_info = None
                if queue.vehicle:
                    owner_info = None
                    if queue.vehicle.owner:
                        owner_info = {
                            "username": queue.vehicle.owner.username,
                            "email": queue.vehicle.owner.email,
                            "phone": getattr(queue.vehicle.owner, 'phone', None)
                        }
                    
                    # 安全地获取队列状态
                    queue_status = queue.status
                    if hasattr(queue_status, 'value'):
                        status_str = queue_status.value
                    else:
                        status_str = str(queue_status)
                    
                    vehicle_info = {
                        "id": queue.vehicle.id,
                        "license_plate": queue.vehicle.license_plate,
                        "battery_capacity": queue.vehicle.battery_capacity or 0.0,
                        "model": queue.vehicle.model or "未知型号",
                        "status": status_str,
                        "owner": owner_info
                    }
                
                # 安全地获取充电桩信息
                pile_id = None
                if queue.pile:
                    pile_id = queue.pile.pile_number
                elif queue.charging_pile_id:
                    # 如果pile关联为空，但有charging_pile_id，尝试查询
                    pile = db.query(ChargingPile).filter(ChargingPile.id == queue.charging_pile_id).first()
                    if pile:
                        pile_id = pile.pile_number
                
                # 安全地获取队列状态
                queue_status = queue.status
                if hasattr(queue_status, 'value'):
                    status_str = queue_status.value
                else:
                    status_str = str(queue_status)
                
                queue_data = {
                    "id": queue.id,
                    "queue_number": queue.queue_number,
                    "status": status_str,
                    "pile_id": pile_id,
                    "vehicle": vehicle_info,
                    "estimated_completion": queue.estimated_completion_time
                }
                result.append(queue_data)
            except Exception as e:
                print(f"处理队列 {queue.id} 时出错: {e}")
                continue
        
        return result
    except Exception as e:
        print(f"获取队列数据时出错: {e}")
        return [] 