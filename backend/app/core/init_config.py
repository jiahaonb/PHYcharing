import yaml
import json
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.config import SystemConfig


def load_yaml_config(file_path: str = "config.yaml"):
    """从YAML文件加载配置"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"配置文件 {file_path} 不存在")
        return {}
    except yaml.YAMLError as e:
        print(f"解析配置文件失败: {e}")
        return {}


def init_database_config(db: Session, config_data: dict):
    """将配置数据初始化到数据库"""
    
    # 定义配置项映射
    config_mapping = {
        # 充电桩配置
        "charging_piles": {
            "fast_charging_pile_num": {
                "type": "integer",
                "description": "快充桩数量"
            },
            "trickle_charging_pile_num": {
                "type": "integer", 
                "description": "慢充桩数量"
            },
            "fast_charging_power": {
                "type": "float",
                "description": "快充功率 (度/小时)"
            },
            "trickle_charging_power": {
                "type": "float",
                "description": "慢充功率 (度/小时)"
            }
        },
        
        # 队列配置
        "queue_settings": {
            "waiting_area_size": {
                "type": "integer",
                "description": "等候区车位容量"
            },
            "charging_queue_len": {
                "type": "integer",
                "description": "每个充电桩排队队列长度"
            },
            "max_queue_wait_time": {
                "type": "integer",
                "description": "最大排队等待时间(分钟)"
            }
        },
        
        # 计费配置
        "billing": {
            "prices": {
                "type": "json",
                "description": "电价配置"
            },
            "time_periods": {
                "type": "json", 
                "description": "时段配置"
            }
        },
        
        # 系统配置
        "system": {
            "scheduling_strategy": {
                "type": "string",
                "description": "调度策略"
            },
            "fault_detection_interval": {
                "type": "integer",
                "description": "故障检测间隔(秒)"
            },
            "auto_restart_on_fault": {
                "type": "boolean",
                "description": "故障时自动重启充电桩"
            },
            "max_fault_restart_attempts": {
                "type": "integer",
                "description": "最大故障重启尝试次数"
            },
            "auto_cleanup_records": {
                "type": "boolean",
                "description": "自动清理历史记录"
            },
            "record_retention_days": {
                "type": "integer",
                "description": "记录保留天数"
            }
        },
        
        # 通知配置
        "notifications": {
            "enable_queue_notifications": {
                "type": "boolean",
                "description": "启用排队通知"
            },
            "enable_charging_complete_notifications": {
                "type": "boolean",
                "description": "启用充电完成通知"
            },
            "queue_position_update_interval": {
                "type": "integer",
                "description": "排队位置更新间隔(秒)"
            }
        },
        
        # 安全配置
        "security": {
            "session_timeout_minutes": {
                "type": "integer",
                "description": "会话超时时间(分钟)"
            },
            "max_login_attempts": {
                "type": "integer",
                "description": "最大登录尝试次数"
            },
            "password_min_length": {
                "type": "integer",
                "description": "密码最小长度"
            }
        },
        
        # 服务器配置
        "server": {
            "backend_host": {
                "type": "string",
                "description": "后端监听地址"
            },
            "backend_port": {
                "type": "integer",
                "description": "后端服务端口"
            },
            "frontend_host": {
                "type": "string",
                "description": "前端监听地址"
            },
            "frontend_port": {
                "type": "integer",
                "description": "前端服务端口"
            },
            "api_prefix": {
                "type": "string",
                "description": "API路径前缀"
            }
        },
        
        # 数据库配置
        "database": {
            "url": {
                "type": "string",
                "description": "数据库连接URL"
            },
            "backup_enabled": {
                "type": "boolean",
                "description": "启用数据库备份"
            },
            "backup_interval_hours": {
                "type": "integer",
                "description": "备份间隔(小时)"
            }
        }
    }
    
    created_count = 0
    updated_count = 0
    
    for category, category_data in config_data.items():
        if category not in config_mapping:
            print(f"未知配置分类: {category}")
            continue
            
        category_mapping = config_mapping[category]
        
        for key, value in category_data.items():
            if key not in category_mapping:
                print(f"未知配置项: {category}.{key}")
                continue
                
            config_info = category_mapping[key]
            config_key = f"{category}.{key}"
            
            # 处理配置值
            if config_info["type"] == "json":
                config_value = json.dumps(value, ensure_ascii=False)
            else:
                config_value = str(value)
            
            # 检查配置是否已存在
            existing_config = db.query(SystemConfig).filter(
                SystemConfig.config_key == config_key
            ).first()
            
            if existing_config:
                # 更新现有配置
                existing_config.config_value = config_value
                existing_config.description = config_info["description"]
                updated_count += 1
            else:
                # 创建新配置
                new_config = SystemConfig(
                    config_key=config_key,
                    config_value=config_value,
                    config_type=config_info["type"],
                    description=config_info["description"],
                    category=category,
                    is_active=True
                )
                db.add(new_config)
                created_count += 1
    
    db.commit()
    print(f"配置初始化完成: 创建 {created_count} 个, 更新 {updated_count} 个配置项")
    
    return created_count, updated_count


def initialize_config_from_yaml():
    """从YAML文件初始化配置到数据库"""
    print("开始从YAML文件初始化配置...")
    
    # 加载YAML配置，从项目根目录查找
    import os
    config_path = os.path.join("..", "config.yaml")
    config_data = load_yaml_config(config_path)
    if not config_data:
        print("未能加载配置数据")
        return
    
    # 获取数据库会话
    db = next(get_db())
    
    try:
        # 初始化配置
        created, updated = init_database_config(db, config_data)
        print(f"配置初始化成功: 新建 {created} 项, 更新 {updated} 项")
    except Exception as e:
        print(f"配置初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    initialize_config_from_yaml() 