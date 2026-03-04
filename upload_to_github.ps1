# Gunpla Price Tool - 上传到 GitHub
# PowerShell 脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Gunpla Price Tool - 上传到 GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
try {
    $gitVersion = git --version 2>&1
    Write-Host "[OK] Git 已安装: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] 错误: 未检测到 Git，请先安装 Git" -ForegroundColor Red
    Write-Host "下载地址: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

# 检查是否已初始化 Git 仓库
if (Test-Path .git) {
    Write-Host "[OK] Git 仓库已初始化" -ForegroundColor Green
} else {
    Write-Host "[信息] 初始化 Git 仓库..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[✗] 初始化失败" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "[1/5] 添加所有文件到暂存区..." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] 文件已添加到暂存区" -ForegroundColor Green
} else {
    Write-Host "[ERROR] 添加文件失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] 检查更改状态..." -ForegroundColor Cyan
$status = git status --short
if ($status) {
    Write-Host "以下文件将被提交:" -ForegroundColor Yellow
    git status --short
} else {
    Write-Host "[信息] 没有需要提交的更改" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] 创建提交..." -ForegroundColor Cyan
$commitMsg = Read-Host "请输入提交信息 (直接回车使用默认)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "Initial commit: Gunpla Price Tool"
}
git commit -m $commitMsg
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] 提交成功" -ForegroundColor Green
} else {
    Write-Host "[信息] 可能没有新的更改需要提交" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] 检查远程仓库配置..." -ForegroundColor Cyan
$remotes = git remote -v 2>&1
if ($remotes -match "origin") {
    Write-Host "[OK] 远程仓库已配置:" -ForegroundColor Green
    git remote -v
    Write-Host ""
    Write-Host "[5/5] 推送到 GitHub..." -ForegroundColor Cyan
    $push = Read-Host "是否现在推送到 GitHub? (y/n)"
    if ($push -eq "y" -or $push -eq "Y") {
        git branch -M main 2>&1 | Out-Null
        git push -u origin main
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] 推送成功！" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] 推送失败，请检查远程仓库配置和认证信息" -ForegroundColor Red
        }
    }
} else {
    Write-Host "[!] 尚未配置远程仓库" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请按照以下步骤操作:" -ForegroundColor Cyan
    Write-Host "1. 在 GitHub 上创建新仓库" -ForegroundColor White
    Write-Host "2. 执行以下命令连接远程仓库:" -ForegroundColor White
    Write-Host "   git remote add origin https://github.com/你的用户名/仓库名.git" -ForegroundColor Yellow
    Write-Host "3. 然后执行:" -ForegroundColor White
    Write-Host "   git branch -M main" -ForegroundColor Yellow
    Write-Host "   git push -u origin main" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "详细说明请查看 GITHUB_UPLOAD_GUIDE.md" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "按 Enter 键退出"
