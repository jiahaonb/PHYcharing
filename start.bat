@echo off
chcp 65001 >nul
title 智能充电桩调度计费系统
set PYTHONIOENCODING=utf-8

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                   🔌 智能充电桩调度计费系统                    ║
echo ║                 PHY Charging Station Manager                 ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 🔍 检查环境...

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo ✓ Python环境正常

:: 检查npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm未安装或不在PATH中
    pause
    exit /b 1
)
echo ✓ npm环境正常

:: 检查目录
if not exist "backend" (
    echo ❌ backend目录不存在
    pause
    exit /b 1
)
if not exist "frontend" (
    echo ❌ frontend目录不存在
    pause
    exit /b 1
)
echo ✓ 项目目录结构正常

echo.
echo 🚀 启动系统...
echo.

:: 使用Python启动脚本
python start.py

if errorlevel 1 (
    echo.
    echo ❌ 系统启动失败
    echo 💡 请检查:
    echo    1. Python依赖是否安装完整
    echo    2. Node.js依赖是否安装完整
    echo    3. 端口8000和8088是否被占用
    echo.
    pause
    exit /b 1
)

pause 