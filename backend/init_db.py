
import sys
sys.path.append('.')
from app.core.database import engine, Base
from app.models import *
from app.core.config import settings

# 创建所有表
Base.metadata.create_all(bind=engine)
print("数据库表创建完成")

# 创建管理员用户
from sqlalchemy.orm import sessionmaker
from app.models.user import User
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
        db.commit()
        print("管理员账户创建完成: admin/admin123")
    else:
        print("管理员账户已存在")
finally:
    db.close()
