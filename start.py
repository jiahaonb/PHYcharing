#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能充电桩调度计费系统启动脚本
"""

import os
import sys
import subprocess
import time
import signal
import yaml
from pathlib import Path

# 设置输出编码，解决Windows下中文显示问题
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class ChargingSystemLauncher:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        self.config = self.load_config()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print("✅ 配置文件加载成功")
            return config
        except Exception as e:
            print(f"⚠️  配置文件加载失败: {e}")
            # 返回默认配置
            return {
                'server': {
                    'backend_host': '0.0.0.0',
                    'backend_port': 8000,
                    'frontend_port': 8088
                }
            }
    
    def print_header(self):
        """打印启动标题"""
        print("""
╔════════════════════════════════════════════════════════╗
║            🔌 智能充电桩调度计费系统                   ║
╚════════════════════════════════════════════════════════╝
        """)
        
        # 显示配置信息
        server_config = self.config.get('server', {})
        backend_port = server_config.get('backend_port', 8000)
        frontend_port = server_config.get('frontend_port', 8088)
        
        print(f"📋 系统配置:")
        print(f"   - 后端端口: {backend_port}")
        print(f"   - 前端端口: {frontend_port}")
        
        # 显示充电桩配置
        charging_config = self.config.get('charging_piles', {})
        if charging_config:
            print(f"   - 快充桩: {charging_config.get('fast_charging_pile_num', 2)}个")
            print(f"   - 慢充桩: {charging_config.get('trickle_charging_pile_num', 3)}个")
        print()
    
    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动后端服务...")
        
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print("❌ backend目录不存在")
            return False
        
        try:
            # 使用Popen启动，设置正确的工作目录
            self.backend_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                cwd=str(backend_dir)
            )
            
            # 等待服务启动
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                backend_port = self.config.get('server', {}).get('backend_port', 8000)
                print(f"✅ 后端服务启动成功 - http://0.0.0.0:{backend_port}")
                return True
            else:
                print("❌ 后端服务启动失败")
                return False
        except Exception as e:
            print(f"❌ 后端启动异常: {e}")
            return False
    
    def start_frontend(self):
        """启动前端服务"""
        print("🎨 启动前端服务...")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ frontend目录不存在")
            return False
        
        # Windows下使用npm.cmd，其他系统使用npm
        npm_cmd = 'npm.cmd' if os.name == 'nt' else 'npm'
        
        try:
            # 使用Popen启动，设置正确的工作目录
            self.frontend_process = subprocess.Popen(
                [npm_cmd, 'run', 'dev'],
                cwd=str(frontend_dir)
            )
            
            # 等待服务启动
            time.sleep(5)
            
            if self.frontend_process.poll() is None:
                frontend_port = self.config.get('server', {}).get('frontend_port', 8088)
                print(f"✅ 前端服务启动成功 - http://0.0.0.0:{frontend_port}")
                return True
            else:
                print("❌ 前端服务启动失败")
                return False
        except Exception as e:
            print(f"❌ 前端启动异常: {e}")
            return False
    
    def signal_handler(self, signum, frame):
        """处理停止信号"""
        print("\n\n🛑 正在停止服务...")
        self.shutdown()
    
    def shutdown(self):
        """关闭服务"""
        self.running = False
        
        if self.frontend_process:
            print("  停止前端服务...")
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        if self.backend_process:
            print("  停止后端服务...")
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        print("✅ 系统已停止")
        sys.exit(0)
    
    def run(self):
        """运行启动器"""
        self.print_header()
        
        # 启动后端
        if not self.start_backend():
            print("❌ 后端启动失败，退出...")
            return False
        
        # 启动前端
        if not self.start_frontend():
            print("⚠️  前端启动失败，但后端正常运行")
        
        # 显示访问信息
        backend_port = self.config.get('server', {}).get('backend_port', 8000)
        frontend_port = self.config.get('server', {}).get('frontend_port', 8088)
        
        print(f"""
🎉 系统启动完成！

🌐 访问地址:
   前端: http://0.0.0.0:{frontend_port}
   后端: http://0.0.0.0:{backend_port}
   API文档: http://0.0.0.0:{backend_port}/docs

👤 管理员账户: admin / admin123

按 Ctrl+C 停止系统
        """)
        
        # 保持运行
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return True

def main():
    """主启动函数"""
    launcher = ChargingSystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
