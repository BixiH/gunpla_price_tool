@echo off
chcp 65001 >nul
echo ========================================
echo 高达价格查询工具 - 启动脚本
echo ========================================
echo.

REM 检查Python是否可用
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/2] 使用 py 命令启动应用...
    echo.
    py app.py
    goto :end
)

where python >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/2] 使用 python 命令启动应用...
    echo.
    python app.py
    goto :end
)

where python3 >nul 2>&1
if %errorlevel% equ 0 (
    echo [1/2] 使用 python3 命令启动应用...
    echo.
    python3 app.py
    goto :end
)

echo [错误] 未找到Python！
echo.
echo 请尝试以下方法：
echo 1. 使用 Anaconda Prompt 打开此目录
echo 2. 运行: python app.py
echo 3. 或者运行: py app.py
echo.
pause
:end
