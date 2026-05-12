@echo off
setlocal
chcp 65001 >nul
echo ========================================
echo 高达价格查询工具 - 启动脚本
echo ========================================
echo.

set "PY_CMD="
where py >nul 2>&1 && set "PY_CMD=py"
if not defined PY_CMD (
    where python >nul 2>&1 && set "PY_CMD=python"
)
if not defined PY_CMD (
    where python3 >nul 2>&1 && set "PY_CMD=python3"
)
if not defined PY_CMD goto :no_python

echo [1/3] 使用 %PY_CMD% 命令...
echo [2/3] 检查 Flask 依赖...
%PY_CMD% -c "import flask" >nul 2>&1
if errorlevel 1 goto :missing_deps

echo [3/3] 正在启动应用...
echo.
%PY_CMD% app.py
set "APP_EXIT=%errorlevel%"
if not "%APP_EXIT%"=="0" goto :app_failed
exit /b 0

:missing_deps
echo.
echo [错误] 未检测到 Flask 依赖，应用无法启动。
echo.
echo 请先安装依赖:
echo   %PY_CMD% -m pip install -r requirements.txt
echo.
pause
exit /b 1

:app_failed
echo.
echo [错误] 应用异常退出，退出码: %APP_EXIT%
echo 你可以手动执行以下命令查看完整错误:
echo   %PY_CMD% app.py
echo.
pause
exit /b %APP_EXIT%

:no_python
echo [错误] 未找到Python！
echo.
echo 请尝试以下方法：
echo 1. 使用 Anaconda Prompt 打开此目录
echo 2. 运行: python app.py
echo 3. 或者运行: py app.py
echo.
pause
exit /b 1
