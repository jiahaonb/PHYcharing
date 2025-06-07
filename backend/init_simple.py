#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的数据库初始化脚本
"""

import sys
import os

# 设置输出编码，解决Windows下中文显示问题
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 导入必要的模块
    from app.core.database import engine, Base
    from app.models.user import User, Vehicle
    from app.models.charging import ChargingPile, ChargingQueue, ChargingRecord, ChargingMode, ChargingPileStatus
    from app.core.config import settings
    
    print("[INFO] 导入模块成功")
    
    # 创建所有数据库表
    print("[INFO] 创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("[SUCCESS] 数据库表创建完成")
    
    # 创建管理员用户和初始充电桩
    from sqlalchemy.orm import sessionmaker
    from passlib.context import CryptContext
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db = SessionLocal()
    try:
        # 检查是否已有管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@charging.com",
                hashed_password=pwd_context.hash("admin123"),
                is_admin=True
            )
            db.add(admin_user)
            print("[SUCCESS] 管理员账户创建完成: admin/admin123")
        else:
            print("[INFO] 管理员账户已存在")
        
        # 检查是否已有充电桩
        existing_piles = db.query(ChargingPile).count()
        if existing_piles == 0:
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
            
            print(f"[SUCCESS] 创建了 {settings.FAST_CHARGING_PILE_NUM} 个快充桩和 {settings.TRICKLE_CHARGING_PILE_NUM} 个慢充桩")
        else:
            print(f"[INFO] 已存在 {existing_piles} 个充电桩")
        
        db.commit()
        print("[SUCCESS] 数据库初始化完成！")
        
    except Exception as e:
        print(f"[ERROR] 数据库初始化过程中发生错误: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

except ImportError as e:
    print(f"[ERROR] 导入错误: {e}")
    print("[TIP] 请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] 初始化失败: {e}")
    sys.exit(1) 