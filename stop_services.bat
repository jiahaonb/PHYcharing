@echo off
echo 🛑 停止充电桩系统服务...
echo.

echo 停止后端服务（Python进程）...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel%==0 (
    echo ✅ 后端服务已停止
) else (
    echo ℹ️  没有找到运行中的后端服务
)

echo 停止前端服务（Node.js进程）...
taskkill /F /IM node.exe >nul 2>&1
if %errorlevel%==0 (
    echo ✅ 前端服务已停止
) else (
    echo ℹ️  没有找到运行中的前端服务
)

echo.
echo 🎉 所有服务已停止！端口已释放。
echo 💡 您现在可以重新启动系统了。
pause 