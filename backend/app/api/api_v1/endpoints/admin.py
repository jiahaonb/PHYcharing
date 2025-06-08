from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models import User, Vehicle, ChargingPile, ChargingQueue, ChargingRecord, ChargingPileStatus, QueueStatus
from app.services.charging_service import ChargingScheduleService
from app.services.config_service import config_service
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
    charging_mode: Optional[str] = None
    charging_pile_id: Optional[int] = None
    pile_id: Optional[str] = None
    vehicle: Optional[VehicleWithOwnerResponse] = None
    estimated_completion: Optional[datetime] = None
    queue_time: Optional[datetime] = None
    
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
    try:
        # 获取所有活跃的队列（等待中、排队中、充电中）
        active_queues = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).all()
        
        # 分类统计
        waiting_count = 0
        charging_count = 0
        
        for queue in active_queues:
            status = queue.status.value if hasattr(queue.status, 'value') else str(queue.status)
            if status in ['waiting', 'queuing']:
                waiting_count += 1
            elif status == 'charging':
                charging_count += 1
        
        # 总排队人数（等待+充电）
        total_queues = waiting_count + charging_count
        
        # 计算平均等待时间（简单估算）
        avg_wait_time = waiting_count * 15 if waiting_count > 0 else 0  # 每人平均15分钟
        
        print(f"队列统计 - 总计: {total_queues}, 等待: {waiting_count}, 充电: {charging_count}")
        
        return {
            "total_queues": total_queues,
            "waiting_count": waiting_count,
            "charging_count": charging_count,
            "avg_wait_time": avg_wait_time
        }
    except Exception as e:
        print(f"获取队列统计信息失败: {e}")
        return {
            "total_queues": 0,
            "waiting_count": 0,
            "charging_count": 0,
            "avg_wait_time": 0
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
        # 获取该充电桩的活跃队列（等待、排队、充电中）
        queues = db.query(ChargingQueue).filter(
            ChargingQueue.charging_pile_id == pile.id,
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
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
                "queue_id": queue.id,  # 添加queue_id用于管理操作
                "position": i + 1,
                "username": username,
                "vehicle_info": vehicle_info,
                "request_time": queue.queue_time,
                "status": queue.status.value
            })
        
        # 计算等待队列长度（排除正在充电的）
        waiting_queues = [q for q in queues if q.status in [QueueStatus.WAITING, QueueStatus.QUEUING]]
        actual_queue_length = len(waiting_queues)
        estimated_wait_time = actual_queue_length * 30  # 每人30分钟
        
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
            queue_length=actual_queue_length,  # 使用修正后的队列长度
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
        
        # 获取所有排队信息，用于确定车辆状态
        queues = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).all()
        
        # 创建车辆ID到队列状态的映射
        vehicle_status_map = {}
        for queue in queues:
            status = queue.status.value if hasattr(queue.status, 'value') else str(queue.status)
            vehicle_status_map[queue.vehicle_id] = status
        
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
                
                # 根据队列状态确定车辆的实际状态
                current_status = vehicle_status_map.get(vehicle.id, "暂留")
                
                # 状态映射到中文显示
                status_text_map = {
                    "waiting": "等候",
                    "queuing": "等候",
                    "charging": "充电中"
                }
                display_status = status_text_map.get(current_status, "暂留")
                
                # 安全地获取所有字段
                vehicle_data = {
                    "id": vehicle.id,
                    "license_plate": getattr(vehicle, 'license_plate', ''),
                    "battery_capacity": getattr(vehicle, 'battery_capacity', 0.0) or 0.0,
                    "model": getattr(vehicle, 'model', '') or "未知型号",
                    "status": display_status,
                    "owner": owner_info,
                    "created_at": getattr(vehicle, 'created_at', None)
                }
                
                result.append(vehicle_data)
                
            except Exception as e:
                print(f"处理车辆 {vehicle.id} 时出错: {e}")
                continue
        
        return result
        
    except Exception as e:
        print(f"获取车辆数据时出错: {e}")
        return []

@router.post("/piles/sync-config", summary="同步充电桩配置")
def sync_pile_config(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """同步充电桩配置，从数据库配置更新充电桩功率"""
    try:
        # 获取最新配置
        charging_config = config_service.get_charging_pile_config(db)
        
        # 获取所有充电桩
        piles = db.query(ChargingPile).all()
        
        updated_count = 0
        for pile in piles:
            try:
                charging_mode = pile.charging_mode
                if hasattr(charging_mode, 'value'):
                    mode_str = charging_mode.value
                else:
                    mode_str = str(charging_mode)
                
                # 根据模式更新功率
                if mode_str == "fast":
                    new_power = charging_config["fast_charging_power"]
                else:
                    new_power = charging_config["trickle_charging_power"]
                
                if pile.power != new_power:
                    pile.power = new_power
                    updated_count += 1
                    print(f"充电桩 {pile.pile_number} 功率更新：{pile.power} -> {new_power}")
                    
            except Exception as e:
                print(f"更新充电桩 {pile.id} 功率失败: {e}")
                continue
        
        if updated_count > 0:
            db.commit()
        
        return {
            "message": "充电桩配置同步完成",
            "updated_count": updated_count,
            "total_piles": len(piles),
            "config": charging_config
        }
        
    except Exception as e:
        print(f"同步充电桩配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步配置失败: {str(e)}")

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
                
                # 安全地获取充电模式
                charging_mode = queue.charging_mode
                if hasattr(charging_mode, 'value'):
                    mode_str = charging_mode.value
                else:
                    mode_str = str(charging_mode)
                
                queue_data = {
                    "id": queue.id,
                    "queue_number": queue.queue_number,
                    "status": status_str,
                    "charging_mode": mode_str,
                    "charging_pile_id": queue.charging_pile_id,
                    "pile_id": pile_id,
                    "vehicle": vehicle_info,
                    "estimated_completion": queue.estimated_completion_time,
                    "queue_time": queue.queue_time
                }
                result.append(queue_data)
            except Exception as e:
                print(f"处理队列 {queue.id} 时出错: {e}")
                continue
        
        return result
    except Exception as e:
        print(f"获取队列数据时出错: {e}")
        return []

@router.post("/piles/auto-configure", summary="根据系统配置自动配置充电桩")
def auto_configure_piles(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """根据系统配置自动配置充电桩数量和功率"""
    try:
        # 获取最新配置
        pile_config = config_service.get_charging_pile_config(db)
        fast_count = int(pile_config["fast_charging_pile_num"])
        trickle_count = int(pile_config["trickle_charging_pile_num"])
        fast_power = pile_config["fast_charging_power"]
        trickle_power = pile_config["trickle_charging_power"]
        
        # 获取现有充电桩
        existing_piles = db.query(ChargingPile).all()
        existing_fast = [p for p in existing_piles if p.charging_mode.value == "fast"]
        existing_trickle = [p for p in existing_piles if p.charging_mode.value == "trickle"]
        
        from app.models import ChargingMode, ChargingPileStatus
        
        actions = []
        
        # 处理快充桩
        if len(existing_fast) < fast_count:
            # 需要添加快充桩
            for i in range(len(existing_fast), fast_count):
                pile_number = f"F{i+1:02d}"
                # 确保编号不重复
                while db.query(ChargingPile).filter(ChargingPile.pile_number == pile_number).first():
                    i += 1
                    pile_number = f"F{i+1:02d}"
                
                new_pile = ChargingPile(
                    pile_number=pile_number,
                    charging_mode=ChargingMode.FAST,
                    power=fast_power,
                    status=ChargingPileStatus.NORMAL,
                    is_active=True
                )
                db.add(new_pile)
                actions.append(f"添加快充桩 {pile_number} (功率: {fast_power}kW)")
                
        elif len(existing_fast) > fast_count:
            # 需要删除快充桩（删除最新的几个）
            to_remove = existing_fast[fast_count:]
            for pile in to_remove:
                # 检查是否有排队或充电中的任务
                active_queues = db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
                ).count()
                
                if active_queues > 0:
                    actions.append(f"无法删除快充桩 {pile.pile_number}：有活跃任务")
                else:
                    db.delete(pile)
                    actions.append(f"删除快充桩 {pile.pile_number}")
        
        # 处理慢充桩
        if len(existing_trickle) < trickle_count:
            # 需要添加慢充桩
            for i in range(len(existing_trickle), trickle_count):
                pile_number = f"T{i+1:02d}"
                # 确保编号不重复
                while db.query(ChargingPile).filter(ChargingPile.pile_number == pile_number).first():
                    i += 1
                    pile_number = f"T{i+1:02d}"
                
                new_pile = ChargingPile(
                    pile_number=pile_number,
                    charging_mode=ChargingMode.TRICKLE,
                    power=trickle_power,
                    status=ChargingPileStatus.NORMAL,
                    is_active=True
                )
                db.add(new_pile)
                actions.append(f"添加慢充桩 {pile_number} (功率: {trickle_power}kW)")
                
        elif len(existing_trickle) > trickle_count:
            # 需要删除慢充桩
            to_remove = existing_trickle[trickle_count:]
            for pile in to_remove:
                # 检查是否有排队或充电中的任务
                active_queues = db.query(ChargingQueue).filter(
                    ChargingQueue.charging_pile_id == pile.id,
                    ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
                ).count()
                
                if active_queues > 0:
                    actions.append(f"无法删除慢充桩 {pile.pile_number}：有活跃任务")
                else:
                    db.delete(pile)
                    actions.append(f"删除慢充桩 {pile.pile_number}")
        
        # 更新现有充电桩的功率
        for pile in existing_piles:
            if pile.charging_mode.value == "fast" and pile.power != fast_power:
                pile.power = fast_power
                actions.append(f"更新快充桩 {pile.pile_number} 功率：{pile.power} -> {fast_power}kW")
            elif pile.charging_mode.value == "trickle" and pile.power != trickle_power:
                pile.power = trickle_power
                actions.append(f"更新慢充桩 {pile.pile_number} 功率：{pile.power} -> {trickle_power}kW")
        
        db.commit()
        
        # 获取最终状态
        final_piles = db.query(ChargingPile).all()
        final_fast_count = len([p for p in final_piles if p.charging_mode.value == "fast"])
        final_trickle_count = len([p for p in final_piles if p.charging_mode.value == "trickle"])
        
        return {
            "message": "充电桩自动配置完成",
            "target_config": {
                "fast_piles": fast_count,
                "trickle_piles": trickle_count,
                "fast_power": fast_power,
                "trickle_power": trickle_power
            },
            "final_status": {
                "fast_piles": final_fast_count,
                "trickle_piles": final_trickle_count,
                "total_piles": len(final_piles)
            },
            "actions": actions
        }
        
    except Exception as e:
        print(f"自动配置充电桩失败: {e}")
        raise HTTPException(status_code=500, detail=f"自动配置失败: {str(e)}")

@router.get("/users", response_model=List[dict])
async def get_all_users(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有用户列表（管理员功能）
    """
    users = db.query(User).all()
    
    result = []
    for user in users:
        # 获取用户的车辆数量
        vehicle_count = db.query(Vehicle).filter(Vehicle.owner_id == user.id).count()
        
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": getattr(user, 'phone', None),
            "is_admin": user.is_admin,
            "is_active": getattr(user, 'is_active', True),
            "created_at": user.created_at,
            "vehicle_count": vehicle_count
        })
    
    return result

@router.get("/users/{user_id}/detail", response_model=dict)
async def get_user_detail(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取用户详细信息（管理员功能）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户的车辆
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == user_id).all()
    
    # 获取用户的充电记录统计
    charging_records = db.query(ChargingRecord).filter(ChargingRecord.user_id == user_id).all()
    
    # 计算统计信息
    charging_count = len(charging_records)
    total_energy = sum(record.charging_amount or 0 for record in charging_records)
    total_cost = sum(record.total_fee or 0 for record in charging_records)
    
    # 获取最近的充电记录（最多5条）
    recent_records = db.query(ChargingRecord)\
        .filter(ChargingRecord.user_id == user_id)\
        .order_by(ChargingRecord.start_time.desc())\
        .limit(5)\
        .all()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": getattr(user, 'phone', None),
        "is_admin": user.is_admin,
        "is_active": getattr(user, 'is_active', True),
        "created_at": user.created_at,
        "vehicle_count": len(vehicles),
        "charging_count": charging_count,
        "total_energy": total_energy,
        "total_cost": total_cost,
        "vehicles": [
            {
                "id": vehicle.id,
                "license_plate": vehicle.license_plate,
                "model": getattr(vehicle, 'model', None),
                "battery_capacity": vehicle.battery_capacity,
                "created_at": vehicle.created_at
            }
            for vehicle in vehicles
        ],
        "recent_records": [
            {
                "id": record.id,
                "record_number": record.record_number,
                "charging_amount": record.charging_amount,
                "total_fee": record.total_fee,
                "start_time": record.start_time,
                "end_time": record.end_time
            }
            for record in recent_records
        ]
    }

@router.put("/users/{user_id}/status", response_model=dict)
async def update_user_status(
    user_id: int,
    status_data: dict,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新用户状态（管理员功能）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新is_active字段（如果用户模型有这个字段）
    if hasattr(user, 'is_active'):
        user.is_active = status_data.get('is_active', True)
        db.commit()
        db.refresh(user)
    
    return {"message": "用户状态更新成功", "user_id": user_id}

@router.delete("/queue/{queue_id}/cancel", summary="取消排队")
async def cancel_queue(
    queue_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理员取消排队中的车辆
    """
    # 查找排队记录
    queue = db.query(ChargingQueue).filter(ChargingQueue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="排队记录不存在")
    
    # 检查状态是否可以取消
    if queue.status != QueueStatus.QUEUING:
        raise HTTPException(
            status_code=400, 
            detail=f"无法取消：当前状态为 {queue.status.value}"
        )
    
    # 获取车辆和用户信息用于日志
    vehicle = db.query(Vehicle).filter(Vehicle.id == queue.vehicle_id).first()
    user = db.query(User).filter(User.id == queue.user_id).first()
    
    vehicle_info = f"{vehicle.license_plate}" if vehicle else f"车辆ID:{queue.vehicle_id}"
    user_info = f"{user.username}" if user else f"用户ID:{queue.user_id}"
    
    # 删除排队记录
    db.delete(queue)
    db.commit()
    
    return {
        "message": f"已取消 {user_info} 的车辆 {vehicle_info} 的排队",
        "queue_id": queue_id,
        "action": "cancelled"
    }

@router.post("/queue/{queue_id}/stop-charging", summary="停止充电")
async def stop_charging(
    queue_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理员强制停止正在充电的车辆
    """
    # 查找充电记录
    queue = db.query(ChargingQueue).filter(ChargingQueue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="充电记录不存在")
    
    # 检查状态是否为充电中
    if queue.status != QueueStatus.CHARGING:
        raise HTTPException(
            status_code=400, 
            detail=f"无法停止：当前状态为 {queue.status.value}"
        )
    
    # 获取车辆和用户信息用于响应
    vehicle = db.query(Vehicle).filter(Vehicle.id == queue.vehicle_id).first()
    user = db.query(User).filter(User.id == queue.user_id).first()
    charging_pile = db.query(ChargingPile).filter(ChargingPile.id == queue.charging_pile_id).first()
    
    vehicle_info = f"{vehicle.license_plate}" if vehicle else f"车辆ID:{queue.vehicle_id}"
    user_info = f"{user.username}" if user else f"用户ID:{queue.user_id}"
    pile_info = f"{charging_pile.pile_number}" if charging_pile else f"充电桩ID:{queue.charging_pile_id}"
    
    try:
        # 使用充电服务来完成充电
        from app.services.charging_service import ChargingScheduleService
        charging_service = ChargingScheduleService(db)
        
        # 调用完成充电方法
        charging_record = charging_service.complete_charging(queue_id)
        
        return {
            "message": f"已强制停止 {user_info} 的车辆 {vehicle_info} 在 {pile_info} 的充电",
            "queue_id": queue_id,
            "action": "stopped",
            "charging_record": {
                "record_number": charging_record.record_number,
                "duration_hours": round(charging_record.charging_duration, 2),
                "amount_kwh": round(charging_record.charging_amount, 2),
                "total_fee": round(charging_record.total_fee, 2)
            }
        }
        
    except Exception as e:
        print(f"停止充电失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止充电失败: {str(e)}")

@router.get("/queue/active", summary="获取所有活跃队列")
async def get_active_queues(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取所有排队中和充电中的记录（用于管理操作）
    """
    queues = db.query(ChargingQueue).filter(
        ChargingQueue.status.in_([QueueStatus.QUEUING, QueueStatus.CHARGING])
    ).all()
    
    result = []
    for queue in queues:
        vehicle = db.query(Vehicle).filter(Vehicle.id == queue.vehicle_id).first()
        user = db.query(User).filter(User.id == queue.user_id).first()
        charging_pile = db.query(ChargingPile).filter(ChargingPile.id == queue.charging_pile_id).first()
        
        result.append({
            "id": queue.id,
            "queue_number": queue.queue_number,
            "status": queue.status.value,
            "user": {
                "id": user.id if user else None,
                "username": user.username if user else "未知用户"
            },
            "vehicle": {
                "id": vehicle.id if vehicle else None,
                "license_plate": vehicle.license_plate if vehicle else "未知车辆"
            },
            "charging_pile": {
                "id": charging_pile.id if charging_pile else None,
                "pile_number": charging_pile.pile_number if charging_pile else None
            },
            "queue_time": queue.queue_time,
            "start_charging_time": queue.start_charging_time,
            "requested_amount": queue.requested_amount
        })
    
    return result

@router.get("/users/{user_id}/charging-orders", summary="获取用户充电详单")
async def get_user_charging_orders(
    user_id: int,
    limit: int = 10,
    offset: int = 0,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取指定用户的充电详单记录
    """
    # 验证用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取充电记录，按创建时间倒序排列
    charging_records = db.query(ChargingRecord)\
        .filter(ChargingRecord.user_id == user_id)\
        .order_by(ChargingRecord.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    # 格式化返回数据
    result = []
    for record in charging_records:
        # 获取关联的车辆和充电桩信息
        vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
        charging_pile = db.query(ChargingPile).filter(ChargingPile.id == record.charging_pile_id).first()
        
        result.append({
            "id": record.id,
            "record_number": record.record_number,
            "status": record.status if hasattr(record, 'status') else 'completed',
            "charging_amount": record.charging_amount,
            "charging_duration": record.charging_duration,
            "charging_mode": record.charging_mode,
            "start_time": record.start_time,
            "end_time": record.end_time,
            "electricity_fee": record.electricity_fee,
            "service_fee": record.service_fee,
            "total_fee": record.total_fee,
            "unit_price": record.unit_price,
            "time_period": record.time_period,
            "created_at": record.created_at,
            "vehicle": {
                "id": vehicle.id if vehicle else None,
                "license_plate": vehicle.license_plate if vehicle else "未知车辆",
                "model": getattr(vehicle, 'model', None) if vehicle else None
            } if vehicle else None,
            "charging_pile": {
                "id": charging_pile.id if charging_pile else None,
                "pile_number": charging_pile.pile_number if charging_pile else "未知充电桩"
            } if charging_pile else None
        })
    
    # 获取总记录数
    total_count = db.query(ChargingRecord).filter(ChargingRecord.user_id == user_id).count()
    
    return {
        "data": result,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }

@router.get("/vehicles/{vehicle_id}/detail", summary="获取车辆详细信息（管理端）")
async def get_vehicle_detail_admin(
    vehicle_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    管理员获取任意车辆的详细信息，包括车主信息、当前队列状态、历史充电记录
    """
    try:
        from sqlalchemy.orm import joinedload
        from app.models import Vehicle, ChargingQueue, ChargingRecord, QueueStatus
        
        # 获取车辆信息（管理员可以查看任意车辆）
        vehicle = db.query(Vehicle).options(joinedload(Vehicle.owner)).filter(
            Vehicle.id == vehicle_id
        ).first()
        
        if not vehicle:
            raise HTTPException(status_code=404, detail="车辆不存在")
        
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
        
        # 获取充电桩信息
        charging_pile_info = None
        if current_queue and current_queue.charging_pile_id:
            charging_pile = db.query(ChargingPile).filter(
                ChargingPile.id == current_queue.charging_pile_id
            ).first()
            if charging_pile:
                charging_pile_info = {
                    "id": charging_pile.id,
                    "pile_number": charging_pile.pile_number,
                    "charging_mode": charging_pile.charging_mode.value if hasattr(charging_pile.charging_mode, 'value') else str(charging_pile.charging_mode),
                    "power": charging_pile.power,
                    "status": charging_pile.status.value if hasattr(charging_pile.status, 'value') else str(charging_pile.status)
                }
        
        # 构建响应数据
        result = {
            "id": vehicle.id,
            "license_plate": vehicle.license_plate,
            "battery_capacity": vehicle.battery_capacity or 0.0,
            "model": vehicle.model or "未知型号",
            "status": display_status,
            "status_code": current_status,
            "owner": {
                "id": vehicle.owner.id if vehicle.owner else None,
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
                    "total_fee": record.total_fee,
                    "charging_mode": record.charging_mode,
                    "electricity_fee": record.electricity_fee,
                    "service_fee": record.service_fee,
                    "unit_price": record.unit_price,
                    "time_period": record.time_period
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
                "start_charging_time": current_queue.start_charging_time,
                "estimated_completion_time": current_queue.estimated_completion_time,
                "charging_pile": charging_pile_info,
                "status": current_queue.status.value if hasattr(current_queue.status, 'value') else str(current_queue.status)
            }
        
        return {"status": "success", "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取车辆详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queue/{queue_id}/detail", response_model=dict, summary="获取队列详细信息（包括关联的充电记录）")
async def get_queue_detail(
    queue_id: int, 
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取队列详细信息（包括关联的充电记录）"""
    try:
        # 查找队列记录
        queue_record = db.query(ChargingQueue).filter(ChargingQueue.id == queue_id).first()
        if not queue_record:
            return {"success": False, "error": "Queue not found"}
        
        # 查找关联的充电记录
        charging_record = db.query(ChargingRecord).filter(
            ChargingRecord.queue_number == queue_record.queue_number
        ).first()
        
        result = {
            "success": True,
            "queue": {
                "id": queue_record.id,
                "queue_number": queue_record.queue_number,
                "user_id": queue_record.user_id,
                "vehicle_id": queue_record.vehicle_id,
                "charging_mode": queue_record.charging_mode.value if hasattr(queue_record.charging_mode, 'value') else str(queue_record.charging_mode),
                "requested_amount": queue_record.requested_amount,
                "status": queue_record.status.value if hasattr(queue_record.status, 'value') else str(queue_record.status),
                "queue_time": queue_record.queue_time,
                "estimated_wait_time": queue_record.estimated_wait_time,
                "charging_pile_id": queue_record.charging_pile_id,
                "start_charging_time": queue_record.start_charging_time,
                "estimated_completion_time": queue_record.estimated_completion_time,
                "created_at": queue_record.created_at
            }
        }
        
        # 如果有关联的充电记录，添加到返回结果中
        if charging_record:
            result["charging_record"] = {
                "record_number": charging_record.record_number,
                "queue_number": charging_record.queue_number,
                "license_plate": charging_record.license_plate,
                "charging_mode": charging_record.charging_mode,
                "charging_amount": charging_record.charging_amount,
                "status": charging_record.status,
                "created_at": charging_record.created_at,
                "start_time": charging_record.start_time,
                "end_time": charging_record.end_time,
                "charging_duration": charging_record.charging_duration,
                "electricity_fee": charging_record.electricity_fee,
                "service_fee": charging_record.service_fee,
                "total_fee": charging_record.total_fee,
                "unit_price": charging_record.unit_price,
                "time_period": charging_record.time_period,
                "charging_pile_id": charging_record.charging_pile_id
            }
        
        return result
    except Exception as e:
        print(f"获取队列详细信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vehicle/{vehicle_id}/order", response_model=dict, summary="获取车辆订单信息")
async def get_vehicle_order(
    vehicle_id: int, 
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取车辆订单信息"""
    try:
        # 查找该车辆最新的充电记录
        charging_record = db.query(ChargingRecord).filter(
            ChargingRecord.vehicle_id == vehicle_id
        ).order_by(ChargingRecord.created_at.desc()).first()
        
        if charging_record:
            return {
                "success": True,
                "order": {
                    "record_number": charging_record.record_number,
                    "queue_number": charging_record.queue_number,
                    "license_plate": charging_record.license_plate,
                    "charging_mode": charging_record.charging_mode,
                    "charging_amount": charging_record.charging_amount,
                    "status": charging_record.status,
                    "created_at": charging_record.created_at,
                    "start_time": charging_record.start_time,
                    "end_time": charging_record.end_time,
                    "charging_duration": charging_record.charging_duration,
                    "electricity_fee": charging_record.electricity_fee,
                    "service_fee": charging_record.service_fee,
                    "total_fee": charging_record.total_fee,
                    "unit_price": charging_record.unit_price,
                    "time_period": charging_record.time_period,
                    "charging_pile_id": charging_record.charging_pile_id
                }
            }
        else:
            return {"success": False, "error": "No order found"}
    except Exception as e:
        print(f"获取车辆订单失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))