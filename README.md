# 高达价格查询工具

一个用于查询和管理高达（Gundam）模型价格的网页工具。

## 功能特性

- ✅ 多地区价格显示（日本、美国、中国）
- ✅ "算"数自动计算
- ✅ 想要列表和已购买列表管理
- ✅ 优惠券分析和推荐
- ✅ 分类搜索（按级别、名称等）

## 安装步骤

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 运行应用

```bash
python app.py
```

### 3. 访问应用

打开浏览器访问：http://localhost:5000

## 项目结构

```
gunpla_price_tool/
├── app.py              # Flask主应用
├── models.py           # 数据库模型
├── config.py           # 配置文件
├── requirements.txt    # Python依赖
├── docs/               # 使用/维护文档
├── scripts/            # 工具脚本
│   ├── scrapers/        # 各级别爬虫脚本
│   ├── migrations/      # 数据库迁移脚本
│   ├── debug/           # 调试脚本
│   └── examples/        # 示例脚本
├── templates/          # HTML模板
│   ├── base.html
│   ├── index.html
│   └── ...
└── static/             # 静态文件
    ├── css/
    └── js/
```

## 数据库

默认使用SQLite数据库，数据文件为 `gunpla.db`

首次运行时会自动创建数据库表结构。

## 开发计划

- [x] 项目基础搭建
- [ ] 完整的CRUD功能
- [ ] 想要列表和已购买列表功能
- [ ] 优惠券分析功能
- [ ] 价格自动更新（可选）

## 注意事项

- 汇率配置在 `config.py` 中，默认 1人民币 = 20日元（可根据实际汇率调整）
- 开发模式下会自动创建数据库表
- 建议在生产环境中使用PostgreSQL数据库

