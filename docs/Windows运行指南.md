# Windows系统运行指南

## ✅ 好消息：您的电脑已经安装了Python！

从检查结果看，您已经通过**Anaconda**安装了Python 3.13，所以**完全可以运行Python程序**！

## 🔍 如何运行

由于您使用的是Anaconda，有几种方法可以运行应用：

### 方法1：使用 py 命令（推荐）

在PowerShell或命令提示符中运行：

```bash
cd gunpla_price_tool
py app.py
```

### 方法2：使用 Anaconda Prompt（最简单）

1. 打开 **Anaconda Prompt**（在开始菜单搜索"Anaconda Prompt"）
2. 切换到项目目录：
   ```bash
   cd C:\Users\bixi\Downloads\project2-1\gunpla_price_tool
   ```
3. 运行应用：
   ```bash
   python app.py
   ```

### 方法3：双击运行批处理文件（最简单）

1. 双击项目文件夹中的 `运行应用.bat` 文件
2. 会自动启动应用

## 📝 完整步骤

### 步骤1：打开终端

- **方法A**：在项目文件夹中，按住`Shift`键，然后右键点击文件夹空白处，选择"在此处打开PowerShell窗口"
- **方法B**：打开Anaconda Prompt

### 步骤2：进入项目目录

```bash
cd C:\Users\bixi\Downloads\project2-1\gunpla_price_tool
```

### 步骤3：运行应用

尝试以下命令（按顺序尝试，哪个能用就用哪个）：

```bash
py app.py
```

或者：

```bash
python app.py
```

### 步骤4：查看启动信息

如果看到类似这样的输出，说明启动成功：

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### 步骤5：打开浏览器

看到"Running on http://127.0.0.1:5000"后：

1. 打开浏览器（Chrome、Edge等）
2. 在地址栏输入：**http://localhost:5000**
3. 按回车

## ⚠️ 如果遇到问题

### 问题1：找不到python命令

**解决方案**：使用 `py` 命令，或者使用Anaconda Prompt

### 问题2：端口被占用

**解决方案**：修改 `app.py` 的最后一行，改成其他端口：

```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 改成5001
```

### 问题3：模块未找到

**解决方案**：确保已安装依赖：

```bash
pip install -r requirements.txt
```

或：

```bash
py -m pip install -r requirements.txt
```

## 💡 提示

- 您已经安装了Python 3.13（通过Anaconda）
- pip也可以正常使用
- 推荐使用Anaconda Prompt，因为它已经配置好了Python环境
- 运行应用时，保持终端窗口打开

## 🎯 快速测试

想测试Python是否可用？运行：

```bash
py --version
```

或：

```bash
python --version
```

应该显示 Python 3.13.x
