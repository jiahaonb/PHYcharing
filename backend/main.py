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
    
    # 初始化数据库配置
    await init_database_config()
    
    # 从数据库加载配置到全局settings
    settings.ensure_database_config_loaded()
    
    # 恢复系统状态
    system_scheduler.recover_system_state()
    
    # 启动周期性调度器
    system_scheduler.start_periodic_scheduler()
    
    # 启动剩余时间更新服务
    from app.services.remaining_time_service import remaining_time_service
    remaining_time_service.start()
    
    logger.info("系统启动完成")

async def init_database_config():
    """检查并初始化数据库配置"""
    try:
        from app.core.database import get_db
        from app.models.config import SystemConfig
        
        # 获取数据库会话
        db = next(get_db())
        
        # 检查数据库中是否存在配置项
        config_count = db.query(SystemConfig).count()
        
        if config_count == 0:
            # 如果数据库中没有配置，创建基本的默认配置
            logger.info("数据库中没有配置项，创建默认配置...")
            created_count = create_default_config(db)
            logger.info(f"创建了 {created_count} 个默认配置项")
        else:
            logger.info(f"数据库中已存在 {config_count} 个配置项")
            
        db.close()
        
    except Exception as e:
        logger.error(f"检查数据库配置失败: {e}")
        # 不抛出异常，让系统继续启动

def create_default_config(db):
    """创建默认配置项"""
    from app.models.config import SystemConfig
    import json
    
    # 基本的默认配置
    default_configs = [
        # 充电桩配置
        {
            "config_key": "charging_piles.fast_charging_pile_num",
            "config_value": "2",
            "config_type": "integer",
            "description": "快充桩数量",
            "category": "charging_piles"
        },
        {
            "config_key": "charging_piles.trickle_charging_pile_num", 
            "config_value": "3",
            "config_type": "integer",
            "description": "慢充桩数量",
            "category": "charging_piles"
        },
        {
            "config_key": "charging_piles.fast_charging_power",
            "config_value": "30.0",
            "config_type": "float", 
            "description": "快充功率(度/小时)",
            "category": "charging_piles"
        },
        {
            "config_key": "charging_piles.trickle_charging_power",
            "config_value": "10.0",
            "config_type": "float",
            "description": "慢充功率(度/小时)", 
            "category": "charging_piles"
        },
        # 队列配置
        {
            "config_key": "queue_settings.waiting_area_size",
            "config_value": "10",
            "config_type": "integer",
            "description": "等候区车位容量",
            "category": "queue_settings"
        },
        {
            "config_key": "queue_settings.charging_queue_len",
            "config_value": "3",
            "config_type": "integer", 
            "description": "每个充电桩排队队列长度",
            "category": "queue_settings"
        },
        {
            "config_key": "queue_settings.max_queue_wait_time",
            "config_value": "120",
            "config_type": "integer",
            "description": "最大排队等待时间(分钟)",
            "category": "queue_settings"
        },
        # 计费配置
        {
            "config_key": "billing.prices.peak_time_price",
            "config_value": "1.0",
            "config_type": "float",
            "description": "峰时电价(元/度)",
            "category": "billing"
        },
        {
            "config_key": "billing.prices.normal_time_price", 
            "config_value": "0.7",
            "config_type": "float",
            "description": "平时电价(元/度)",
            "category": "billing"
        },
        {
            "config_key": "billing.prices.valley_time_price",
            "config_value": "0.4", 
            "config_type": "float",
            "description": "谷时电价(元/度)",
            "category": "billing"
        },
        {
            "config_key": "billing.prices.service_fee_price",
            "config_value": "0.8",
            "config_type": "float",
            "description": "服务费单价(元/度)",
            "category": "billing"
        },
        # 时段配置
        {
            "config_key": "billing.time_periods.peak_times",
            "config_value": json.dumps([[10, 15], [18, 21]]),
            "config_type": "json",
            "description": "峰时时段",
            "category": "billing"
        },
        {
            "config_key": "billing.time_periods.normal_times",
            "config_value": json.dumps([[7, 10], [15, 18], [21, 23]]),
            "config_type": "json", 
            "description": "平时时段",
            "category": "billing"
        },
        {
            "config_key": "billing.time_periods.valley_times",
            "config_value": json.dumps([[23, 7]]),
            "config_type": "json",
            "description": "谷时时段", 
            "category": "billing"
        },
        # 系统配置
        {
            "config_key": "system.scheduling_strategy",
            "config_value": "shortest_time",
            "config_type": "string",
            "description": "调度策略",
            "category": "system"
        },
        {
            "config_key": "system.fault_detection_interval",
            "config_value": "30",
            "config_type": "integer",
            "description": "故障检测间隔(秒)",
            "category": "system"
        },
        {
            "config_key": "system.auto_restart_on_fault",
            "config_value": "true",
            "config_type": "boolean",
            "description": "故障时自动重启充电桩",
            "category": "system"
        },
        {
            "config_key": "system.max_fault_restart_attempts",
            "config_value": "3",
            "config_type": "integer",
            "description": "最大故障重启尝试次数",
            "category": "system"
        }
    ]
    
    created_count = 0
    for config_data in default_configs:
        config = SystemConfig(
            config_key=config_data["config_key"],
            config_value=config_data["config_value"],
            config_type=config_data["config_type"],
            description=config_data["description"],
            category=config_data["category"],
            is_active=True
        )
        db.add(config)
        created_count += 1
    
    db.commit()
    return created_count

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