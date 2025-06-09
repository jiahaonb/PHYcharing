import yaml
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List, Tuple

class Settings(BaseSettings):
    """系统配置类"""
    
    def __init__(self, **kwargs):
        # 先使用默认值初始化
        super().__init__(**kwargs)
        
        # 标记是否已从数据库加载配置
        self._database_loaded = False
    
    def _load_and_apply_database_config(self):
        """从数据库加载并应用配置"""
        try:
            config_data = self._load_database_config()
            
            # 动态设置属性值
            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    
            print(f"[OK] 已从数据库加载 {len(config_data)} 个配置项")
        except Exception as e:
            print(f"[WARNING] 从数据库加载配置失败，使用默认配置: {e}")
            # 如果数据库配置加载失败，使用默认配置
            self._apply_default_config()
    
    def _load_database_config(self) -> dict:
        """从数据库加载配置"""
        try:
            # 导入数据库相关模块
            from app.core.database import get_db
            from app.models.config import SystemConfig
            import json
            
            # 获取数据库会话
            db = next(get_db())
            
            # 查询所有启用的配置项
            configs = db.query(SystemConfig).filter(SystemConfig.is_active == True).all()
            
            config_data = {}
            for config in configs:
                # 将数据库中的配置键转换为类属性名
                attr_name = self._convert_config_key_to_attr(config.config_key)
                
                # 根据配置类型解析值
                if config.config_type == "integer":
                    value = int(config.config_value)
                elif config.config_type == "float":
                    value = float(config.config_value)
                elif config.config_type == "boolean":
                    value = self._parse_boolean(config.config_value)
                elif config.config_type == "json":
                    try:
                        value = json.loads(config.config_value)
                    except json.JSONDecodeError:
                        value = config.config_value
                else:
                    value = config.config_value
                
                config_data[attr_name] = value
            
            db.close()
            return config_data
            
        except Exception as e:
            print(f"[ERROR] 数据库配置加载失败: {e}")
            raise e
    
    def _convert_config_key_to_attr(self, config_key: str) -> str:
        """将数据库配置键转换为类属性名"""
        # 例如: "charging_piles.fast_charging_pile_num" -> "CHARGING_PILES_FAST_CHARGING_PILE_NUM"
        return config_key.replace(".", "_").upper()
    
    def _parse_boolean(self, value) -> bool:
        """解析布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "1", "yes", "on"]
        return bool(value)
    
    def _apply_default_config(self):
        """应用默认配置"""
        default_config = self._get_default_config()
        for key, value in default_config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def reload_config(self):
        """重新加载配置（供管理员修改配置后调用）"""
        try:
            self._load_and_apply_database_config()
            self._database_loaded = True
            print("[OK] 配置已重新加载")
        except Exception as e:
            print(f"[ERROR] 重新加载配置失败: {e}")
    
    def ensure_database_config_loaded(self):
        """确保已从数据库加载配置"""
        if not self._database_loaded:
            try:
                self._load_and_apply_database_config()
                self._database_loaded = True
                print("[OK] 首次从数据库加载配置")
            except Exception as e:
                print(f"[WARNING] 从数据库加载配置失败，使用默认配置: {e}")
                self._database_loaded = True  # 即使失败也标记为已尝试，避免重复尝试
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            # 充电桩配置
            "CHARGING_PILES_FAST_CHARGING_PILE_NUM": 2,
            "CHARGING_PILES_TRICKLE_CHARGING_PILE_NUM": 3,
            "CHARGING_PILES_FAST_CHARGING_POWER": 30.0,
            "CHARGING_PILES_TRICKLE_CHARGING_POWER": 10.0,
            
            # 队列配置
            "QUEUE_SETTINGS_WAITING_AREA_SIZE": 10,
            "QUEUE_SETTINGS_CHARGING_QUEUE_LEN": 3,
            "QUEUE_SETTINGS_MAX_QUEUE_WAIT_TIME": 120,
            
            # 计费配置
            "BILLING_PRICES_PEAK_TIME_PRICE": 1.0,
            "BILLING_PRICES_NORMAL_TIME_PRICE": 0.7,
            "BILLING_PRICES_VALLEY_TIME_PRICE": 0.4,
            "BILLING_PRICES_SERVICE_FEE_PRICE": 0.8,
            
            # 时段配置
            "BILLING_TIME_PERIODS_PEAK_TIMES": [[10, 15], [18, 21]],
            "BILLING_TIME_PERIODS_NORMAL_TIMES": [[7, 10], [15, 18], [21, 23]],
            "BILLING_TIME_PERIODS_VALLEY_TIMES": [[23, 7]],
            
            # 系统配置
            "SYSTEM_SCHEDULING_STRATEGY": "shortest_time",
            "SYSTEM_FAULT_DETECTION_INTERVAL": 30,
            "SYSTEM_AUTO_RESTART_ON_FAULT": True,
            "SYSTEM_MAX_FAULT_RESTART_ATTEMPTS": 3,
            
            # 安全配置
            "SECURITY_SESSION_TIMEOUT_MINUTES": 30,
            "SECURITY_MAX_LOGIN_ATTEMPTS": 5,
            "SECURITY_PASSWORD_MIN_LENGTH": 6,
            
            # 服务器配置
            "SERVER_BACKEND_HOST": "0.0.0.0",
            "SERVER_BACKEND_PORT": 8000,
            "SERVER_FRONTEND_HOST": "0.0.0.0", 
            "SERVER_FRONTEND_PORT": 3001,
            "SERVER_API_PREFIX": "/api/v1",
            
            # 数据库配置
            "DATABASE_URL": "sqlite:///./charging_system.db",
        }
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./charging_system.db"
    
    # 安全配置
    SECRET_KEY: str = "charging-station-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 充电站配置参数 - 从YAML文件加载
    CHARGING_PILES_FAST_CHARGING_PILE_NUM: int = 2
    CHARGING_PILES_TRICKLE_CHARGING_PILE_NUM: int = 3
    CHARGING_PILES_FAST_CHARGING_POWER: float = 30.0
    CHARGING_PILES_TRICKLE_CHARGING_POWER: float = 10.0
    
    # 队列配置
    QUEUE_SETTINGS_WAITING_AREA_SIZE: int = 10
    QUEUE_SETTINGS_CHARGING_QUEUE_LEN: int = 3  # 每个充电桩排队位数量
    QUEUE_SETTINGS_MAX_QUEUE_WAIT_TIME: int = 120
    
    # 计费配置
    BILLING_PRICES_PEAK_TIME_PRICE: float = 1.0
    BILLING_PRICES_NORMAL_TIME_PRICE: float = 0.7
    BILLING_PRICES_VALLEY_TIME_PRICE: float = 0.4
    BILLING_PRICES_SERVICE_FEE_PRICE: float = 0.8
    
    # 时段配置
    BILLING_TIME_PERIODS_PEAK_TIMES: List[List[int]] = [[10, 15], [18, 21]]
    BILLING_TIME_PERIODS_NORMAL_TIMES: List[List[int]] = [[7, 10], [15, 18], [21, 23]]
    BILLING_TIME_PERIODS_VALLEY_TIMES: List[List[int]] = [[23, 7]]
    
    # 系统配置
    SYSTEM_SCHEDULING_STRATEGY: str = "shortest_time"
    SYSTEM_FAULT_DETECTION_INTERVAL: int = 30
    SYSTEM_AUTO_RESTART_ON_FAULT: bool = True
    SYSTEM_MAX_FAULT_RESTART_ATTEMPTS: int = 3
    
    # 安全配置
    SECURITY_SESSION_TIMEOUT_MINUTES: int = 30
    SECURITY_MAX_LOGIN_ATTEMPTS: int = 5
    SECURITY_PASSWORD_MIN_LENGTH: int = 6
    
    # 服务器配置
    SERVER_BACKEND_HOST: str = "0.0.0.0"
    SERVER_BACKEND_PORT: int = 8000
    SERVER_FRONTEND_HOST: str = "0.0.0.0"
    SERVER_FRONTEND_PORT: int = 3001
    SERVER_API_PREFIX: str = "/api/v1"
    
    # 兼容性属性 - 保持向后兼容
    @property
    def FAST_CHARGING_PILE_NUM(self) -> int:
        return self.CHARGING_PILES_FAST_CHARGING_PILE_NUM
    
    @property
    def TRICKLE_CHARGING_PILE_NUM(self) -> int:
        return self.CHARGING_PILES_TRICKLE_CHARGING_PILE_NUM
    
    @property
    def FAST_CHARGING_POWER(self) -> float:
        return self.CHARGING_PILES_FAST_CHARGING_POWER
    
    @property
    def TRICKLE_CHARGING_POWER(self) -> float:
        return self.CHARGING_PILES_TRICKLE_CHARGING_POWER
    
    @property
    def WAITING_AREA_SIZE(self) -> int:
        return self.QUEUE_SETTINGS_WAITING_AREA_SIZE
    
    @property
    def CHARGING_QUEUE_LEN(self) -> int:
        return self.QUEUE_SETTINGS_CHARGING_QUEUE_LEN
    
    @property
    def PEAK_TIME_PRICE(self) -> float:
        return self.BILLING_PRICES_PEAK_TIME_PRICE
    
    @property
    def NORMAL_TIME_PRICE(self) -> float:
        return self.BILLING_PRICES_NORMAL_TIME_PRICE
    
    @property
    def VALLEY_TIME_PRICE(self) -> float:
        return self.BILLING_PRICES_VALLEY_TIME_PRICE
    
    @property
    def SERVICE_FEE_PRICE(self) -> float:
        return self.BILLING_PRICES_SERVICE_FEE_PRICE
    
    @property
    def PEAK_TIME_RANGES(self) -> List[Tuple[int, int]]:
        return [tuple(t) for t in self.BILLING_TIME_PERIODS_PEAK_TIMES]
    
    @property
    def NORMAL_TIME_RANGES(self) -> List[Tuple[int, int]]:
        return [tuple(t) for t in self.BILLING_TIME_PERIODS_NORMAL_TIMES]
    
    @property
    def VALLEY_TIME_RANGES(self) -> List[Tuple[int, int]]:
        return [tuple(t) for t in self.BILLING_TIME_PERIODS_VALLEY_TIMES]
    
    class Config:
        env_file = ".env"

settings = Settings() 