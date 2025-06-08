#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络配置检查脚本
检查服务是否正确绑定到 0.0.0.0 而不是 127.0.0.1
"""

import yaml
import sys
import socket
import subprocess
import time

def load_config():
    """加载配置文件"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 无法加载配置文件: {e}")
        return None

def check_port_binding(port):
    """检查端口绑定情况"""
    try:
        # 检查端口是否被占用
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('0.0.0.0', port))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {port} 在 0.0.0.0 上可访问")
            return True
        else:
            print(f"❌ 端口 {port} 在 0.0.0.0 上不可访问")
            return False
    except Exception as e:
        print(f"❌ 检查端口 {port} 时出错: {e}")
        return False

def check_local_binding(port):
    """检查本地绑定情况"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {port} 在 127.0.0.1 上可访问")
            return True
        else:
            print(f"❌ 端口 {port} 在 127.0.0.1 上不可访问")
            return False
    except Exception as e:
        print(f"❌ 检查本地端口 {port} 时出错: {e}")
        return False

def main():
    print("🔍 网络配置检查")
    print("=" * 50)
    
    # 加载配置
    config = load_config()
    if not config:
        return
    
    server_config = config.get('server', {})
    backend_host = server_config.get('backend_host', '127.0.0.1')
    backend_port = server_config.get('backend_port', 8000)
    frontend_host = server_config.get('frontend_host', '127.0.0.1')
    frontend_port = server_config.get('frontend_port', 8088)
    
    print(f"📋 当前配置:")
    print(f"   - 后端主机: {backend_host}:{backend_port}")
    print(f"   - 前端主机: {frontend_host}:{frontend_port}")
    print()
    
    # 检查配置是否正确
    if backend_host == '0.0.0.0' and frontend_host == '0.0.0.0':
        print("✅ 配置文件设置正确 - 使用 0.0.0.0 绑定所有网络接口")
    else:
        print("⚠️  配置文件设置 - 注意主机绑定设置")
        if backend_host != '0.0.0.0':
            print(f"   - 后端绑定到 {backend_host} (建议使用 0.0.0.0)")
        if frontend_host != '0.0.0.0':
            print(f"   - 前端绑定到 {frontend_host} (建议使用 0.0.0.0)")
    
    print()
    print("🌐 检查端口可访问性:")
    
    # 检查后端端口
    print(f"\n后端端口 {backend_port}:")
    check_local_binding(backend_port)
    check_port_binding(backend_port)
    
    # 检查前端端口
    print(f"\n前端端口 {frontend_port}:")
    check_local_binding(frontend_port)
    check_port_binding(frontend_port)
    
    print()
    print("💡 如果服务正在运行但端口检查失败，请确保:")
    print("   1. 服务已完全启动 (可能需要等待几秒)")
    print("   2. 防火墙允许对应端口通信")
    print("   3. 服务确实绑定到 0.0.0.0 而不是 127.0.0.1")

if __name__ == "__main__":
    main() 