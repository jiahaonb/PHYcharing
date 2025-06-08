"""
时区统一处理工具
确保前后端时间显示的一致性
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

# 设置为中国标准时间 (UTC+8)
CHINA_TZ = timezone(timedelta(hours=8))

def get_china_time() -> datetime:
    """
    获取中国标准时间 (UTC+8)
    返回带时区信息的datetime对象
    """
    return datetime.now(CHINA_TZ)

def utc_to_china_time(utc_time: datetime) -> datetime:
    """
    将UTC时间转换为中国标准时间
    """
    if utc_time is None:
        return None
    
    if utc_time.tzinfo is None:
        # 如果是naive datetime，假设它是UTC时间
        utc_time = utc_time.replace(tzinfo=timezone.utc)
    
    return utc_time.astimezone(CHINA_TZ)

def china_time_to_utc(china_time: datetime) -> datetime:
    """
    将中国标准时间转换为UTC时间
    """
    if china_time is None:
        return None
    
    if china_time.tzinfo is None:
        # 如果是naive datetime，假设它是中国时间
        china_time = china_time.replace(tzinfo=CHINA_TZ)
    
    return china_time.astimezone(timezone.utc)

def format_china_time(dt: Optional[datetime]) -> str:
    """
    将datetime格式化为中国时间字符串
    """
    if dt is None:
        return ""
    
    # 转换为中国时间
    china_dt = utc_to_china_time(dt)
    
    # 格式化为字符串，去掉时区信息（前端会当作本地时间处理）
    return china_dt.replace(tzinfo=None).isoformat()

def now_china_string() -> str:
    """
    获取当前中国时间的字符串表示
    """
    return format_china_time(get_china_time())

def format_currency(amount: Optional[float]) -> Optional[float]:
    """
    格式化金额，保留两位小数
    解决浮点数精度问题
    """
    if amount is None:
        return None
    return round(float(amount), 2) 