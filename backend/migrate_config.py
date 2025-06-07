#!/usr/bin/env python3
"""
配置迁移脚本
将config.yaml中的配置迁移到数据库中
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.database import engine, Base
    from app.core.init_config import initialize_config_from_yaml
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖包：pip install -r requirements.txt")
    sys.exit(1)


def create_tables():
    """创建数据库表"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def main():
    """主函数"""
    print("=" * 50)
    print("智能充电桩配置迁移工具")
    print("=" * 50)
    
    try:
        # 1. 创建数据库表
        create_tables()
        
        # 2. 初始化配置
        initialize_config_from_yaml()
        
        print("\n" + "=" * 50)
        print("配置迁移完成！")
        print("您现在可以：")
        print("1. 启动后端服务器")
        print("2. 在前端管理界面中管理配置")
        print("=" * 50)
        
    except Exception as e:
        print(f"配置迁移失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 