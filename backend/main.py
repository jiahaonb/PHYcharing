from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import engine, Base
from app.services.system_scheduler import system_scheduler
import uvicorn
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="智能充电桩调度计费系统",
    description="PHY Charging Station Management System",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """系统启动事件"""
    logger.info("系统启动中...")
    
    # 恢复系统状态
    system_scheduler.recover_system_state()
    
    # 启动周期性调度器
    system_scheduler.start_periodic_scheduler()
    
    # 启动剩余时间更新服务
    from app.services.remaining_time_service import remaining_time_service
    remaining_time_service.start()
    
    logger.info("系统启动完成")

# 跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://0.0.0.0:8088", "http://localhost:8088"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.SERVER_API_PREFIX)

@app.get("/")
async def root():
    return {"message": "智能充电桩调度计费系统API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_BACKEND_HOST,
        port=settings.SERVER_BACKEND_PORT,
        reload=True
    ) 