"""
一次性清理脚本：清除所有排队和充电的车辆数据
解决数据结构变更后的残留数据问题
"""

from app.core.database import get_db
from app.models import ChargingQueue, ChargingRecord, ChargingPile, QueueStatus, ChargingPileStatus
from sqlalchemy.orm import Session

def clean_charging_data():
    """清理所有充电相关数据"""
    
    db = next(get_db())
    
    try:
        print("🧹 开始清理充电系统数据...")
        
        # 1. 查看当前数据状态
        print("\n📊 当前数据状态：")
        
        total_queues = db.query(ChargingQueue).count()
        waiting_queues = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.WAITING).count()
        queuing_queues = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.QUEUING).count()
        charging_queues = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.CHARGING).count()
        completed_queues = db.query(ChargingQueue).filter(ChargingQueue.status == QueueStatus.COMPLETED).count()
        
        print(f"  总排队记录: {total_queues}")
        print(f"  等候中: {waiting_queues}")
        print(f"  排队中: {queuing_queues}")
        print(f"  充电中: {charging_queues}")
        print(f"  已完成: {completed_queues}")
        
        total_records = db.query(ChargingRecord).count()
        print(f"  充电记录: {total_records}")
        
        # 2. 清除正在进行的排队和充电数据
        print("\n🗑️  清除正在进行的排队和充电数据...")
        
        # 删除等候、排队、充电中的队列记录
        active_statuses = [QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING]
        active_queues = db.query(ChargingQueue).filter(ChargingQueue.status.in_(active_statuses)).all()
        
        print(f"  找到 {len(active_queues)} 条活跃排队记录")
        
        for queue in active_queues:
            print(f"    删除排队记录: {queue.queue_number} ({queue.status.value})")
            
            # 同时删除对应的充电记录（如果存在）
            related_record = db.query(ChargingRecord).filter(
                ChargingRecord.queue_number == queue.queue_number
            ).first()
            
            if related_record:
                print(f"      删除关联充电记录: {related_record.record_number}")
                db.delete(related_record)
            
            db.delete(queue)
        
        # 3. 重置所有充电桩状态为正常
        print("\n🔋 重置充电桩状态...")
        
        all_piles = db.query(ChargingPile).all()
        reset_count = 0
        
        for pile in all_piles:
            if pile.status != ChargingPileStatus.NORMAL:
                print(f"  重置充电桩 {pile.pile_number}: {pile.status.value} -> normal")
                pile.status = ChargingPileStatus.NORMAL
                reset_count += 1
        
        print(f"  重置了 {reset_count} 个充电桩状态")
        
        # 4. 提交所有更改
        db.commit()
        print("\n✅ 数据清理完成！")
        
        # 5. 验证清理结果
        print("\n📊 清理后数据状态：")
        remaining_queues = db.query(ChargingQueue).count()
        remaining_active = db.query(ChargingQueue).filter(
            ChargingQueue.status.in_([QueueStatus.WAITING, QueueStatus.QUEUING, QueueStatus.CHARGING])
        ).count()
        
        print(f"  剩余排队记录: {remaining_queues}")
        print(f"  活跃排队记录: {remaining_active}")
        
        if remaining_active == 0:
            print("🎉 所有活跃排队和充电数据已清除！")
        else:
            print("⚠️  仍有活跃记录未清除")
            
        # 显示充电桩状态
        normal_piles = db.query(ChargingPile).filter(ChargingPile.status == ChargingPileStatus.NORMAL).count()
        total_piles = db.query(ChargingPile).count()
        print(f"  充电桩状态: {normal_piles}/{total_piles} 正常")
        
    except Exception as e:
        print(f"❌ 清理过程中出错: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def clean_all_data():
    """完全清空所有充电数据（包括历史记录）"""
    
    db = next(get_db())
    
    try:
        print("🧹 完全清空所有充电数据...")
        
        # 删除所有充电记录
        record_count = db.query(ChargingRecord).count()
        if record_count > 0:
            db.query(ChargingRecord).delete()
            print(f"  删除了 {record_count} 条充电记录")
        
        # 删除所有排队记录
        queue_count = db.query(ChargingQueue).count()
        if queue_count > 0:
            db.query(ChargingQueue).delete()
            print(f"  删除了 {queue_count} 条排队记录")
        
        # 重置所有充电桩状态
        all_piles = db.query(ChargingPile).all()
        for pile in all_piles:
            pile.status = ChargingPileStatus.NORMAL
            pile.total_charging_count = 0
            pile.total_charging_duration = 0.0
            pile.total_charging_amount = 0.0
        
        print(f"  重置了 {len(all_piles)} 个充电桩状态和统计数据")
        
        db.commit()
        print("✅ 所有充电数据已清空！")
        
    except Exception as e:
        print(f"❌ 清空过程中出错: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        print("⚠️  警告：将清空所有充电数据（包括历史记录）")
        confirm = input("确认操作？(yes/no): ")
        if confirm.lower() == 'yes':
            clean_all_data()
        else:
            print("操作已取消")
    else:
        print("清理活跃的排队和充电数据...")
        clean_charging_data()
        print("\n💡 如需清空所有数据（包括历史），请使用: python clean_charging_data.py --all")