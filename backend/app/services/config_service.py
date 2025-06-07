from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.config import SystemConfig
from app.core.database import get_db
import json
import threading
import time


class ConfigService:
    """配置服务 - 提供配置的动态加载和热重载功能"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._config_cache = {}
            self._last_update = None
            self._initialized = True
    
    def get_config(self, key: str, default: Any = None, db: Session = None) -> Any:
        """获取配置值"""
        if db is None:
            db = next(get_db())
        
        # 检查缓存是否需要刷新
        self._refresh_cache_if_needed(db)
        
        return self._config_cache.get(key, default)
    
    def get_charging_power(self, charging_mode: str, db: Session = None) -> float:
        """获取充电功率配置"""
        if charging_mode == "fast":
            return self.get_config("charging_piles.fast_charging_power", 30.0, db)
        else:
            return self.get_config("charging_piles.trickle_charging_power", 10.0, db)
    
    def get_charging_pile_config(self, db: Session = None) -> Dict[str, Any]:
        """获取充电桩配置"""
        return {
            "fast_charging_pile_num": self.get_config("charging_piles.fast_charging_pile_num", 2, db),
            "trickle_charging_pile_num": self.get_config("charging_piles.trickle_charging_pile_num", 3, db),
            "fast_charging_power": self.get_config("charging_piles.fast_charging_power", 30.0, db),
            "trickle_charging_power": self.get_config("charging_piles.trickle_charging_power", 10.0, db),
        }
    
    def get_billing_config(self, db: Session = None) -> Dict[str, Any]:
        """获取计费配置"""
        prices_json = self.get_config("billing.prices", "{}", db)
        time_periods_json = self.get_config("billing.time_periods", "{}", db)
        
        try:
            prices = json.loads(prices_json) if isinstance(prices_json, str) else prices_json
        except (json.JSONDecodeError, TypeError):
            prices = {
                "peak_time_price": 1.0,
                "normal_time_price": 0.7,
                "valley_time_price": 0.4,
                "service_fee_price": 0.8
            }
        
        try:
            time_periods = json.loads(time_periods_json) if isinstance(time_periods_json, str) else time_periods_json
        except (json.JSONDecodeError, TypeError):
            time_periods = {
                "peak_times": [[10, 15], [18, 21]],
                "normal_times": [[7, 10], [15, 18], [21, 23]],
                "valley_times": [[23, 7]]
            }
        
        return {
            "prices": prices,
            "time_periods": time_periods
        }
    
    def get_queue_config(self, db: Session = None) -> Dict[str, Any]:
        """获取队列配置"""
        return {
            "waiting_area_size": self.get_config("queue_settings.waiting_area_size", 10, db),
            "charging_queue_len": self.get_config("queue_settings.charging_queue_len", 5, db),
            "max_queue_wait_time": self.get_config("queue_settings.max_queue_wait_time", 120, db)
        }
    
    def get_system_config(self, db: Session = None) -> Dict[str, Any]:
        """获取系统配置"""
        return {
            "scheduling_strategy": self.get_config("system.scheduling_strategy", "shortest_time", db),
            "fault_detection_interval": self.get_config("system.fault_detection_interval", 30, db),
            "auto_restart_on_fault": self._parse_boolean(self.get_config("system.auto_restart_on_fault", "true", db)),
            "max_fault_restart_attempts": self.get_config("system.max_fault_restart_attempts", 3, db),
            "auto_cleanup_records": self._parse_boolean(self.get_config("system.auto_cleanup_records", "true", db)),
            "record_retention_days": self.get_config("system.record_retention_days", 90, db)
        }
    
    def invalidate_cache(self):
        """清空配置缓存，强制重新加载"""
        self._config_cache.clear()
        self._last_update = None
    
    def _refresh_cache_if_needed(self, db: Session):
        """如果需要则刷新缓存"""
        current_time = time.time()
        
        # 如果缓存为空或者超过5秒没有更新，则刷新
        if not self._config_cache or (self._last_update and current_time - self._last_update > 5):
            self._refresh_cache(db)
    
    def _refresh_cache(self, db: Session):
        """刷新配置缓存"""
        try:
            configs = db.query(SystemConfig).filter(SystemConfig.is_active == True).all()
            
            new_cache = {}
            for config in configs:
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
                
                new_cache[config.config_key] = value
            
            self._config_cache = new_cache
            self._last_update = time.time()
            
        except Exception as e:
            print(f"刷新配置缓存失败: {e}")
    
    def _parse_boolean(self, value) -> bool:
        """解析布尔值"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ["true", "1", "yes", "on"]
        return bool(value)


# 创建全局配置服务实例
config_service = ConfigService() 