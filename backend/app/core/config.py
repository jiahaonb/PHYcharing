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
        
        # 然后加载YAML配置文件并覆盖
        self._load_and_apply_config()
    
    def _load_and_apply_config(self):
        """加载并应用YAML配置"""
        config_data = self._load_config_file()
        
        # 动态设置属性值
        for key, value in config_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _load_config_file(self) -> dict:
        """加载YAML配置文件"""
        # 查找配置文件路径
        config_paths = [
            Path(__file__).parent.parent.parent.parent / "config.yaml",  # 项目根目录
            Path("config.yaml"),  # 当前目录
            Path("../config.yaml"),  # 上级目录
        ]
        
        config_data = {}
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        yaml_data = yaml.safe_load(f)
                        config_data = self._flatten_config(yaml_data)
                        print(f"[OK] 已加载配置文件: {config_path}")
                        break
                except Exception as e:
                    print(f"[ERROR] 加载配置文件失败 {config_path}: {e}")
                    continue
        else:
            print("[WARNING] 未找到配置文件，使用默认配置")
            config_data = self._get_default_config()
        
        return config_data
    
    def _flatten_config(self, config: dict, prefix: str = "") -> dict:
        """扁平化配置数据"""
        result = {}
        for key, value in config.items():
            if isinstance(value, dict):
                result.update(self._flatten_config(value, f"{prefix}{key}_"))
            else:
                result[f"{prefix}{key}".upper()] = value
        return result
    
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
            "QUEUE_SETTINGS_CHARGING_QUEUE_LEN": 5,
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
    QUEUE_SETTINGS_CHARGING_QUEUE_LEN: int = 5
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