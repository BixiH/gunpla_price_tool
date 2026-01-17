# HG级别拆分说明

## 概述

将原来的HG级别拆分为三个独立的级别：
- **HGUC** (HG Universal Century) - 宇宙世纪系列
- **HGGTO** (HG Gundam The Origin) - 高达起源/重力战线系列
- **HGBF/BD** (HG Build Fighters / Build Divers) - 创制系列/创战者/创形者

## 迁移步骤

### 1. 备份数据库
在运行迁移脚本之前，请先备份数据库文件 `gunpla.db`

### 2. 运行迁移脚本
```bash
cd gunpla_price_tool
py migrate_hg_to_subcategories.py
```

### 3. 检查迁移结果
脚本会显示：
- 迁移的模型数量
- 每个新级别的模型数量
- 无法判断的模型（会默认归类为HGUC）

### 4. 手动调整（如需要）
如果某些模型的分类不正确，可以：
- 在网页应用中编辑模型，修改级别
- 或者直接修改数据库

## 判断逻辑

迁移脚本会根据以下规则判断模型应该属于哪个级别：

### HGBF/BD
- 名称中包含：BF、BD、Build、创制、创战、创形
- 系列中包含：Build

### HGGTO
- 名称中包含：GTO、重力战线、THE ORIGIN
- 系列中包含：GTO、重力战线、THE ORIGIN

### HGUC（默认）
- 其他所有HG模型默认归类为HGUC

## 注意事项

1. **迁移脚本会修改数据库**，请确保已备份
2. 如果判断逻辑不准确，可能需要手动调整
3. 迁移后，原有的HG级别数据会被替换为新的三个级别之一
4. 如果数据库中已经有HGUC、HGGTO、HGBF/BD的数据，迁移脚本不会覆盖它们

## 后续工作

迁移完成后，您需要：
1. 为每个新级别创建专门的爬虫脚本（类似 `scrape_rg_with_price.py`）
2. 提供每个级别的78dm.net链接，以便创建爬虫
