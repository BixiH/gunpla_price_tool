# GitHub 上传指南

## 前提条件

1. **安装 Git**
   - 如果还没有安装 Git，请访问 https://git-scm.com/download/win 下载并安装
   - 安装完成后，重启终端或命令提示符

2. **创建 GitHub 账户**
   - 访问 https://github.com 注册账户（如果还没有）

3. **配置 Git（首次使用）**
   ```bash
   git config --global user.name "你的用户名"
   git config --global user.email "你的邮箱"
   ```

## 上传步骤

### 方法一：使用命令行（推荐）

1. **打开终端/命令提示符**
   - 在项目文件夹中，按住 Shift + 右键，选择"在此处打开 PowerShell"或"在此处打开命令窗口"

2. **检查 Git 状态**
   ```bash
   git status
   ```

3. **如果还没有初始化 Git 仓库，执行：**
   ```bash
   git init
   ```

4. **添加所有文件到暂存区**
   ```bash
   git add .
   ```

5. **创建初始提交**
   ```bash
   git commit -m "Initial commit: Gunpla Price Tool"
   ```

6. **在 GitHub 上创建新仓库**
   - 登录 GitHub
   - 点击右上角的 "+" 号，选择 "New repository"
   - 输入仓库名称（例如：`gunpla_price_tool`）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
   - 点击 "Create repository"

7. **连接本地仓库到 GitHub**
   ```bash
   git remote add origin https://github.com/你的用户名/仓库名.git
   ```
   例如：
   ```bash
   git remote add origin https://github.com/yourusername/gunpla_price_tool.git
   ```

8. **推送代码到 GitHub**
   ```bash
   git branch -M main
   git push -u origin main
   ```

9. **如果遇到认证问题**
   - GitHub 已不再支持密码认证
   - 需要使用 Personal Access Token (PAT) 或 SSH 密钥
   - 生成 PAT：GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
   - 使用 PAT 作为密码进行推送

### 方法二：使用 GitHub Desktop（图形界面，更简单）

1. **下载 GitHub Desktop**
   - 访问 https://desktop.github.com/ 下载并安装

2. **登录 GitHub 账户**

3. **添加本地仓库**
   - File > Add Local Repository
   - 选择项目文件夹

4. **提交更改**
   - 在左侧输入提交信息
   - 点击 "Commit to main"

5. **发布到 GitHub**
   - 点击 "Publish repository"
   - 输入仓库名称和描述
   - 点击 "Publish Repository"

## 注意事项

⚠️ **重要：在上传前检查敏感信息**

1. **检查 `config.py` 文件**
   - 确保没有包含真实的密钥、密码等敏感信息
   - 如果包含敏感信息，请使用环境变量或 `.env` 文件（已在 .gitignore 中）

2. **数据库文件**
   - `gunpla.db` 已在 .gitignore 中，不会被上传
   - 如果需要上传初始数据，使用 `data/seed_gunpla.csv`

3. **环境变量**
   - 确保 `.env` 文件不会被上传（已在 .gitignore 中）
   - 在 README 中说明需要设置的环境变量

## 后续更新

每次修改代码后，使用以下命令更新 GitHub：

```bash
git add .
git commit -m "描述你的更改"
git push
```

## 常见问题

**Q: 提示 "fatal: not a git repository"**
A: 需要先执行 `git init` 初始化仓库

**Q: 提示 "remote origin already exists"**
A: 使用 `git remote set-url origin https://github.com/你的用户名/仓库名.git` 更新远程地址

**Q: 推送时要求输入用户名和密码**
A: 使用 Personal Access Token 作为密码，或配置 SSH 密钥

**Q: 如何查看远程仓库地址**
A: 使用 `git remote -v` 命令
