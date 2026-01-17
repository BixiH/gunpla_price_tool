"""
完善RG数据库 - 包含价格信息
改进价格爬取逻辑
"""
import requests
from bs4 import BeautifulSoup
import time
import re
from models import db, Gunpla
from app import app
import sys
import importlib.util

# 导入基础爬虫类
spec = importlib.util.spec_from_file_location("scraper78dm", "78dm_scraper.py")
scraper78dm_module = importlib.util.module_from_spec(spec)
sys.modules["scraper78dm"] = scraper78dm_module
spec.loader.exec_module(scraper78dm_module)
Scraper78DM = scraper78dm_module.Scraper78DM

def scrape_price_improved(url):
    """
    改进的价格爬取函数
    """
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_data = {}
        
        # 方法1：查找表格中的价格
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    
                    # 查找价格相关字段
                    if any(keyword in label for keyword in ['价格', '定价', '日元', '发售价格']):
                        # 提取价格数字
                        price_match = re.search(r'(\d+)', value.replace(',', '').replace('，', ''))
                        if price_match:
                            price = float(price_match.group(1))
                            if not price_data.get('price_jp_msrp'):
                                price_data['price_jp_msrp'] = price
        
        # 方法2：在页面文本中搜索价格模式
        page_text = soup.get_text()
        
        # 常见的价格模式
        price_patterns = [
            r'(\d+)\s*→\s*(\d+)\s*日元',  # 2500→2800日元
            r'定价[：:]\s*(\d+)',  # 定价：2500
            r'价格[：:]\s*(\d+)',  # 价格：2500
            r'发售价格[：:]\s*(\d+)',  # 发售价格：2500
            r'(\d+)\s*日元',  # 2500日元
            r'JPY\s*(\d+)',  # JPY 2500
            r'¥\s*(\d+)',  # ¥ 2500
        ]
        
        if not price_data.get('price_jp_msrp'):
            for pattern in price_patterns:
                match = re.search(pattern, page_text)
                if match:
                    # 如果有两个数字，取第一个（通常是定价）
                    price = float(match.group(1))
                    if 100 <= price <= 50000:  # 合理的价格范围
                        price_data['price_jp_msrp'] = price
                        break
        
        # 方法3：查找包含"价格"的div或span
        price_elements = soup.find_all(['div', 'span', 'p'], string=re.compile(r'.*\d+.*日元'))
        for elem in price_elements:
            text = elem.get_text(strip=True)
            match = re.search(r'(\d+)', text.replace(',', ''))
            if match:
                price = float(match.group(1))
                if 100 <= price <= 50000:
                    if not price_data.get('price_jp_msrp'):
                        price_data['price_jp_msrp'] = price
                        break
        
        return price_data
        
    except Exception as e:
        print(f"    价格爬取失败: {e}")
        return {}

def scrape_rg_with_price(include_price=True):
    """
    完善RG数据库，包含价格信息
    """
    scraper = Scraper78DM()
    
    # RG系列URL
    rg_url = 'https://acg.78dm.net/ct/341672.html'
    
    print("=" * 60)
    print("完善RG数据库 - 包含价格信息")
    print("=" * 60)
    print(f"URL: {rg_url}\n")
    
    try:
        response = scraper.session.get(rg_url, timeout=15)
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        gunpla_list = []
        
        # 查找所有模型链接
        links = soup.find_all('a', href=re.compile(r'/ct/\d+\.html'))
        
        print(f"找到 {len(links)} 个链接，正在处理...")
        
        # 获取页面文本，用于查找子分类
        page_text = soup.get_text()
        
        # 找到所有子分类标题的位置
        subcategory_markers = []
        patterns = [
            (r'普通版共\d+款', '普通版'),
            (r'网络限定版共\d+款', '网络限定版'),
            (r'其他限定版共\d+款', '其他限定版'),
            (r'EVANGELION系列共\d+款', 'EVANGELION系列'),
            (r'勇者王系列共\d+款', '勇者王系列'),
            (r'参考出品/开发中商品共\d+款', '参考出品/开发中'),
        ]
        
        for pattern, subcat in patterns:
            for match in re.finditer(pattern, page_text):
                subcategory_markers.append((match.start(), subcat))
        
        subcategory_markers.sort()
        
        # 非RG级别的关键词（这些是其他级别，不是RG产品）
        # 这些级别名称通常单独出现，或者只包含级别名称
        non_rg_grades = ['PG', 'MG', 'RE/100', 'HGUC', 'HGGTO', 'HGBF', 'HGBD', 'SDCS', 
                         'MB', 'MR魂', 'FIX', 'R魂', 'GU', 'FW食玩', 'G-FRAME', 'MSE',
                         '30MM', '万代机甲', '万代人形', '超合金魂', 'BEASTBOX', 'MEGABOX',
                         '骨装机兵', 'FA', 'FAG', '女神装置', 'MODEROID', '千值练', '海洋堂',
                         'threezero', 'Hot Toys', '麦克法兰', 'Sideshow', 'NECA', 'MEDICOM',
                         'Mezco', '田宫', '小号手', '威龙', 'MENG', '爱德美', '长谷川',
                         '青岛社', '威骏', '红星']
        
        # 其他品类关键词（这些是其他产品类别，不是RG产品）
        other_categories = [
            # 变形金刚及其子系列
            '变形金刚', 'SS系列', '大黄蜂美版', '变5美版', '日经', 'MP日版', 'G系列', 
            '王国', '地出', 'TFP美版', 'G1', '铁机巧', 'DLX',
            # 特摄周边及其子系列
            '特摄周边', 'S.H.Figuarts', 'DX假面骑士', 'S.I.C', 'RAH', 'X-PLUS', 
            'S.H.M', '假面骑士大集结', '掌动SHODO',
            # 潮流玩具及其子系列
            '潮流玩具', '52TOYS', 'POP MART', '末匠', '19八3', '奇谭俱乐部', 
            '撕裂熊', 'tokidoki', '豆芽水产',
            # 其他品类
            '科幻机甲', '美系周边', '军模民用'
        ]
        
        # 处理每个链接
        for link in links:
            name = link.get_text(strip=True)
            href = link.get('href', '')
            
            # 过滤无效链接
            if not name or len(name) < 2:
                continue
            
            # 跳过导航链接
            skip_keywords = ['更多', '显示', '隐藏', '加载', '级别分类详情']
            if any(keyword in name for keyword in skip_keywords):
                continue
            
            # 过滤非RG产品（这些是其他级别，不是RG系列的产品）
            # 检查链接文本是否完全匹配或只包含级别名称（这些是导航链接，不是产品）
            name_stripped = name.strip()
            if name_stripped in non_rg_grades:
                # 完全匹配级别名称，这是导航链接，跳过
                continue
            
            # 检查是否是其他级别的导航链接（包含"共X款"的级别名称）
            if any(grade in name and ('共' in name or '款' in name) for grade in non_rg_grades):
                # 这是其他级别的分类标题，跳过
                continue
            
            # 过滤其他品类（变形金刚、特摄周边、潮流玩具等）
            if name_stripped in other_categories:
                # 完全匹配其他品类名称，这是导航链接，跳过
                continue
            
            # 检查是否是其他品类的导航链接
            if any(category in name and ('共' in name or '款' in name) for category in other_categories):
                # 这是其他品类的分类标题，跳过
                continue
            
            # 跳过"往期未商品化企划"等没有实际产品的条目（这些通常没有价格）
            if '往期未商品化企划' in name or '未商品化' in name:
                continue
            
            # 确定子分类
            link_pos = page_text.find(name)
            link_subcategory = '普通版'
            for pos, subcat in subcategory_markers:
                if link_pos > pos:
                    link_subcategory = subcat
                else:
                    break
            
            # 构建完整URL
            if href.startswith('/'):
                full_url = scraper.base_url + href
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            # 提取基本信息
            data = {
                'name_cn': name,
                'grade': 'RG',
                'url': full_url,
                'subcategory': link_subcategory,
            }
            
            # 提取编号
            ms_number = scraper.extract_model_number(name)
            if ms_number:
                data['ms_number'] = ms_number
            
            gunpla_list.append(data)
        
        # 去重
        seen = set()
        unique_list = []
        for item in gunpla_list:
            name_key = item['name_cn']
            if name_key not in seen:
                seen.add(name_key)
                unique_list.append(item)
        
        # 统计子分类
        subcategory_count = {}
        for item in unique_list:
            subcat = item.get('subcategory', '未知')
            subcategory_count[subcat] = subcategory_count.get(subcat, 0) + 1
        
        print(f"\n找到 {len(unique_list)} 个RG模型")
        print("\n子分类统计：")
        for subcat, count in sorted(subcategory_count.items()):
            print(f"  {subcat}: {count} 个")
        
        # 爬取价格信息
        if include_price:
            print(f"\n开始爬取价格信息...")
            print(f"预计需要 {len(unique_list) * 1.5 / 60:.1f} 分钟\n")
            
            price_found = 0
            price_failed = 0
            items_to_remove = []  # 记录需要移除的项（参考出品/开发中且无价格）
            
            for i, item in enumerate(unique_list, 1):
                if item.get('url'):
                    print(f"[{i}/{len(unique_list)}] {item['name_cn']}")
                    
                    # 爬取价格
                    price_data = scrape_price_improved(item['url'])
                    
                    if price_data.get('price_jp_msrp'):
                        item['price_jp_msrp'] = price_data['price_jp_msrp']
                        
                        # 换算为美元和人民币定价
                        converted = scraper.convert_price(price_data['price_jp_msrp'])
                        item.update(converted)
                        
                        print(f"  价格: ¥{item['price_jp_msrp']:.0f} (JPY) → ${item.get('price_us_msrp', 0):.2f} (USD) / ¥{item.get('price_cn_msrp', 0):.2f} (CNY)")
                        price_found += 1
                    else:
                        # 如果是"参考出品/开发中"类且没有价格，标记为移除
                        if item.get('subcategory') == '参考出品/开发中':
                            print(f"  参考出品/开发中，无价格，将跳过录入")
                            items_to_remove.append(item)
                            price_failed += 1
                        else:
                            print(f"  未找到价格信息（但仍会录入）")
                            price_failed += 1
                    
                    # 延迟
                    if i < len(unique_list):
                        time.sleep(1.5)
            
            # 移除没有价格的参考出品/开发中项
            for item in items_to_remove:
                if item in unique_list:
                    unique_list.remove(item)
            
            print(f"\n价格爬取统计：")
            print(f"  找到价格: {price_found} 个")
            print(f"  未找到价格: {price_failed} 个")
            print(f"  跳过录入（参考出品/开发中且无价格）: {len(items_to_remove)} 个")
            print(f"  最终将录入: {len(unique_list)} 个模型")
        
        # 保存到数据库
        print(f"\n保存数据到数据库...")
        with app.app_context():
            saved_count = 0
            updated_count = 0
            skipped_count = 0
            
            for data in unique_list:
                try:
                    name = data.get('name_cn', '').strip()
                    if not name:
                        continue
                    
                    # 检查是否已存在
                    existing = Gunpla.query.filter_by(
                        name_cn=name,
                        grade='RG'
                    ).first()
                    
                    if existing:
                        # 更新所有信息
                        updated = False
                        if data.get('subcategory') and existing.subcategory != data.get('subcategory'):
                            existing.subcategory = data.get('subcategory')
                            updated = True
                        if data.get('ms_number') and not existing.ms_number:
                            existing.ms_number = data.get('ms_number')
                            updated = True
                        if data.get('price_jp_msrp') and not existing.price_jp_msrp:
                            existing.price_jp_msrp = data.get('price_jp_msrp')
                            updated = True
                        if data.get('price_us_msrp') and not existing.price_us_msrp:
                            existing.price_us_msrp = data.get('price_us_msrp')
                            updated = True
                        if data.get('price_cn_msrp') and not existing.price_cn_msrp:
                            existing.price_cn_msrp = data.get('price_cn_msrp')
                            updated = True
                        
                        if updated:
                            db.session.commit()
                            updated_count += 1
                        else:
                            skipped_count += 1
                        continue
                    
                    # 对于"参考出品/开发中"类，如果没有价格，可以选择不录入
                    # 但这里先录入，价格可以后续补充
                    gunpla = Gunpla(
                        name_cn=name,
                        grade='RG',
                        ms_number=data.get('ms_number'),
                        subcategory=data.get('subcategory'),
                        series='RG系列拼装模型',
                        price_jp_msrp=data.get('price_jp_msrp'),
                        price_us_msrp=data.get('price_us_msrp'),
                        price_cn_msrp=data.get('price_cn_msrp'),
                    )
                    
                    db.session.add(gunpla)
                    saved_count += 1
                    
                except Exception as e:
                    print(f"保存失败: {name} - {e}")
                    db.session.rollback()
                    continue
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("保存完成！")
            print(f"新增: {saved_count} 条")
            print(f"更新: {updated_count} 条")
            print(f"跳过（已存在）: {skipped_count} 条")
            print("=" * 60)
            
    except Exception as e:
        print(f"爬取失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    scrape_rg_with_price(include_price=True)
