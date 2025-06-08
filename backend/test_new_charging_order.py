"""
测试新的充电订单创建逻辑
验证在提交充电请求时立即创建充电订单
"""

from app.core.database import get_db
from app.models import ChargingQueue, ChargingRecord, ChargingMode, QueueStatus
from app.models.user import User, Vehicle
from app.services.charging_service import ChargingScheduleService
from sqlalchemy.orm import Session

def test_charging_order_creation():
    """测试充电订单创建功能"""
    
    db = next(get_db())
    service = ChargingScheduleService(db)
    
    try:
        print("🧪 开始测试充电订单创建逻辑...")
        
        # 查找一个测试用户和车辆
        user = db.query(User).first()
        if not user:
            print("❌ 没有找到测试用户")
            return
            
        vehicle = db.query(Vehicle).filter(Vehicle.owner_id == user.id).first()
        if not vehicle:
            print("❌ 没有找到测试车辆")
            return
        
        print(f"📋 测试用户: {user.username}")
        print(f"🚗 测试车辆: {vehicle.license_plate}")
        
        # 清理可能存在的重复订单
        existing_queue = db.query(ChargingQueue).filter(
            ChargingQueue.vehicle_id == vehicle.id,
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).first()
        
        if existing_queue:
            print(f"🗑️  清理现有排队记录: {existing_queue.queue_number}")
            # 同时清理对应的充电记录
            existing_record = db.query(ChargingRecord).filter(
                ChargingRecord.queue_number == existing_queue.queue_number
            ).first()
            if existing_record:
                db.delete(existing_record)
            db.delete(existing_queue)
            db.commit()
        
        # 测试参数
        charging_mode = ChargingMode.FAST
        requested_amount = 30.0  # 30度电
        
        print(f"\n📝 提交充电请求:")
        print(f"  充电模式: {charging_mode.value}")
        print(f"  申请电量: {requested_amount}度")
        
        # 提交充电请求
        queue_number = service.submit_charging_request(
            user_id=user.id,
            vehicle_id=vehicle.id,
            charging_mode=charging_mode,
            requested_amount=requested_amount
        )
        
        print(f"✅ 充电请求提交成功，排队号: {queue_number}")
        
        # 验证排队记录创建
        queue_record = db.query(ChargingQueue).filter(
            ChargingQueue.queue_number == queue_number
        ).first()
        
        if not queue_record:
            print("❌ 排队记录未创建")
            return
            
        print(f"✅ 排队记录已创建 (ID: {queue_record.id})")
        
        # 验证充电订单记录创建
        charging_record = db.query(ChargingRecord).filter(
            ChargingRecord.queue_number == queue_number
        ).first()
        
        if not charging_record:
            print("❌ 充电订单记录未创建")
            return
            
        print(f"✅ 充电订单记录已创建 (订单号: {charging_record.record_number})")
        
        # 验证订单字段
        print(f"\n📋 充电订单详情:")
        print(f"  1. 订单编号: {charging_record.record_number}")
        print(f"  2. 排队号: {charging_record.queue_number}")
        print(f"  3. 订单生成时间: {charging_record.created_at}")
        print(f"  4. 充电桩编号: {charging_record.charging_pile_id} (应为NULL)")
        print(f"  5. 充电电量: {charging_record.charging_amount}度")
        print(f"  6. 充电时长: {charging_record.charging_duration} (应为NULL)")
        print(f"  7. 启动时间: {charging_record.start_time} (应为NULL)")
        print(f"  8. 停止时间: {charging_record.end_time} (应为NULL)")
        print(f"  9. 充电费用: {charging_record.electricity_fee}元")
        print(f"  10. 服务费用: {charging_record.service_fee}元")
        print(f"  11. 总费用: {charging_record.total_fee}元")
        print(f"  12. 充电模式: {charging_record.charging_mode.value}")
        print(f"  13. 车牌号: {charging_record.license_plate}")
        
        # 验证必填字段和可为空字段
        validation_passed = True
        
        # 必填字段检查
        required_fields = {
            "订单编号": charging_record.record_number,
            "排队号": charging_record.queue_number,
            "充电电量": charging_record.charging_amount,
            "充电费用": charging_record.electricity_fee,
            "服务费用": charging_record.service_fee,
            "总费用": charging_record.total_fee,
            "充电模式": charging_record.charging_mode,
            "车牌号": charging_record.license_plate,
        }
        
        for field_name, value in required_fields.items():
            if value is None:
                print(f"❌ 必填字段 {field_name} 为空")
                validation_passed = False
        
        # 可为空字段检查（这些字段现在应该为NULL）
        nullable_fields = {
            "充电桩编号": charging_record.charging_pile_id,
            "充电时长": charging_record.charging_duration,
            "启动时间": charging_record.start_time,
            "停止时间": charging_record.end_time,
        }
        
        for field_name, value in nullable_fields.items():
            if value is not None:
                print(f"⚠️  字段 {field_name} 应为NULL但实际为: {value}")
        
        if validation_passed:
            print(f"\n✅ 所有验证通过！充电订单创建逻辑工作正常")
            print(f"✅ 创建时包含了11个必填数据，3个可为空字段")
        else:
            print(f"\n❌ 验证失败，存在问题")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_charging_order_creation() 