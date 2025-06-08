from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.models import User, ChargingQueue, ChargingRecord, ChargingMode, QueueStatus
from app.services.charging_service import ChargingScheduleService
from .auth import get_current_user

router = APIRouter()

class ChargingRequest(BaseModel):
    vehicle_id: int
    charging_mode: str  # "fast" or "trickle"
    requested_amount: float

class QueueResponse(BaseModel):
    id: int
    queue_number: str
    charging_mode: str
    requested_amount: float
    status: str
    queue_time: datetime
    estimated_completion_time: datetime = None
    
    class Config:
        from_attributes = True

class ChargingRecordResponse(BaseModel):
    id: int
    record_number: str
    queue_number: str
    license_plate: str
    charging_amount: float
    charging_duration: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    electricity_fee: float
    service_fee: float
    total_fee: float
    unit_price: Optional[float] = None
    time_period: Optional[str] = None
    charging_mode: str
    status: str = "created"
    created_at: datetime
    
    class Config:
        from_attributes = True

class ModifyRequest(BaseModel):
    charging_mode: str = None
    requested_amount: float = None

@router.post("/request", response_model=dict, summary="提交充电请求")
def submit_charging_request(
    request: ChargingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交充电请求"""
    try:
        # 转换充电模式
        charging_mode = ChargingMode.FAST if request.charging_mode == "fast" else ChargingMode.TRICKLE
        
        # 创建调度服务
        service = ChargingScheduleService(db)
        
        # 提交请求
        queue_number = service.submit_charging_request(
            user_id=current_user.id,
            vehicle_id=request.vehicle_id,
            charging_mode=charging_mode,
            requested_amount=request.requested_amount
        )
        
        return {"message": "充电请求提交成功", "queue_number": queue_number}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/queue", response_model=List[QueueResponse], summary="查看排队状态")
def get_user_queue(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查看用户的排队状态"""
    queues = db.query(ChargingQueue).filter(
        ChargingQueue.user_id == current_user.id,
        ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
    ).all()
    
    return queues

@router.get("/queue/{queue_id}", response_model=QueueResponse, summary="查看特定排队信息")
def get_queue_info(
    queue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查看特定排队信息"""
    queue = db.query(ChargingQueue).filter(
        ChargingQueue.id == queue_id,
        ChargingQueue.user_id == current_user.id
    ).first()
    
    if not queue:
        raise HTTPException(status_code=404, detail="排队记录不存在")
    
    return queue

@router.get("/waiting-count/{charging_mode}", summary="查看排队等待数量")
def get_waiting_count(
    charging_mode: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查看指定充电模式的等待数量"""
    mode = ChargingMode.FAST if charging_mode == "fast" else ChargingMode.TRICKLE
    
    count = db.query(ChargingQueue).filter(
        ChargingQueue.charging_mode == mode,
        ChargingQueue.status == QueueStatus.WAITING
    ).count()
    
    return {"charging_mode": charging_mode, "waiting_count": count}

@router.put("/modify/{queue_id}", summary="修改充电请求")
def modify_charging_request(
    queue_id: int,
    request: ModifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改充电请求"""
    try:
        # 验证队列记录属于当前用户
        queue = db.query(ChargingQueue).filter(
            ChargingQueue.id == queue_id,
            ChargingQueue.user_id == current_user.id
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="排队记录不存在")
        
        service = ChargingScheduleService(db)
        
        new_mode = None
        if request.charging_mode:
            new_mode = ChargingMode.FAST if request.charging_mode == "fast" else ChargingMode.TRICKLE
        
        service.modify_charging_request(
            queue_id=queue_id,
            new_mode=new_mode,
            new_amount=request.requested_amount
        )
        
        return {"message": "充电请求修改成功"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/cancel/{queue_id}", summary="取消充电")
def cancel_charging(
    queue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消充电"""
    try:
        # 验证队列记录属于当前用户
        queue = db.query(ChargingQueue).filter(
            ChargingQueue.id == queue_id,
            ChargingQueue.user_id == current_user.id
        ).first()
        
        if not queue:
            raise HTTPException(status_code=404, detail="排队记录不存在")
        
        service = ChargingScheduleService(db)
        service.cancel_charging(queue_id)
        
        return {"message": "充电已取消"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/records", response_model=List[ChargingRecordResponse], summary="查看充电详单")
def get_charging_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查看用户的充电详单"""
    try:
        # 检查表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'charging_records' not in tables:
            print("充电记录表不存在，返回空列表")
            return []
        
        records = db.query(ChargingRecord).filter(
            ChargingRecord.user_id == current_user.id
        ).order_by(ChargingRecord.created_at.desc()).all()
        
        return records or []
        
    except Exception as e:
        print(f"获取充电记录时出错: {e}")
        import traceback
        traceback.print_exc()
        # 如果查询失败，返回空列表而不是抛出异常
        return []

@router.get("/records/{record_id}", response_model=ChargingRecordResponse, summary="查看特定充电详单")
def get_charging_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查看特定充电详单"""
    record = db.query(ChargingRecord).filter(
        ChargingRecord.id == record_id,
        ChargingRecord.user_id == current_user.id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="充电记录不存在")
    
    return record 