@echo off
chcp 65001 >nul
echo ========================================
echo    Gunpla Price Tool - 上传到 GitHub
echo ========================================
echo.

REM 检查 Git 是否安装
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Git，请先安装 Git
    echo 下载地址: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [1/6] 检查 Git 状态...
git status
if %errorlevel% neq 0 (
    echo [信息] 初始化 Git 仓库...
    git init
)

echo.
echo [2/6] 添加所有文件到暂存区...
git add .

echo.
echo [3/6] 检查是否有未提交的更改...
git status --short
if %errorlevel% neq 0 (
    echo [信息] 没有需要提交的更改
) else (
    echo.
    echo [4/6] 创建提交...
    set /p commit_msg="请输入提交信息 (直接回车使用默认): "
    if "!commit_msg!"=="" set commit_msg=Initial commit: Gunpla Price Tool
    git commit -m "!commit_msg!"
)

echo.
echo [5/6] 检查远程仓库配置...
git remote -v
if %errorlevel% neq 0 (
    echo.
    echo [提示] 尚未配置远程仓库
    echo 请按照以下步骤操作:
    echo 1. 在 GitHub 上创建新仓库
    echo 2. 执行以下命令连接远程仓库:
    echo    git remote add origin https://github.com/你的用户名/仓库名.git
    echo 3. 然后执行: git push -u origin main
) else (
    echo.
    echo [6/6] 推送到 GitHub...
    echo 提示: 如果这是第一次推送，请先执行:
    echo   git branch -M main
    echo   git push -u origin main
    echo.
    set /p push_now="是否现在推送? (y/n): "
    if /i "!push_now!"=="y" (
        git branch -M main
        git push -u origin main
    )
)

echo.
echo ========================================
echo 完成！详细说明请查看 GITHUB_UPLOAD_GUIDE.md
echo ========================================
pause
