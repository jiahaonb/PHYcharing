from fastapi import APIRouter
from .endpoints import auth, users, charging, admin, config

api_router = APIRouter()

# 包含各个端点路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(charging.router, prefix="/charging", tags=["充电"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理"])
api_router.include_router(config.router, prefix="/admin/config", tags=["配置管理"]) 